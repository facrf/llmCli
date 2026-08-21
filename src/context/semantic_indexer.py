"""Semantic Codebase Indexer and Search (RAG) for llmCli.

Chunks codebase files by classes, functions, and logical blocks,
and builds an inverted index with TF-IDF vector similarity for instant,
zero-dependency, offline semantic code search.
"""
from __future__ import annotations

import ast
import json
import math
import os
import re
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from src.config import PROJECT_ROOT
from src.tools.base import BaseTool, ToolResult


@dataclass
class CodeChunk:
    file_path: str
    symbol_name: str
    symbol_type: str  # "class", "function", "module", "block"
    start_line: int
    end_line: int
    content: str


@dataclass
class SearchResult:
    chunk: CodeChunk
    score: float


class SemanticIndexer:
    SUPPORTED_EXTENSIONS = {
        ".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".rs", ".java",
        ".c", ".cpp", ".h", ".hpp", ".php", ".rb", ".md", ".json", ".yaml", ".yml"
    }

    IGNORE_DIRS = {
        ".git", ".venv", "venv", "__pycache__", "node_modules", "dist",
        "build", ".pytest_cache", ".ruff_cache", ".mypy_cache", ".cache"
    }

    def __init__(self, project_root: Optional[Path] = None) -> None:
        self.project_root = project_root or PROJECT_ROOT
        self.chunks: List[CodeChunk] = []
        self.doc_freq: Dict[str, int] = defaultdict(int)
        self.doc_lengths: List[int] = []
        self.avg_doc_len: float = 0.0
        self.total_docs: int = 0
        self.cache_path = self.project_root / ".cache" / "semantic_index.json"

    def _tokenize(self, text: str) -> List[str]:
        # Divide palavras em snake_case, camelCase e separadores comuns
        words = re.findall(r"[a-zA-Z0-9_]+", text)
        tokens = []
        for w in words:
            # Quebrar camelCase
            parts = re.findall(r"[A-Z]?[a-z0-9]+|[A-Z]+(?=[A-Z][a-z0-9]|\b)", w)
            if parts:
                tokens.extend(p.lower() for p in parts if len(p) > 1)
            tokens.append(w.lower())
        return tokens

    def _chunk_python_file(self, rel_path: str, content: str) -> List[CodeChunk]:
        chunks: List[CodeChunk] = []
        lines = content.splitlines()
        try:
            tree = ast.parse(content)
            for node in tree.body:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    start = node.lineno
                    end = getattr(node, "end_lineno", start + 20)
                    chunk_text = "\n".join(lines[start - 1:end])
                    chunks.append(CodeChunk(
                        file_path=rel_path,
                        symbol_name=node.name,
                        symbol_type="function",
                        start_line=start,
                        end_line=end,
                        content=chunk_text
                    ))
                elif isinstance(node, ast.ClassDef):
                    start = node.lineno
                    end = getattr(node, "end_lineno", start + 30)
                    chunk_text = "\n".join(lines[start - 1:end])
                    chunks.append(CodeChunk(
                        file_path=rel_path,
                        symbol_name=node.name,
                        symbol_type="class",
                        start_line=start,
                        end_line=end,
                        content=chunk_text
                    ))
        except Exception:
            pass

        # Se não extraiu nós AST ou sobraram linhas, criar chunk do arquivo
        if not chunks and content.strip():
            chunks.append(CodeChunk(
                file_path=rel_path,
                symbol_name=Path(rel_path).stem,
                symbol_type="module",
                start_line=1,
                end_line=len(lines),
                content=content[:3000]
            ))

        return chunks

    def _chunk_generic_file(self, rel_path: str, content: str) -> List[CodeChunk]:
        chunks: List[CodeChunk] = []
        lines = content.splitlines()
        chunk_size = 60
        overlap = 15

        for i in range(0, max(1, len(lines)), chunk_size - overlap):
            chunk_lines = lines[i:i + chunk_size]
            if not chunk_lines:
                break
            chunks.append(CodeChunk(
                file_path=rel_path,
                symbol_name=f"{Path(rel_path).name}:{i+1}",
                symbol_type="block",
                start_line=i + 1,
                end_line=i + len(chunk_lines),
                content="\n".join(chunk_lines)
            ))
        return chunks

    def index_codebase(self) -> int:
        """Varre o repositório e indexa todos os arquivos de código suportados."""
        self.chunks.clear()
        self.doc_freq.clear()
        self.doc_lengths.clear()

        for root, dirs, files in os.walk(self.project_root):
            dirs[:] = [d for d in dirs if d not in self.IGNORE_DIRS]
            for file in files:
                ext = Path(file).suffix.lower()
                if ext in self.SUPPORTED_EXTENSIONS:
                    full_path = Path(root) / file
                    try:
                        rel_path = str(full_path.relative_to(self.project_root))
                        content = full_path.read_text(encoding="utf-8", errors="ignore")
                        if not content.strip():
                            continue

                        if ext == ".py":
                            file_chunks = self._chunk_python_file(rel_path, content)
                        else:
                            file_chunks = self._chunk_generic_file(rel_path, content)

                        self.chunks.extend(file_chunks)
                    except Exception:
                        pass

        # Calcular estatísticas BM25 / TF-IDF
        self.total_docs = len(self.chunks)
        for chunk in self.chunks:
            tokens = self._tokenize(chunk.symbol_name + " " + chunk.content)
            self.doc_lengths.append(len(tokens))
            unique_tokens = set(tokens)
            for t in unique_tokens:
                self.doc_freq[t] += 1

        self.avg_doc_len = sum(self.doc_lengths) / max(1, self.total_docs)
        self.save_index()
        return self.total_docs

    def search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """Realiza busca semântica/léxica ponderada pelo BM25 no índice."""
        if not self.chunks:
            self.load_index()
            if not self.chunks:
                self.index_codebase()

        query_tokens = self._tokenize(query)
        if not query_tokens or self.total_docs == 0:
            return []

        scores: List[Tuple[int, float]] = []
        k1 = 1.5
        b = 0.75

        for idx, chunk in enumerate(self.chunks):
            doc_tokens = self._tokenize(chunk.symbol_name + " " + chunk.content)
            doc_len = len(doc_tokens)
            token_counts = Counter(doc_tokens)
            score = 0.0

            for q in query_tokens:
                tf = token_counts.get(q, 0)
                if tf == 0:
                    continue

                df = self.doc_freq.get(q, 1)
                idf = math.log(1.0 + (self.total_docs - df + 0.5) / (df + 0.5))

                # Ponderação BM25
                num = tf * (k1 + 1.0)
                den = tf + k1 * (1.0 - b + b * (doc_len / max(1.0, self.avg_doc_len)))
                score += idf * (num / max(1.0, den))

                # Bônus se o termo bater no nome do símbolo/função
                if q in chunk.symbol_name.lower():
                    score += 2.5

            if score > 0:
                scores.append((idx, score))

        scores.sort(key=lambda x: x[1], reverse=True)
        results = [
            SearchResult(chunk=self.chunks[idx], score=score)
            for idx, score in scores[:top_k]
        ]
        return results

    def save_index(self) -> None:
        try:
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "total_docs": self.total_docs,
                "chunks": [asdict(c) for c in self.chunks]
            }
            with open(self.cache_path, "w", encoding="utf-8") as f:
                json.dump(data, f)
        except Exception:
            pass

    def load_index(self) -> bool:
        if self.cache_path.exists():
            try:
                with open(self.cache_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.chunks = [CodeChunk(**item) for item in data.get("chunks", [])]
                    self.total_docs = len(self.chunks)
                    self.doc_freq.clear()
                    self.doc_lengths.clear()
                    for chunk in self.chunks:
                        tokens = self._tokenize(chunk.symbol_name + " " + chunk.content)
                        self.doc_lengths.append(len(tokens))
                        for t in set(tokens):
                            self.doc_freq[t] += 1
                    self.avg_doc_len = sum(self.doc_lengths) / max(1, self.total_docs)
                    return True
            except Exception:
                pass
        return False


class SemanticSearchTool(BaseTool):
    """Ferramenta para a IA realizar busca semântica na base de código."""
    def __init__(self, indexer: Optional[SemanticIndexer] = None) -> None:
        self.indexer = indexer or SemanticIndexer()

    @property
    def name(self) -> str:
        return "semantic_search"

    @property
    def description(self) -> str:
        return "Busca funções, classes e trechos relevantes na base de código por significado semântico e palavras-chave."

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Termo de busca, conceito técnico ou nome de função/classe a pesquisar"
                },
                "top_k": {
                    "type": "integer",
                    "description": "Número máximo de resultados a retornar (padrão: 5)"
                }
            },
            "required": ["query"]
        }

    async def execute(self, query: str, top_k: int = 5) -> ToolResult:
        results = self.indexer.search(query, top_k=top_k)
        if not results:
            return ToolResult(tool_call_id="", name=self.name, success=True, output=f"Nenhum trecho de código relevante encontrado para: '{query}'")

        formatted = []
        for r in results:
            c = r.chunk
            formatted.append(
                f"--- [{c.file_path} | Linhas {c.start_line}-{c.end_line} | {c.symbol_type}: {c.symbol_name} (Score: {r.score:.2f})] ---\n{c.content}\n"
            )

        return ToolResult(
            tool_call_id="",
            name=self.name,
            success=True,
            output="\n".join(formatted)
        )

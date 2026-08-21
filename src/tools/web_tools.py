"""Web search and URL content reader tools for llmCli."""
from __future__ import annotations

import os
import re
import urllib.parse
from typing import Any, Dict, List, Optional
import httpx

from src.tools.base import BaseTool, ToolResult


class WebSearchTool(BaseTool):
    """Ferramenta de pesquisa na web via DuckDuckGo ou APIs de busca."""
    
    @property
    def name(self) -> str:
        return "web_search"

    @property
    def description(self) -> str:
        return "Pesquisa informações atualizadas, documentações de APIs, bibliotecas e soluções de erros na Web."

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Termo de busca a ser pesquisado na internet"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Número máximo de resultados (padrão: 5)"
                }
            },
            "required": ["query"]
        }

    async def execute(self, query: str, max_results: int = 5) -> ToolResult:
        # Se tiver TAVILY_API_KEY configurada, usar Tavily
        tavily_key = os.getenv("TAVILY_API_KEY", "")
        if tavily_key:
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    resp = await client.post(
                        "https://api.tavily.com/search",
                        json={"api_key": tavily_key, "query": query, "max_results": max_results}
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        results = data.get("results", [])
                        lines = [f"Resultados da Web para '{query}':"]
                        for r in results:
                            lines.append(f"- **{r.get('title')}**: {r.get('content')}\n  URL: {r.get('url')}")
                        return ToolResult(tool_call_id="", name=self.name, success=True, output="\n".join(lines))
            except Exception:
                pass

        # Fallback gratuito via DuckDuckGo HTML Lite
        try:
            url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                resp = await client.get(url, headers=headers)
                if resp.status_code == 200:
                    html = resp.text
                    # Extrair resultados simples do DuckDuckGo HTML
                    snippets = re.findall(r'<a class="result__snippet[^>]*>(.*?)</a>', html, re.DOTALL)
                    titles = re.findall(r'<a class="result__url"[^>]*href="([^"]*)"[^>]*>(.*?)</a>', html, re.DOTALL)
                    
                    if snippets:
                        output_lines = [f"Resultados da Web para '{query}':"]
                        for i in range(min(max_results, len(snippets))):
                            snippet_clean = re.sub(r"<[^>]+>", "", snippets[i]).strip()
                            url_match = titles[i][0] if i < len(titles) else ""
                            output_lines.append(f"{i+1}. {snippet_clean}\n   Link: {url_match}")
                        return ToolResult(tool_call_id="", name=self.name, success=True, output="\n\n".join(output_lines))

            return ToolResult(
                tool_call_id="",
                name=self.name,
                success=True,
                output=f"Busca realizada para: '{query}'. Para melhores resultados na web, configure TAVILY_API_KEY no arquivo .env."
            )
        except Exception as e:
            return ToolResult(tool_call_id="", name=self.name, success=False, output=f"Erro na pesquisa web: {e}")


class ReadUrlTool(BaseTool):
    """Ferramenta para extrair o conteúdo de páginas e documentações web."""

    @property
    def name(self) -> str:
        return "read_url"

    @property
    def description(self) -> str:
        return "Lê e extrai o conteúdo de texto legível a partir de uma URL da web (ex: documentações, artigos, repositórios)."

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "URL HTTP ou HTTPS completa para leitura"
                },
                "max_chars": {
                    "type": "integer",
                    "description": "Limite máximo de caracteres a extrair (padrão: 6000)"
                }
            },
            "required": ["url"]
        }

    async def execute(self, url: str, max_chars: int = 6000) -> ToolResult:
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            async with httpx.AsyncClient(timeout=12.0, follow_redirects=True) as client:
                resp = await client.get(url, headers=headers)
                if resp.status_code != 200:
                    return ToolResult(tool_call_id="", name=self.name, success=False, output=f"Erro HTTP {resp.status_code} ao acessar {url}")

                html = resp.text
                # Remover scripts, estilos e tags HTML
                clean = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", html, flags=re.DOTALL | re.IGNORECASE)
                clean = re.sub(r"<[^>]+>", " ", clean)
                clean = re.sub(r"\s+", " ", clean).strip()

                truncated = clean[:max_chars]
                if len(clean) > max_chars:
                    truncated += f"\n... [conteúdo truncado em {max_chars} caracteres]"

                return ToolResult(
                    tool_call_id="",
                    name=self.name,
                    success=True,
                    output=f"Conteúdo extraído de {url}:\n\n{truncated}"
                )
        except Exception as e:
            return ToolResult(tool_call_id="", name=self.name, success=False, output=f"Falha ao ler URL {url}: {e}")

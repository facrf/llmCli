"""Configuration management for llmCli."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional
import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Carregar variáveis de ambiente do .env local
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")


class LocalEndpoints(BaseModel):
    llamacpp: str = Field(default_factory=lambda: os.getenv("LLAMACPP_BASE_URL", "http://localhost:8080"))
    ollama: str = Field(default_factory=lambda: os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"))
    lmstudio: str = Field(default_factory=lambda: os.getenv("LMSTUDIO_BASE_URL", "http://localhost:1234/v1"))
    vllm: str = Field(default_factory=lambda: os.getenv("VLLM_BASE_URL", "http://localhost:8000/v1"))


class GitConfig(BaseModel):
    auto_commit_on_edit: bool = True
    commit_prefix: str = "llmCli:"


class SecurityConfig(BaseModel):
    workspace_only: bool = True
    command_timeout_seconds: int = 60


class Config(BaseModel):
    project_root: Path = PROJECT_ROOT
    default_model: str = Field(default_factory=lambda: os.getenv("DEFAULT_MODEL", "gemini/gemini-2.5-flash"))
    active_model: str = ""
    yolo_mode: bool = Field(default_factory=lambda: os.getenv("YOLO_MODE", "false").lower() in ("true", "1", "yes"))
    temperature: float = 0.2
    max_tokens: int = 4096
    local_endpoints: LocalEndpoints = Field(default_factory=LocalEndpoints)
    git: GitConfig = Field(default_factory=GitConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)

    def model_post_init(self, __context: Any) -> None:
        if not self.active_model:
            self.active_model = self.default_model

    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> "Config":
        path = config_path or (PROJECT_ROOT / "config.yaml")
        data: Dict[str, Any] = {}
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    loaded = yaml.safe_load(f)
                    if isinstance(loaded, dict):
                        data = loaded
            except Exception as e:
                print(f"[Aviso] Erro ao ler {path}: {e}")

        # Se houver variáveis de ambiente explícitas, elas têm precedência
        if "DEFAULT_MODEL" in os.environ:
            data["default_model"] = os.environ["DEFAULT_MODEL"]
        if "YOLO_MODE" in os.environ:
            data["yolo_mode"] = os.environ["YOLO_MODE"].lower() in ("true", "1", "yes")

        endpoints = data.get("local_endpoints", {})
        if "LLAMACPP_BASE_URL" in os.environ:
            endpoints["llamacpp"] = os.environ["LLAMACPP_BASE_URL"]
        if "OLLAMA_BASE_URL" in os.environ:
            endpoints["ollama"] = os.environ["OLLAMA_BASE_URL"]
        if "LMSTUDIO_BASE_URL" in os.environ:
            endpoints["lmstudio"] = os.environ["LMSTUDIO_BASE_URL"]
        if "VLLM_BASE_URL" in os.environ:
            endpoints["vllm"] = os.environ["VLLM_BASE_URL"]
        data["local_endpoints"] = endpoints

        return cls(**data)

    def is_path_safe(self, target_path: str | Path) -> bool:
        """Verifica se o caminho está estritamente dentro do workspace permitido."""
        if not self.security.workspace_only:
            return True
        try:
            resolved = Path(target_path).resolve()
            return self.project_root in resolved.parents or resolved == self.project_root
        except Exception:
            return False


# Instância global compartilhada
_config_instance: Optional[Config] = None


def get_config() -> Config:
    global _config_instance
    if _config_instance is None:
        _config_instance = Config.load()
    return _config_instance

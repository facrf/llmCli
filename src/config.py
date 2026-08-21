"""Configuration management for llmCli."""
from __future__ import annotations

import json
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
    architect_mode: bool = False
    architect_model: str = Field(default_factory=lambda: os.getenv("ARCHITECT_MODEL", "gemini/gemini-2.5-pro"))
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

        cfg = cls(**data)

        # Aplicar preferências persistentes do usuário se disponíveis
        try:
            prefs = get_preferences()
            last_model = prefs.get_global_pref("last_active_model")
            if last_model and "DEFAULT_MODEL" not in os.environ:
                cfg.active_model = last_model
            # Aplicar preferências para o modelo ativo
            prefs.apply_model_preferences(cfg.active_model, cfg)
        except Exception:
            pass

        return cfg

    def is_path_safe(self, target_path: str | Path) -> bool:
        """Verifica se o caminho está estritamente dentro do workspace permitido."""
        if not self.security.workspace_only:
            return True
        try:
            resolved = Path(target_path).resolve()
            return self.project_root in resolved.parents or resolved == self.project_root
        except Exception:
            return False


class UserPreferences:
    """Gerenciador de preferências persistentes do usuário (globais e por LLM)."""
    def __init__(self, prefs_path: Optional[Path] = None) -> None:
        self.prefs_path = prefs_path or (Path.home() / ".llmcli_preferences.json")
        self.data: Dict[str, Any] = {
            "global": {},
            "models": {}
        }
        self.load()

    def load(self) -> None:
        if self.prefs_path.exists():
            try:
                with open(self.prefs_path, "r", encoding="utf-8") as f:
                    content = json.load(f)
                    if isinstance(content, dict):
                        self.data["global"] = content.get("global", {})
                        self.data["models"] = content.get("models", {})
            except Exception:
                pass

    def save(self) -> None:
        try:
            self.prefs_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.prefs_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def get_global_pref(self, key: str, default: Any = None) -> Any:
        return self.data.get("global", {}).get(key, default)

    def set_global_pref(self, key: str, value: Any) -> None:
        if "global" not in self.data:
            self.data["global"] = {}
        self.data["global"][key] = value
        self.save()

    def get_model_pref(self, model: str, key: str, default: Any = None) -> Any:
        """Obtém a preferência para o modelo indicado, caindo para a preferência global se não definida."""
        model_prefs = self.data.get("models", {}).get(model, {})
        if key in model_prefs:
            return model_prefs[key]
        return self.get_global_pref(key, default)

    def set_model_pref(self, model: str, key: str, value: Any) -> None:
        """Salva uma preferência específica para um modelo de LLM."""
        if not model:
            return
        if "models" not in self.data:
            self.data["models"] = {}
        if model not in self.data["models"]:
            self.data["models"][model] = {}
        self.data["models"][model][key] = value
        self.save()

    def apply_model_preferences(self, model: str, config: "Config") -> None:
        """Aplica preferências salvas para o modelo indicado no objeto Config."""
        if not model:
            return
        self.set_global_pref("last_active_model", model)

        yolo_val = self.get_model_pref(model, "yolo_mode", None)
        if yolo_val is not None:
            config.yolo_mode = bool(yolo_val)

        temp_val = self.get_model_pref(model, "temperature", None)
        if temp_val is not None:
            config.temperature = float(temp_val)

        arch_mode = self.get_global_pref("architect_mode", None)
        if arch_mode is not None:
            config.architect_mode = bool(arch_mode)

        arch_model = self.get_global_pref("architect_model", None)
        if arch_model:
            config.architect_model = str(arch_model)

    def reset(self) -> None:
        """Redefine todas as preferências de usuário e remove o arquivo de persistência."""
        self.data = {"global": {}, "models": {}}
        try:
            if self.prefs_path.exists():
                self.prefs_path.unlink()
        except Exception:
            pass


# Instância global compartilhada
_config_instance: Optional[Config] = None
_preferences_instance: Optional[UserPreferences] = None


def get_preferences(prefs_path: Optional[Path] = None) -> UserPreferences:
    global _preferences_instance
    if _preferences_instance is None or prefs_path is not None:
        _preferences_instance = UserPreferences(prefs_path=prefs_path)
    return _preferences_instance


def get_config() -> Config:
    global _config_instance
    if _config_instance is None:
        _config_instance = Config.load()
    return _config_instance

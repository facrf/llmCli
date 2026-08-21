"""Provider registry, model resolver, and auto-discovery."""
from __future__ import annotations

import os
from typing import Dict, List, Optional, Tuple
from src.config import get_config
from src.providers.anthropic import AnthropicProvider
from src.providers.base import LLMProvider
from src.providers.gemini import GeminiProvider
from src.providers.llamacpp import LlamaCppProvider
from src.providers.ollama import OllamaProvider
from src.providers.openai_compatible import OpenAICompatibleProvider


class ProviderRegistry:
    @staticmethod
    def create_provider(model_string: Optional[str] = None) -> LLMProvider:
        config = get_config()
        model_str = model_string or config.active_model or config.default_model

        # Normalizar prefixo se houver
        parts = model_str.split("/", 1)
        if len(parts) == 2:
            provider_type, model_name = parts[0].lower().replace(".", ""), parts[1]
        else:
            # Auto-inferência pelo nome
            raw = model_str.lower()
            if "gemini" in raw:
                provider_type, model_name = "gemini", model_str
            elif "claude" in raw:
                provider_type, model_name = "anthropic", model_str
            elif "gpt" in raw or "o1" in raw or "o3" in raw:
                provider_type, model_name = "openai", model_str
            elif "deepseek" in raw:
                provider_type, model_name = "deepseek", model_str
            elif "llama.cpp" in raw or "llamacpp" in raw:
                provider_type, model_name = "llamacpp", "default"
            elif "ollama" in raw:
                provider_type, model_name = "ollama", "qwen2.5-coder:latest"
            else:
                provider_type, model_name = "gemini", model_str

        # Instanciar provedor específico
        if provider_type in ("llamacpp", "llama_cpp", "llama"):
            return LlamaCppProvider(
                model_name=model_name,
                base_url=config.local_endpoints.llamacpp
            )

        elif provider_type == "ollama":
            return OllamaProvider(
                model_name=model_name,
                base_url=config.local_endpoints.ollama
            )

        elif provider_type == "lmstudio":
            return OpenAICompatibleProvider(
                model_name=model_name,
                base_url=config.local_endpoints.lmstudio,
                api_key="lm-studio"
            )

        elif provider_type == "vllm":
            return OpenAICompatibleProvider(
                model_name=model_name,
                base_url=config.local_endpoints.vllm,
                api_key="vllm"
            )

        elif provider_type == "gemini":
            return GeminiProvider(
                model_name=model_name
            )

        elif provider_type == "anthropic":
            return AnthropicProvider(
                model_name=model_name
            )

        elif provider_type == "openai":
            return OpenAICompatibleProvider(
                model_name=model_name,
                base_url="https://api.openai.com/v1",
                api_key=os.getenv("OPENAI_API_KEY", "")
            )

        elif provider_type == "deepseek":
            return OpenAICompatibleProvider(
                model_name=model_name,
                base_url="https://api.deepseek.com",
                api_key=os.getenv("DEEPSEEK_API_KEY", "")
            )

        elif provider_type == "groq":
            return OpenAICompatibleProvider(
                model_name=model_name,
                base_url="https://api.groq.com/openai/v1",
                api_key=os.getenv("GROQ_API_KEY", "")
            )

        elif provider_type == "openrouter":
            return OpenAICompatibleProvider(
                model_name=model_name,
                base_url="https://openrouter.ai/api/v1",
                api_key=os.getenv("OPENROUTER_API_KEY", ""),
                headers={"HTTP-Referer": "https://github.com/llmCli", "X-Title": "llmCli"}
            )

        # Fallback genérico para OpenAI-compatível
        return OpenAICompatibleProvider(
            model_name=model_name,
            base_url="https://api.openai.com/v1",
            api_key=os.getenv("OPENAI_API_KEY", "")
        )

    @staticmethod
    async def get_status_overview() -> List[Dict[str, Any]]:
        """Retorna visão geral do status de todos os provedores suportados."""
        config = get_config()
        results: List[Dict[str, Any]] = []

        # 1. Llama.cpp (Local)
        p_llama = LlamaCppProvider(base_url=config.local_endpoints.llamacpp)
        ok, msg = await p_llama.check_health()
        models = await p_llama.list_available_models() if ok else []
        results.append({
            "provider": "llama.cpp (Local)",
            "endpoint": config.local_endpoints.llamacpp,
            "status": "ONLINE" if ok else "OFFLINE",
            "detail": msg,
            "models": models,
            "example": "llamacpp/default"
        })

        # 2. Ollama (Local)
        p_ollama = OllamaProvider(base_url=config.local_endpoints.ollama)
        ok, msg = await p_ollama.check_health()
        models = await p_ollama.list_available_models() if ok else []
        results.append({
            "provider": "Ollama (Local)",
            "endpoint": config.local_endpoints.ollama,
            "status": "ONLINE" if ok else "OFFLINE",
            "detail": msg,
            "models": models,
            "example": "ollama/qwen2.5-coder:latest"
        })

        # 3. LM Studio (Local)
        p_lms = OpenAICompatibleProvider("default", base_url=config.local_endpoints.lmstudio)
        ok, msg = await p_lms.check_health()
        results.append({
            "provider": "LM Studio (Local)",
            "endpoint": config.local_endpoints.lmstudio,
            "status": "ONLINE" if ok else "OFFLINE",
            "detail": msg,
            "models": [],
            "example": "lmstudio/local-model"
        })

        # 4. Provedores em Nuvem (Verificação de Chave)
        cloud_providers = [
            ("Google Gemini", "GEMINI_API_KEY", "gemini/gemini-2.5-flash"),
            ("Anthropic Claude", "ANTHROPIC_API_KEY", "anthropic/claude-3-7-sonnet-20250219"),
            ("OpenAI", "OPENAI_API_KEY", "openai/gpt-4o"),
            ("DeepSeek", "DEEPSEEK_API_KEY", "deepseek/deepseek-chat"),
            ("Groq", "GROQ_API_KEY", "groq/llama-3.3-70b-versatile"),
            ("OpenRouter", "OPENROUTER_API_KEY", "openrouter/anthropic/claude-3.5-sonnet")
        ]

        for name, env_var, example in cloud_providers:
            has_key = bool(os.getenv(env_var))
            results.append({
                "provider": f"{name} (Nuvem)",
                "endpoint": "Cloud API",
                "status": "CONFIGURADO" if has_key else "SEM CHAVE",
                "detail": f"{env_var} {'presente no .env' if has_key else 'não definida'}",
                "models": [],
                "example": example
            })

        return results

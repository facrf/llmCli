"""Network scanner and automatic model discovery for local/remote LLM servers."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import httpx


@dataclass
class DiscoveredService:
    service_name: str
    base_url: str
    provider_type: str  # 'ollama', 'llamacpp', 'lmstudio', 'vllm', 'openai_compatible'
    status: str
    version: Optional[str] = None
    models: List[str] = field(default_factory=list)
    details: str = ""


class HostScanner:
    """Escaneia um IP ou hostname em busca de servidores de LLM ativos e seus modelos."""

    STANDARD_PROBES = [
        {"name": "Ollama", "port": 11434, "type": "ollama"},
        {"name": "llama.cpp", "port": 8080, "type": "llamacpp"},
        {"name": "llama.cpp (Alt)", "port": 8081, "type": "llamacpp"},
        {"name": "LM Studio", "port": 1234, "type": "lmstudio"},
        {"name": "vLLM / LocalAI", "port": 8000, "type": "vllm"},
        {"name": "Text-Gen-WebUI", "port": 5000, "type": "openai_compatible"}
    ]

    def __init__(self, host: str, timeout: float = 3.0) -> None:
        clean_host = host.strip()
        if clean_host.startswith("http://"):
            clean_host = clean_host[7:]
        elif clean_host.startswith("https://"):
            clean_host = clean_host[8:]
        clean_host = clean_host.split("/")[0].split(":")[0]  # pegar apenas o ip/host

        self.host = clean_host
        self.timeout = timeout

    async def _probe_ollama(self, client: httpx.AsyncClient, port: int) -> Optional[DiscoveredService]:
        url = f"http://{self.host}:{port}"
        try:
            res_ver = await client.get(f"{url}/api/version")
            if res_ver.status_code == 200:
                version = res_ver.json().get("version", "desconhecida")
                models: List[str] = []
                try:
                    res_tags = await client.get(f"{url}/api/tags")
                    if res_tags.status_code == 200:
                        data = res_tags.json()
                        models = [m.get("name") for m in data.get("models", []) if m.get("name")]
                except Exception:
                    pass

                return DiscoveredService(
                    service_name="Ollama",
                    base_url=url,
                    provider_type="ollama",
                    status="ONLINE",
                    version=version,
                    models=models,
                    details=f"Ollama v{version} ({len(models)} modelos instalados)"
                )
        except Exception:
            pass
        return None

    async def _probe_llamacpp(self, client: httpx.AsyncClient, port: int, name: str) -> Optional[DiscoveredService]:
        url = f"http://{self.host}:{port}"
        try:
            # 1. Tentar /props
            try:
                res_props = await client.get(f"{url}/props")
                if res_props.status_code == 200:
                    data = res_props.json()
                    gen = data.get("default_generation_settings", {})
                    ctx = gen.get("n_ctx", "")
                    models = []
                    try:
                        res_m = await client.get(f"{url}/v1/models")
                        if res_m.status_code == 200:
                            models = [m.get("id") for m in res_m.json().get("data", []) if m.get("id")]
                    except Exception:
                        pass
                    if not models:
                        models = ["default"]

                    return DiscoveredService(
                        service_name=name,
                        base_url=url,
                        provider_type="llamacpp",
                        status="ONLINE",
                        models=models,
                        details=f"llama.cpp server ativo (Contexto: {ctx} tokens)" if ctx else "llama.cpp server ativo"
                    )
            except Exception:
                pass

            # 2. Tentar /v1/models
            res_m = await client.get(f"{url}/v1/models")
            if res_m.status_code == 200:
                data = res_m.json()
                models = [m.get("id") for m in data.get("data", []) if m.get("id")] or ["default"]
                return DiscoveredService(
                    service_name=name,
                    base_url=url,
                    provider_type="llamacpp",
                    status="ONLINE",
                    models=models,
                    details=f"llama.cpp / API compatível ({len(models)} modelo(s))"
                )
        except Exception:
            pass
        return None

    async def _probe_openai_compatible(self, client: httpx.AsyncClient, port: int, name: str, ptype: str) -> Optional[DiscoveredService]:
        url = f"http://{self.host}:{port}/v1"
        try:
            res = await client.get(f"{url}/models")
            if res.status_code == 200:
                data = res.json()
                models = [m.get("id") for m in data.get("data", []) if m.get("id")]
                return DiscoveredService(
                    service_name=name,
                    base_url=url,
                    provider_type=ptype,
                    status="ONLINE",
                    models=models,
                    details=f"{name} ativo ({len(models)} modelos detectados)"
                )
        except Exception:
            pass
        return None

    async def _probe_target(self, client: httpx.AsyncClient, probe: Dict[str, Any]) -> Optional[DiscoveredService]:
        ptype = probe["type"]
        port = probe["port"]
        name = probe["name"]

        if ptype == "ollama":
            return await self._probe_ollama(client, port)
        elif ptype == "llamacpp":
            return await self._probe_llamacpp(client, port, name)
        else:
            return await self._probe_openai_compatible(client, port, name, ptype)

    async def scan(self) -> List[DiscoveredService]:
        """Executa varredura paralela em todas as portas suportadas no host alvo."""
        discovered: List[DiscoveredService] = []
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            tasks = [self._probe_target(client, probe) for probe in self.STANDARD_PROBES]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for res in results:
                if isinstance(res, DiscoveredService):
                    discovered.append(res)

        return discovered

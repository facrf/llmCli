"""Tests for network host scanner and model auto-discovery."""
import pytest
from src.providers.scanner import HostScanner, DiscoveredService


def test_host_scanner_normalization():
    s1 = HostScanner("http://192.168.0.11:11434")
    assert s1.host == "192.168.0.11"

    s2 = HostScanner("https://my-llm-host.local/path")
    assert s2.host == "my-llm-host.local"

    s3 = HostScanner("localhost")
    assert s3.host == "localhost"


@pytest.mark.asyncio
async def test_host_scanner_scan_localhost():
    # Deve executar sem levantar exceções mesmo que servidores estejam offline
    scanner = HostScanner("127.0.0.1", timeout=0.5)
    services = await scanner.scan()
    assert isinstance(services, list)

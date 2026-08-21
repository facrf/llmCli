"""Unit tests for global and per-model user preferences persistence."""
import pytest
from pathlib import Path
from src.config import Config, UserPreferences


def test_user_preferences_global_and_model_persistence(tmp_path: Path):
    prefs_file = tmp_path / "test_prefs.json"
    prefs = UserPreferences(prefs_path=prefs_file)

    # Definir preferência global
    prefs.set_global_pref("yolo_mode", False)
    prefs.set_global_pref("temperature", 0.3)
    assert prefs.get_global_pref("yolo_mode") is False
    assert prefs.get_global_pref("temperature") == 0.3

    # Definir preferência específica por modelo
    prefs.set_model_pref("ollama/qwen2.5-coder:7b", "yolo_mode", True)
    prefs.set_model_pref("ollama/qwen2.5-coder:7b", "temperature", 0.1)

    prefs.set_model_pref("gpt/codex", "yolo_mode", False)
    prefs.set_model_pref("gpt/codex", "temperature", 0.0)

    # Recarregar do arquivo em uma nova instância
    loaded_prefs = UserPreferences(prefs_path=prefs_file)
    assert loaded_prefs.get_model_pref("ollama/qwen2.5-coder:7b", "yolo_mode") is True
    assert loaded_prefs.get_model_pref("ollama/qwen2.5-coder:7b", "temperature") == 0.1

    assert loaded_prefs.get_model_pref("gpt/codex", "yolo_mode") is False
    assert loaded_prefs.get_model_pref("gpt/codex", "temperature") == 0.0

    # Modelo não configurado explicitamente herda preferência global
    assert loaded_prefs.get_model_pref("gemini/gemini-2.5-flash", "yolo_mode") is False
    assert loaded_prefs.get_model_pref("gemini/gemini-2.5-flash", "temperature") == 0.3


def test_apply_model_preferences_to_config(tmp_path: Path):
    prefs_file = tmp_path / "test_prefs_config.json"
    prefs = UserPreferences(prefs_path=prefs_file)

    cfg = Config()
    cfg.yolo_mode = False
    cfg.temperature = 0.5

    # Configurar preferência do modelo XYZ com YOLO ativado
    prefs.set_model_pref("model/xyz", "yolo_mode", True)
    prefs.set_model_pref("model/xyz", "temperature", 0.7)

    # Aplicar no config
    prefs.apply_model_preferences("model/xyz", cfg)
    assert cfg.yolo_mode is True
    assert cfg.temperature == 0.7
    assert prefs.get_global_pref("last_active_model") == "model/xyz"


def test_reset_user_preferences(tmp_path: Path):
    prefs_file = tmp_path / "test_prefs_reset.json"
    prefs = UserPreferences(prefs_path=prefs_file)

    prefs.set_model_pref("model/abc", "yolo_mode", True)
    assert prefs_file.exists()

    prefs.reset()
    assert not prefs_file.exists()
    assert prefs.get_model_pref("model/abc", "yolo_mode", False) is False

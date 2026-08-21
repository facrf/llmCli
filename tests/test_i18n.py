"""Unit tests for multi-language i18n support, language switching, aliases, and translations."""
import pytest
from src.i18n import (
    SUPPORTED_LANGUAGES,
    TRANSLATIONS,
    detect_system_language,
    get_active_language,
    resolve_language_code,
    set_active_language,
    t
)
from src.core.agent import Agent
from src.ui.repl import ReplSession


def test_supported_languages_list():
    assert "pt-BR" in SUPPORTED_LANGUAGES
    assert "en-US" in SUPPORTED_LANGUAGES
    assert "es-ES" in SUPPORTED_LANGUAGES
    assert "de-DE" in SUPPORTED_LANGUAGES
    assert "fr-FR" in SUPPORTED_LANGUAGES
    assert "zh-CN" in SUPPORTED_LANGUAGES
    assert "ru-RU" in SUPPORTED_LANGUAGES
    assert "hi-IN" in SUPPORTED_LANGUAGES
    assert len(SUPPORTED_LANGUAGES) == 8


def test_language_aliases_resolution():
    # Português
    assert resolve_language_code("pt") == "pt-BR"
    assert resolve_language_code("portugues") == "pt-BR"

    # Inglês
    assert resolve_language_code("en") == "en-US"
    assert resolve_language_code("english") == "en-US"

    # Espanhol
    assert resolve_language_code("es") == "es-ES"
    assert resolve_language_code("spanish") == "es-ES"

    # Alemão
    assert resolve_language_code("de") == "de-DE"
    assert resolve_language_code("german") == "de-DE"
    assert resolve_language_code("alemao") == "de-DE"

    # Francês
    assert resolve_language_code("fr") == "fr-FR"
    assert resolve_language_code("french") == "fr-FR"
    assert resolve_language_code("frances") == "fr-FR"

    # Chinês
    assert resolve_language_code("zh") == "zh-CN"
    assert resolve_language_code("chinese") == "zh-CN"
    assert resolve_language_code("chines") == "zh-CN"

    # Russo
    assert resolve_language_code("ru") == "ru-RU"
    assert resolve_language_code("russian") == "ru-RU"
    assert resolve_language_code("russo") == "ru-RU"

    # Hindi / Indiano
    assert resolve_language_code("hi") == "hi-IN"
    assert resolve_language_code("hindi") == "hi-IN"
    assert resolve_language_code("indiano") == "hi-IN"

    # Auto
    assert resolve_language_code("auto") == "auto"


def test_translation_keys_across_all_languages():
    required_keys = [
        "banner_subtitle",
        "banner_desc",
        "yolo_on",
        "yolo_off",
        "model_switched",
        "arch_on",
        "arch_off",
        "confirm_commit",
        "prompt_ai_instruction"
    ]
    for lang_code, trans_dict in TRANSLATIONS.items():
        for key in required_keys:
            assert key in trans_dict, f"Chave '{key}' ausente no idioma '{lang_code}'"


def test_set_active_language_and_translate():
    set_active_language("en-US")
    assert get_active_language() == "en-US"
    assert "YOLO MODE ENABLED" in t("yolo_on", model="test-model")

    set_active_language("de-DE")
    assert get_active_language() == "de-DE"
    assert "YOLO-MODUS AKTIVIERT" in t("yolo_on", model="test-model")

    set_active_language("fr-FR")
    assert get_active_language() == "fr-FR"
    assert "MODE YOLO ACTIVÉ" in t("yolo_on", model="test-model")

    set_active_language("zh-CN")
    assert get_active_language() == "zh-CN"
    assert "YOLO 模式" in t("yolo_on", model="test-model")

    set_active_language("ru-RU")
    assert get_active_language() == "ru-RU"
    assert "РЕЖИМ YOLO ВКЛЮЧЕН" in t("yolo_on", model="test-model")

    set_active_language("hi-IN")
    assert get_active_language() == "hi-IN"
    assert "YOLO मोड सक्षम" in t("yolo_on", model="test-model")

    # Restaurar para pt-BR
    set_active_language("pt-BR")
    assert get_active_language() == "pt-BR"
    assert "MODO YOLO ATIVADO" in t("yolo_on", model="test-model")


@pytest.mark.asyncio
async def test_slash_lang_command():
    agent = Agent()
    repl = ReplSession(agent=agent)

    # /lang exibe idiomas
    assert await repl.handle_slash_command("/lang") is True

    # /lang en altera para inglês
    assert await repl.handle_slash_command("/lang en") is True
    assert get_active_language() == "en-US"

    # /lang de altera para alemão
    assert await repl.handle_slash_command("/lang de") is True
    assert get_active_language() == "de-DE"

    # /lang fr altera para francês
    assert await repl.handle_slash_command("/lang fr") is True
    assert get_active_language() == "fr-FR"

    # /lang zh altera para chinês
    assert await repl.handle_slash_command("/lang zh") is True
    assert get_active_language() == "zh-CN"

    # /lang ru altera para russo
    assert await repl.handle_slash_command("/lang ru") is True
    assert get_active_language() == "ru-RU"

    # /lang hi altera para hindi
    assert await repl.handle_slash_command("/lang hi") is True
    assert get_active_language() == "hi-IN"

    # /lang auto
    assert await repl.handle_slash_command("/lang auto") is True

    # Restaurar pt-BR
    await repl.handle_slash_command("/lang pt")
    assert get_active_language() == "pt-BR"

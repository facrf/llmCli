# 🤖 llmCli

> **Language / Sprache:** 🇧🇷 [Português](README.md) | 🇺🇸 [English](README_EN.md) | 🇪🇸 [Español](README_ES.md) | 🇩🇪 [Deutsch](README_DE.md) | 🇫🇷 [Français](README_FR.md) | 🇨🇳 [中文](README_ZH.md) | 🇷🇺 [Русский](README_RU.md) | 🇮🇳 [हिन्दी](README_HI.md)

**llmCli** ist ein moderner interaktiver KI-Programmierassistent für das Terminal (inspiriert von OpenAI Codex, Aider und Claude Code), entwickelt für den nahtlosen Einsatz mit **lokalen LLMs** (llama.cpp, Ollama, LM Studio, vLLM) und **Cloud-LLMs** (Google Gemini, OpenAI GPT-4o / o-Serie, Anthropic Claude 3.7 / 3.5, DeepSeek V3 / R1, Groq, OpenRouter).

---

## 🌟 Hauptfunktionen

- 🔄 **Vollständige Hybrid-Unterstützung:**
  - **Lokal:** **llama.cpp** (`http://localhost:8080`), **Ollama** (`http://localhost:11434`), **LM Studio** (`http://localhost:1234/v1`), **vLLM** (`http://localhost:8000/v1`).
  - **Cloud:** **Google Gemini** (2.5 Flash / Pro), **OpenAI** (GPT-4o / o3-mini), **Anthropic Claude** (3.7 Sonnet / 3.5 Haiku), **DeepSeek** (V3 / R1), **Groq** und **OpenRouter**.
- 🏛️ **Architektenmodus (`/architect` / `/arch`):**
  - Zweistufige Pipeline: Ein hochintelligentes Modell (Architekt) plant die Lösung, und ein schnelles Modell (Editor) wendet die Änderungen im Code an.
- 🌐 **Mehrsprachige Lokalisierung (`/lang`):**
  - Native Unterstützung für 8 Sprachen (**Deutsch**, **Englisch**, **Portugiesisch**, **Spanisch**, **Französisch**, **Chinesisch**, **Russisch**, **Hindi**) mit automatischer Erkennung (`/lang auto`).
- ⚡ **YOLO-Modus (`/yolo`):**
  - Vollautonome Ausführung ohne wiederholte manuelle Bestätigungsabfragen.
- 🧠 **Offline Semantische Suche & Lokales RAG (`/index` / `/search`):**
  - AST-basierte Code-Indexierung mit BM25- und TF-IDF-Algorithmen ohne externe Vektordatenbank.
- 🔌 **Model Context Protocol (MCP) (`/mcp`):**
  - Dynamische Integration externer MCP-Server und Werkzeuge.
- 🌐 **Websuche & URL-Leser (`/web` / `read_url`):**
  - Live-Recherche nach Dokumentationen und Fehlerbehebungen via DuckDuckGo oder Tavily API.
- 📋 **Checklisten- & Aufgabenplaner (`/plan` / `/todo`):**
  - Automatische Aufgabenaufteilung aus Zielbeschreibungen mit Fortschrittsanzeige im Terminal.
- 🧪 **Testgenerierung & Auto-Reparatur (`/gentest` / `/test`):**
  - Automatische Erstellung von `pytest`-Testsuiten und Fehleranalyse mit KI-Korrektur.
- 💾 **Dauerhafte Benutzereinstellungen:**
  - Speicherung von aktivem Modell, YOLO-Status, Sprache und Temperatur in `~/.llmcli_preferences.json`.
- 📄 **Sitzungsexport (`/export`):**
  - Export von Sitzungsberichten nach **Markdown** (`.md`) oder **HTML** (`.html`).
- 🛡️ **Sicherheit & Git-Wiederherstellungspunkte:**
  - Isolierung auf den Projektordner ([AGENTS.md](file:///storage/www/projetos/utils/llmCli/AGENTS.md)).
  - Automatische Git-Snapshots vor jeder Änderung mit Sofort-Rücknahme über `/undo`.

---

## 🚀 Schnellstart

```bash
# 1. Virtuelle Umgebung erstellen und aktivieren
python3 -m venv .venv
source .venv/bin/activate

# 2. Abhängigkeiten installieren
pip install -r requirements.txt

# 3. Umgebungsvariablen anpassen
cp .env.example .env

# 4. Terminal starten
./bin/llm-cli
```

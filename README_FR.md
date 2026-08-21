# 🤖 llmCli

> **Language / Langue :** 🇧🇷 [Português](README.md) | 🇺🇸 [English](README_EN.md) | 🇪🇸 [Español](README_ES.md) | 🇩🇪 [Deutsch](README_DE.md) | 🇫🇷 [Français](README_FR.md) | 🇨🇳 [中文](README_ZH.md) | 🇷🇺 [Русский](README_RU.md) | 🇮🇳 [हिन्दी](README_HI.md)

**llmCli** est un assistant de développement interactif par intelligence artificielle dans le terminal (inspiré d'OpenAI Codex, Aider et Claude Code), conçu pour fonctionner en parfaite synergie avec les **LLMs locaux** (llama.cpp, Ollama, LM Studio, vLLM) et les **LLMs dans le cloud** (Google Gemini, OpenAI GPT-4o / série o, Anthropic Claude 3.7 / 3.5, DeepSeek V3 / R1, Groq, OpenRouter).

---

## 🌟 Fonctionnalités Clés

- 🔄 **Support Hybride Complet :**
  - **Local :** **llama.cpp** (`http://localhost:8080`), **Ollama** (`http://localhost:11434`), **LM Studio** (`http://localhost:1234/v1`), **vLLM** (`http://localhost:8000/v1`).
  - **Cloud :** **Google Gemini** (2.5 Flash / Pro), **OpenAI** (GPT-4o / o3-mini), **Anthropic Claude** (3.7 Sonnet / 3.5 Haiku), **DeepSeek** (V3 / R1), **Groq** et **OpenRouter**.
- 🏛️ **Mode Architecte (`/architect` / `/arch`) :**
  - Pipeline à deux étapes : un modèle de haut raisonnement (Architecte) élabore le plan technique, et un modèle rapide (Éditeur) applique les modifications dans le code.
- 🌐 **Support Multi-langues (`/lang`) :**
  - Support natif de 8 langues (**Français**, **Anglais**, **Portugais**, **Espagnol**, **Allemand**, **Chinois**, **Russe**, **Hindi**) avec détection automatique du système (`/lang auto`).
- ⚡ **Mode YOLO (`/yolo`) :**
  - Mode d'exécution autonome continue sans interruption pour confirmation manuelle.
- 🧠 **Recherche Sémantique & RAG Local (`/index` / `/search`) :**
  - Indexation locale par AST avec algorithmes BM25 et TF-IDF, 100 % hors ligne.
- 🔌 **Client Model Context Protocol (MCP) (`/mcp`) :**
  - Connexion dynamique aux serveurs et outils MCP externes.
- 🌐 **Recherche Web & Lecteur d'URLs (`/web` / `read_url`) :**
  - Consultation en direct de documentations et solutions via DuckDuckGo ou Tavily API.
- 📋 **Checklist & Planificateur (`/plan` / `/todo`) :**
  - Décomposition automatique d'objectifs en liste de tâches interactive.
- 🧪 **Génération de Tests & Auto-Correction (`/gentest` / `/test`) :**
  - Création de tests `pytest` et réparation automatique du code en cas d'échec.
- 💾 **Préférences Utilisateur Persistantes :**
  - Sauvegarde automatique dans `~/.llmcli_preferences.json`.
- 📄 **Exportation de Sessions (`/export`) :**
  - Génération de rapports complets en **Markdown** (`.md`) ou **HTML stylisé** (`.html`).
- 🛡️ **Sécurité & Points de Restauration Git :**
  - Confinement au dossier du projet ([AGENTS.md](file:///storage/www/projetos/utils/llmCli/AGENTS.md)).
  - Snapshots Git automatiques avant chaque modification pour annulation immédiate avec `/undo`.

---

## 🚀 Démarrage Rapide

```bash
# 1. Créer et activer l'environnement virtuel
python3 -m venv .venv
source .venv/bin/activate

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Configurer l'environnement
cp .env.example .env

# 4. Lancer le terminal interactif
./bin/llm-cli
```

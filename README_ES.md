# 🤖 llmCli

> **Language / Idioma:** 🇧🇷 [Português](README.md) | 🇺🇸 [English](README_EN.md) | 🇪🇸 [Español](README_ES.md) | 🇩🇪 [Deutsch](README_DE.md) | 🇫🇷 [Français](README_FR.md) | 🇨🇳 [中文](README_ZH.md) | 🇷🇺 [Русский](README_RU.md) | 🇮🇳 [हिन्दी](README_HI.md)

**llmCli** es un asistente interactivo de inteligencia artificial de última generación para desarrollo en terminal (inspirado en OpenAI Codex, Aider y Claude Code), diseñado para operar fluidamente con **LLMs locales** (llama.cpp, Ollama, LM Studio, vLLM) y **LLMs en la nube** (Google Gemini, OpenAI GPT-4o / o-series, Anthropic Claude 3.7 / 3.5, DeepSeek V3 / R1, Groq, OpenRouter).

---

## 🌟 Características Principales

- 🔄 **Soporte Híbrido Completo:**
  - **Local:** **llama.cpp** (`http://localhost:8080`), **Ollama** (`http://localhost:11434`), **LM Studio** (`http://localhost:1234/v1`), **vLLM** (`http://localhost:8000/v1`).
  - **Nube:** **Google Gemini** (2.5 Flash / Pro), **OpenAI** (GPT-4o / o3-mini), **Anthropic Claude** (3.7 Sonnet / 3.5 Haiku), **DeepSeek** (V3 / R1), **Groq** y **OpenRouter**.
- 🏛️ **Modo Arquitecto (`/architect` / `/arch`):**
  - Pipeline en dos etapas: un modelo de alto razonamiento (Arquitecto) formula el plan técnico estructurado y un modelo rápido (Editor) aplica los cambios y ejecuta herramientas en el código.
- 🌐 **Internacionalización y Multi-idioma (`/lang`):**
  - Soporte nativo para 8 idiomas (**Español**, **Portugués**, **Inglés**, **Alemán**, **Francés**, **Chino**, **Ruso**, **Hindi**) con detección automática mediante locale del sistema operativo (`/lang auto`).
- ⚡ **Modo YOLO (`/yolo`):**
  - Ejecución autónoma total. Aplica ediciones y ejecuta comandos de terminal sin detenerse para pedir confirmación manual en cada paso.
- 🧠 **Búsqueda Semántica y RAG Local (`/index` / `/search`):**
  - Indexación de código basada en AST para clases, funciones y bloques con puntuación BM25 y TF-IDF 100% offline.
- 🔌 **Integración MCP (Model Context Protocol) (`/mcp`):**
  - Conexión dinámica a servidores MCP externos definidos en `mcp_servers.json` o `~/.llmcli_mcp.json`.
- 🌐 **Búsqueda Web y Lector de URLs (`/web` / `read_url`):**
  - Consulta en tiempo real de documentación, bibliotecas y soluciones de errores en la web mediante DuckDuckGo o Tavily API.
- 📋 **Checklist y Planificador de Tareas (`/plan` / `/todo`):**
  - Desglose automático de objetivos en listas de tareas interactivas.
- 🧪 **Generación y Corrección de Pruebas (`/gentest` / `/test`):**
  - Creación automática de suites de pruebas con `pytest` y auto-corrección de fallos guiada por IA.
- 💾 **Preferencias Persistentes de Usuario:**
  - Persistencia de modelo activo, modo YOLO, idioma y temperatura en `~/.llmcli_preferences.json`.
- 📄 **Exportación de Sesiones (`/export`):**
  - Exportación de informes completos en formato **Markdown** (`.md`) o **HTML interactivo** (`.html`).
- 🛡️ **Seguridad Estricta y Checkpoints Git:**
  - Aislamiento riguroso del workspace ([AGENTS.md](file:///storage/www/projetos/utils/llmCli/AGENTS.md)).
  - Snapshots automáticos de Git antes de cada cambio para reversión inmediata con `/undo`.
  - Mensajes de commit semánticos (`/commit`) y revisiones de código automáticas (`/review`).

---

## 🚀 Inicio Rápido

```bash
# 1. Crear y activar entorno virtual
python3 -m venv .venv
source .venv/bin/activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar variables de entorno
cp .env.example .env

# 4. Iniciar sesión interactiva
./bin/llm-cli
```

---

## 🎮 Comandos Slash Principales

| Comando | Descripción |
| :--- | :--- |
| `/yolo` | Alterna el modo autónomo YOLO (on/off). |
| `/architect` | Alterna el Modo Arquitecto (planificador + editor). |
| `/lang <código>` | Cambia el idioma (`es`, `en`, `pt`, `de`, `fr`, `zh`, `ru`, `hi`, `auto`). |
| `/model [nombre]` | Menú interactivo o cambio de modelo de LLM. |
| `/models` | Estado de salud y conectividad de todos los proveedores. |
| `/scan <ip>` | Escanea servidores y modelos de LLM en un host de la red. |
| `/host <ip>` | Conecta y configura endpoints hacia el servidor remoto. |
| `/add <ruta>` | Añade archivo o carpeta al contexto de la IA. |
| `/drop <ruta>` | Quita un archivo del contexto. |
| `/files` | Lista los archivos en el contexto actual. |
| `/index` | Indexa el código para búsqueda semántica local. |
| `/search <query>` | Realiza búsqueda semántica/BM25 en el código indexado. |
| `/web <query>` | Búsqueda en la web (DuckDuckGo/Tavily). |
| `/diff` | Muestra las diferencias Git pendientes. |
| `/commit [msg]` | Crea commit semántico generado por IA. |
| `/review` | Ejecuta Code Review de los cambios pendientes. |
| `/undo` | Revierte la última modificación realizada por la IA. |
| `/test [args]` | Ejecuta pruebas con `pytest` y sugiere correcciones si fallan. |
| `/gentest <archivo>`| Genera suite completa de pruebas unitarias con pytest. |
| `/plan <objetivo>` | Crea un plan estructurado y añade tareas a `/todo`. |
| `/todo` | Visualiza y gestiona la lista de tareas de la sesión. |
| `/export [md\|html]`| Exporta la sesión a Markdown o HTML. |
| `/exit` | Sale del asistente. |

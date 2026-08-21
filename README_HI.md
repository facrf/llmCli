# 🤖 llmCli

> **Language / भाषा:** 🇧🇷 [Português](README.md) | 🇺🇸 [English](README_EN.md) | 🇪🇸 [Español](README_ES.md) | 🇩🇪 [Deutsch](README_DE.md) | 🇫🇷 [Français](README_FR.md) | 🇨🇳 [中文](README_ZH.md) | 🇷🇺 [Русский](README_RU.md) | 🇮🇳 [हिन्दी](README_HI.md)

**llmCli** टर्मिनल में सॉफ़्टवेयर विकास के लिए एक उन्नत AI कोडिंग सहायक है (OpenAI Codex, Aider और Claude Code से प्रेरित), जो **स्थानीय LLMs** (llama.cpp, Ollama, LM Studio, vLLM) और **क्लाउड LLMs** (Google Gemini, OpenAI GPT-4o / o-series, Anthropic Claude 3.7 / 3.5, DeepSeek V3 / R1, Groq, OpenRouter) के साथ काम करने के लिए डिज़ाइन किया गया है।

---

## 🌟 मुख्य विशेषताएं

- 🔄 **हाइब्रिड मॉडल समर्थन:** स्थानीय (llama.cpp, Ollama, LM Studio) और क्लाउड (Gemini, OpenAI, Claude, DeepSeek, Groq) मॉडल।
- 🏛️ **आर्किटेक्ट मोड (`/architect`):** योजना बनाने और कोड संपादन के लिए दो अलग-अलग मॉडल का उपयोग।
- 🌐 **बहुभाषी समर्थन (`/lang`):** हिन्दी, अंग्रेज़ी, पुर्तगाली सहित 8 भाषाओं का समर्थन।
- ⚡ **YOLO मोड (`/yolo`):** पूर्ण स्वायत्त निष्पादन मोड।
- 🧠 **ऑफ़लाइन कोड खोज और लोकल RAG (`/index` / `/search`):** BM25 और TF-IDF के साथ ऑफ़लाइन कोड सर्च।
- 🔌 **Model Context Protocol (MCP) (`/mcp`):** बाहरी टूल्स और सर्वर इंटीग्रेशन।
- 🌐 **वेब सर्च (`/web` / `read_url`):** DuckDuckGo और Tavily के माध्यम से लाइव वेब सर्च।
- 📋 **टास्क प्लानर (`/plan` / `/todo`):** इंटरैक्टिव टास्क और चेकलिस्ट प्रबंधन।
- 🧪 **टेस्ट जनरेटर (`/gentest` / `/test`):** Pytest यूनिट टेस्ट निर्माण और स्वचालित सुधार।
- 💾 **उपयोगकर्ता प्राथमिकताएं:** ~/.llmcli_preferences.json में ऑटो-सेव।
- 📄 **सत्र निर्यात (`/export`):** Markdown और HTML में सेशन एक्सपोर्ट।
- 🛡️ **सुरक्षा और Git चेकपॉइंट:** हर बदलाव से पहले Git स्नैपशॉट और `/undo` रोलबैक।

---

## 🚀 त्वरित शुरुआत

```bash
# 1. वर्चुअल वातावरण बनाएं और सक्रिय करें
python3 -m venv .venv
source .venv/bin/activate

# 2. निर्भरताएं इंस्टॉल करें
pip install -r requirements.txt

# 3. .env फाइल कॉन्फ़िगर करें
cp .env.example .env

# 4. llmCli शुरू करें
./bin/llm-cli
```

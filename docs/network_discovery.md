# 📡 Descoberta Automática de Modelos por IP (Network Discovery)

O **llmCli** possui um mecanismo integrado de varredura assíncrona de rede que permite localizar servidores de LLM em execução em qualquer máquina local ou remota (como outro computador, servidor dedicado ou nó na rede local) e identificar automaticamente todos os modelos disponíveis.

---

## 🎯 Por que usar?

Ao trabalhar com modelos locais pesados (ex: 7B, 14B, 32B, 70B), é comum rodar os servidores de inferência (como **Ollama** ou **llama.cpp**) em uma máquina dedicada com GPU na mesma rede (ex: `192.168.0.11`) e usar o `llmCli` em sua estação de desenvolvimento.

O módulo de descoberta automática elimina a necessidade de configurar URLs manualmente ou saber quais modelos estão baixados na máquina remota.

---

## 🚀 Como Usar

### 1. Varredura Rápida via CLI (`--scan <IP>`)

Para inspecionar um IP e ver quais servidores e modelos estão ativos:

```bash
./bin/llm-cli --scan 192.168.0.11
```

**Exemplo de Saída:**
```text
Escaneando host 192.168.0.11 em busca de modelos de LLM...

                 Serviços e Modelos Detectados em 192.168.0.11                  
┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Serviço / Servidor┃ Endpoint                   ┃ Modelos          ┃ Comando para Usar           ┃
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Ollama            │ http://192.168.0.11:11434  │ qwen2.5-coder:7b │ /model                      │
│                   │                            │ hermes3:latest   │ ollama/qwen2.5-coder:7b     │
└───────────────────┴────────────────────────────┴──────────────────┴─────────────────────────────┘
```

---

### 2. Conexão Direta via CLI (`--host <IP>`)

Conecta ao host remoto, ajusta os endpoints automaticamente e seleciona o primeiro modelo encontrado:

```bash
# Conectar ao servidor remoto e abrir o terminal interativo
./bin/llm-cli --host 192.168.0.11 --yolo

# Ou executar um prompt direto no servidor remoto
./bin/llm-cli --host 192.168.0.11 "Crie um algoritmo de ordenação rápida em Python"
```

---

### 3. Comandos Interativos (Slash Commands)

Durante qualquer sessão no terminal interativo:

| Comando | Descrição |
| :--- | :--- |
| **`/scan <IP>`** | Escaneia o host especificado e exibe a tabela com modelos encontrados. |
| **`/host <IP>`** | Conecta ao host, atualiza os endpoints e ativa automaticamente o modelo disponível. |

**Exemplo no REPL:**
```text
llmCli [gemini-2.5-flash | 🛡️ YOLO: OFF] ❯ /scan 192.168.0.11
Escaneando host 192.168.0.11 em busca de servidores e modelos de LLM...
(Tabela de modelos exibida)

llmCli [gemini-2.5-flash | 🛡️ YOLO: OFF] ❯ /model ollama/qwen2.5-coder:7b
✓ Modelo ativo alterado para: ollama/qwen2.5-coder:7b
```

---

## 🔍 Portas e Protocolos Sondados

A classe [HostScanner](file:///storage/www/projetos/utils/llmCli/src/providers/scanner.py) dispara requisições assíncronas concorrentes nas seguintes portas padrão:

| Servidor / Serviço | Porta Padrão | Endpoints Verificados |
| :--- | :---: | :--- |
| **Ollama** | `11434` | `GET /api/version` (versão)<br>`GET /api/tags` (lista de modelos) |
| **llama.cpp Server** | `8080` e `8081` | `GET /health`<br>`GET /props` (tamanho de contexto `n_ctx`)<br>`GET /v1/models` |
| **LM Studio** | `1234` | `GET /v1/models` |
| **vLLM / LocalAI** | `8000` | `GET /v1/models` |
| **Text-Gen-WebUI** | `5000` | `GET /v1/models` |

---

## ⚙️ Dicas para Configuração do Servidor Remoto

Para que o servidor remoto aceite conexões do `llmCli`, certifique-se de que ele está vinculado a `0.0.0.0` (todas as interfaces de rede):

### Para o Ollama:
No servidor onde o Ollama roda, defina a variável de ambiente:
```bash
# No Linux (systemd):
# Adicione em /etc/systemd/system/ollama.service.d/override.conf:
# [Service]
# Environment="OLLAMA_HOST=0.0.0.0:11434"

# Ou ao rodar manualmente:
OLLAMA_HOST=0.0.0.0:11434 ollama serve
```

### Para o llama.cpp (`llama-server`):
Inicie o servidor com a flag `--host 0.0.0.0`:
```bash
./llama-server -m /caminho/modelo.gguf --host 0.0.0.0 --port 8080 -c 8192
```

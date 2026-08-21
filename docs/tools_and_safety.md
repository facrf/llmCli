# 🛡️ Ferramentas, Segurança e Checkpoints Git

O **llmCli** opera com princípios rigorosos de segurança e integridade de código, garantindo que suas tarefas sejam realizadas com proteção total do seu sistema operacional.

---

## 🔒 1. Política de Isolamento do Workspace (AGENTS.md)

Em conformidade estrita com o arquivo [AGENTS.md](file:///storage/www/projetos/utils/llmCli/AGENTS.md):

1. **Sandbox de Caminhos:**
   - Todas as ferramentas de leitura e escrita validam a árvore de caminhos. Tentativas de acessar diretórios como `/etc`, `/home` ou pastas fora de `/storage/www/projetos/utils/llmCli` são bloqueadas imediatamente pelo resolvedor de caminhos seguros (`_resolve_safe_path`).
2. **Execução de Comandos Segura:**
   - Comandos de shell são executados exclusivamente com `Cwd` apontado para a raiz do repositório.
   - Padrões potencialmente catastróficos (como `rm -rf /` ou fork bombs) são interceptados e cancelados.
   - Todos os comandos possuem um tempo limite configurável (`command_timeout_seconds`, padrão 60s) para evitar travamentos infinitos.

---

## 🛠️ 2. Ferramentas Disponíveis para o Agente

| Ferramenta | Parâmetros | Descrição |
| :--- | :--- | :--- |
| `read_file` | `path`, `start_line`, `end_line` | Lê conteúdo de arquivos com paginação opcional por linha. |
| `write_file` | `path`, `content` | Escreve ou sobrescreve arquivos dentro do workspace. |
| `list_dir` | `path`, `max_depth` | Lista arquivos e subpastas de forma estruturada. |
| `grep_search` | `query`, `path`, `case_sensitive` | Realiza buscas textuais ou regex em arquivos do projeto. |
| `find_files` | `pattern`, `path` | Encontra arquivos usando padrões glob (ex: `*.py`, `test_*`). |
| `run_command` | `command`, `timeout_seconds` | Executa comandos no terminal do workspace capturando stdout/stderr. |

---

## 🔄 3. Estratégias Híbridas de Edição

O assistente possui capacidade de adaptação dinâmica:

### A. Function Calling (Nativo)
Utilizado quando o modelo possui suporte nativo a ferramentas (como Gemini 2.5 Flash/Pro, GPT-4o, Claude 3.7 Sonnet). As chamadas são estruturadas em JSON schemas estritos.

### B. Blocos SEARCH/REPLACE (Estilo Aider)
Para modelos locais (como llama.cpp ou Ollama menores) que não suportam function calling nativo, o sistema processa automaticamente blocos no padrão:

```text
Arquivo: src/exemplo.py
<<<<<<< SEARCH
codigo_original_a_substituir
=======
novo_codigo_atualizado
>>>>>>>
```

O módulo [diff_applier.py](file:///storage/www/projetos/utils/llmCli/src/core/diff_applier.py) possui tolerância a diferenças de espaços e identação (*fuzzy whitespace matching*).

---

## ⏪ 4. Checkpoints Automáticos e o Comando `/undo`

Antes de aplicar qualquer modificação de arquivo:
1. O assistente cria automaticamente um commit de snapshot no Git com a mensagem `llmCli: patch em <arquivo>` ou `llmCli: write_file em <arquivo>`.
2. Caso você queira reverter a alteração feita pela IA, basta digitar:
   ```bash
   /undo
   ```
3. O `llmCli` reverterá o snapshot com segurança, restaurando seu código ao estado anterior.

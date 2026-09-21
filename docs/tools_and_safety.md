# 🛡️ Ferramentas, Segurança e Checkpoints Git

O **llmCli** opera com princípios rigorosos de segurança e integridade de código, garantindo que tarefas sejam realizadas com proteção total do seu ambiente de trabalho.

---

## 🔒 1. Política de Isolamento do Workspace (AGENTS.md)

Em conformidade estrita com as diretrizes do [AGENTS.md](file:///storage/www/projetos/utils/llmCli/AGENTS.md):

1. **Sandbox de Arquivos e Diretórios:**
   - Todas as ferramentas de leitura e escrita validam a árvore de caminhos. Tentativas de acessar diretórios fora da raiz do repositório (`/storage/www/projetos/utils/llmCli`) são bloqueadas imediatamente pelo resolvedor de caminhos seguros (`_resolve_safe_path`).
2. **Execução Controlada de Comandos:**
   - Não há interpretação por shell: pipes, redirecionamentos e encadeamentos são tratados como argumentos literais.
   - Apenas executáveis comuns de desenvolvimento são aceitos; opções que executam código arbitrário ou apontam para fora do workspace são bloqueadas.
   - Todos os comandos possuem um tempo limite configurável (`command_timeout_seconds`, padrão 60s) para evitar travamentos infinitos.
3. **Proteção de Segredos e Chaves:**
   - Arquivos `.env`, chaves, credenciais e arquivos ignorados pelo Git não podem ser adicionados ao contexto da LLM.

---

## 🛠️ 2. Catálogo de Ferramentas Nativas do Agente

| Ferramenta | Parâmetros | Descrição |
| :--- | :--- | :--- |
| `read_file` | `path`, `start_line`, `end_line` | Lê o conteúdo de arquivos com paginação opcional por linha. |
| `write_file` | `path`, `content` | Grava ou sobrescreve arquivos dentro do workspace com criação automática de pastas pai. |
| `list_dir` | `path`, `max_depth` | Lista arquivos e subpastas de forma estruturada. |
| `grep_search` | `query`, `path`, `case_sensitive` | Realiza buscas textuais ou regex em arquivos do projeto. |
| `find_files` | `pattern`, `path` | Encontra arquivos usando padrões glob (ex: `*.py`, `test_*`). |
| `run_command` | `command`, `timeout_seconds` | Executa comandos no terminal do workspace capturando stdout/stderr. |
| `semantic_search` | `query`, `top_k` | Busca funções, classes e trechos no código indexado com pontuação BM25. |
| `web_search` | `query`, `max_results` | Pesquisa soluções, documentações e referências na Web (DuckDuckGo/Tavily). |
| `read_url` | `url`, `max_chars` | Extrai texto limpo e legível a partir de URLs ou documentações online. |
| `mcp_*` | `kwargs dinâmicos` | Ferramentas registradas dinamicamente via servidores MCP configurados. |

---

## 🔄 3. Estratégias Híbridas de Edição de Código

O assistente adapta dinamicamente sua estratégia de edição:

### A. Function Calling Nativo
Utilizado automaticamente em modelos com suporte nativo (Gemini 2.5 Flash/Pro, GPT-4o, Claude 3.7 Sonnet). As chamadas de ferramentas utilizam schemas JSON estritos validados via Pydantic.

### B. Blocos SEARCH/REPLACE Tolerantes (Estilo Aider)
Para modelos locais (como llama.cpp ou Ollama menores) ou modelos sem suporte a function calling nativo, o sistema processa blocos no padrão:

```text
Arquivo: src/exemplo.py
<<<<<<< SEARCH
codigo_original_a_substituir
=======
novo_codigo_atualizado
>>>>>>>
```

O módulo [diff_applier.py](file:///storage/www/projetos/utils/llmCli/src/core/diff_applier.py) possui tolerância inteligente a variações de espaços em branco e identação (*fuzzy whitespace matching*).

---

## ⏪ 4. Checkpoints Automáticos e o Comando `/undo`

Antes de aplicar qualquer modificação de arquivo:
1. Com a árvore Git limpa, o assistente cria um commit apenas para o arquivo alterado, com a mensagem `llmCli: patch em <arquivo>` ou `llmCli: write_file em <arquivo>`. Se houver trabalho preexistente, o checkpoint é ignorado para preservá-lo.
2. Caso você queira reverter a alteração feita pela IA, basta digitar:
   ```bash
   /undo
   ```
3. O `llmCli` usa `git revert`, sem `reset --hard` ou restauração ampla da árvore de trabalho.

---

## 🔍 5. Code Review e Commits Semânticos

- **`/review`**: Analisa automaticamente as diferenças (`git diff`) pendentes no repositório, identificando potenciais bugs, regressões, riscos de segurança e oportunidades de refatoração.
- **`/commit`**: Analisa o código modificado e propõe mensagens padronizadas no formato *Conventional Commits* (`feat:`, `fix:`, `refactor:`, `docs:`, `test:`).

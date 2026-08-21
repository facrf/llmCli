# 🔧 Diagnóstico e Resolução de Problemas (Troubleshooting)

Este guia reúne soluções práticas para os problemas e dúvidas mais comuns ao utilizar o **llmCli**.

---

## ❓ 1. Servidor Local Marcado como OFFLINE no `/models`

### Llama.cpp
- **Causa:** O servidor `llama-server` não foi iniciado ou está escutando em outra porta.
- **Solução:** Inicie o servidor especificando a porta 8080:
  ```bash
  ./llama-server -m /caminho/do/modelo.gguf --port 8080 -c 8192
  ```
  Se estiver em outra porta (ex: 8081), ajuste a variável `LLAMACPP_BASE_URL=http://localhost:8081` no seu `.env`.

### Ollama
- **Causa:** O serviço do Ollama não está em execução.
- **Solução:** Inicie o serviço com `ollama serve` ou execute um modelo diretamente `ollama run qwen2.5-coder:7b`.

---

## ❓ 2. Erro: `Chave de API ausente no .env` (Gemini, OpenAI, Anthropic, etc.)

- **Causa:** O arquivo `.env` não existe ou a variável do provedor está vazia.
- **Solução:**
  1. Copie o arquivo de exemplo: `cp .env.example .env`
  2. Adicione sua chave válida no `.env` (ex: `GEMINI_API_KEY=...`).
  3. No terminal do `llmCli`, execute `/models` para confirmar que a chave foi reconhecida como `CONFIGURADO`.

---

## ❓ 3. A IA gerou código, mas o patch não foi aplicado

- **Causa:** O modelo local gerou um trecho `SEARCH` com divergência em relação ao arquivo original.
- **Solução:**
  1. Use o comando `/add <arquivo>` para recarregar a versão mais recente do arquivo no contexto.
  2. Use o **Modo Arquiteto** (`/architect gemini/gemini-2.5-pro`) para planejar a alteração com maior precisão antes de aplicar.

---

## ❓ 4. Como Reverter uma Edição ou Checkpoint Indesejado?

- **Solução:**
  Digite o comando `/undo` a qualquer momento no prompt interativo. O `llmCli` reverterá o snapshot de segurança criado antes da alteração.

---

## ❓ 5. Redefinir Preferências Salvas do Usuário

- **Causa:** Configurações personalizadas (temperatura, modelo, modo YOLO) salvas em `~/.llmcli_preferences.json` precisam ser restauradas para os padrões de fábrica.
- **Solução:**
  No REPL, execute:
  ```bash
  /reset prefs
  # ou para limpar sessão e preferências conjuntamente:
  /reset all
  ```

---

## ❓ 6. Busca Semântica (`/search`) Não Encontra Trechos Esperados

- **Causa:** Novos arquivos foram criados ou editados após a última indexação.
- **Solução:**
  Execute o comando `/index` para atualizar o índice local de classes e funções:
  ```bash
  /index
  ```

---

## ❓ 7. Servidores MCP Não Conectam ou Ferramentas Não Aparecem

- **Causa:** O arquivo `mcp_servers.json` ou `~/.llmcli_mcp.json` contém sintaxe JSON inválida ou o comando/binário não está no `PATH`.
- **Solução:**
  1. Execute `/mcp` no REPL para inspecionar os servidores detectados.
  2. Valide se os comandos definidos em `command` podem ser executados no terminal.

---

## ❓ 8. Executar a Suíte de Testes Automatizados

Para validar todas as ferramentas, adaptadores e isolamento de segurança:
```bash
./scripts/run_tests.sh
```


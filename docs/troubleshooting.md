# 🔧 Diagnóstico e Resolução de Problemas (Troubleshooting)

Este guia reúne soluções para os problemas e dúvidas mais comuns ao utilizar o **llmCli**.

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

## ❓ 2. Erro: `GEMINI_API_KEY ausente no .env` (ou outro provedor de nuvem)

- **Causa:** O arquivo `.env` não existe ou a variável do provedor está vazia.
- **Solução:**
  1. Copie o arquivo de exemplo: `cp .env.example .env`
  2. Adicione sua chave válida no `.env`.
  3. No terminal do `llmCli`, execute `/models` para confirmar que a chave foi reconhecida.

---

## ❓ 3. A IA gerou código, mas o patch não foi aplicado

- **Causa:** O modelo local gerou um trecho `SEARCH` que divergiu ligeiramente do arquivo original.
- **Solução:**
  1. Use o comando `/add <arquivo>` para recarregar o arquivo no contexto antes de pedir a alteração.
  2. Alterne temporariamente para um modelo com maior capacidade de raciocínio (ex: `/model gemini/gemini-2.5-flash` ou `/model anthropic/claude-3-7-sonnet-20250219`).

---

## ❓ 4. Como Reverter uma Edição Indesejada?

- **Solução:**
  Digite o comando `/undo` a qualquer momento no prompt interativo. O `llmCli` utilizará os checkpoints automáticos do Git para voltar ao estado anterior.

---

## ❓ 5. Executar a Suíte de Testes Automatizados

Para validar todo o ambiente e ferramentas:
```bash
.venv/bin/pytest -v
```

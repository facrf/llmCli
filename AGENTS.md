# Diretrizes e Regras para Agentes (AGENTS.md)

Este documento estabelece as regras obrigatórias de operação e restrição de escopo para qualquer agente de IA ou automação que interaja com este repositório (`llmCli`).

---

## 🔒 1. Restrição Estrita de Escopo (Workspace Boundary)

1. **Isolamento de Diretório:**
   - Todas as operações (leitura, escrita, edição, remoção, busca e execução de comandos) **DEVEM** ser realizadas exclusivamente dentro deste diretório (`/storage/www/projetos/utils/llmCli`) e suas respectivas subpastas.
   - **NÃO** acesse, inspecione, crie, modifique ou exclua arquivos/pastas fora desta árvore de diretórios (por exemplo: diretórios pais como `/storage/www/projetos/`, `/tmp/`, `/home/`, `/var/`, etc.).
   
2. **Execução de Comandos:**
   - Qualquer comando de terminal (`run_command`) deve ter seu diretório de trabalho (`Cwd`) configurado estritamente dentro desta raiz (`/storage/www/projetos/utils/llmCli`) ou em alguma de suas subpastas.
   - Não execute comandos que afetem o sistema operacional globalmente ou modifiquem outros projetos.

3. **Arquivos Temporários e Artefatos:**
   - Quaisquer arquivos temporários, logs locais de teste, caches ou scripts auxiliares devem ser armazenados em subpastas locais dedicadas (ex: `tmp/`, `scratch/` ou `.cache/`) respeitando o `.gitignore`.

---

## 🛠️ 2. Boas Práticas e Padrões de Desenvolvimento

1. **Segurança e Chaves de API:**
   - **Nunca** versione ou exponha credenciais, chaves de API (OpenAI, Anthropic, Google Gemini, Groq, etc.) ou segredos diretamente no código-fonte.
   - Utilize arquivos `.env` locais para configuração de credenciais e garanta que estejam listados no `.gitignore`.
   - Forneça sempre um arquivo de modelo `.env.example`.

2. **Qualidade e Estilo de Código:**
   - Mantenha o código limpo, modular, documentado e tipado quando aplicável.
   - Escreva mensagens de commit claras e semânticas (ex: `feat:`, `fix:`, `docs:`, `refactor:`).
   - Mantenha tratamento de exceções robusto em todas as integrações com LLMs (timeouts, retries, rate limits).

3. **Integridade de Arquivos:**
   - Ao alterar código existente, preserve comentários relevantes e formate adequadamente.
   - Valide modificações executando testes locais ou linter antes de finalizar tarefas.

---

## 📂 3. Estrutura de Pastas Recomendada

```text
llmCli/
├── .env.example          # Exemplo de variáveis de ambiente
├── .gitignore            # Arquivos e pastas ignorados pelo Git
├── AGENTS.md             # Regras operacionais dos agentes (este arquivo)
├── README.md             # Documentação principal do projeto
├── docs/                 # Documentações adicionais e especificações
├── src/ / scripts/       # Código-fonte e scripts de utilitários
└── tests/                # Testes unitários e de integração
```

---

## 💬 4. Comunicação e Relatórios

- Forneça respostas claras, concisas e objetivas ao usuário.
- Ao citar caminhos de arquivos e símbolos de código, utilize links clicáveis no padrão markdown (`[arquivo](file:///caminho/absoluto)`).

# Roadmap: modo multiagente

Este documento define a evolução do llmCli para executar agentes especializados sob coordenação de um agente orquestrador. A Fase 1 está implementada; o modo padrão de agente único permanece inalterado.

## Objetivo

Permitir que uma tarefa seja decomposta em papéis especializados, usando modelos diferentes quando necessário, sem perder rastreabilidade, segurança do workspace ou controle sobre alterações concorrentes.

```text
Orquestrador
├── Pesquisador  → reúne evidências do código e da documentação
├── Arquiteto    → produz plano, dependências e critérios de aceite
├── Implementador→ aplica alterações aprovadas
├── Testador     → executa validações e diagnostica falhas
└── Revisor      → inspeciona o diff, riscos e regressões
```

## Arquitetura proposta

`src/core/multi_agent.py` contém o `MultiAgentCoordinator`. Ele recebe o objetivo, cria sessões isoladas para os papéis somente leitura e encaminha os resultados no pipeline sequencial.

Cada agente deve possuir:

- papel e prompt de sistema próprios;
- provider/modelo configurável;
- orçamento de iterações e timeout;
- conjunto de ferramentas mínimo para sua função;
- relatório estruturado com evidências, decisão, arquivos afetados e bloqueios.

Uma interface mínima de resultado pode seguir este formato:

```json
{
  "agent": "researcher",
  "status": "complete",
  "summary": "...",
  "evidence": ["src/config.py:53"],
  "affected_files": ["src/config.py"],
  "next_action": "Criar validação para ..."
}
```

## Estado atual

Implementado nesta etapa:

- `MultiAgentCoordinator` sequencial, sem paralelismo;
- `/team <objetivo>` para pesquisador e arquiteto e `/team --apply <objetivo>` para o pipeline completo, com confirmação fora do modo YOLO;
- `/agents` para visualizar papéis e modelos;
- configuração `multi_agent` e seleção opcional de modelo por papel;
- ferramentas de leitura para pesquisador, arquiteto e revisor;
- `run_project_tests` restrita a `pytest -q` para o testador;
- relatórios registrados no histórico da sessão e incluídos nas exportações;
- isolamento de falhas: um relatório com status `failed` não encerra os demais papéis.

Limitações desta etapa:

- a configuração por papel não possui ainda orçamento individual de tokens, custo ou timeout;
- o testador interpreta e pode disparar apenas a suíte completa; não há seleção de testes nem auto-correção restrita;
- não existe reconciliação de worktrees, execução paralela ou painel de progresso;
- `affected_files`, evidências estruturadas e próxima ação ainda são campos previstos, mas não são extraídos automaticamente;
- MCP fica fora dos papéis especializados até existir uma política de permissões por papel e servidor.

## Fases de entrega

### Fase 1 — Pipeline sequencial (implementada)

Implementar `/team <objetivo>` com fluxo fixo:

1. Pesquisador analisa o repositório em modo somente leitura.
2. Arquiteto transforma as evidências em plano.
3. Usuário confirma o plano, exceto em modo YOLO.
4. Implementador executa alterações.
5. Testador e revisor validam o resultado.

O comando `/team <objetivo>` executa pesquisador e arquiteto, retornando evidências e um plano sem alterar o workspace. `/team --apply <objetivo>` solicita confirmação e executa o fluxo completo; `/agents` exibe os papéis e modelos configurados.

Os papéis de planejamento recebem somente `read_file`, `list_dir`, `grep_search`, `find_files` e `semantic_search`; ferramentas de mutação, terminal e MCP ficam bloqueadas. O testador também recebe `run_project_tests`, que executa somente `pytest -q`, sem aceitar comando ou argumentos livres. Os relatórios de cada papel são incluídos no histórico da sessão e, portanto, nos relatórios exportados.

### Fase 2 — Configuração por papel e limites (parcialmente implementada)

Adicionar ao `config.yaml` uma seção opcional:

```yaml
multi_agent:
  enabled: false
  max_parallel_agents: 1
  roles:
    researcher: { model: "ollama/qwen2.5-coder:7b" }
    architect: { model: "gemini/gemini-2.5-pro" }
    implementer: { model: "gemini/gemini-2.5-flash" }
    tester: { model: "ollama/qwen2.5-coder:7b" }
    reviewer: { model: "gemini/gemini-2.5-flash" }
```

`multi_agent.roles` e `/agents` já existem. Falta incluir status em tempo real, consumo estimado, orçamento individual de rodadas/tokens e timeout por papel.

### Fase 3 — Paralelismo seguro (não iniciada)

Permitir pesquisadores, testadores e revisores em paralelo. Para implementações concorrentes, criar um Git worktree por agente e exigir uma etapa explícita de reconciliação/merge pelo orquestrador.

Nunca permitir que dois agentes escrevam simultaneamente no mesmo workspace principal.

## Segurança e governança

- O orquestrador é responsável por aplicar orçamento, timeout e número máximo de rodadas.
- Agentes sem papel de implementação não recebem `write_file` nem `run_command`.
- Ferramentas MCP precisam de permissão explícita por agente e por servidor.
- Toda edição deve registrar agente responsável, arquivos e checkpoint Git.
- O orquestrador deve cancelar trabalhos dependentes quando o plano for rejeitado ou um agente crítico falhar.
- Segredos, arquivos ignorados e limites de contexto seguem as mesmas proteções do agente atual.

## Critérios de aceite

- `/team` executa o pipeline sequencial e mostra o relatório de cada papel.
- Nenhum agente somente leitura consegue modificar arquivos ou executar comandos.
- Falha de um subagente é apresentada ao orquestrador sem encerrar a sessão inteira.
- O relatório exportado identifica decisões e alterações por agente.
- Testes cobrem delegação, cancelamento, limites, falhas de provider e bloqueio de escrita concorrente.
- O modo padrão de agente único continua compatível e inalterado.

## Decisões em aberto

1. Quais papéis devem poder usar ferramentas MCP?
2. Qual limite de custo/tempo deve interromper o time?
3. A reconciliação de worktrees será automática, assistida ou sempre manual?
4. As sessões dos subagentes devem ser persistidas ou descartadas ao fim da tarefa?

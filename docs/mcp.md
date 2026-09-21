# Integração MCP via stdio

O llmCli pode iniciar servidores compatíveis com o Model Context Protocol (MCP) via `stdio`, descobrir suas ferramentas e disponibilizá-las ao modelo com o prefixo `mcp_<servidor>_<ferramenta>`.

## Configuração

Crie `mcp_servers.json` na raiz do projeto ou `.mcp.json` (normalmente ignorado pelo Git quando contiver dados específicos do ambiente):

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "."],
      "enabled": true,
      "timeout_seconds": 15
    }
  }
}
```

`command` e `args` definem o processo do servidor; `env` permite variáveis específicas do servidor. Não inclua segredos no arquivo versionado: prefira `.mcp.json` local ou referências a variáveis do ambiente.

## Uso e segurança

Use `/mcp` para iniciar a descoberta e listar ferramentas disponíveis. A descoberta também ocorre antes de prompts, para que ferramentas configuradas possam ser oferecidas ao modelo.

Cada servidor configurado executa como processo local do usuário. Portanto, configure somente comandos confiáveis e mantenha `enabled: false` para integrações que não devam iniciar automaticamente. As ferramentas MCP participam da mesma política de confirmação do agente quando aplicável; o modo YOLO elimina confirmações.

O cliente suporta o fluxo JSON-RPC `initialize`, `notifications/initialized`, `tools/list` e `tools/call`. Conexões e chamadas respeitam `timeout_seconds`; uma falha de servidor é exibida no `/mcp` sem interromper a sessão.

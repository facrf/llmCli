#!/usr/bin/env bash
# Script utilitário para execução rápida de testes e cobertura

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$SCRIPT_DIR"

if [ -f ".venv/bin/pytest" ]; then
    PYTEST_EXEC=".venv/bin/pytest"
else
    PYTEST_EXEC="pytest"
fi

echo "=================================================="
echo " Executando Suíte Completa de Testes do llmCli"
echo "=================================================="

"$PYTEST_EXEC" -v --cov=src --cov-report=term-missing "$@"

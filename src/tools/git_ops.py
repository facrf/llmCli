"""Git operations for checkpoints, diff inspection, and rollbacks."""
from __future__ import annotations

import asyncio
from typing import Optional, Tuple
from src.config import get_config


async def run_git_cmd(*args: str) -> Tuple[int, str, str]:
    config = get_config()
    proc = await asyncio.create_subprocess_exec(
        "git",
        *args,
        cwd=str(config.project_root),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout_b, stderr_b = await proc.communicate()
    return (
        proc.returncode or 0,
        stdout_b.decode("utf-8", errors="replace").strip(),
        stderr_b.decode("utf-8", errors="replace").strip()
    )


async def is_git_repo() -> bool:
    code, _, _ = await run_git_cmd("rev-parse", "--is-inside-work-tree")
    return code == 0


async def get_git_diff(cached: bool = False) -> str:
    if not await is_git_repo():
        return "(Repositório Git não inicializado neste diretório)"
    args = ["diff"]
    if cached:
        args.append("--cached")
    code, out, err = await run_git_cmd(*args)
    if code != 0:
        return f"Erro ao obter diff: {err}"
    return out or "(Nenhuma modificação não commitada no momento)"


async def get_git_status() -> str:
    if not await is_git_repo():
        return "(Repositório Git não inicializado)"
    code, out, err = await run_git_cmd("status", "--short")
    if code != 0:
        return f"Erro ao obter status: {err}"
    return out or "(Árvore de trabalho limpa)"


async def create_checkpoint_commit(message: str) -> Optional[str]:
    """Cria um commit automático como ponto de restauração."""
    config = get_config()
    if not config.git.auto_commit_on_edit or not await is_git_repo():
        return None

    # Adicionar modificações
    await run_git_cmd("add", "-A")
    full_msg = f"{config.git.commit_prefix} {message}"
    code, out, _ = await run_git_cmd("commit", "-m", full_msg)
    if code == 0:
        # Obter hash do commit
        _, hash_out, _ = await run_git_cmd("rev-parse", "--short", "HEAD")
        return hash_out
    return None


async def undo_last_checkpoint() -> Tuple[bool, str]:
    """Desfaz o último commit ou reverte modificações não salvas."""
    if not await is_git_repo():
        return False, "Git não está configurado neste diretório."

    # Verificar se o último commit foi gerado pelo llmCli
    config = get_config()
    code, last_msg, _ = await run_git_cmd("log", "-1", "--pretty=%B")
    if code == 0 and config.git.commit_prefix in last_msg:
        code_reset, _, err = await run_git_cmd("reset", "--hard", "HEAD~1")
        if code_reset == 0:
            return True, f"Última alteração desfeita com sucesso (Commit revertido: {last_msg.strip()})."
        return False, f"Falha ao reverter commit: {err}"

    # Se não houver commit do llmCli, tenta restaurar arquivos modificados na working tree
    code_restore, _, err = await run_git_cmd("restore", ".")
    if code_restore == 0:
        return True, "Modificações não commitadas foram revertidas com sucesso."
    return False, f"Não foi possível reverter: {err}"


async def get_raw_git_diff() -> str:
    """Retorna o diff bruto (unstaged + staged) do repositório ou string vazia se limpo."""
    if not await is_git_repo():
        return ""
    code_unstaged, out_unstaged, _ = await run_git_cmd("diff")
    code_staged, out_staged, _ = await run_git_cmd("diff", "--cached")
    
    diff_parts = []
    if out_unstaged.strip():
        diff_parts.append(out_unstaged.strip())
    if out_staged.strip():
        diff_parts.append(out_staged.strip())
    return "\n\n".join(diff_parts)


async def create_user_commit(message: str) -> Tuple[bool, str]:
    """Realiza git add -A e cria um commit explícito com a mensagem informada."""
    if not await is_git_repo():
        return False, "Git não está configurado neste repositório."
    
    await run_git_cmd("add", "-A")
    code, out, err = await run_git_cmd("commit", "-m", message.strip())
    if code == 0:
        _, hash_out, _ = await run_git_cmd("rev-parse", "--short", "HEAD")
        return True, f"Commit criado com sucesso [{hash_out}]: {message.strip()}"
    return False, f"Erro ao criar commit: {err or out}"

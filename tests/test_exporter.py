"""Unit tests for session exporter to Markdown and HTML."""
import pytest
from src.core.session import Session
from src.core.exporter import SessionExporter


def test_session_exporter_md_and_html(tmp_path):
    session = Session()
    session.add_user_message("Como criar uma API em FastAPI?")
    session.add_assistant_message("Aqui está um exemplo com FastAPI...")

    exporter = SessionExporter(session, project_root=tmp_path)

    # Exportar Markdown
    md_file = tmp_path / "test_session.md"
    out_md = exporter.export_markdown(target_path=md_file)
    assert out_md.exists()
    content_md = out_md.read_text(encoding="utf-8")
    assert "Como criar uma API em FastAPI?" in content_md
    assert "Relatório de Sessão" in content_md

    # Exportar HTML
    html_file = tmp_path / "test_session.html"
    out_html = exporter.export_html(target_path=html_file)
    assert out_html.exists()
    content_html = out_html.read_text(encoding="utf-8")
    assert "<!DOCTYPE html>" in content_html
    assert "FastAPI" in content_html

"""Utilitários simples para geração de PDFs a partir de templates HTML."""
from pathlib import Path

from django.http import HttpResponse
from django.template.loader import render_to_string


def get_weasy_html():
    """Carrega WeasyPrint de forma tardia para manter mensagens de erro controladas."""
    try:
        from weasyprint import HTML
    except ImportError as exc:
        raise RuntimeError("Instale a dependência WeasyPrint para gerar PDFs.") from exc
    return HTML


def get_empresa_logo_url(empresa):
    """Retorna uma URL local utilizável pelo renderizador de PDF para a logo da empresa."""
    if not getattr(empresa, "logo", None):
        return None
    try:
        logo_path = Path(empresa.logo.path)
    except (NotImplementedError, ValueError):
        return getattr(empresa.logo, "url", None)
    if logo_path.exists():
        return logo_path.resolve().as_uri()
    return None


def render_pdf_response(request, template_name, context, filename):
    """Renderiza um template HTML em PDF e devolve resposta inline para o navegador."""
    html_string = render_to_string(template_name, context, request=request)
    html = get_weasy_html()(string=html_string, base_url=request.build_absolute_uri("/"))
    response = HttpResponse(html.write_pdf(), content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="{filename}"'
    return response

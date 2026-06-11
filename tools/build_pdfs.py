"""Converte os relatorios em Markdown (docs/*.md) para PDF, com tabelas e figuras.

Uso:
    python tools/build_pdfs.py            # converte os relatorios padrao
    python tools/build_pdfs.py a.md b.pdf # converte um arquivo especifico

Suporta um subconjunto do Markdown suficiente para os relatorios: titulos
(#, ##, ###), paragrafos, **negrito**, *italico*, `codigo`, listas (-, 1.),
tabelas (| ... |) e imagens (![alt](caminho)). Usa reportlab (pure-python).
"""
from __future__ import annotations

import os
import re
import sys

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (Image, ListFlowable, ListItem, PageBreak,
                                Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Substitui caracteres Unicode fora do latin-1 por equivalentes seguros.
_UNICODE = {"→": "->", "×": "x", "≥": ">=", "≤": "<=",
            "—": "-", "–": "-", "“": '"', "”": '"',
            "‘": "'", "’": "'", "±": "+/-", "≈": "~",
            "…": "...", "•": "-"}


def _sanitize(s: str) -> str:
    for k, v in _UNICODE.items():
        s = s.replace(k, v)
    return s


def _inline(text: str) -> str:
    """Formatacao inline -> mini-markup do reportlab."""
    text = _sanitize(text)
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"`(.+?)`", r'<font face="Courier">\1</font>', text)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<i>\1</i>", text)
    text = re.sub(r"\[(.+?)\]\((.+?)\)", r"\1", text)  # links -> texto
    return text


def _styles():
    ss = getSampleStyleSheet()
    ss.add(ParagraphStyle("Body2", parent=ss["BodyText"], fontSize=10, leading=14,
                          spaceAfter=6, alignment=4))  # justificado
    ss.add(ParagraphStyle("Cell", parent=ss["BodyText"], fontSize=8, leading=10))
    ss.add(ParagraphStyle("CellH", parent=ss["BodyText"], fontSize=8, leading=10,
                          textColor=colors.white))
    for k in ("Heading1", "Heading2", "Heading3"):
        ss[k].textColor = colors.HexColor("#1f3a63")
    return ss


def _image_flowable(path_rel: str, md_dir: str, max_w: float):
    path = os.path.normpath(os.path.join(md_dir, path_rel))
    if not os.path.exists(path):
        return Paragraph(f"<i>[figura ausente: {path_rel}]</i>", _styles()["Body2"])
    iw, ih = ImageReader(path).getSize()
    w = min(max_w, iw)
    return Image(path, width=w, height=w * ih / iw)


def _table_flowable(rows, ss, max_w):
    header = [Paragraph(_inline(c), ss["CellH"]) for c in rows[0]]
    body = [[Paragraph(_inline(c), ss["Cell"]) for c in r] for r in rows[1:]]
    data = [header] + body
    ncol = len(rows[0])
    t = Table(data, colWidths=[max_w / ncol] * ncol, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f3a63")),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#eef2f8")]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return t


def _parse_table(lines):
    rows = []
    for ln in lines:
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if set("".join(cells)) <= set("-: "):  # linha separadora
            continue
        rows.append(cells)
    return rows


def build_pdf(md_path: str, pdf_path: str):
    md_dir = os.path.dirname(os.path.abspath(md_path))
    with open(md_path, encoding="utf-8") as f:
        lines = f.read().split("\n")

    ss = _styles()
    doc = SimpleDocTemplate(pdf_path, pagesize=A4, topMargin=1.6 * cm,
                            bottomMargin=1.6 * cm, leftMargin=1.8 * cm, rightMargin=1.8 * cm)
    max_w = doc.width
    flow = []
    i = 0
    para_buf, list_buf = [], []

    def flush_para():
        if para_buf:
            flow.append(Paragraph(_inline(" ".join(para_buf)), ss["Body2"]))
            para_buf.clear()

    def flush_list():
        if list_buf:
            items = [ListItem(Paragraph(_inline(x), ss["Body2"]), leftIndent=10) for x in list_buf]
            flow.append(ListFlowable(items, bulletType="bullet", start="-"))
            flow.append(Spacer(1, 4))
            list_buf.clear()

    while i < len(lines):
        ln = lines[i]
        s = ln.strip()
        if not s:
            flush_para(); flush_list()
        elif s.startswith("#"):
            flush_para(); flush_list()
            level = len(s) - len(s.lstrip("#"))
            txt = _inline(s.lstrip("#").strip())
            flow.append(Paragraph(txt, ss[f"Heading{min(level,3)}"]))
        elif s.startswith("|"):
            flush_para(); flush_list()
            tbl = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                tbl.append(lines[i]); i += 1
            flow.append(_table_flowable(_parse_table(tbl), ss, max_w))
            flow.append(Spacer(1, 6)); continue
        elif re.match(r"!\[.*\]\(.*\)", s):
            flush_para(); flush_list()
            m = re.match(r"!\[.*\]\((.+?)\)", s)
            flow.append(Spacer(1, 4))
            flow.append(_image_flowable(m.group(1), md_dir, max_w))
            flow.append(Spacer(1, 6))
        elif s.startswith("- ") or s.startswith("* "):
            flush_para()
            list_buf.append(s[2:])
        elif re.match(r"^\d+\.\s", s):
            flush_para()
            list_buf.append(re.sub(r"^\d+\.\s", "", s))
        elif len(s) >= 3 and (set(s) <= set("-") or set(s) <= set("*") or set(s) <= set("_")):
            flush_para(); flush_list()  # regua horizontal -> quebra de pagina (separador de slide)
            flow.append(PageBreak())
        else:
            para_buf.append(s)
        i += 1
    flush_para(); flush_list()

    doc.build(flow)
    print("wrote", pdf_path)


DEFAULT = [
    ("docs/relatorio_parte1_fuzzy.md", "docs/relatorio_parte1_fuzzy.pdf"),
    ("docs/relatorio_parte2_evolutiva.md", "docs/relatorio_parte2_evolutiva.pdf"),
    ("docs/base_de_regras.md", "docs/base_de_regras.pdf"),
    ("docs/slides_parte1.md", "slides/slides_parte1.pdf"),
    ("docs/slides_parte2.md", "slides/slides_parte2.pdf"),
]

if __name__ == "__main__":
    if len(sys.argv) == 3:
        build_pdf(sys.argv[1], sys.argv[2])
    else:
        for md, pdf in DEFAULT:
            p = os.path.join(ROOT, md)
            if os.path.exists(p):
                build_pdf(p, os.path.join(ROOT, pdf))

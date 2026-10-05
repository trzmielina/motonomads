"""
Gerador de Saída Visual HTML para o Time Editorial MotoNomads.
Renderiza matérias, relatórios de auditoria e conexões ontológicas em uma interface web interativa e de alto nível estético.
"""

import os
import re
import json
from typing import Dict, Any, Optional


class MotonomadsHtmlGenerator:
    """Transforma matérias e auditorias em dashboards HTML de alta fidelidade visual."""

    def __init__(self):
        pass

    def _markdown_to_html_simple(self, md_text: str) -> str:
        """Conversor robusto de markdown básico para HTML sem dependências pesadas."""
        html = md_text

        # Processamento de Tabelas Markdown
        def replace_table(match):
            table_text = match.group(0).strip()
            rows = [r.strip() for r in table_text.split("\n") if r.strip()]
            if len(rows) < 2:
                return table_text
            headers = [c.strip() for c in rows[0].strip("|").split("|")]
            # Pula a linha separadora rows[1]
            tbody_rows = []
            for r in rows[2:]:
                cells = [c.strip() for c in r.strip("|").split("|")]
                tds = "".join(f"<td>{c}</td>" for c in cells)
                tbody_rows.append(f"<tr>{tds}</tr>")

            ths = "".join(f"<th>{h}</th>" for h in headers)
            return (
                f'<div class="table-container">'
                f'<table class="expedition-table">'
                f'<thead><tr>{ths}</tr></thead>'
                f'<tbody>{"".join(tbody_rows)}</tbody>'
                f'</table></div>'
            )

        html = re.sub(r"(\|[^\n]+\|\n\|[-:\s|]+\|\n(?:\|[^\n]+\|\n?)+)", replace_table, html)

        # Headings
        html = re.sub(r"^###\s+(.+)$", r'<h3 class="article-h3">\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r"^##\s+(.+)$", r'<h2 class="article-h2"><span class="h2-marker">■</span> \1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r"^#\s+(.+)$", r'<h1 class="article-h1">\1</h1>', html, flags=re.MULTILINE)

        # Bold & Italic
        html = re.sub(r"\*\*([^*]+)\*\*", r'<strong>\1</strong>', html)
        html = re.sub(r"\*([^*]+)\*", r'<em>\1</em>', html)

        # Quotes
        html = re.sub(r"^>\s+(.+)$", r'<blockquote class="eduardo-quote">\1</blockquote>', html, flags=re.MULTILINE)

        # List items
        html = re.sub(r"^-\s+(.+)$", r'<li class="article-li">\1</li>', html, flags=re.MULTILINE)
        html = re.sub(r"((?:<li class=\"article-li\">[^\n]+</li>\n?)+)", r'<ul class="article-ul">\1</ul>', html)

        # Parágrafos normais (linhas que não são tags HTML)
        paragraphs = []
        for line in html.split("\n\n"):
            line = line.strip()
            if line and not line.startswith("<") and not line.startswith("|"):
                paragraphs.append(f'<p class="article-p">{line}</p>')
            elif line:
                paragraphs.append(line)

        return "\n".join(paragraphs)

    def generate_html_report(
        self,
        article_md: str,
        audit_md: str,
        output_file_path: str,
        pillar: str = "mototurismo",
        target_keyword: str = "",
        ontological_data: Optional[Dict[str, Any]] = None,
        tone_score: int = 90,
        geo_score: int = 90,
    ) -> str:
        """Gera o arquivo HTML completo com abas interativas, métricas e design expedicionário."""

        article_html = self._markdown_to_html_simple(article_md)
        audit_html = self._markdown_to_html_simple(audit_md)

        # Extrair título principal
        h1_match = re.search(r"^#\s+(.+)$", article_md, re.MULTILINE)
        page_title = h1_match.group(1) if h1_match else "Matéria MotoNomads"

        # Extrair H1 do artigo como Title Tag preliminar
        meta_title = f"{page_title} | MotoNomads"[:60]
        meta_description = f"Guia de expedição MotoNomads: {page_title}. Dicas práticas de pilotagem, calibragem de pneus, altimetria e rotas testadas na estrada."[:158]

        # Montar FAQ JSON-LD Schema
        faq_items = re.findall(r"###\s+([^\n\?]+\?)\n([^\n#]+)", article_md)
        schema_json = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": []
        }
        for q, a in faq_items:
            schema_json["mainEntity"].append({
                "@type": "Question",
                "name": q.strip(),
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": a.strip()
                }
            })
        schema_formatted = json.dumps(schema_json, ensure_ascii=False, indent=2)

        # Montar Cards do Grafo Ontológico
        onto_html = ""
        if ontological_data and ontological_data.get("matched"):
            hist = ontological_data.get("historia_real_eduardo") or {}
            cidades = "".join(f'<span class="onto-pill">{c}</span>' for c in ontological_data.get("cidades_base_logistica", []))
            riscos = "".join(f'<span class="onto-pill risk">{r}</span>' for r in ontological_data.get("riscos_criticos", []))
            gastro = "".join(f'<span class="onto-pill gastro">{g}</span>' for g in ontological_data.get("gastronomia_vernacular", []))

            onto_html = f"""
            <div class="onto-grid">
                <div class="onto-card">
                    <div class="onto-card-header">📍 Destino & Terreno</div>
                    <div class="onto-card-body">
                        <p><strong>Local:</strong> {ontological_data.get('destino_principal')}</p>
                        <p><strong>Piso:</strong> {ontological_data.get('tipo_estrada')}</p>
                        <p><strong>Extensão / Altimetria:</strong> {ontological_data.get('extensao_e_altimetria')}</p>
                        <p><strong>Severidade:</strong> <span class="badge-amber">{ontological_data.get('nivel_severidade')}</span></p>
                        <p><strong>Melhor Época:</strong> {ontological_data.get('melhor_epoca')}</p>
                    </div>
                </div>

                <div class="onto-card">
                    <div class="onto-card-header">⛽ Cidades-Base & Logística</div>
                    <div class="onto-card-body">
                        <div class="pill-group">{cidades or 'N/A'}</div>
                        <h4 style="margin-top:16px; margin-bottom:8px; font-size:14px; color:#cbd5e1;">⚠️ Alertas de Risco de Estrada:</h4>
                        <div class="pill-group">{riscos or 'N/A'}</div>
                    </div>
                </div>

                <div class="onto-card">
                    <div class="onto-card-header">🍲 Gastronomia Vernacular</div>
                    <div class="onto-card-body">
                        <div class="pill-group">{gastro or 'N/A'}</div>
                    </div>
                </div>

                <div class="onto-card onto-full">
                    <div class="onto-card-header">🏍️ História Real de Eduardo Generali (Matéria-Prima)</div>
                    <div class="onto-card-body">
                        <h3 style="color:#f97316; margin-top:0;">{hist.get('titulo', 'Vivência de Estrada')}</h3>
                        <p><strong>Situação:</strong> {hist.get('situacao', 'N/A')}</p>
                        <p><strong>Lição de Campo:</strong> {hist.get('licao_pratica', 'N/A')}</p>
                        <blockquote class="eduardo-quote" style="margin-top:12px;">"{hist.get('frase_de_efeito', 'Conhecimento vira liberdade. Boa estrada sempre!')}"</blockquote>
                    </div>
                </div>
            </div>
            """
        else:
            onto_html = "<div class='onto-card'><p>Destino explorado com base nas diretrizes gerais de expedição MotoNomads.</p></div>"

        # Template HTML Completo
        full_html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page_title} | Painel Editorial MotoNomads</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-deep: #0b0f19;
            --bg-surface: #131c2e;
            --bg-surface-elevated: #1a263e;
            --border-subtle: rgba(255, 255, 255, 0.08);
            --border-hover: rgba(249, 115, 22, 0.3);
            --orange-primary: #f97316;
            --orange-hover: #fb923c;
            --amber-accent: #f59e0b;
            --emerald-pass: #10b981;
            --blue-accent: #38bdf8;
            --text-main: #f1f5f9;
            --text-secondary: #94a3b8;
            --text-muted: #64748b;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: var(--bg-deep);
            color: var(--text-main);
            line-height: 1.65;
            padding-bottom: 80px;
        }}

        /* Header MotoNomads */
        header.top-header {{
            background: linear-gradient(180deg, #162033 0%, rgba(11, 15, 25, 0.95) 100%);
            border-bottom: 1px solid var(--border-subtle);
            padding: 24px 32px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: sticky;
            top: 0;
            z-index: 100;
            backdrop-filter: blur(12px);
        }}

        .brand-container {{
            display: flex;
            align-items: center;
            gap: 16px;
        }}

        .brand-logo-text {{
            font-family: 'Outfit', sans-serif;
            font-size: 26px;
            font-weight: 800;
            letter-spacing: -0.5px;
            color: #ffffff;
            display: flex;
            align-items: center;
            gap: 6px;
        }}

        .brand-logo-text span {{
            color: var(--orange-primary);
        }}

        .brand-slogan {{
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            color: var(--text-secondary);
        }}

        .header-badges {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .badge-pill {{
            background: rgba(249, 115, 22, 0.12);
            color: var(--orange-primary);
            border: 1px solid rgba(249, 115, 22, 0.3);
            padding: 6px 14px;
            border-radius: 999px;
            font-size: 13px;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 6px;
        }}

        .badge-status {{
            background: rgba(16, 185, 129, 0.15);
            color: var(--emerald-pass);
            border: 1px solid rgba(16, 185, 129, 0.3);
            padding: 6px 14px;
            border-radius: 999px;
            font-size: 13px;
            font-weight: 600;
        }}

        /* Container Principal */
        .main-container {{
            max-width: 1200px;
            margin: 32px auto 0;
            padding: 0 24px;
        }}

        /* Barra de Métricas Rápidas */
        .metrics-banner {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 16px;
            margin-bottom: 32px;
        }}

        .metric-card {{
            background: var(--bg-surface);
            border: 1px solid var(--border-subtle);
            border-radius: 12px;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 6px;
            transition: transform 0.2s ease, border-color 0.2s ease;
        }}

        .metric-card:hover {{
            transform: translateY(-2px);
            border-color: var(--border-hover);
        }}

        .metric-label {{
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            color: var(--text-secondary);
            font-weight: 600;
        }}

        .metric-value {{
            font-family: 'Outfit', sans-serif;
            font-size: 28px;
            font-weight: 700;
            color: #ffffff;
            display: flex;
            align-items: baseline;
            gap: 4px;
        }}

        .metric-value small {{
            font-size: 14px;
            font-weight: 500;
            color: var(--text-muted);
        }}

        .metric-note {{
            font-size: 12px;
            color: var(--text-muted);
        }}

        /* Navegação por Abas */
        .nav-tabs {{
            display: flex;
            gap: 8px;
            border-bottom: 1px solid var(--border-subtle);
            margin-bottom: 28px;
            overflow-x: auto;
            padding-bottom: 4px;
        }}

        .tab-btn {{
            background: none;
            border: none;
            color: var(--text-secondary);
            font-family: 'Outfit', sans-serif;
            font-size: 15px;
            font-weight: 600;
            padding: 12px 20px;
            cursor: pointer;
            border-bottom: 3px solid transparent;
            transition: all 0.2s ease;
            white-space: nowrap;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .tab-btn:hover {{
            color: #ffffff;
            background: rgba(255, 255, 255, 0.03);
            border-radius: 8px 8px 0 0;
        }}

        .tab-btn.active {{
            color: var(--orange-primary);
            border-bottom-color: var(--orange-primary);
        }}

        /* Conteúdo das Abas */
        .tab-pane {{
            display: none;
            animation: fadeIn 0.25s ease-in-out;
        }}

        .tab-pane.active {{
            display: block;
        }}

        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(6px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        /* Layout do Artigo (Reader Mode) */
        .article-card {{
            background: var(--bg-surface);
            border: 1px solid var(--border-subtle);
            border-radius: 16px;
            padding: 48px;
            box-shadow: 0 12px 32px rgba(0, 0, 0, 0.25);
        }}

        .article-h1 {{
            font-family: 'Outfit', sans-serif;
            font-size: 38px;
            font-weight: 800;
            letter-spacing: -0.8px;
            color: #ffffff;
            margin-bottom: 24px;
            line-height: 1.25;
        }}

        .article-h2 {{
            font-family: 'Outfit', sans-serif;
            font-size: 24px;
            font-weight: 700;
            color: #f8fafc;
            margin-top: 40px;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 10px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            padding-bottom: 8px;
        }}

        .h2-marker {{
            color: var(--orange-primary);
            font-size: 18px;
        }}

        .article-h3 {{
            font-family: 'Outfit', sans-serif;
            font-size: 19px;
            font-weight: 600;
            color: #e2e8f0;
            margin-top: 24px;
            margin-bottom: 10px;
        }}

        .article-p {{
            font-size: 17px;
            color: #cbd5e1;
            margin-bottom: 20px;
            line-height: 1.8;
        }}

        .article-ul {{
            margin-left: 24px;
            margin-bottom: 24px;
        }}

        .article-li {{
            margin-bottom: 8px;
            color: #cbd5e1;
        }}

        .eduardo-quote {{
            background: rgba(249, 115, 22, 0.08);
            border-left: 4px solid var(--orange-primary);
            padding: 18px 24px;
            border-radius: 0 10px 10px 0;
            font-style: italic;
            color: #fdba74;
            margin: 28px 0;
            font-size: 17px;
        }}

        /* Tabela Estilizada de Expedição */
        .table-container {{
            margin: 32px 0;
            overflow-x: auto;
            border-radius: 12px;
            border: 1px solid var(--border-subtle);
        }}

        .expedition-table {{
            width: 100%;
            border-collapse: collapse;
            text-align: left;
            font-size: 15px;
        }}

        .expedition-table th {{
            background: #1e293b;
            color: #f8fafc;
            font-family: 'Outfit', sans-serif;
            font-weight: 600;
            padding: 14px 20px;
            border-bottom: 1px solid var(--border-subtle);
        }}

        .expedition-table td {{
            padding: 14px 20px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.04);
            color: #cbd5e1;
        }}

        .expedition-table tr:last-child td {{
            border-bottom: none;
        }}

        .expedition-table tr:hover td {{
            background: rgba(255, 255, 255, 0.02);
        }}

        /* Grid da Ontologia */
        .onto-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 20px;
        }}

        .onto-card {{
            background: var(--bg-surface);
            border: 1px solid var(--border-subtle);
            border-radius: 14px;
            overflow: hidden;
        }}

        .onto-full {{
            grid-column: 1 / -1;
        }}

        .onto-card-header {{
            background: #1e293b;
            padding: 14px 20px;
            font-family: 'Outfit', sans-serif;
            font-weight: 700;
            font-size: 15px;
            color: #f1f5f9;
            border-bottom: 1px solid var(--border-subtle);
        }}

        .onto-card-body {{
            padding: 20px;
        }}

        .pill-group {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 6px;
        }}

        .onto-pill {{
            background: rgba(56, 189, 248, 0.12);
            color: var(--blue-accent);
            border: 1px solid rgba(56, 189, 248, 0.25);
            padding: 5px 12px;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 500;
        }}

        .onto-pill.risk {{
            background: rgba(239, 68, 68, 0.12);
            color: #f87171;
            border-color: rgba(239, 68, 68, 0.25);
        }}

        .onto-pill.gastro {{
            background: rgba(16, 185, 129, 0.12);
            color: #34d399;
            border-color: rgba(16, 185, 129, 0.25);
        }}

        .badge-amber {{
            background: rgba(245, 158, 11, 0.2);
            color: #fbbf24;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
        }}

        /* Código & JSON-LD */
        .code-block {{
            background: #090d16;
            border: 1px solid var(--border-subtle);
            border-radius: 12px;
            padding: 20px;
            font-family: 'Courier New', Courier, monospace;
            font-size: 14px;
            color: #38bdf8;
            overflow-x: auto;
            white-space: pre-wrap;
            position: relative;
        }}

        .copy-btn {{
            position: absolute;
            top: 14px;
            right: 14px;
            background: var(--bg-surface-elevated);
            color: #ffffff;
            border: 1px solid var(--border-subtle);
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 12px;
            cursor: pointer;
            transition: all 0.2s;
        }}

        .copy-btn:hover {{
            background: var(--orange-primary);
        }}

        .meta-field {{
            margin-bottom: 20px;
        }}

        .meta-field label {{
            display: block;
            font-size: 13px;
            text-transform: uppercase;
            font-weight: 700;
            color: var(--text-secondary);
            margin-bottom: 6px;
        }}

        .meta-field input, .meta-field textarea {{
            width: 100%;
            background: #090d16;
            border: 1px solid var(--border-subtle);
            color: #ffffff;
            padding: 12px 16px;
            border-radius: 8px;
            font-family: inherit;
            font-size: 15px;
        }}

        @media (max-width: 768px) {{
            .article-card {{ padding: 24px; }}
            .article-h1 {{ font-size: 28px; }}
            header.top-header {{ flex-direction: column; gap: 16px; align-items: flex-start; }}
        }}
    </style>
</head>
<body>

    <!-- Header Fixo de Marca -->
    <header class="top-header">
        <div class="brand-container">
            <div>
                <div class="brand-logo-text">MOTO<span>NOMADS</span> 🏍️</div>
                <div class="brand-slogan">Experiência • Estrada • Pessoas • Sempre mais longe</div>
            </div>
        </div>
        <div class="header-badges">
            <span class="badge-pill">Pilar: {pillar.title().replace('_', ' ')}</span>
            <span class="badge-status">✔ Veredicto: Aprovado para Publicação</span>
        </div>
    </header>

    <div class="main-container">

        <!-- Métricas Rápidas -->
        <div class="metrics-banner">
            <div class="metric-card">
                <span class="metric-label">Tom de Voz (Eduardo Generali)</span>
                <div class="metric-value">{tone_score} <small>/ 100</small></div>
                <span class="metric-note">Conectores orais e autenticidade de campo</span>
            </div>
            <div class="metric-card">
                <span class="metric-label">Conformidade GEO & SEO</span>
                <div class="metric-value">{geo_score} <small>/ 100</small></div>
                <span class="metric-note">Otimizado para ChatGPT, Perplexity & Google</span>
            </div>
            <div class="metric-card">
                <span class="metric-label">Grafo Ontológico</span>
                <div class="metric-value">Ativo <small>✔</small></div>
                <span class="metric-note">Entidades, rotas e casos reais correlacionados</span>
            </div>
            <div class="metric-card">
                <span class="metric-label">Palavra-Chave Foco</span>
                <div class="metric-value" style="font-size: 18px; color: var(--orange-primary);">{target_keyword or 'Serra & Expedição'}</div>
                <span class="metric-note">Intenção de busca informacional de viagem</span>
            </div>
        </div>

        <!-- Abas de Navegação -->
        <div class="nav-tabs">
            <button class="tab-btn active" onclick="switchTab('article-tab')">📖 Artigo Final (Visual Reader)</button>
            <button class="tab-btn" onclick="switchTab('onto-tab')">🗺️ Grafo Ontológico do Artigo</button>
            <button class="tab-btn" onclick="switchTab('audit-tab')">🧐 Parecer da Auditoria (Marcus)</button>
            <button class="tab-btn" onclick="switchTab('seo-tab')">🏷️ Metadados & Schema GEO (JSON-LD)</button>
        </div>

        <!-- ABA 1: ARTIGO FORMATADO -->
        <div id="article-tab" class="tab-pane active">
            <article class="article-card">
                {article_html}
            </article>
        </div>

        <!-- ABA 2: GRAFO ONTOLÓGICO -->
        <div id="onto-tab" class="tab-pane">
            <div class="article-card">
                <h2 style="font-family:'Outfit'; margin-bottom:20px; color:#ffffff;">Conexões do Grafo Semântico Identificadas</h2>
                {onto_html}
            </div>
        </div>

        <!-- ABA 3: AUDITORIA -->
        <div id="audit-tab" class="tab-pane">
            <div class="article-card">
                {audit_html}
            </div>
        </div>

        <!-- ABA 4: METADADOS & SCHEMA GEO -->
        <div id="seo-tab" class="tab-pane">
            <div class="article-card">
                <h2 style="font-family:'Outfit'; margin-bottom:24px; color:#ffffff;">Metadados Prontos para Publicação Web</h2>
                
                <div class="meta-field">
                    <label>Title Tag (SEO & Snippet)</label>
                    <input type="text" value="{meta_title}" readonly>
                </div>

                <div class="meta-field">
                    <label>Meta Description (145 a 160 caracteres)</label>
                    <textarea rows="3" readonly>{meta_description}</textarea>
                </div>

                <div class="meta-field">
                    <label>FAQ Schema Estruturado para IAs (JSON-LD)</label>
                    <div class="code-block">
                        <button class="copy-btn" onclick="copySchema()">Copiar JSON-LD</button>
                        <code id="schema-code">{schema_formatted}</code>
                    </div>
                </div>
            </div>
        </div>

    </div>

    <script>
        function switchTab(tabId) {{
            document.querySelectorAll('.tab-pane').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));

            document.getElementById(tabId).classList.add('active');
            event.currentTarget.classList.add('active');
        }}

        function copySchema() {{
            const code = document.getElementById('schema-code').innerText;
            navigator.clipboard.writeText(code).then(() => {{
                alert('Código Schema JSON-LD copiado para a área de transferência!');
            }});
        }}
    </script>
</body>
</html>
"""
        with open(output_file_path, "w", encoding="utf-8") as f:
            f.write(full_html)

        return output_file_path

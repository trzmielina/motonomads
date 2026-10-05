"""
Módulo de Otimização e Validação GEO (Generative Engine Optimization) e SEO.
Garante que o artigo atenda aos requisitos de ranqueamento tradicional e citação direta por LLMs.
"""

import json
import re
import yaml
from typing import Dict, Any, List


class GeoSeoOptimizer:
    """Verifica e enriquece matérias com padrões estritos de GEO e SEO."""

    def __init__(self, config_path: str = "config/geo_seo_guidelines.yaml"):
        self.config = self._load_config(config_path)
        self.geo_cfg = self.config.get("geo", {})
        self.seo_cfg = self.config.get("seo", {})

    def _load_config(self, path: str) -> Dict[str, Any]:
        try:
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception:
            return {}

    def audit_geo_seo(self, markdown_text: str, target_keyword: str = "") -> Dict[str, Any]:
        """Avalia conformidade do artigo com normas GEO e SEO."""
        findings = []
        score = 100

        # 1. Checagem de H1
        h1_matches = re.findall(r"^#\s+(.+)$", markdown_text, re.MULTILINE)
        if len(h1_matches) == 0:
            score -= 20
            findings.append("Erro SEO Crítico: Artigo não possui tag H1.")
        elif len(h1_matches) > 1:
            score -= 10
            findings.append("Alerta SEO: Múltiplas tags H1 detectadas. Mantenha apenas uma única tag H1.")

        # 2. Checagem de Tabela Estruturada (Obrigatória em GEO)
        table_match = re.search(r"\|.+\|\n\|[-:\s|]+\|\n(\|.+\|\n?)+", markdown_text)
        has_table = bool(table_match)
        if not has_table:
            score -= 15
            findings.append("Erro GEO: Nenhuma tabela Markdown estruturada encontrada. Ficha técnica de rota é obrigatória.")

        # 3. Checagem de FAQ (Obrigatório para citação em IA)
        has_faq = bool(re.search(r"##\s+(Perguntas Frequentes|FAQ)", markdown_text, re.IGNORECASE))
        if not has_faq:
            score -= 15
            findings.append("Erro GEO/SEO: Seção de Perguntas Frequentes (FAQ) ausente.")

        # 4. Checagem de Direct-Answer Snippets sob os H2s
        h2_sections = re.split(r"\n##\s+", markdown_text)[1:]
        short_answers_count = 0
        for sec in h2_sections:
            lines = [l.strip() for l in sec.split("\n") if l.strip() and not l.startswith("#") and not l.startswith("|")]
            if lines:
                first_p_words = len(lines[0].split())
                if 35 <= first_p_words <= 70:
                    short_answers_count += 1

        if short_answers_count < 2:
            score -= 10
            findings.append(
                "Alerta GEO: Poucos parágrafos de resposta direta (35-70 palavras) logo abaixo dos H2s. "
                "Adicione respostas diretas e concisas para alimentar citações por IA."
            )

        # 5. Checagem de Palavra-chave (se informada)
        if target_keyword:
            kw_count = len(re.findall(re.escape(target_keyword), markdown_text, re.IGNORECASE))
            total_words = len(markdown_text.split())
            density = (kw_count / max(total_words, 1)) * 100
            if kw_count == 0:
                score -= 15
                findings.append(f"Erro SEO: Palavra-chave foco '{target_keyword}' não encontrada no texto.")
            elif density < 0.8:
                findings.append(f"Alerta SEO: Densidade da palavra-chave baixa ({density:.2f}%). Alvo recomendado: 1.2% a 1.8%.")
            elif density > 2.5:
                score -= 10
                findings.append(f"Alerta SEO: Densidade da palavra-chave excessiva ({density:.2f}%). Risco de keyword stuffing.")

        return {
            "score": max(0, score),
            "passed": score >= 85,
            "has_h1": len(h1_matches) == 1,
            "has_structured_table": has_table,
            "has_faq_section": has_faq,
            "findings": findings,
        }

    def generate_faq_json_ld(self, faq_pairs: List[Dict[str, str]]) -> str:
        """Gera código Schema.org JSON-LD para a seção de FAQ."""
        schema = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": []
        }
        for item in faq_pairs:
            schema["mainEntity"].append({
                "@type": "Question",
                "name": item.get("question", ""),
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": item.get("answer", "")
                }
            })
        return json.dumps(schema, ensure_ascii=False, indent=2)

"""
Módulo de Validação e Análise da Matriz de Tom de Voz Motonomads.
Avalia a presença de clichês, ritmo de frases, jargões técnicos dos pilares e sensorialidade.
"""

import re
import yaml
from typing import Dict, Any, List


class ToneMatrixEvaluator:
    """Audita e pontua textos de acordo com a tabela de tom de voz Motonomads."""

    def __init__(self, config_path: str = "config/tone_of_voice.yaml"):
        self.config = self._load_config(config_path)
        self.config = self._load_config(config_path)
        self.forbidden_terms = self.config.get("forbidden_cliches", self.config.get("forbidden_terms", []))
        self.oral_connectors = self.config.get("oral_connectors", {}).get("always_use_naturally", [])
        self.pillars = self.config.get("pillars", {})

    def _load_config(self, path: str) -> Dict[str, Any]:
        try:
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception:
            return {}

    def audit_text(self, text: str, pillar_key: str = "mototurismo") -> Dict[str, Any]:
        """Executa auditoria completa de tom de voz e gera pontuação de 0 a 100."""
        text_lower = text.lower()
        findings = []
        deductions = 0

        # 1. Checagem de Termos Proibidos (Clichês)
        forbidden_found = []
        for term in self.forbidden_terms:
            if term.lower() in text_lower:
                forbidden_found.append(term)
                deductions += 10
                findings.append(f"Clichê detectado: '{term}'. Substitua pela voz autêntica e sensorial do Eduardo Generali.")

        # 2. Checagem de Conectores de Oralidade Naturais do Eduardo
        connectors_found = [c for c in self.oral_connectors if c.lower().strip("...") in text_lower]
        if len(connectors_found) < 2:
            deductions += 10
            findings.append(
                "Texto soando excessivamente acadêmico ou impessoal. Incorpore conectores naturais do Eduardo "
                "(ex: 'Na verdade...', 'Para mim...', 'Minha dica é...', 'Por exemplo...', 'Faz muita diferença', 'Boa estrada sempre!')."
            )

        # 3. Checagem de Jargões do Pilar
        pillar_info = self.pillars.get(pillar_key, {})
        expected_keywords = pillar_info.get("keywords", [])
        keywords_present = [kw for kw in expected_keywords if kw.lower() in text_lower]

        jargon_ratio = len(keywords_present) / max(len(expected_keywords), 1)
        if jargon_ratio < 0.25:
            deductions += 10
            findings.append(
                f"Baixa densidade de vocabulário específico do pilar '{pillar_key}'. "
                f"Palavras recomendadas a incorporar: {', '.join(expected_keywords)}"
            )

        # 3. Análise de Ritmo e Extensão Média de Frases
        sentences = [s.strip() for s in re.split(r"[.!?]+", text) if len(s.strip()) > 5]
        if sentences:
            avg_words_per_sentence = sum(len(s.split()) for s in sentences) / len(sentences)
            if avg_words_per_sentence > 25:
                deductions += 10
                findings.append(
                    f"Frases excessivamente longas (média de {avg_words_per_sentence:.1f} palavras). "
                    "Quebre em orações mais diretas para manter o ritmo expedicionário dinâmico."
                )
        else:
            avg_words_per_sentence = 0

        # 4. Checagem de Especificações Técnicas (Métricas / Entidades)
        metric_patterns = [
            r"\d+\s*km",
            r"\d+\s*psi",
            r"\d+\s*m(etros)?\s*(de altitude)?",
            r"\d+\s*cc",
            r"br-\d+",
        ]
        has_metrics = any(re.search(pat, text_lower) for pat in metric_patterns)
        if not has_metrics:
            deductions += 15
            findings.append(
                "Falta de especificações métricas e dados de campo (quilometragem, altitude, pressão de pneus, rodovias)."
            )

        score = max(0, 100 - deductions)

        return {
            "score": score,
            "passed": score >= 85,
            "pillar_evaluated": pillar_key,
            "forbidden_terms_found": forbidden_found,
            "pillar_keywords_found": keywords_present,
            "average_words_per_sentence": round(avg_words_per_sentence, 1),
            "findings_and_recommendations": findings,
        }

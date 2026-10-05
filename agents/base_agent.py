"""
Classe Base para todos os agentes do time Motonomads Redatores.
Gerencia personas, regras de prompt, e chamadas para provedores de LLM.
"""

import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()


class BaseAgent:
    """Classe base para os especialistas da redação Motonomads."""

    def __init__(
        self,
        name: str,
        title: str,
        icon: str,
        role: str,
        communication_style: str,
        principles: list,
        forbidden_terms: list,
        recommended_terms: list,
    ):
        self.name = name
        self.title = title
        self.icon = icon
        self.role = role
        self.communication_style = communication_style
        self.principles = principles
        self.forbidden_terms = forbidden_terms
        self.recommended_terms = recommended_terms

        self.provider = os.getenv("DEFAULT_LLM_PROVIDER", "openai").lower()
        self.model = os.getenv("DEFAULT_MODEL", "gpt-4o")

    def build_system_prompt(self) -> str:
        """Monta o system prompt do agente com todas as diretrizes de persona."""
        prompt = [
            f"# VOCÊ É: {self.name} {self.icon} — {self.title}",
            "",
            "## SEU PAPEL:",
            self.role,
            "",
            "## ESTILO DE COMUNICAÇÃO:",
            self.communication_style,
            "",
            "## SEUS PRINCÍPIOS FUNDAMENTAIS:",
        ]
        for p in self.principles:
            prompt.append(f"- {p}")

        prompt.append("")
        prompt.append("## VOCABULÁRIO PROIBIDO (NUNCA UTILIZE):")
        for term in self.forbidden_terms:
            prompt.append(f"- '{term}'")

        prompt.append("")
        prompt.append("## TERMOS E JARGÕES OBRIGATÓRIOS DO SEU DOMÍNIO:")
        for term in self.recommended_terms:
            prompt.append(f"- '{term}'")

        prompt.append("")
        prompt.append("## NORMA EDITORIAL MOTONOMADS:")
        prompt.append(
            "Você escreve com rigor factual, vivência de estrada e campo, "
            "sem clichês turísticos vazios, otimizando simultaneamente para SEO e citação direta por IAs (GEO)."
        )

        return "\n".join(prompt)

    def execute_prompt(self, user_prompt: str, system_override: Optional[str] = None) -> str:
        """Envia o prompt para a LLM configurada (OpenAI, Anthropic, Gemini) ou gera resposta fallback."""
        system_prompt = system_override or self.build_system_prompt()

        # 1. Tentativa OpenAI
        if self.provider == "openai" and os.getenv("OPENAI_API_KEY"):
            try:
                from openai import OpenAI
                client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                response = client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.6,
                )
                return response.choices[0].message.content or ""
            except Exception as e:
                print(f"[{self.name}] Erro OpenAI: {e}. Tentando fallback.")

        # 2. Tentativa Anthropic
        if self.provider == "anthropic" and os.getenv("ANTHROPIC_API_KEY"):
            try:
                import anthropic
                client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
                message = client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=4000,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_prompt}],
                )
                return message.content[0].text
            except Exception as e:
                print(f"[{self.name}] Erro Anthropic: {e}. Tentando fallback.")

        # 3. Tentativa Google Gemini
        if self.provider == "gemini" and os.getenv("GEMINI_API_KEY"):
            try:
                import google.generativeai as genai
                genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
                model = genai.GenerativeModel(
                    model_name="gemini-1.5-pro-latest",
                    system_instruction=system_prompt,
                )
                response = model.generate_content(user_prompt)
                return response.text
            except Exception as e:
                print(f"[{self.name}] Erro Gemini: {e}. Tentando fallback.")

        # 4. Resposta Estruturada Local (quando rodado sem chaves no ambiente de desenvolvimento)
        return self._generate_local_fallback(user_prompt)

    def _generate_local_fallback(self, user_prompt: str) -> str:
        """Retorna uma estrutura consistente e realista quando executado em modo offline."""
        return (
            f"<!-- Resposta gerada por {self.name} ({self.title}) [Modo Simulado / Chave de API não detectada] -->\n\n"
            f"Processamento editorial realizado por **{self.name}** com base nas diretrizes de **{self.title}**.\n\n"
            f"Para execução com os modelos de ponta (GPT-4o, Claude 3.5 Sonnet ou Gemini Pro), "
            f"configure sua respectiva chave de API no arquivo `.env`."
        )

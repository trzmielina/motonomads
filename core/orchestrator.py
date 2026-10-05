"""
Orquestrador Central da Redação Motonomads.
Executa o pipeline editorial unindo pesquisa jornalística, estratégia SEO/GEO,
redação especialista temática, harmonização de tom de voz e auditoria rigorosa.
"""

import os
import time
from typing import Dict, Any, Optional

from core.crawler import ArticleExtractor
from core.tone_matrix import ToneMatrixEvaluator
from core.geo_optimizer import GeoSeoOptimizer
from core.ontology_engine import OntologyEngine

from agents.diego_jornalista import DiegoJornalista
from agents.marina_estrategista import MarinaEstrategista
from agents.rodrigo_mototurismo import RodrigoMototurismo
from agents.bruno_offroad import BrunoOffroad
from agents.clara_aventura import ClaraAventura
from agents.lucas_turismo import LucasTurismo
from agents.helena_editora import HelenaEditora
from agents.marcus_auditor import MarcusAuditor


class MotonomadsOrchestrator:
    """Orquestrador do squad de redação Motonomads."""

    def __init__(self, base_dir: str = "."):
        self.base_dir = base_dir
        self.extractor = ArticleExtractor()
        self.tone_evaluator = ToneMatrixEvaluator(os.path.join(base_dir, "config/tone_of_voice.yaml"))
        self.geo_optimizer = GeoSeoOptimizer(os.path.join(base_dir, "config/geo_seo_guidelines.yaml"))
        self.ontology = OntologyEngine(os.path.join(base_dir, "input/ontologias"))

        # Carregar time de agentes
        self.diego = DiegoJornalista()
        self.marina = MarinaEstrategista()
        self.rodrigo = RodrigoMototurismo()
        self.bruno = BrunoOffroad()
        self.clara = ClaraAventura()
        self.lucas = LucasTurismo()
        self.helena = HelenaEditora()
        self.marcus = MarcusAuditor()

        # Carregar referência de tom de voz
        self.tabela_tom_ref = self._load_file("data/tone_matrix_reference.md")

    def _load_file(self, rel_path: str) -> str:
        full_path = os.path.join(self.base_dir, rel_path)
        if os.path.exists(full_path):
            with open(full_path, "r", encoding="utf-8") as f:
                return f.read()
        return ""

    def run_pipeline(
        self,
        source: str,
        pillar: str = "mototurismo",
        target_keyword: str = "",
        on_step_callback: Optional[callable] = None,
    ) -> Dict[str, Any]:
        """
        Executa o pipeline editorial completo de ponta a ponta.
        :param source: URL web ou caminho de arquivo local (.md / .txt).
        :param pillar: 'mototurismo' | 'offroad_4x4' | 'aventura_outdoor' | 'turismo_cultura'
        :param target_keyword: Palavra-chave principal opcional para SEO/GEO.
        :param on_step_callback: Função para reportar progresso para a CLI / UI.
        """
        def step(msg: str):
            if on_step_callback:
                on_step_callback(msg)
            else:
                print(f"[*] {msg}")

        # ETAPA 1: Ingestão de Conteúdo Base
        step("Etapa 1/6: Ingestão e extração do artigo ou texto base...")
        if source.startswith("http://") or source.startswith("https://"):
            raw_data = self.extractor.extract_from_url(source)
        else:
            raw_data = self.extractor.extract_from_file(source)

        if raw_data.get("status") == "error":
            return {"status": "error", "error": raw_data.get("error_message")}

        titulo_original = raw_data.get("title", "Expedição sem título")
        conteudo_original = raw_data.get("content", "")

        # ETAPA INTERMEDIÁRIA: Consulta ao Grafo Ontológico MotoNomads
        step("Etapa de Inteligência: Cruzando entidades e relações no Grafo Ontológico...")
        ontological_data = self.ontology.build_ontological_brief(f"{titulo_original} {conteudo_original}")
        contexto_ontologico_txt = ""
        if ontological_data.get("matched"):
            contexto_ontologico_txt = (
                f"\n\n--- DADOS VINCULADOS DO GRAFO ONTOLÓGICO MOTONOMADS ---\n"
                f"Destino Mapeado: {ontological_data.get('destino_principal')}\n"
                f"Tipo de Pavimento: {ontological_data.get('tipo_estrada')}\n"
                f"Extensão e Altimetria: {ontological_data.get('extensao_e_altimetria')}\n"
                f"Nível de Severidade: {ontological_data.get('nivel_severidade')}\n"
                f"Melhor Época: {ontological_data.get('melhor_epoca')}\n"
                f"Cidades-Base de Apoio: {', '.join(ontological_data.get('cidades_base_logistica', []))}\n"
                f"Riscos Críticos de Campo: {', '.join(ontological_data.get('riscos_criticos', []))}\n"
                f"Gastronomia Vernacular: {', '.join(ontological_data.get('gastronomia_vernacular', []))}\n"
            )
            hist = ontological_data.get("historia_real_eduardo")
            if hist and hist.get("titulo"):
                contexto_ontologico_txt += (
                    f"\nHistória Real do Eduardo Generali para Conexão:\n"
                    f"- Caso: {hist.get('titulo')}\n"
                    f"- Situação: {hist.get('situacao')}\n"
                    f"- Lição Prática: {hist.get('licao_pratica')}\n"
                    f"- Frase de Efeito do Eduardo: '{hist.get('frase_de_efeito')}'\n"
                )

        # ETAPA 2: Investigação Jornalística & Enriquecimento
        step(f"Etapa 2/6: Diego Jornalista realizando fact-checking e dossiê investigativo...")
        texto_para_investigacao = f"{conteudo_original}\n{contexto_ontologico_txt}"
        dossie_jornalistico = self.diego.investigar_e_enriquecer(texto_para_investigacao, titulo_original)

        # ETAPA 3: Arquitetura de SEO Tradicional & GEO para IAs
        step("Etapa 3/6: Marina Estrategista desenhando arquitetura de busca e blocos de citação para IAs...")
        briefing_seo_geo = self.marina.planejar_arquitetura_seo_geo(titulo_original, dossie_jornalistico)

        # ETAPA 4: Redação por Especialista Temático
        specialist_name = ""
        specialist_text = ""
        if pillar == "mototurismo":
            step("Etapa 4/6: Rodrigo Mototurismo redigindo matéria especializada em duas rodas...")
            specialist_name = self.rodrigo.name
            specialist_text = self.rodrigo.redigir_materia(briefing_seo_geo, dossie_jornalistico, conteudo_original)
        elif pillar in ["offroad_4x4", "4x4"]:
            step("Etapa 4/6: Bruno Off-Road redigindo matéria especializada em 4x4 e overlanding...")
            specialist_name = self.bruno.name
            specialist_text = self.bruno.redigir_materia(briefing_seo_geo, dossie_jornalistico, conteudo_original)
        elif pillar in ["aventura_outdoor", "aventura", "outdoor"]:
            step("Etapa 4/6: Clara Aventura redigindo matéria especializada em trekking e outdoor...")
            specialist_name = self.clara.name
            specialist_text = self.clara.redigir_materia(briefing_seo_geo, dossie_jornalistico, conteudo_original)
        else:
            step("Etapa 4/6: Lucas Turismo redigindo matéria especializada em destinos e cultura regional...")
            specialist_name = self.lucas.name
            specialist_text = self.lucas.redigir_materia(briefing_seo_geo, dossie_jornalistico, conteudo_original)

        # ETAPA 5: Harmonização Editorial & Aplicação da Matriz de Tom de Voz
        step("Etapa 5/6: Helena Editora aplicando rigorosamente a Tabela de Tom de Voz Motonomads...")
        artigo_harmonizado = self.helena.harmonizar_e_editar(
            texto_rascunho=specialist_text,
            pilar_escolhido=pillar,
            tabela_tom_ref=self.tabela_tom_ref,
        )

        # Checagens Algorítmicas Locais (Validação estática de regras)
        local_tone_audit = self.tone_evaluator.audit_text(artigo_harmonizado, pillar)
        local_geo_audit = self.geo_optimizer.audit_geo_seo(artigo_harmonizado, target_keyword)

        # ETAPA 6: Auditoria Cruzada de Qualidade, Fatos e Padrões GEO/SEO
        step("Etapa 6/6: Marcus Auditor realizando auditoria final cruzada e emitindo parecer formal...")
        relatorio_auditoria = self.marcus.auditar_artigo(artigo_harmonizado, pillar, target_keyword)

        # Gerar arquivos de saída
        timestamp = int(time.time())
        slug_seguro = "".join(c if c.isalnum() else "_" for c in titulo_original.lower())[:30]
        filename_base = f"materia_{slug_seguro}_{timestamp}"

        output_dir = os.path.join(self.base_dir, "output")
        os.makedirs(output_dir, exist_ok=True)

        artigo_path = os.path.join(output_dir, f"{filename_base}.md")
        auditoria_path = os.path.join(output_dir, f"{filename_base}_auditoria.md")

        with open(artigo_path, "w", encoding="utf-8") as f:
            f.write(artigo_harmonizado)

        with open(auditoria_path, "w", encoding="utf-8") as f:
            f.write(relatorio_auditoria)

        return {
            "status": "success",
            "article_file": artigo_path,
            "audit_file": auditoria_path,
            "pillar": pillar,
            "specialist": specialist_name,
            "article_preview": artigo_harmonizado[:500] + "...",
            "local_tone_score": local_tone_audit.get("score"),
            "local_geo_score": local_geo_audit.get("score"),
            "local_findings": local_tone_audit.get("findings_and_recommendations", [])
            + local_geo_audit.get("findings", []),
        }

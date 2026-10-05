"""
Motor de Ontologia e Grafo de Conhecimento MotoNomads.
Carrega, indexa e cruza as entidades do universo de viagem, mototurismo e aventura,
gerando dossiês relacionais para alimentar o pipeline dos agentes redatores.
"""

import os
import yaml
from typing import Dict, Any, List, Optional


class OntologyEngine:
    """Explorador e resolvedor de relações do Grafo de Conhecimento MotoNomads."""

    def __init__(self, ontologies_dir: str = "input/ontologias"):
        self.ontologies_dir = ontologies_dir
        self.destinos: List[Dict[str, Any]] = []
        self.veiculos: List[Dict[str, Any]] = []
        self.equipamentos: List[Dict[str, Any]] = []
        self.pilotagem: List[Dict[str, Any]] = []
        self.logistica: List[Dict[str, Any]] = []
        self.historias_eduardo: List[Dict[str, Any]] = []

        self._load_all()

    def _load_yaml(self, filename: str) -> List[Dict[str, Any]]:
        path = os.path.join(self.ontologies_dir, filename)
        if not os.path.exists(path):
            return []
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
                # Se for lista direta ou dicionário com chave raiz
                for val in data.values():
                    if isinstance(val, list):
                        return val
                return []
        except Exception as e:
            print(f"[OntologyEngine] Erro ao carregar {filename}: {e}")
            return []

    def _load_all(self):
        """Carrega todos os domínios ontológicos em memória."""
        self.destinos = self._load_yaml("01_destinos_e_rotas.yaml")
        self.veiculos = self._load_yaml("02_motocicletas_e_veiculos.yaml")
        self.equipamentos = self._load_yaml("03_equipamentos_e_seguranca.yaml")
        self.pilotagem = self._load_yaml("04_pilotagem_e_dinamica_terreno.yaml")
        self.logistica = self._load_yaml("05_logistica_planejamento_cultura.yaml")
        self.historias_eduardo = self._load_yaml("06_historias_e_casos_eduardo.yaml")

    def find_matching_destination(self, text: str) -> Optional[Dict[str, Any]]:
        """Identifica se o texto cita algum destino cadastrado na ontologia."""
        text_lower = text.lower()
        for dest in self.destinos:
            # Checa por ID, nome ou cidades limite
            if dest.get("id", "").replace("_", " ") in text_lower:
                return dest
            if dest.get("nome", "").lower() in text_lower:
                return dest
            for cidade in dest.get("cidades_limite", []):
                if cidade.lower() in text_lower:
                    return dest
        # Se for menções parciais (ex: Canastra, Rastro, Jalapão, Patagônia)
        palavras_chave = {
            "rastro": "serra_do_rio_do_rastro",
            "canastra": "serra_da_canastra",
            "jalapão": "jalapao",
            "jalapao": "jalapao",
            "patagônia": "ruta_40_patagonia",
            "patagonia": "ruta_40_patagonia",
            "ruta 40": "ruta_40_patagonia",
        }
        for kw, dest_id in palavras_chave.items():
            if kw in text_lower:
                for dest in self.destinos:
                    if dest.get("id") == dest_id:
                        return dest
        return None

    def get_related_story(self, destination_id: str) -> Optional[Dict[str, Any]]:
        """Retorna uma história ou caso real do Eduardo associado ao destino."""
        for hist in self.historias_eduardo:
            if hist.get("destino_associado") == destination_id:
                return hist
        return None

    def build_ontological_brief(self, text_or_title: str) -> Dict[str, Any]:
        """
        Gera um dossiê relacional completo cruzando as entidades encontradas
        para guiar Diego Jornalista, Marina Estrategista e o redator especialista.
        """
        destination = self.find_matching_destination(text_or_title)

        if not destination:
            # Fallback genérico quando o destino não está previamente mapeado
            return {
                "matched": False,
                "summary": "Destino específico não mapeado diretamente na ontologia básica. Utilizando diretrizes gerais de mototurismo e aventura.",
            }

        dest_id = destination.get("id")
        conexoes = destination.get("conexoes", {})
        story = self.get_related_story(dest_id)

        # Buscar técnicas de pilotagem compatíveis
        pilotagem_dicas = []
        for pil in self.pilotagem:
            terreno = pil.get("terreno", "").lower()
            if any(t in destination.get("tipo_pavimento", "").lower() for t in ["concreto", "asfalto", "pedra", "areia", "ríp"]):
                pilotagem_dicas.append(pil)

        brief = {
            "matched": True,
            "destino_principal": destination.get("nome"),
            "tipo_estrada": destination.get("tipo_pavimento"),
            "extensao_e_altimetria": f"{destination.get('extensao_km', 'N/A')} km | Altitude Máx: {destination.get('altimetria_maxima_m', 'N/A')} m",
            "nivel_severidade": destination.get("severidade"),
            "melhor_epoca": destination.get("melhor_epoca"),
            "cidades_base_logistica": destination.get("conexoes", {}).get("cidades_base", []),
            "riscos_criticos": destination.get("conexoes", {}).get("riscos", []),
            "gastronomia_vernacular": destination.get("conexoes", {}).get("gastronomia", []),
            "historia_real_eduardo": {
                "titulo": story.get("titulo") if story else None,
                "situacao": story.get("situacao") if story else None,
                "licao_pratica": story.get("licao_pratica") if story else None,
                "frase_de_efeito": story.get("frase_eduardo") if story else None,
            } if story else None,
        }

        return brief

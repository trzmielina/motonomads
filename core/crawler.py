"""
Módulo extrator e limpador de textos e matérias já publicadas.
Suporta URLs da web e arquivos de texto locais (Markdown / TXT / HTML).
"""

import os
import re
from typing import Dict, Any
import requests
from bs4 import BeautifulSoup


class ArticleExtractor:
    """Extrai e higieniza textos de artigos para o time de redação."""

    def __init__(self, timeout: int = 15):
        self.timeout = timeout
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
        }

    def extract_from_url(self, url: str) -> Dict[str, Any]:
        """Baixa o conteúdo de uma URL e extrai título, texto e metadados."""
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # Remover scripts, styles e tags desnecessárias
            for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
                tag.decompose()

            # Extração de Título
            title = ""
            if soup.title and soup.title.string:
                title = soup.title.string.strip()
            elif soup.find("h1"):
                title = soup.find("h1").get_text().strip()

            # Extração dos parágrafos principais
            paragraphs = []
            article_tag = soup.find("article") or soup.find("main") or soup.body
            if article_tag:
                for p in article_tag.find_all(["p", "h2", "h3", "li"]):
                    text = p.get_text().strip()
                    if len(text) > 25:
                        paragraphs.append(text)

            clean_text = "\n\n".join(paragraphs)

            return {
                "source_type": "url",
                "source_path": url,
                "title": title,
                "content": clean_text,
                "word_count": len(clean_text.split()),
                "status": "success",
            }
        except Exception as e:
            return {
                "source_type": "url",
                "source_path": url,
                "title": "",
                "content": "",
                "word_count": 0,
                "status": "error",
                "error_message": str(e),
            }

    def extract_from_file(self, file_path: str) -> Dict[str, Any]:
        """Lê arquivo local (Markdown, TXT ou HTML)."""
        if not os.path.exists(file_path):
            return {
                "source_type": "file",
                "source_path": file_path,
                "status": "error",
                "error_message": f"Arquivo não encontrado: {file_path}",
            }

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                raw_content = f.read()

            title = os.path.basename(file_path).replace(".md", "").replace(".txt", "").replace("_", " ").title()
            # Se for markdown com H1
            h1_match = re.search(r"^#\s+(.+)$", raw_content, re.MULTILINE)
            if h1_match:
                title = h1_match.group(1).strip()

            return {
                "source_type": "file",
                "source_path": file_path,
                "title": title,
                "content": raw_content.strip(),
                "word_count": len(raw_content.split()),
                "status": "success",
            }
        except Exception as e:
            return {
                "source_type": "file",
                "source_path": file_path,
                "status": "error",
                "error_message": str(e),
            }

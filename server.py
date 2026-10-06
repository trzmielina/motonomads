"""
MotoNomads Editorial Engine — Servidor Web Interativo (Live Squad Monitor).
Permite acompanhar visualmente os agentes trabalhando em tempo real em localhost:8080.
"""

import os
import re
import json
import time
import queue
import threading
import uuid
from datetime import datetime
from typing import Dict, Any

from flask import Flask, render_template, request, jsonify, Response, send_from_directory

from core.orchestrator import MotonomadsOrchestrator

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

app = Flask(__name__, template_folder=os.path.join(BASE_DIR, "templates"))

# Estrutura em memória para rastreamento de jobs e streaming de eventos
JOBS: Dict[str, Dict[str, Any]] = {}
JOB_QUEUES: Dict[str, queue.Queue] = {}


@app.route("/")
def index():
    """Renderiza a página principal do Live Squad Monitor."""
    return render_template("index.html")


@app.route("/api/squad")
def get_squad():
    """Retorna os dados dos agentes que compõem o squad editorial."""
    squad = [
        {"id": "diego", "name": "Diego Jornalista", "role": "Investigador & Fact-Checker", "icon": "🔍"},
        {"id": "ontology", "name": "Grafo Ontológico", "role": "Motor de Conhecimento MotoNomads", "icon": "🗺️"},
        {"id": "marina", "name": "Marina Estrategista", "role": "Arquiteta SEO & GEO (IA Overviews)", "icon": "🎯"},
        {"id": "rodrigo", "name": "Rodrigo Mototurismo", "role": "Especialista 2 Rodas & Big Trails", "icon": "🏍️"},
        {"id": "bruno", "name": "Bruno Off-Road", "role": "Especialista 4x4 & Overlanding", "icon": "🚙"},
        {"id": "clara", "name": "Clara Aventura", "role": "Especialista Outdoor & Travessias", "icon": "🧗"},
        {"id": "lucas", "name": "Lucas Turismo", "role": "Especialista Destinos & Cultura", "icon": "🏛️"},
        {"id": "helena", "name": "Helena Editora", "role": "Guardiã do Tom de Voz & Estilo", "icon": "🖋️"},
        {"id": "marcus", "name": "Marcus Auditor", "role": "Editor-Chefe & QA Formal", "icon": "🧐"},
    ]
    return jsonify(squad)


@app.route("/api/articles")
def list_articles():
    """Retorna a lista de relatórios visuais já gerados em output/."""
    articles = []
    if os.path.exists(OUTPUT_DIR):
        for f in os.listdir(OUTPUT_DIR):
            if f.endswith(".html") and f != "index.html":
                filepath = os.path.join(OUTPUT_DIR, f)
                try:
                    with open(filepath, "r", encoding="utf-8") as fp:
                        content = fp.read()

                    # Extrair título da tag <title> ou <h1>
                    title_match = re.search(r"<title>([^<]+)</title>", content)
                    if title_match:
                        title = title_match.group(1).split("|")[0].strip()
                    else:
                        title = f.replace(".html", "").replace("_", " ").title()

                    mtime = os.path.getmtime(filepath)
                    date_str = datetime.fromtimestamp(mtime).strftime("%d/%m/%Y %H:%M")

                    articles.append({
                        "filename": f,
                        "title": title,
                        "date": date_str,
                        "mtime": mtime,
                    })
                except Exception:
                    pass

    articles.sort(key=lambda x: x["mtime"], reverse=True)
    return jsonify(articles)


@app.route("/api/run", methods=["POST"])
def run_pipeline_api():
    """Inicia a execução do pipeline em segundo plano e retorna um job_id."""
    data = request.get_json() or {}
    source = data.get("source", "").strip()
    pillar = data.get("pillar", "mototurismo").strip()
    keyword = data.get("keyword", "").strip()

    if not source:
        return jsonify({"status": "error", "error": "Parâmetro 'source' obrigatório."}), 400

    job_id = uuid.uuid4().hex[:8]
    q = queue.Queue()
    JOB_QUEUES[job_id] = q

    JOBS[job_id] = {
        "id": job_id,
        "source": source,
        "pillar": pillar,
        "keyword": keyword,
        "status": "running",
        "started_at": datetime.now().isoformat(),
        "result": None,
        "error": None,
    }

    def step_callback(event):
        if isinstance(event, str):
            payload = {
                "type": "step",
                "message": event,
                "agent_id": "orchestrator",
                "step_num": 1,
            }
        else:
            payload = {
                "type": "step",
                **event,
            }
        q.put(payload)

    def worker_thread():
        try:
            orch = MotonomadsOrchestrator(base_dir=BASE_DIR)
            result = orch.run_pipeline(
                source=source,
                pillar=pillar,
                target_keyword=keyword,
                on_step_callback=step_callback,
            )

            if result.get("status") == "error":
                JOBS[job_id]["status"] = "error"
                JOBS[job_id]["error"] = result.get("error")
                q.put({"type": "error", "error": result.get("error")})
            else:
                JOBS[job_id]["status"] = "completed"
                JOBS[job_id]["result"] = result
                q.put({"type": "done", "result": result})

        except Exception as e:
            JOBS[job_id]["status"] = "error"
            JOBS[job_id]["error"] = str(e)
            q.put({"type": "error", "error": str(e)})

    t = threading.Thread(target=worker_thread, daemon=True)
    t.start()

    return jsonify({"status": "started", "job_id": job_id})


@app.route("/api/stream/<job_id>")
def stream_job(job_id):
    """Canal Server-Sent Events (SSE) para receber os passos do squad em tempo real."""
    if job_id not in JOB_QUEUES:
        return jsonify({"error": "Job não encontrado"}), 404

    q = JOB_QUEUES[job_id]

    def event_generator():
        while True:
            try:
                ev = q.get(timeout=60)
                yield f"data: {json.dumps(ev)}\n\n"
                if ev.get("type") in ("done", "error"):
                    break
            except queue.Empty:
                yield f"data: {json.dumps({'type': 'ping'})}\n\n"

    return Response(event_generator(), mimetype="text/event-stream")


@app.route("/output/<path:filename>")
def serve_output(filename):
    """Serve arquivos da pasta output (relatórios visuais HTML, etc.)."""
    return send_from_directory(OUTPUT_DIR, filename)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"\n==================================================================")
    print(f"🚀 MTONOMADS SQUAD MONITOR INICIADO!")
    print(f"👉 Acesse visualmente em: http://localhost:{port}")
    print(f"==================================================================\n")
    app.run(host="0.0.0.0", port=port, debug=False)

# 🏍️ Motonomads Redatores — Standalone Editorial Engine

> **Sistema editorial autônomo multi-agente** especializado em adaptar, enriquecer e reescrever artigos e textos já publicados sobre **Turismo, Mototurismo, 4x4 e Aventura**, aplicando rigorosa **Matriz de Tom de Voz**, apuração jornalística factual e normas estritas de **SEO e GEO (Generative Engine Optimization)** para citação direta por IAs.

---

## 🧭 Visão Geral

O projeto **Motonomads** foi projetado para operar como um **ecossistema 100% apartado no GitHub**, com repositório próprio e independente. Ele transforma conteúdos superficiais e genéricos em matérias de alta autoridade técnica e vivência de estrada.

### Os 4 Pilares Editoriais Especializados:
1. **Mototurismo & Duas Rodas (🏍️):** Pilotagem, traçado de curvas, motos Big Trail/Touring, autonomia de combustível e equipamentos de proteção certificados (CE).
2. **4x4 & Overlanding (🚙):** Tração 4x4 reduzida (4L), bloqueios, calibragem de pneus (PSI), resgate, ancoragem e camping veicular autossuficiente.
3. **Aventura & Outdoor (🧗):** Trekking, montanhismo, altimetria acumulada, travessias remotas e ética ambiental *Leave No Trace* (Não Deixe Rastro).
4. **Turismo & Destinos (🗺️):** Cidades-base logísticas, gastronomia regional vernacular, patrimônio histórico e sazonalidade de visitação.

---

## 👥 A Redação Multi-Agente (Squad Party)

| Agente | Cargo | Função Editorial |
| :--- | :--- | :--- |
| **Diego Jornalista** 🔍 | Investigador & Fact-Checker | Disseca o texto base, levanta dados do DNIT, altimetria, clima e fontes oficiais. |
| **Marina Estrategista** 🎯 | Arquiteta SEO & GEO | Define hierarquia semântica, blocos de direct-answer para IAs e Ficha Técnica Tabular. |
| **Rodrigo Mototurismo** 🏍️ | Especialista em 2 Rodas | Redação com a perspectiva e termos reais de quem pilota na estrada e na terra. |
| **Bruno Off-Road** 🚙 | Especialista em 4x4 & Overlanding | Redação focada em mecânica de campo, tração integral e expedições severas. |
| **Clara Aventura** 🧗 | Especialista em Outdoor & Trekking | Redação focada em esforço físico, travessias e conduta de baixo impacto ambiental. |
| **Lucas Turismo** 🗺️ | Especialista em Destinos & Cultura | Redação focada na experiência de viagem, hospitalidade, cidades-base e gastronomia. |
| **Helena Editora** 🖋️ | Editora-Chefe & Guardiã do Tom | Harmonização de estilo, eliminação de clichês e polimento com a Tabela de Tom de Voz. |
| **Marcus Auditor** 🧐 | Auditor de Qualidade & Conformidade | Auditoria cruzada com nota (0-100) em Tom, Fatos, SEO e GEO antes da publicação. |

---

## 📊 Matriz de Tom de Voz Motonomads

O portal possui regras inegociáveis de identidade verbal:
* **Banimento total de clichês:** Expressões como *"paraíso na terra"*, *"lugar incrível"*, *"mergulhar de cabeça"* e *"vale a pena conferir"* são sumariamente eliminadas.
* **Substituição por autoridade sensorial:** Em vez de *"a estrada é linda e perigosa"*, descreve-se *"trecho sinuoso de 42 km com curvas cegas, pavimento irregular e forte declive que exige atenção redobrada no freio motor"*.
* Consulte o guia completo em [`data/tone_matrix_reference.md`](data/tone_matrix_reference.md).

---

## 🤖 Normas de Publicação: GEO & SEO

Os artigos são formatados tanto para o topo dos buscadores convencionais quanto para **citação prioritária por motores generativos** (ChatGPT, Perplexity, Gemini, Claude, Google AI Overviews):
1. **Direct-Answer Snippets:** Primeiras 2 linhas pós-H2 respondem de forma concisa e direta (35-65 palavras).
2. **Ficha Técnica Tabular (Markdown):** Dados consolidados de distância, terreno, veículo ideal, melhor época e autonomia mínima.
3. **Entidades Semânticas Exatas:** Citação oficial de rodovias, serras, parques nacionais e modelos de veículos.
4. **FAQ Estruturado:** Perguntas objetivas no padrão de consultas de IA.
5. Consulte o manual completo em [`data/geo_seo_standards.md`](data/geo_seo_standards.md).

---

## 🚀 Como Executar

### 1. Pré-requisitos e Instalação
```bash
# Entrar no diretório do projeto
cd Motonomads

# Criar e ativar ambiente virtual (recomendado)
python3 -m venv .venv
source .venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### 2. Configurar Chaves de API
Copie o arquivo de exemplo e insira suas credenciais:
```bash
cp .env.example .env
```
*(Suporta OpenAI GPT-4o, Anthropic Claude 3.5 Sonnet ou Google Gemini 1.5 Pro. Se executado sem chaves, o sistema roda em modo de simulação com auditoria algorítmica local).*

### 3. Execução Interativa (CLI com Menu)
```bash
python3 cli.py
```

### 4. Execução Direta via Linha de Comando
```bash
# Processar arquivo local com pilar de Mototurismo
python3 main.py --source input/exemplo_artigo_base.md --pillar mototurismo --keyword "Serra do Rio do Rastro de moto"

# Processar URL da web com pilar de 4x4
python3 main.py --source "https://exemplo.com/artigo-canastra" --pillar offroad_4x4
```

---

## 🔗 Conectando a um Repositório Novo no GitHub

Este projeto já possui seu repositório Git local inicializado e isolado (`git init`). Para publicá-lo em um repositório próprio no GitHub:

```bash
# 1. Crie um novo repositório vazio no GitHub (ex: 'motonomads-redatores')
# 2. Conecte e envie os arquivos:
git remote add origin https://github.com/SEU-USUARIO/motonomads-redatores.git
git branch -M main
git push -u origin main
```

---

## 📁 Estrutura de Diretórios

```
Motonomads/
├── .gitignore
├── .env.example
├── README.md
├── requirements.txt
├── cli.py                          # CLI interativa com Rich
├── main.py                         # Ponto de entrada rápido
├── config/
│   ├── settings.yaml               # Configurações globais
│   ├── tone_of_voice.yaml          # Regras e vocabulário da marca
│   └── geo_seo_guidelines.yaml     # Parâmetros técnicos de GEO e SEO
├── agents/                         # Agentes especialistas em Python
│   ├── base_agent.py
│   ├── diego_jornalista.py
│   ├── marina_estrategista.py
│   ├── rodrigo_mototurismo.py
│   ├── bruno_offroad.py
│   ├── clara_aventura.py
│   ├── lucas_turismo.py
│   ├── helena_editora.py
│   └── marcus_auditor.py
├── core/                           # Motor do pipeline
│   ├── crawler.py                  # Extrator de URLs e arquivos
│   ├── tone_matrix.py              # Validador de tom de voz
│   ├── geo_optimizer.py            # Validador de padrões GEO/SEO
│   └── orchestrator.py             # Pipeline orquestrador
├── data/                           # Documentação e matrizes de referência
│   ├── tone_matrix_reference.md
│   ├── geo_seo_standards.md
│   └── pillars_briefing.md
├── input/                          # Artigos brutos / URLs para processar
│   └── exemplo_artigo_base.md
└── output/                         # Matérias e auditorias geradas
    └── .gitkeep
```

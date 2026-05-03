# ZORA: The Integrity Agent
### Multi-Agent Academic Research System with Tamper-Evident Proof Trail

![Zora Banner](https://img.shields.io/badge/ZORA-The%20Integrity%20Agent-7c3aed?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat-square)
![React](https://img.shields.io/badge/React-18-61dafb?style=flat-square)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=flat-square)
![Gemini](https://img.shields.io/badge/Gemini-Free%20API-4285f4?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## 🧠 What is Zora?

Zora is an **agentic research assistant** designed for the university ecosystem. Unlike standard LLMs that provide "black-box" answers, Zora records every step of the research process — from search queries and source retrieval to content verification and citation — generating an immutable **"Research Receipt"** (PDF) that proves the work is human-led and fact-grounded.

---

## ✨ Key Features

- 🔍 **Autonomous Research** — Searches ArXiv, web, and academic sources automatically
- 🧠 **Vector Memory** — Embeds all sources into ChromaDB for semantic retrieval
- ⚡ **Anti-Hallucination Engine** — Verifies every claim with cosine similarity + Gemini AI
- ✍️ **Grounded Draft Generation** — Produces cited drafts backed by real sources
- 📜 **Research Receipt** — Tamper-evident PDF with Zora ID, Integrity Score, and Source Map
- 🔄 **Real-time Pipeline** — WebSocket streaming shows every agent step live

---

## 🏗️ Architecture

```
User Input
    ↓
Orchestrator (FSM)
    ↓
Researcher Agent → ArXiv + Web Search + Jina Scraper
    ↓
ChromaDB Vector Store ← Embeds all source chunks locally
    ↓
Verifier Agent → Checks each claim → Gemini: Verified / Partial / Hallucinated
    ↓
Citation Specialist → APA citations + Improved grounded draft
    ↓
PDF Generator → Research Receipt (Zora ID + Integrity Score + Source Map)
    ↓
WebSocket streams all progress to UI in real-time
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Free Gemini API key from [aistudio.google.com](https://aistudio.google.com)

### Setup

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/zora-integrity-agent.git
cd zora-integrity-agent

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Add your Gemini API key
copy .env.example .env       # Windows
cp .env.example .env         # Mac/Linux
# Edit .env and add: GEMINI_API_KEY=your_key_here

# 5. Install frontend dependencies
cd frontend && npm install && cd ..

# 6. Run backend (Terminal 1)
python -m backend.main

# 7. Run frontend (Terminal 2)
cd frontend && npm run dev
```

Open **http://localhost:5173** 🎉

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Vite, TailwindCSS |
| Backend | FastAPI, Python 3.11 |
| Orchestration | LangGraph (Finite State Machine) |
| AI | Google Gemini 2.0 Flash (Free) |
| Vector DB | ChromaDB (local) |
| Embeddings | Sentence Transformers (all-MiniLM-L6-v2) |
| Search | ArXiv API, DuckDuckGo, Jina Reader |
| PDF | WeasyPrint + Jinja2 |
| Streaming | WebSockets |

---

## 📊 Agent Roles

| Agent | Role | Tools |
|-------|------|-------|
| **Orchestrator** | FSM Brain | LangGraph, State Machine |
| **Researcher** | The Librarian | ArXiv, DuckDuckGo, Jina Reader |
| **Verifier** | The Editor | ChromaDB, Gemini, Cosine Similarity |
| **Citation Specialist** | The Archivist | Gemini, WeasyPrint, Jinja2 |

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

Built with ❤️ for academic integrity.

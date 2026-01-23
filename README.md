# InnoFolio

AI-powered career coach for students, jobseekers, and early professionals.

## 🎯 Features

- **Resume Guidance** - Get tips on formatting, content, and tailoring your resume
- **Interview Prep** - Practice common questions and learn the STAR method
- **Job Search Strategy** - Learn effective networking and application strategies
- **Career Roadmaps** - Get personalized skill development advice

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│             Frontend (Next.js)          │
│              Vercel Hosting             │
└───────────────────┬─────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│            Backend (FastAPI)            │
│             Render Hosting              │
├─────────────────────────────────────────┤
│  RAG Pipeline │ Gemini LLM │ Safety     │
└───────────────────┬─────────────────────┘
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
   ChromaDB    Supabase    Gemini 2.5
  (Vectors)     (Auth)      (FREE)
```

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- Python 3.11+
- Google Gemini API key (free at https://makersuite.google.com/app/apikey)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY

# Seed the knowledge base
python scripts/seed_knowledge_base.py

# Run the server
uvicorn api.main:app --reload
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local
cp .env.local.example .env.local

# Run development server
npm run dev
```

Visit http://localhost:3000 to see InnoFolio!

## 📁 Project Structure

```
innofolio/
├── frontend/                 # Next.js app
│   ├── src/
│   │   ├── app/             # App router pages
│   │   └── lib/             # Utilities and API client
│   └── package.json
├── backend/                  # FastAPI server
│   ├── api/
│   │   ├── main.py          # FastAPI app entry
│   │   └── routes/          # API endpoints
│   ├── core/
│   │   ├── rag/             # RAG pipeline
│   │   ├── llm/             # Gemini client
│   │   └── safety/          # Guardrails
│   ├── scripts/             # Utility scripts
│   └── requirements.txt
└── knowledge-base/          # Source documents for RAG
```

## 🔑 Environment Variables

### Backend (.env)

```
GOOGLE_API_KEY=your_gemini_api_key
```

### Frontend (.env.local)

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🚢 Deployment

### Frontend (Vercel)

1. Push to GitHub
2. Import project in Vercel
3. Set `NEXT_PUBLIC_API_URL` environment variable
4. Deploy

### Backend (Render)

1. Create new Web Service on Render
2. Connect GitHub repo
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
5. Add `GOOGLE_API_KEY` environment variable
6. Deploy

## 💰 Cost

**$0/month** for MVP:
- Gemini 2.5 Flash: FREE (1500 requests/day)
- Vercel: FREE (hobby tier)
- Render: FREE (750 hours/month)
- ChromaDB: FREE (local storage)

## 📄 License

MIT

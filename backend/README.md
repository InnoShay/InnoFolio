# InnoFolio Backend

FastAPI backend for InnoFolio AI career chatbot.

## Setup

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn api.main:app --reload
```

## Environment Variables

Create a `.env` file:

```
GOOGLE_API_KEY=your_gemini_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

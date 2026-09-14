# GleamLearn AI Microservice

FastAPI-powered microservice responsible for AI-driven document parsing, text analysis, and automated study material generation (summaries, notes, flashcards, quizzes, exams, and interactive live AI classes) for the GleamLearn platform.

---

## Tech Stack

* **Framework:** FastAPI (Python)
* **Server:** Uvicorn (ASGI)
* **Validation:** Pydantic v2
* **AI Provider:** OpenAI API (GPT-4o-mini)
* **Authentication:** Bearer Token (`AI_API_KEY`)

---

## Core Endpoints

| Endpoint | Method | Description |
| --- | --- | --- |
| `/` | `GET` | Health check and service status |
| `/api/v1/ai/documents/{id}/analyze` | `POST` | Deep document parsing and structured analysis |
| `/api/v1/ai/documents/{id}/analysis` | `GET` | Retrieve cached document analysis results |
| `/api/v1/ai/documents/{id}/generate-notes` | `POST` | Generates comprehensive study notes |
| `/api/v1/ai/documents/{id}/generate-summary` | `POST` | Produces concise document summaries |
| `/api/v1/ai/documents/{id}/generate-flashcards` | `POST` | Creates interactive study flashcards (JSON format) |
| `/api/v1/ai/documents/{id}/generate-questions` | `POST` | Generates important study review questions |
| `/api/v1/ai/documents/{id}/generate-quiz` | `POST` | Builds multiple-choice quizzes with options and correct answers |
| `/api/v1/ai/documents/{id}/generate-test` | `POST` | Generates a comprehensive midterm test structure |
| `/api/v1/ai/documents/{id}/generate-exam` | `POST` | Generates a full academic final exam paper |
| `/api/v1/ai/documents/{id}/create-course` | `POST` | Automatically constructs a multi-tier course outline |
| `/api/v1/ai/documents/{id}/generate-live-class` | `POST` | Converts documents into timeline scripts for interactive live AI classes (with narration, visual canvas instructions, and captions) |
| `/api/v1/ai/documents/{id}/live-class-stream` | `GET` | Streams playback sync metadata and session states for the live player |
| `/api/v1/ai/documents/{id}/export-pdf` | `POST` | Compiles generated content into a downloadable PDF format |

---

## Local Development Setup

1. **Clone the repository:**

```bash
git clone https://github.com/Hilosthone/gleamlearn-ai-service.git
cd gleamlearn-ai-service

```

2. **Create and activate a virtual environment:**

```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

```

3. **Install dependencies:**

```bash
pip install -r requirements.txt

```

4. **Configure environment variables:**
Create a `.env` file in the root directory (ensure this file is never committed to version control):

```env
AI_API_KEY=your_secure_shared_token_here
OPENAI_API_KEY=your_openai_api_key_here

```

5. **Run the development server:**

```bash
uvicorn main:app --reload --port 8000

```

Access the interactive Swagger documentation at: `[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)`

---

## Environment Variables

| Variable | Description | Required |
| --- | --- | --- |
| `AI_API_KEY` | Shared secret token required by the NestJS backend gateway to communicate securely with this service. | Yes |
| `OPENAI_API_KEY` | Secret API key for accessing OpenAI language models. | Yes |

---

## Deployment (Render)

1. Create a new **Web Service** on Render linked to this repository.
2. Set the **Runtime** to `Python 3`.
3. Set the **Build Command**: `pip install -r requirements.txt`
4. Set the **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add your `AI_API_KEY` and `OPENAI_API_KEY` under the Environment variables tab.
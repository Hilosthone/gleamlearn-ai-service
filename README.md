# GleamLearn AI Microservice

FastAPI-powered microservice responsible for AI-driven document parsing, text analysis, and automated study material generation (summaries, notes, flashcards, and quizzes) for the GleamLearn platform.

---

## Tech Stack

* **Framework:** FastAPI (Python)
* **Server:** Uvicorn (ASGI)
* **Validation:** Pydantic v2
* **Authentication:** Bearer Token (`AI_API_KEY`)

---

## Core Endpoints

| Endpoint | Method | Description |
| --- | --- | --- |
| `/` | `GET` | Health check and service status |
| `/api/v1/analyze` | `POST` | Deep document parsing and analysis |
| `/api/v1/generate-notes` | `POST` | Generates comprehensive study notes |
| `/api/v1/generate-summary` | `POST` | Produces concise document summaries |
| `/api/v1/generate-flashcards` | `POST` | Creates interactive study flashcards |
| `/api/v1/generate-quiz` | `POST` | Builds multiple-choice quizzes and tests |

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
Create a `.env` file in the root directory:
```env
AI_API_KEY=your_secure_shared_token_here

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
| `AI_API_KEY` | Shared secret token required by the NestJS backend to communicate securely with this service. | Yes |

---

## Deployment (Render)

1. Create a new **Web Service** on Render linked to this repository.
2. Set the **Runtime** to `Python 3`.
3. Set the **Build Command**: `pip install -r requirements.txt`
4. Set the **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add your `AI_API_KEY` under the Environment variables tab.

# CS Pathfinder

A comprehensive web application designed to guide computer science students and professionals through their career paths. The platform offers personalized field recommendations via quizzes, interactive roadmap tracking, and an AI-powered CV ranking tool to match resumes against job descriptions.

**Deployment Link:** [https://cs-pathfinder-production-5756.up.railway.app](https://cs-pathfinder-production-5756.up.railway.app)

## Features

- **User Authentication:** Secure sign-up, login, and session management.
- **Career Quiz & Recommendations:** Take a tailored quiz to discover your ideal computer science field (e.g., Software Engineering, Data Science, Cybersecurity).
- **Interactive Roadmaps:** Track your progress step-by-step through customized learning roadmaps based on your recommended field.
- **AI-Powered CV Ranker:** Upload your CV (PDF) and rank it against predefined or custom job descriptions. The app uses Google Generative AI to analyze and provide an overall score, matching analysis, and actionable recommendations.
- **Tech News & Blogs:** Stay updated with the latest tech news gathered via RSS feeds and web scraping.
- **Admin Dashboard:** Comprehensive admin controls to manage users, quiz questions, learning roadmaps, job descriptions, and blog posts.

## Tech Stack

- **Backend:** Flask (Python), Werkzeug
- **Database:** PostgreSQL (`psycopg2-binary`)
- **AI Integration:** Google Generative AI (`google-generativeai`)
- **Document Processing:** `pdfplumber`, `PyPDF2` (for parsing CVs)
- **Web Scraping & RSS:** `beautifulsoup4`, `feedparser`, `requests`
- **Frontend:** HTML, CSS (via Flask templates and static files)

## Project Structure

```
cs-pathfinder-main/
├── app.py                 # Main Flask application and routing
├── DB.py                  # Database connection and initialization
├── ai_helper.py           # Logic for determining fields from quiz answers
├── api_ranker.py          # AI CV ranking logic
├── BlogScraping.py        # Web scraping and RSS feed handling
├── requirements.txt       # Python dependencies
├── static/                # Static assets (CSS, JS, images)
├── templates/             # HTML templates for rendering pages
└── .env.example           # Example environment variables
```

## Setup Instructions

### 1. Prerequisites
- Python 3.8+
- PostgreSQL server running locally or remotely

### 2. Clone the Repository
```bash
git clone <repository-url>
cd cs-pathfinder-main
```

### 3. Create a Virtual Environment and Install Dependencies
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Environment Variables
Create a `.env` file in the root directory and copy the contents of `.env.example`. Make sure to fill in your specific credentials:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/cspathfinder
GEMINI_API_KEY=your_google_gemini_api_key
SECRET_KEY=your_flask_secret_key
```

### 5. Initialize the Database
The application is designed to initialize the required tables automatically on startup (via `init_db()` in `DB.py`).

### 6. Run the Application
```bash
python app.py
# or
flask run
```

The application should now be accessible at `http://127.0.0.1:5000`.

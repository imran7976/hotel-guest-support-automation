# Setup & Installation Guide

This guide details how to configure, launch, and test the **AI-Powered Hotel Guest Support Automation System** in both Dockerized and Local development environments.

---

## Prerequisites
- **Python 3.10+** (FastAPI, SQLAlchemy, Pytest)
- **Node.js 18+** / **npm 9+** (Next.js Dashboard)
- **MySQL 8.0+** (or SQLite for rapid local development)
- **Docker & Docker Compose** (Optional, for single-command production container deployment)
- **OpenAI API Key** (Optional: the system features an intelligent local fallback agent for offline/demo operation if an OpenAI key is not provided)

---

## Quickstart: Local Development Mode

### 1. Clone & Configure Environment
```bash
git clone <repo-url>
cd hotel-guest-support-automation

# Copy environment template
cp .env.example .env
```
Inspect `.env` and verify your configuration:
- By default `DATABASE_URL=sqlite:///./hotel_support.db` is ready for instant local testing without spinning up MySQL.
- For MySQL 8: `DATABASE_URL=mysql+pymysql://hotel_user:hotel_secure_pass_2025@localhost:3306/hotel_guest_support`.

### 2. Backend Setup
```bash
cd backend
python -m venv venv

# Windows activate
.\venv\Scripts\activate
# Linux/macOS activate
# source venv/bin/activate

pip install -r requirements.txt

# Run database migrations and seed data
python app/database/seed_data.py

# Start FastAPI Server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Interactive API docs will be available at: [http://localhost:8000/docs](http://localhost:8000/docs).

### 3. Frontend Setup
In a new terminal:
```bash
cd frontend
npm install
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## Docker Compose Quickstart
To launch all services (MySQL 8, FastAPI, Next.js, and n8n) in isolated containers:
```bash
docker compose up -d
```
- **Guest Support & Staff Portal**: [http://localhost:3000](http://localhost:3000)
- **FastAPI Backend & Swagger**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **n8n Workflow Automation**: [http://localhost:5678](http://localhost:5678)
- **MySQL 8 Database**: Port `3306`

---

## Default Demo Credentials
- **Admin Email**: `admin@grandhotelazure.demo`
- **Admin Password**: `AdminHotel2025!`
- **Sample Guest**: `john@example.com`
- **Sample Booking Reference**: `GAH-78901`


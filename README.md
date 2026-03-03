# 🚚 Dynamic Route Optimization System

## 🌐 Live Demo
https://dynamic-route-optimization.onrender.com

---

## 📌 Overview
A multi-vehicle route optimization system built using:

- FastAPI
- Google OR-Tools
- Leaflet.js
- JavaScript + HTML + CSS

The system calculates optimal delivery routes, supports traffic simulation, and allows urgent order insertion.

---

## 🚀 Features
- Multi-vehicle optimization
- Traffic simulation
- Urgent order handling
- Real-time route recalculation
- Interactive map UI

---

## 🛠 Tech Stack

### Backend
- FastAPI
- OR-Tools
- Pydantic

### Frontend
- Leaflet.js
- Vanilla JavaScript
- HTML & CSS

### Deployment
- Render
- GitHub

---

## 💻 Run Locally

```bash
git clone https://github.com/DIVYAPRAKASH111/dynamic-route-optimization.git
cd dynamic-route-optimization
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Open:
http://127.0.0.1:8000

---

## 🚀 Deployment (Render)

Build Command:
pip install -r requirements.txt

Start Command:
uvicorn main:app --host 0.0.0.0 --port 10000
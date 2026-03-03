# Dynamic Route Optimization System

A multi-vehicle route optimization system built using:

- FastAPI (Backend)
- OR-Tools (VRP Solver)
- Leaflet.js (Frontend Map)
- JavaScript + HTML + CSS

## Features

- Multi-vehicle routing
- Traffic simulation
- Urgent order insertion
- Dynamic route re-optimization

## Setup Instructions

1. Clone repository:
   git clone https://github.com/YOUR_USERNAME/dynamic-route-optimization.git

2. Create virtual environment:
   python -m venv .venv

3. Activate:
   Windows:
   .venv\Scripts\activate

4. Install dependencies:
   pip install -r requirements.txt

5. Run server:
   uvicorn main:app --reload

6. Open browser:
   http://127.0.0.1:8000

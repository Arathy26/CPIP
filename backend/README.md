# CPIP Backend

Career & Placement Intelligence Platform — Backend Service

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Backend
```bash
python -m uvicorn app.main:app --reload
```

Backend runs at: `http://localhost:8000`

### 3. Test Health Endpoint
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "message": "CPIP backend is running"
}
```

## API Documentation
Visit: `http://localhost:8000/docs`
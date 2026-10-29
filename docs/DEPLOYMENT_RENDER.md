# WealthOS AI — Render.com Blueprint Deployment Guide

This guide walks you through deploying the complete WealthOS AI stack on [Render.com](https://render.com) using the included `render.yaml` Blueprint specification.

---

## Architecture on Render

```
                                +---------------------------+
                                |  Render Managed Postgres  |
                                |       (wealthos-db)       |
                                +-------------+-------------+
                                              |
                                     DATABASE_URL (Internal)
                                              |
                                              v
+--------------------------+        +---------+---------+
|    Streamlit Frontend    | =====> |  FastAPI Backend  |
|   (wealthos-frontend)    |  HTTP  | (wealthos-backend)|
+--------------------------+        +-------------------+
    Public Web Port ($PORT)           Public API ($PORT)
```

The `render.yaml` blueprint deploys 3 linked services:
1. **`wealthos-db`**: A managed PostgreSQL database instance.
2. **`wealthos-backend`**: A FastAPI web service that runs database migrations (`alembic upgrade head`) and serves REST APIs at `/api/v1/`.
3. **`wealthos-frontend`**: A Streamlit web service that connects directly to the backend via `RENDER_EXTERNAL_URL`.

---

## Step-by-Step Deployment

### Step 1: Open Render Dashboard
1. Log in to [dashboard.render.com](https://dashboard.render.com).
2. Ensure your GitHub account (`Mukesh-S284`) is connected to Render.

### Step 2: Deploy via Blueprint
1. Click the **"New +"** button in the top right corner and select **"Blueprint"**.
2. Connect your repository: **`Mukesh-S284/WEALTHOS-AI`**.
3. Render will automatically read the [`render.yaml`](../render.yaml) file at the root of the repository.
4. Render will preview the 3 components to be created:
   - **PostgreSQL Database:** `wealthos-db`
   - **Web Service:** `wealthos-backend`
   - **Web Service:** `wealthos-frontend`
5. Click **"Apply"** to trigger the build.

---

## Automatic Provisioning Sequence

1. **Database Provisioning:**
   Render creates `wealthos-db` and exports the PostgreSQL connection string.

2. **Backend Build & Migration:**
   - Installs dependencies from `requirements.txt` (including `fastapi`, `sqlalchemy`, `psycopg2-binary`, etc.).
   - Executes `alembic upgrade head` to construct all 13 database tables and constraints.
   - Starts Uvicorn listening on `0.0.0.0:$PORT`.
   - Verifies deployment via `/health`.

3. **Frontend Build & Linking:**
   - Installs frontend dependencies.
   - Automatically injects the backend's external URL into `API_BASE_URL`.
   - Starts Streamlit on `0.0.0.0:$PORT` in headless mode.

---

## Post-Deployment & Optional Configuration

### Initial Demo Data Seeding
If you want to populate demo financial records (transactions, budgets, savings goals, multi-asset portfolio) on your production database:
1. Open the **`wealthos-backend`** service on Render.
2. Navigate to the **"Shell"** tab.
3. Run:
   ```bash
   python scripts/seed_demo_data.py
   ```
4. Log in on the Streamlit frontend with:
   - **Email:** `demo@wealthos.ai`
   - **Password:** `SecurePass123!`

### Optional Environment Variables
In the Render dashboard under **`wealthos-backend` > Environment**:
- `GEMINI_API_KEY`: *(Optional)* Add your Google Gemini API key to activate live LLM capabilities for the AI Finance Assistant (in addition to the built-in grounded local fallback).

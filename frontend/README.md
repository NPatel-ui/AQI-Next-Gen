# AQI Next-Gen Frontend

React + Vite frontend for the AQI Next-Gen FastAPI service. The existing page structure, navigation flow, authentication screens, and visual design have been retained while the forecasting workflow has been connected to the current backend contract.

## Requirements

- Node.js 20.19+ or 22.12+
- npm
- AQI Next-Gen FastAPI backend running at `http://127.0.0.1:8000`
- Supabase project credentials if you want sign-up/sign-in, profile preferences, and saved forecasts

## Setup

```bash
npm install
```

Copy `.env.example` to `.env`.

For local development, leave `VITE_API_URL` empty. Vite proxies `/api/*` to `http://127.0.0.1:8000` and preserves the `/api` prefix used by FastAPI.

Set your own Supabase values in `.env`:

```env
VITE_SUPABASE_URL=https://YOUR_PROJECT.supabase.co
VITE_SUPABASE_PUBLISHABLE_KEY=YOUR_SUPABASE_PUBLISHABLE_OR_ANON_KEY
```

Do not commit `.env` or share service-role keys in a browser application.

## Run

Start the FastAPI backend in one terminal:

```bash
uvicorn backend.main:app --reload
```

Start the frontend in a second terminal:

```bash
npm run dev
```

Open `http://localhost:5173`.

## Production API configuration

Set `VITE_API_URL` to the backend origin or API base URL. Both are accepted:

```env
VITE_API_URL=https://your-backend.example.com
```

or

```env
VITE_API_URL=https://your-backend.example.com/api
```

Then build:

```bash
npm run build
npm run preview
```

## Current API contract

- `GET /api/health`
- `GET /api/cities`
- `POST /api/forecast/by-city-date`

Forecast request body:

```json
{
  "city": "Nagpur",
  "forecast_date": "2026-11-06"
}
```

The response is mapped from `results.full_aqi.predicted_aqi` and `results.pm_aqi.predicted_aqi`. The frontend does not fabricate fallback predictions if the API is unavailable.

## Supabase features

Authentication, profile preferences, and saved forecasts continue to use Supabase. Configure the project credentials and apply `supabase/schema.sql` to your Supabase database before using those features.

## Notes

- The model forecasts one day ahead and requires eight consecutive input dates.
- The API returns predictions for the selected target date, using data through the preceding date.
- Some recently fetched API records may be forecast-estimated inputs rather than finalized observations. The interface labels outputs as model forecasts and does not present them as official monitoring readings.
- Analytics displays the project's reported test-set metrics; it does not call a benchmark endpoint that the current FastAPI backend does not provide.

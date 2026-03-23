# 🚌 CrowdRoute

**CrowdRoute** predicts crowd levels across public transport options — helping you find the least crowded way to travel in Indian cities.

---

## ✨ Features

- 🤖 **ML-powered predictions** using an XGBoost classifier trained on time, weather, and holiday signals
- 🌤️ **Live weather integration** via OpenWeatherMap (current & 5-day forecast)
- 📅 **Holiday impact detection** — crowd multipliers applied on public holidays
- 🗺️ **Google Maps routing** — real-time traffic, distance, and travel time estimation
- 🌐 **Intercity route detection** — automatically switches to bus/train for cross-city journeys
- 🟢🟡🔴 **Crowd levels**: LOW / MEDIUM / HIGH with confidence scores and travel advice
- 🏙️ **70+ Indian cities** supported

---

## 🏗️ Project Structure

```
crowdroute/
├── backend/                  # FastAPI backend
│   ├── app/
│   │   ├── main.py           # FastAPI application entry point
│   │   ├── routes/           # API route handlers (predict, weather, holiday, city)
│   │   ├── services/         # Business logic (weather, holiday, route, corridor validation)
│   │   ├── models/           # ML model loader
│   │   ├── schemas/          # Pydantic request/response schemas
│   │   └── data/             # Metro city data
│   ├── ml/                   # ML pipeline
│   │   ├── prepare_data.py   # Data preparation
│   │   ├── train.py          # Model training (XGBoost + SMOTE)
│   │   └── predict.py        # Standalone prediction helper
│   ├── data/                 # Raw data and city definitions
│   └── requirements.txt      # Python dependencies
└── frontend/                 # React + Vite frontend
    ├── src/
    │   ├── App.jsx            # Main application component
    │   ├── components/        # SearchForm, ResultCard, WeatherBadge
    │   └── services/          # API client functions
    ├── public/
    └── package.json
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- Node.js 18+
- API keys for [OpenWeatherMap](https://openweathermap.org/api) and [Google Maps](https://developers.google.com/maps)

### 1. Clone the repository

```bash
git clone https://github.com/patilsurajcp/crowdroute.git
cd crowdroute
```

### 2. Backend Setup

```bash
cd backend
pip install -r requirements.txt
```

Create a `.env` file in the `backend/` directory:

```env
OPENWEATHER_API_KEY=your_openweather_api_key
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
```

Train or generate the ML model:

```bash
# Generate a dummy model for testing
python ml/create_dummy_model.py

# Or train on real data (place your CSV at data/raw/your_dataset.csv)
cd ml
python train.py
```

Start the backend server:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:5173`.

---

## 🔌 API Reference

All endpoints are prefixed with `/api/v1`.

### `POST /api/v1/predict`

Predict crowd levels for a journey.

**Request body:**

```json
{
  "datetime_str": "2024-12-25T08:30:00",
  "city": "Hubli",
  "source": "Keshwapur",
  "destination": "Dharwad Bus Stand",
  "transport_types": ["bus", "chigari", "train"],
  "is_holiday": false,
  "temperature": 25.0
}
```

**Supported transport types:** `bus`, `metro`, `train`, `chigari`, `ferry`, `tram`, `toy_train`, `shared_cab`, `shikara`

**Response:**

```json
{
  "city": "Hubli",
  "source": "Keshwapur",
  "destination": "Dharwad Bus Stand",
  "datetime_str": "2024-12-25T08:30:00",
  "best_option": "train",
  "results": [
    {
      "transport": "train",
      "level": "LOW",
      "emoji": "🟢",
      "confidence": 87.5,
      "advice": "Great time to travel — very comfortable!",
      "estimated_time": "25 min",
      "route_note": "Via NH-48"
    }
  ],
  "summary": "Best option is TRAIN (LOW crowd, ~25 min). Great time to travel!",
  "route_summary": "Keshwapur → Dharwad Bus Stand (12.3 km) · 🟢 LOW traffic"
}
```

### `GET /api/v1/weather?city={city}`

Get current weather conditions for a city.

### `GET /api/v1/holiday?datetime_str={datetime_str}`

Get holiday impact information for a given date/time.

### `GET /api/v1/city`

List supported cities and their available transport modes.

### `GET /api/v1/health`

Health check — returns API status and model load state.

---

## 🤖 Machine Learning

The crowd prediction model is an **XGBoost classifier** trained with SMOTE for class balancing.

### Input Features

| Feature             | Description                        |
|---------------------|------------------------------------|
| `hour`              | Hour of travel (0–23)             |
| `day_of_week`       | Day of week (0=Monday)            |
| `month`             | Month (1–12)                      |
| `is_weekend`        | 1 if Saturday/Sunday              |
| `is_peak_hour`      | 1 if 7–9 AM or 5–7 PM            |
| `is_holiday`        | 1 if public holiday               |
| `temperature`       | Temperature in °C                 |
| `weather_code`      | Weather category (0=clear, 3=storm)|
| `transport_encoded` | Transport type as integer         |

### Output Classes

| Label    | Emoji | Meaning                                    |
|----------|-------|--------------------------------------------|
| `LOW`    | 🟢    | Comfortable — great time to travel         |
| `MEDIUM` | 🟡    | Moderate crowd — plan accordingly          |
| `HIGH`   | 🔴    | Very crowded — consider an alternate time  |

### Crowd Multipliers

Predictions are adjusted by combining:
- **Traffic multiplier** — derived from real-time Google Maps traffic ratio
- **Holiday multiplier** — scaled by holiday type (normal → very high impact)

---

## 🌆 Supported Cities

CrowdRoute supports 70+ Indian cities including Mumbai, Delhi, Bengaluru, Chennai, Kolkata, Hyderabad, Pune, Ahmedabad, Jaipur, Kochi, Hubli-Dharwad, Mysuru, Chandigarh, Srinagar, and many more.

---

## 🛠️ Tech Stack

| Layer     | Technology                                      |
|-----------|-------------------------------------------------|
| Frontend  | React 19, Vite, Tailwind CSS, Google Maps API  |
| Backend   | Python, FastAPI, Uvicorn                        |
| ML        | XGBoost, scikit-learn, SMOTE (imbalanced-learn)|
| Data      | pandas, numpy                                   |
| APIs      | OpenWeatherMap, Google Maps                     |

---

## 📄 License

This project is licensed under the terms of the [LICENSE](LICENSE) file.

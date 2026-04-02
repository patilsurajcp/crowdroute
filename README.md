# 🚌 CrowdRoute

**CrowdRoute** is an AI-powered public transport crowd prediction app for Indian cities. It helps commuters find the least crowded way to travel by predicting crowd levels across bus, metro, train, and other transport modes — factoring in real-time weather, live traffic, and holiday impacts.

---

## ✨ Features

- **Crowd Prediction** — ML model predicts LOW / MEDIUM / HIGH crowd levels per transport mode
- **Live Traffic Integration** — Google Maps Directions API provides real-time traffic data and travel time estimates
- **Weather Awareness** — OpenWeatherMap integration adjusts predictions based on current/forecast weather
- **Holiday Impact Analysis** — Detects public holidays, long weekends, bridge days, and festival clusters using Calendarific API
- **Intercity Detection** — Automatically detects cross-city routes and filters transport options accordingly
- **Transport Corridor Validation** — Smart validation ensures city-specific transports (Chigari, Tram, Ferry, Toy Train, Shikara, Shared Cab) are only suggested on valid routes
- **80+ Indian Cities** — Covers major metros down to smaller cities with accurate transport availability data
- **Google Places Autocomplete** — Location search with smart suggestions for source and destination

---

## 🏗️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 19, Vite, Tailwind CSS v4 |
| Backend | FastAPI (Python) |
| ML Model | Random Forest / XGBoost (scikit-learn) |
| Maps | Google Maps API (Directions + Places) |
| Weather | OpenWeatherMap API |
| Holidays | Calendarific API |
| Train Data | IRCTC via RapidAPI (optional) |
| Bus Data | RedBus via RapidAPI (optional) |

---

## 📁 Project Structure

```
crowdroute/
├── backend/
│   ├── app/
│   │   ├── data/
│   │   │   └── metro_cities.py        # City → transport type mappings
│   │   ├── models/
│   │   │   └── loader.py              # ML model loader (singleton)
│   │   ├── routes/
│   │   │   ├── predict.py             # POST /api/v1/predict
│   │   │   ├── weather.py             # GET /api/v1/weather/*
│   │   │   ├── holiday.py             # GET /api/v1/holiday/impact
│   │   │   └── city.py                # GET /api/v1/cities, /city/transport/{city}
│   │   ├── schemas/
│   │   │   └── request.py             # Pydantic request/response models
│   │   ├── services/
│   │   │   ├── weather.py             # OpenWeatherMap integration
│   │   │   ├── holiday.py             # Calendarific integration
│   │   │   ├── route.py               # Google Maps Directions integration
│   │   │   └── corridor_validator.py  # Transport corridor validation
│   │   └── main.py                    # FastAPI app entry point
│   ├── ml/
│   │   ├── create_dummy_model.py      # Generate a dummy model for testing
│   │   ├── prepare_data.py            # Data loading and feature engineering
│   │   ├── train.py                   # XGBoost training script
│   │   ├── predict.py                 # Standalone prediction script
│   │   └── saved_models/              # Trained model artifacts (.joblib)
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── SearchForm.jsx         # Main search form with city/transport selector
│   │   │   ├── PlacesAutocomplete.jsx # Google Places search input
│   │   │   ├── ResultCard.jsx         # Individual transport result card
│   │   │   ├── WeatherBadge.jsx       # Weather display badge
│   │   │   └── Crowdmeter.jsx         # Crowd percentage meter
│   │   ├── services/
│   │   │   └── api.js                 # Axios API client
│   │   ├── App.jsx                    # Root component
│   │   └── main.jsx                   # React entry point
│   ├── package.json
│   └── vite.config.js
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Node.js 20+
- API keys (see [Environment Variables](#-environment-variables))

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/crowdroute.git
cd crowdroute
```

### 2. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create a .env file (see Environment Variables section)
cp .env.example .env

# Generate a dummy ML model for testing
cd ml && python create_dummy_model.py && cd ..

# Start the API server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`. Swagger docs at `http://localhost:8000/docs`.

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create a .env file
echo "VITE_GOOGLE_MAPS_API_KEY=your_google_maps_key" > .env

# Start the dev server
npm run dev
```

The app will be available at `http://localhost:5173`.

---

## 🔑 Environment Variables

### Backend — `backend/.env`

```env
OPENWEATHER_API_KEY=your_openweathermap_api_key
CALENDARIFIC_API_KEY=your_calendarific_api_key
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
RAPIDAPI_KEY=your_rapidapi_key          # Optional — for IRCTC/RedBus live data
```

### Frontend — `frontend/.env`

```env
VITE_GOOGLE_MAPS_API_KEY=your_google_maps_api_key
```

> **Getting API Keys:**
> - OpenWeatherMap: [openweathermap.org/api](https://openweathermap.org/api) (free tier available)
> - Calendarific: [calendarific.com](https://calendarific.com) (free tier available)
> - Google Maps: [console.cloud.google.com](https://console.cloud.google.com) — enable **Maps JavaScript API**, **Places API**, and **Directions API**
> - RapidAPI: [rapidapi.com](https://rapidapi.com) — optional, for live seat availability

---

## 🤖 ML Model

The prediction model uses these features:

| Feature | Description |
|---|---|
| `hour` | Hour of the day (0–23) |
| `day_of_week` | Day of the week (0=Mon, 6=Sun) |
| `month` | Month (1–12) |
| `is_weekend` | Binary flag |
| `is_peak_hour` | Binary flag (7–9 AM, 5–7 PM) |
| `is_holiday` | Binary flag from Calendarific |
| `temperature` | Temperature in °C |
| `transport_encoded` | Transport type (bus=0, metro=1, train=2) |

**Output classes:** `0 = LOW 🟢`, `1 = MEDIUM 🟡`, `2 = HIGH 🔴`

### Training Your Own Model

```bash
cd backend/ml

# Place your dataset at backend/data/raw/your_dataset.csv
# The CSV should have columns: datetime, transport_type, passenger_count, is_holiday, temperature

python train.py
```

The dummy model (`create_dummy_model.py`) is provided for testing without real data.

---

## 🗺️ Supported Transport Modes

| Mode | Cities | Notes |
|---|---|---|
| 🚌 Bus | All cities | City-wide service |
| 🚇 Metro | Mumbai, Delhi, Bengaluru, Chennai, Kolkata, Hyderabad, Pune, Ahmedabad, Jaipur, Kochi, Lucknow, Nagpur, Noida, Faridabad | Operational metro networks |
| 🚆 Train | Most cities | Indian Railways / suburban rail |
| ⚡ Chigari | Hubli, Dharwad | Electric bus — twin city corridor only |
| ⛴️ Ferry | Mumbai, Kochi, Guwahati, Port Blair, Panaji, Kavaratti | Water routes only |
| 🚋 Tram | Kolkata | Heritage tram — specific routes only |
| 🚂 Toy Train | Shimla | Kalka–Shimla UNESCO heritage railway |
| 🚖 Shared Cab | Gangtok, Shillong | Hill route corridors |
| 🛶 Shikara | Srinagar | Dal Lake & Nagin Lake only |

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/predict` | Get crowd predictions for a route |
| `GET` | `/api/v1/weather/current/{city}` | Current weather for a city |
| `GET` | `/api/v1/weather/forecast/{city}?datetime_str=` | Forecast weather |
| `GET` | `/api/v1/holiday/impact?datetime_str=` | Holiday crowd impact |
| `GET` | `/api/v1/city/transport/{city}` | Available transports for a city |
| `GET` | `/api/v1/cities` | List of all supported cities |
| `GET` | `/api/v1/health` | Health check |

### Example Prediction Request

```json
POST /api/v1/predict
{
  "datetime_str": "2024-12-25T08:30:00",
  "city": "Hubli",
  "source": "Keshwapur, Hubli, Karnataka, India",
  "destination": "Dharwad Bus Stand, Dharwad, Karnataka, India",
  "transport_types": ["bus", "chigari", "train"],
  "is_holiday": false,
  "temperature": 25.0
}
```

### Example Response

```json
{
  "city": "Hubli",
  "source": "Keshwapur, Hubli",
  "destination": "Dharwad Bus Stand",
  "best_option": "chigari",
  "summary": "Best option is CHIGARI (LOW crowd, ~22 mins). Great time to travel!",
  "route_summary": "Keshwapur → Dharwad Bus Stand (6.2 km) · 🟢 LOW traffic",
  "results": [
    {
      "transport": "chigari",
      "level": "LOW",
      "emoji": "🟢",
      "confidence": 87.3,
      "advice": "Great time to travel — very comfortable!",
      "estimated_time": "22 mins",
      "route_note": "Chigari electric bus running smoothly — eco-friendly!"
    }
  ]
}
```

---

## 🔄 How It Works

1. **User submits** a route (source → destination), city, date/time, and transport modes
2. **Intercity detection** checks if the route spans multiple cities (bus/train only for intercity)
3. **Corridor validation** removes transports that don't serve the route (e.g., Chigari outside Hubli-Dharwad)
4. **Google Maps** fetches real route distance, travel time, and traffic level
5. **OpenWeatherMap** fetches current or forecast weather
6. **Calendarific** checks for holidays, long weekends, bridge days, and festival clusters
7. **ML model** predicts crowd class for each transport mode
8. **Multipliers** from traffic and holidays adjust the raw ML prediction
9. **Results** are sorted by crowd level (lowest first) and returned with travel time estimates

---

## 🚧 Known Limitations

- The default model (`create_dummy_model.py`) is a toy model trained on 8 samples — replace it with a real trained model for production use
- Metro crowd data is estimated from time-of-day patterns (no public API available in India)
- IRCTC and RedBus live availability requires a paid RapidAPI subscription; the app falls back to smart time-based estimation when unavailable
- Google Maps API usage incurs costs beyond the free tier

---

## 📄 License

This project is licensed under the **GNU General Public License v3.0**. See [LICENSE](LICENSE) for details.

---

## 🙌 Contributing

Contributions are welcome! To get started:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m 'Add your feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

Please report bugs or security issues via the [Security Policy](SECURITY.md).

EcoCred
=================================
Make sustainability feel rewarding. EcoCred helps people and organizations measure their carbon footprint, earn green credits for eco‑friendly actions, and build lasting climate‑positive habits.

What is EcoCred?
---------------------------------
- Carbon footprint tracking for everyday activities (travel, electricity, purchases, waste, etc.)
- Automatic emissions calculations using trusted emission factors
- Green credits and rewards for sustainable choices
- Personal dashboard with progress, trends, and tips

In simple words: EcoCred = Environmental + Credits. Do good for the planet, earn points/credits.

Core Concepts
---------------------------------
- Activities: User‑logged events (e.g., "drove 10 km by car", "used 12 kWh electricity").
- Emissions: Calculated as quantity × emission factor for the activity type.
- Credits: Earned for reductions, low‑carbon choices, streaks, and goals met.
- Insights: Trends, comparisons, and personalized tips to reduce emissions.

MVP Scope
---------------------------------
1) Auth and profiles (individual users; optional org field)
2) Activity logging (transport, electricity to start)
3) Emissions calculator (per activity; daily/weekly/monthly totals)
4) Credits engine (simple thresholds and streaks)
5) Dashboard (totals, trends, recent activities, credits earned)
6) Tips (rule‑based suggestions)

How It Works (high level)
---------------------------------
1) Log an activity → provide category, sub‑type, quantity, unit, date.
2) System looks up emission factor → computes CO₂e.
3) Totals aggregate by user and time period.
4) Credits are awarded based on eco-friendly choices and goals.
5) Dashboard shows progress and personalized tips.

## Quick Start

### Local Development
```bash
# Install backend dependencies
cd backend
pip install -r requirements.txt

# Run the application
python app.py
```

The app will be available at http://localhost:5000


### Production Deployment
See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

## Tech Stack
- **Backend**: Python Flask with SQLAlchemy
- **Frontend**: HTML/CSS/JavaScript
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Authentication**: JWT
- **Deployment**: Docker, Railway, Heroku, etc.

## API Documentation

### Authentication
- `POST /v1/auth/signup` - User registration
- `POST /v1/auth/login` - User login
- `GET /v1/auth/me` - Get current user info

### Activities
- `POST /v1/activities` - Log new activity
- `GET /v1/activities` - List user activities

### Analytics
- `GET /v1/summary` - Monthly emissions summary
- `GET /v1/credits` - User credits and rewards
- `GET /v1/tips` - Sustainability tips

## Project Structure
```
ecocred/
├── backend/           # Flask API server
│   ├── app.py        # Main application
│   ├── requirements.txt
│   ├── ecocred.db    # SQLite database
│   └── .env          # Environment variables
├── frontend/         # Static web files
│   ├── index.html    # Landing page
│   ├── dashboard.html # User dashboard
│   ├── login.html    # Login page
│   ├── signup.html   # Registration page
│   ├── log.html      # Activity logging
│   ├── styles.css    # Global styles
│   └── js/
│       └── common.js # Shared JavaScript
├── docs/             # Documentation
│   └── spec.md       # Product specification
├── Dockerfile        # Docker configuration
├── docker-compose.yml
└── DEPLOYMENT.md     # Deployment guide
```

## Contributing
Open an issue or PR with a clear description, reproduction steps (if applicable), and screenshots for UI changes.

## License
MIT (to be confirmed)

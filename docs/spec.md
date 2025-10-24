EcoCred – Product Spec (Concise)
=================================

Goals
---------------------------------
- Make it easy and motivating to reduce personal/organizational carbon footprint.
- Provide credible emissions estimates and simple, meaningful credits.

Non‑Goals (MVP)
---------------------------------
- Carbon offsets marketplace
- Advanced ML recommendations
- Complex org hierarchies and SSO

Personas
---------------------------------
- Individual: Wants to understand impact and improve habits.
- Team lead: Wants to engage a small group in friendly competition.

Primary User Stories (MVP)
---------------------------------
- As a user, I can log transport and electricity usage.
- As a user, I can see my CO₂e totals by day/week/month.
- As a user, I earn credits for eco‑friendly choices and streaks.
- As a user, I can view tips to reduce my emissions.

Activity Model
---------------------------------
- category: transport | electricity (extendable)
- type: car | bus | train | flight | bike | walk | grid_electricity
- quantity: numeric (e.g., km, kWh)
- unit: km | mi | kWh
- date: ISO timestamp
- metadata: optional (e.g., vehicle fuel type)

Emissions Calculation
---------------------------------
CO₂e = activity_quantity × emission_factor

Notes:
- Store emission factors with versioning and source metadata.
- Prefer per‑unit factors (e.g., kg CO₂e per km or per kWh).
- Support overrides by region where relevant (e.g., grid intensity).

Credits Logic (MVP)
---------------------------------
- Low‑carbon choice bonus (e.g., bike/walk/public transit over car)
- Streaks: daily logging streak and weekly reduction streak
- Milestones: first 10 activities, first 1 kg CO₂e saved, etc.

Data Model (relational, draft)
---------------------------------
- users(id, email, display_name, created_at)
- activities(id, user_id, category, type, quantity, unit, date, metadata_json, co2e, created_at)
- emission_factors(id, category, type, unit, factor_value, factor_unit, region, source, version, valid_from, valid_to)
- credits(id, user_id, activity_id nullable, reason, points, created_at)
- tips(id, key, title, body, category, enabled)
- goals(id, user_id, period, target_co2e, created_at)

Key API Endpoints (draft)
---------------------------------
- POST /v1/auth/signup { email, password }
- POST /v1/auth/login { email, password }
- GET  /v1/profile
- POST /v1/activities { category, type, quantity, unit, date, metadata }
- GET  /v1/activities?from=&to=&page=
- GET  /v1/summary?period=day|week|month → { total_co2e, trend }
- GET  /v1/credits → { total_points, recent }
- GET  /v1/tips → list of applicable tips

Dashboard (MVP)
---------------------------------
- Header: total CO₂e this month, credits balance
- Chart: emissions over time (line or bar)
- Feed: recent activities and credits earned
- CTA: log new activity, see tips

Privacy & Security
---------------------------------
- Store minimal personal data; allow account deletion and data export.
- Hash passwords with a modern algorithm; use HTTPS and secure cookies/JWT.
- Log audit events for sensitive operations.

Success Metrics
---------------------------------
- DAUs, activity log events per user, 4‑week retention
- Average monthly CO₂e reduction per active user
- Tips engagement rate and credits earned per user

Future Extensions
---------------------------------
- More categories (food, purchases, heating, waste)
- Integrations (utility bills, transit cards, GPS/health apps)
- Teams/orgs, leaderboards, badges, rewards catalog
- Region‑specific grid intensity and factor updates




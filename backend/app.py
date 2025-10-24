import os
from datetime import datetime, timedelta, timezone
from functools import wraps

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from sqlalchemy import Column, String, Float, DateTime, Integer, ForeignKey, create_engine, func
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, scoped_session
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from uuid import uuid4


load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-me")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///ecocred.db")

engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = scoped_session(sessionmaker(bind=engine, autoflush=False, autocommit=False))
Base = declarative_base()


class User(Base):
	__tablename__ = "users"
	id = Column(String, primary_key=True)
	email = Column(String, unique=True, nullable=False)
	password_hash = Column(String, nullable=False)
	display_name = Column(String, nullable=True)
	created_at = Column(DateTime, default=datetime.now(timezone.utc))
	activities = relationship("Activity", back_populates="user")
	credits = relationship("Credit", back_populates="user")


class Activity(Base):
	__tablename__ = "activities"
	id = Column(String, primary_key=True)
	user_id = Column(String, ForeignKey("users.id"), nullable=False)
	category = Column(String, nullable=False)
	type = Column(String, nullable=False)
	quantity = Column(Float, nullable=False)
	unit = Column(String, nullable=False)
	date = Column(DateTime, nullable=False)
	metadata_json = Column(String, nullable=True)
	co2e = Column(Float, nullable=False)
	created_at = Column(DateTime, default=datetime.now(timezone.utc))
	user = relationship("User", back_populates="activities")
	credits = relationship("Credit", back_populates="activity")


class EmissionFactor(Base):
	__tablename__ = "emission_factors"
	id = Column(String, primary_key=True)
	category = Column(String, nullable=False)
	type = Column(String, nullable=False)
	unit = Column(String, nullable=False)
	factor_value = Column(Float, nullable=False)
	factor_unit = Column(String, nullable=False)
	region = Column(String, nullable=True)
	source = Column(String, nullable=True)
	version = Column(String, nullable=True)


class Credit(Base):
	__tablename__ = "credits"
	id = Column(String, primary_key=True)
	user_id = Column(String, ForeignKey("users.id"), nullable=False)
	activity_id = Column(String, ForeignKey("activities.id"), nullable=True)
	reason = Column(String, nullable=False)
	points = Column(Integer, nullable=False)
	created_at = Column(DateTime, default=datetime.now(timezone.utc))
	user = relationship("User", back_populates="credits")
	activity = relationship("Activity", back_populates="credits")


class Tip(Base):
	__tablename__ = "tips"
	id = Column(String, primary_key=True)
	key = Column(String, unique=True, nullable=False)
	title = Column(String, nullable=False)
	body = Column(String, nullable=False)
	category = Column(String, nullable=True)
	enabled = Column(Integer, default=1)


def generate_id(prefix: str) -> str:
	return f"{prefix}_{uuid4().hex}"


def seed_data():
	db = SessionLocal()
	try:
		# emission factors
		if db.query(EmissionFactor).count() == 0:
			factors = [
				("transport", "car", "km", 0.171, "kgCO2e/km"),
				("transport", "bus", "km", 0.089, "kgCO2e/km"),
				("transport", "train", "km", 0.041, "kgCO2e/km"),
				("transport", "flight", "km", 0.255, "kgCO2e/km"),
				("transport", "bike", "km", 0.0, "kgCO2e/km"),
				("transport", "walk", "km", 0.0, "kgCO2e/km"),
				("electricity", "grid_electricity", "kWh", 0.475, "kgCO2e/kWh"),
			]
			for c, t, u, v, fu in factors:
				db.add(
					EmissionFactor(
						id=generate_id("ef"),
						category=c,
						type=t,
						unit=u,
						factor_value=v,
						factor_unit=fu,
						source="seed",
						version="2024",
					)
				)
		# tips
		if db.query(Tip).count() == 0:
			tips = [
				("short-trips-bike", "Bike or walk short trips", "For trips under 3 km, consider biking or walking to avoid car emissions.", "transport"),
				("public-transit", "Use public transit", "Buses and trains have lower emissions per passenger than cars.", "transport"),
				("turn-off-standby", "Reduce standby power", "Unplug devices or use power strips to cut phantom loads.", "electricity"),
				("led-bulbs", "Switch to LED bulbs", "LEDs use much less energy than incandescents.", "electricity"),
			]
			for k, ti, bo, cat in tips:
				db.add(Tip(id=generate_id("tip"), key=k, title=ti, body=bo, category=cat, enabled=1))
		db.commit()
	finally:
		db.close()


# Create Flask app instance
app = Flask(__name__)
CORS(app, supports_credentials=True)

# Serve frontend files
@app.route('/')
def index():
	frontend_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend')
	index_path = os.path.join(frontend_dir, 'index.html')
	if os.path.exists(index_path):
		return send_from_directory(frontend_dir, 'index.html')
	return "EcoCred backend is running 🚀"

@app.route('/test')
def test():
	return "Test route working!"

@app.route('/<path:filename>')
def serve_static(filename):
	frontend_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend')
	file_path = os.path.join(frontend_dir, filename)
	if os.path.exists(file_path):
		return send_from_directory(frontend_dir, filename)
	return "File not found", 404

def auth_required(fn):
	@wraps(fn)
	def wrapper(*args, **kwargs):
		auth = request.headers.get("Authorization", "")
		if not auth.startswith("Bearer "):
			return jsonify({"error": "Unauthorized"}), 401
		token = auth.split(" ", 1)[1]
		try:
			payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
		except Exception:
			return jsonify({"error": "Unauthorized"}), 401
		request.user_id = payload.get("sub")
		return fn(*args, **kwargs)
	return wrapper

@app.get("/v1/health")
def health():
	return {"status": "ok"}

@app.post("/v1/auth/signup")
def signup():
	body = request.get_json(force=True)
	email = (body.get("email") or "").strip().lower()
	password = body.get("password") or ""
	display_name = body.get("displayName")
	if not email or not password or len(password) < 8:
		return jsonify({"error": "Invalid input"}), 400
	db = SessionLocal()
	try:
		existing = db.query(User).filter_by(email=email).first()
		if existing:
			return jsonify({"error": "Email already in use"}), 409
		user = User(
			id=generate_id("user"),
			email=email,
			password_hash=generate_password_hash(password),
			display_name=display_name,
		)
		db.add(user)
		db.commit()
		token = jwt.encode({"sub": user.id, "iat": int(datetime.now(timezone.utc).timestamp())}, JWT_SECRET, algorithm="HS256")
		return jsonify({"token": token})
	finally:
		db.close()

@app.post("/v1/auth/login")
def login():
	body = request.get_json(force=True)
	email = (body.get("email") or "").strip().lower()
	password = body.get("password") or ""
	db = SessionLocal()
	try:
		user = db.query(User).filter_by(email=email).first()
		if not user or not check_password_hash(user.password_hash, password):
			return jsonify({"error": "Invalid credentials"}), 401
		token = jwt.encode({"sub": user.id, "iat": int(datetime.now(timezone.utc).timestamp())}, JWT_SECRET, algorithm="HS256")
		return jsonify({"token": token})
	finally:
		db.close()

@app.get("/v1/auth/me")
@auth_required
def me():
	db = SessionLocal()
	try:
		user = db.query(User).filter_by(id=request.user_id).first()
		if not user:
			return jsonify({"error": "Not found"}), 404
		return jsonify({
			"user": {
				"id": user.id,
				"email": user.email,
				"displayName": user.display_name,
				"createdAt": user.created_at.isoformat(),
			}
		})
	finally:
		db.close()

@app.post("/v1/activities")
@auth_required
def create_activity():
	body = request.get_json(force=True)
	category = body.get("category")
	a_type = body.get("type")
	quantity = float(body.get("quantity") or 0)
	unit = body.get("unit")
	date_str = body.get("date")
	if not (category and a_type and quantity > 0 and unit and date_str):
		return jsonify({"error": "Invalid input"}), 400
	try:
		date_val = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
	except Exception:
		return jsonify({"error": "Invalid date"}), 400
	db = SessionLocal()
	try:
		factor = (
			db.query(EmissionFactor)
			.filter_by(category=category, type=a_type, unit=unit)
			.first()
		)
		if factor is None and unit == "mi":
			# convert miles to km if we only have km factor
			factor = (
				db.query(EmissionFactor)
				.filter_by(category=category, type=a_type, unit="km")
				.first()
			)
			quantity = quantity * 1.60934 if factor else quantity
		if factor is None:
			return jsonify({"error": "No emission factor for this activity"}), 400
		co2e = quantity * factor.factor_value
		activity = Activity(
			id=generate_id("act"),
			user_id=request.user_id,
			category=category,
			type=a_type,
			quantity=quantity,
			unit=unit,
			date=date_val,
			metadata_json=None,
			co2e=co2e,
		)
		db.add(activity)
		# credits
		points = 0
		if a_type in ("bike", "walk"):
			points = 5
		elif a_type in ("bus", "train"):
			points = 3
		if points > 0:
			db.add(Credit(id=generate_id("cred"), user_id=request.user_id, activity_id=activity.id, reason="low_carbon_choice", points=points))
		db.commit()
		return jsonify({"activity": {
			"id": activity.id,
			"co2e": activity.co2e,
		}})
	finally:
		db.close()

@app.get("/v1/activities")
@auth_required
def list_activities():
	db = SessionLocal()
	try:
		items = (
			db.query(Activity)
			.filter(Activity.user_id == request.user_id)
			.order_by(Activity.date.desc())
			.limit(50)
			.all()
		)
		return jsonify({
			"items": [
				{
					"id": a.id,
					"category": a.category,
					"type": a.type,
					"quantity": a.quantity,
					"unit": a.unit,
					"date": a.date.isoformat(),
					"co2e": a.co2e,
				}
				for a in items
			]
		})
	finally:
		db.close()

@app.get("/v1/summary")
@auth_required
def summary():
	period = request.args.get("period", "month")
	now = datetime.now(timezone.utc).replace(tzinfo=None)
	if period == "day":
		start = now.replace(hour=0, minute=0, second=0, microsecond=0)
	elif period == "week":
		start = now - timedelta(days=(now.weekday()))
		start = start.replace(hour=0, minute=0, second=0, microsecond=0)
	else:
		start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
	db = SessionLocal()
	try:
		total = (
			db.query(func.coalesce(func.sum(Activity.co2e), 0.0))
			.filter(Activity.user_id == request.user_id, Activity.date >= start, Activity.date <= now)
			.scalar()
		)
		prev_end = start - timedelta(seconds=1)
		if period == "day":
			prev_start = (start - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
		elif period == "week":
			prev_start = start - timedelta(days=7)
		else:
			prev_month_last_day = start - timedelta(days=1)
			prev_start = prev_month_last_day.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
		prev_total = (
			db.query(func.coalesce(func.sum(Activity.co2e), 0.0))
			.filter(Activity.user_id == request.user_id, Activity.date >= prev_start, Activity.date <= prev_end)
			.scalar()
		)
		trend = None if prev_total == 0 else (total - prev_total) / prev_total
		return jsonify({"total_co2e": float(total or 0), "trend": trend})
	finally:
		db.close()

@app.get("/v1/credits")
@auth_required
def get_credits():
	db = SessionLocal()
	try:
		total_points = (
			db.query(func.coalesce(func.sum(Credit.points), 0))
			.filter(Credit.user_id == request.user_id)
			.scalar()
		)
		recent = (
			db.query(Credit)
			.filter(Credit.user_id == request.user_id)
			.order_by(Credit.created_at.desc())
			.limit(50)
			.all()
		)
		return jsonify({
			"total_points": int(total_points or 0),
			"recent": [
				{
					"id": c.id,
					"reason": c.reason,
					"points": c.points,
					"createdAt": c.created_at.isoformat(),
				}
				for c in recent
			],
		})
	finally:
		db.close()

@app.get("/v1/tips")
@auth_required
def get_tips():
	db = SessionLocal()
	try:
		tips = db.query(Tip).filter(Tip.enabled == 1).all()
		return jsonify([
			{
				"id": t.id,
				"title": t.title,
				"body": t.body,
				"category": t.category,
			}
			for t in tips
		])
	finally:
		db.close()


if __name__ == "__main__":
	Base.metadata.create_all(bind=engine)
	seed_data()
	app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))



import os
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from sqlalchemy import func
from models import db, Patient, Doctor, Bill, Visit, Recommendation, Schedule, Resource

load_dotenv()


def create_app():
    app = Flask(__name__)

    # IMPORTANT: You are using SQLite on Render
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///render_temp.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    CORS(app)
    db.init_app(app)
    
    # --------------------------------------------------
    # ROOT ROUTE (shows backend is running)
    # --------------------------------------------------
    @app.get("/")
    def index():
        return {"message": "Backend is running"}
    
    # --------------------------------------------------
    # TEMPORARY: Create Tables on Render (run once)
    # --------------------------------------------------
    @app.get("/create_tables")
    def create_tables():
        with app.app_context():
            db.create_all()
        return {"status": "tables created"}
    # --------------------------------------------------
    # Health Check
    # --------------------------------------------------
    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    # --------------------------------------------------
    # PATIENT CRUD
    # --------------------------------------------------
    @app.get("/api/patients")
    def list_patients():
        rows = Patient.query.all()
        return jsonify([{c.name: getattr(p, c.name) for c in p.__table__.columns} for p in rows])

    @app.get("/api/patients/<int:pid>")
    def get_patient(pid):
        p = Patient.query.get_or_404(pid)
        return {c.name: getattr(p, c.name) for c in p.__table__.columns}

    @app.post("/api/patients")
    def create_patient():
        d = request.json or {}
        p = Patient(
            SSN=d.get("SSN"),
            Name=d.get("Name"),
            DOB=datetime.fromisoformat(d["DOB"]).date() if d.get("DOB") else None,
            Sex=d.get("Sex"),
            Contact=d.get("Contact"),
            Insurance_Provider=d.get("Insurance_Provider"),
            Admitted=bool(d.get("Admitted", False)),
            Discharged=bool(d.get("Discharged", False)),
            Description=d.get("Description"),
            AdmissionDate=datetime.fromisoformat(d["AdmissionDate"]).date()
                if d.get("AdmissionDate") else None,
            DischargeDate=datetime.fromisoformat(d["DischargeDate"]).date()
                if d.get("DischargeDate") else None,
        )
        db.session.add(p)
        db.session.commit()
        return {"created": p.Patient_ID}, 201

    @app.put("/api/patients/<int:pid>")
    def update_patient(pid):
        p = Patient.query.get_or_404(pid)
        d = request.json or {}

        update_fields = [
            "SSN", "Name", "Sex", "Contact", "Insurance_Provider",
            "Description", "Admitted", "Discharged"
        ]

        for f in update_fields:
            if f in d:
                setattr(p, f, d[f])

        if "DOB" in d:
            p.DOB = datetime.fromisoformat(d["DOB"]).date() if d["DOB"] else None

        if "AdmissionDate" in d:
            p.AdmissionDate = datetime.fromisoformat(d["AdmissionDate"]).date() if d["AdmissionDate"] else None

        if "DischargeDate" in d:
            p.DischargeDate = datetime.fromisoformat(d["DischargeDate"]).date() if d["DischargeDate"] else None

        db.session.commit()
        return {c.name: getattr(p, c.name) for c in p.__table__.columns}

    @app.delete("/api/patients/<int:pid>")
    def delete_patient(pid):
        p = Patient.query.get_or_404(pid)
        db.session.delete(p)
        db.session.commit()
        return {"deleted": pid}

    # --------------------------------------------------
    # DOCTORS
    # --------------------------------------------------
    @app.get("/api/doctors")
    def list_doctors():
        rows = Doctor.query.all()
        return jsonify([{c.name: getattr(r, c.name) for c in r.__table__.columns} for r in rows])
    # --------------------------------------------------
    # CREATE DOCTOR
    # --------------------------------------------------
    @app.post("/api/doctors")
    def create_doctor():
        d = request.json or {}
        doctor = Doctor(
            Name=d.get("Name"),
            Specialty=d.get("Specialty"),
            Contact=d.get("Contact")
        )
        db.session.add(doctor)
        db.session.commit()

        return {"created": doctor.Doctor_ID}, 201
    # --------------------------------------------------
    # BILLS
    # --------------------------------------------------
    @app.get("/api/bills")
    def list_bills():
        rows = Bill.query.all()
        return jsonify([{c.name: getattr(r, c.name) for c in r.__table__.columns} for r in rows])

    @app.get("/api/patients/<int:pid>/bills")
    def bills_for_patient(pid):
        rows = Bill.query.filter_by(Patient_ID=pid).all()
        return jsonify([{c.name: getattr(b, c.name) for c in b.__table__.columns} for b in rows])

    # --------------------------------------------------
    # VISITS
    # --------------------------------------------------
    @app.get("/api/visits/<int:pid>")
    def get_visits(pid):
        rows = Visit.query.filter_by(Patient_ID=pid).all()
        return jsonify([{c.name: getattr(v, c.name) for c in v.__table__.columns} for v in rows])

    @app.post("/api/visits")
    def create_visit():
        d = request.json
        v = Visit(
            Patient_ID=d["Patient_ID"],
            Doctor_ID=d["Doctor_ID"],
            VisitDate=datetime.fromisoformat(d["VisitDate"]).date(),
            Notes=d.get("Notes")
        )
        db.session.add(v)
        db.session.commit()
        return {"created": v.Visit_ID}

    # --------------------------------------------------
    # RECOMMENDATIONS
    # --------------------------------------------------
    @app.get("/api/recommendations/<int:pid>")
    def get_recommendations(pid):
        rows = Recommendation.query.filter_by(Patient_ID=pid).all()
        return jsonify([{c.name: getattr(r, c.name) for c in r.__table__.columns} for r in rows])

    @app.post("/api/recommendations")
    def create_recommendation():
        d = request.json
        r = Recommendation(Patient_ID=d["Patient_ID"], Text=d["Text"])
        db.session.add(r)
        db.session.commit()
        return {"created": r.Rec_ID}

    # --------------------------------------------------
    # SCHEDULE
    # --------------------------------------------------
    @app.get("/api/schedule/<int:eid>")
    def get_schedule(eid):
        rows = Schedule.query.filter_by(Employee_ID=eid).all()
        return jsonify([{c.name: getattr(s, c.name) for c in s.__table__.columns} for s in rows])

    # --------------------------------------------------
    # RESOURCES
    # --------------------------------------------------
    @app.get("/api/resources")
    def get_resources():
        rows = Resource.query.all()
        return jsonify([{c.name: getattr(r, c.name) for c in r.__table__.columns} for r in rows])

    # --------------------------------------------------
    # ANALYTICS — PATIENT FLOW
    # --------------------------------------------------
    @app.get("/api/analytics/patient_flow")
    def patient_flow():
        rows = db.session.query(
            Patient.AdmissionDate,
            func.count(Patient.Patient_ID)
        ).filter(Patient.AdmissionDate.isnot(None)) \
        .group_by(Patient.AdmissionDate) \
        .order_by(Patient.AdmissionDate).all()

        if not rows:
            return {"error": "No admission data"}

        history = [{"date": str(d), "count": c} for d, c in rows]

        counts = [c for _, c in rows]
        window = min(5, len(counts))
        moving_avg = sum(counts[-window:]) / window

        return {
            "history": history,
            "predicted_next_day": round(moving_avg)
        }

    # --------------------------------------------------
    # ANALYTICS — RESOURCE OPTIMIZATION
    # --------------------------------------------------
    @app.get("/api/analytics/resource_optimization")
    def resource_optimization():
        rows = db.session.query(
            Bill.Treatment,
            func.avg(Bill.Total_Amount).label("avg_cost")
        ).group_by(Bill.Treatment) \
        .order_by(func.avg(Bill.Total_Amount).desc()) \
        .all()

        return {
            "most_expensive_procedures": [
                {"treatment": t, "avg_cost": float(c)} for t, c in rows[:5]
            ]
        }

    return app


app = create_app()

if __name__ == "__main__":
    app.run(port=5001, debug=True)

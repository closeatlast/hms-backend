import os
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from sqlalchemy import func

from models import (
    db, Patient, Doctor, Nurse, Receptionist, Employee,
    Bill, Visit, Recommendation, Schedule, Resource,
    Room, Medication
)

load_dotenv()


def create_app():
    app = Flask(__name__)

    # SQLite for Render
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///render_temp2.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    CORS(app)
    db.init_app(app)

    # --------------------------------------------------
    # ROOT
    # --------------------------------------------------
    @app.get("/")
    def index():
        return {"message": "Backend is running"}

    # --------------------------------------------------
    # CREATE TABLES
    # --------------------------------------------------
    @app.get("/create_tables")
    def create_tables():
        with app.app_context():
            db.create_all()
        return {"status": "tables created"}

    # --------------------------------------------------
    # HEALTH CHECK
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
            Room_ID=d.get("Room_ID")
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
            "Description", "Admitted", "Discharged", "Room_ID"
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
    # EMPLOYEE CRUD (parent ISA entity)
    # --------------------------------------------------
    @app.get("/api/employees")
    def list_employees():
        rows = Employee.query.all()
        return jsonify([{c.name: getattr(e, c.name) for c in e.__table__.columns} for e in rows])

    @app.post("/api/employees")
    def create_employee():
        d = request.json or {}
        e = Employee(Name=d.get("Name"), Salary=d.get("Salary"))
        db.session.add(e)
        db.session.commit()
        return {"created": e.Employee_ID}, 201

    # --------------------------------------------------
    # DOCTOR ROUTES (ISA Employee)
    # --------------------------------------------------
    @app.post("/api/doctors")
    def create_doctor():
        d = request.json or {}

        # First create Employee
        e = Employee(Name=d.get("Name"), Salary=d.get("Salary"))
        db.session.add(e)
        db.session.commit()

        doctor = Doctor(
            Employee_ID=e.Employee_ID,
            Name=d.get("Name"),
            Specialty=d.get("Specialty"),
            Contact=d.get("Contact")
        )
        db.session.add(doctor)
        db.session.commit()

        return {"created": doctor.Doctor_ID}, 201

    @app.put("/api/doctors/<int:did>")
    def update_doctor(did):
        d = Doctor.query.get_or_404(did)
        data = request.json or {}

        if "Name" in data:
            d.Name = data["Name"]
        if "Specialty" in data:
            d.Specialty = data["Specialty"]
        if "Contact" in data:
            d.Contact = data["Contact"]

        db.session.commit()
        return {c.name: getattr(d, c.name) for c in d.__table__.columns}

    @app.get("/api/doctors")
    def list_doctors():
        rows = Doctor.query.all()
        return jsonify([{c.name: getattr(r, c.name) for c in r.__table__.columns} for r in rows])

    # --------------------------------------------------
    # NURSE ROUTES
    # --------------------------------------------------
    @app.post("/api/nurses")
    def create_nurse():
        d = request.json or {}

        e = Employee(Name=d.get("Name"), Salary=d.get("Salary"))
        db.session.add(e)
        db.session.commit()

        nurse = Nurse(
            Employee_ID=e.Employee_ID,
            Name=d.get("Name"),
            Contact=d.get("Contact")
        )
        db.session.add(nurse)
        db.session.commit()

        return {"created": nurse.Nurse_ID}, 201

    @app.get("/api/nurses")
    def list_nurses():
        rows = Nurse.query.all()
        return jsonify([{c.name: getattr(n, c.name) for c in n.__table__.columns} for n in rows])

    # --------------------------------------------------
    # RECEPTIONIST
    # --------------------------------------------------
    @app.post("/api/receptionists")
    def create_receptionist():
        d = request.json or {}

        e = Employee(Name=d.get("Name"), Salary=d.get("Salary"))
        db.session.add(e)
        db.session.commit()

        r = Receptionist(
            Employee_ID=e.Employee_ID,
            Name=d.get("Name"),
            Contact=d.get("Contact")
        )
        db.session.add(r)
        db.session.commit()

        return {"created": r.Receptionist_ID}, 201

    @app.get("/api/receptionists")
    def list_receptionists():
        rows = Receptionist.query.all()
        return jsonify([{c.name: getattr(x, c.name) for c in x.__table__.columns} for x in rows])

    # --------------------------------------------------
    # ROOM CRUD
    # --------------------------------------------------
    @app.post("/api/rooms")
    def create_room():
        d = request.json or {}
        r = Room(
            Room_Number=d.get("Room_Number"),
            Room_Type=d.get("Room_Type"),
            Status=d.get("Status"),
            Nurse_ID=d.get("Nurse_ID")
        )
        db.session.add(r)
        db.session.commit()
        return {"created": r.Room_ID}, 201

    @app.get("/api/rooms")
    def list_rooms():
        rows = Room.query.all()
        return jsonify([{c.name: getattr(r, c.name) for c in r.__table__.columns} for r in rows])

    # --------------------------------------------------
    # MEDICATION CRUD
    # --------------------------------------------------
    @app.post("/api/medications")
    def create_medication():
        d = request.json or {}
        m = Medication(
            Name=d.get("Name"),
            Dosage=d.get("Dosage"),
            Patient_ID=d.get("Patient_ID")
        )
        db.session.add(m)
        db.session.commit()
        return {"created": m.Medication_ID}, 201

    @app.get("/api/medications")
    def list_medications():
        rows = Medication.query.all()
        return jsonify([{c.name: getattr(m, c.name) for c in m.__table__.columns} for m in rows])

    # --------------------------------------------------
    # EXISTING BILL, VISIT, RECOMMENDATION, SCHEDULE, RESOURCE
    # (unchanged)
    # --------------------------------------------------

    @app.get("/api/bills")
    def list_bills():
        rows = Bill.query.all()
        return jsonify([{c.name: getattr(r, c.name) for c in r.__table__.columns} for r in rows])

    @app.get("/api/patients/<int:pid>/bills")
    def bills_for_patient(pid):
        rows = Bill.query.filter_by(Patient_ID=pid).all()
        return jsonify([{c.name: getattr(b, c.name) for c in b.__table__.columns} for b in rows])

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

    @app.get("/api/schedule/<int:eid>")
    def get_schedule(eid):
        rows = Schedule.query.filter_by(Employee_ID=eid).all()
        return jsonify([{c.name: getattr(s, c.name) for c in s.__table__.columns} for s in rows])

    @app.get("/api/resources")
    def get_resources():
        rows = Resource.query.all()
        return jsonify([{c.name: getattr(r, c.name) for c in r.__table__.columns} for r in rows])

    # --------------------------------------------------
    # ANALYTICS
    # --------------------------------------------------
    @app.get("/api/analytics/patient_flow")
    def patient_flow():
        rows = (
            db.session.query(Patient.AdmissionDate, func.count(Patient.Patient_ID))
            .filter(Patient.AdmissionDate.isnot(None))
            .group_by(Patient.AdmissionDate)
            .order_by(Patient.AdmissionDate)
            .all()
        )

        if not rows:
            return {"error": "No admission data"}

        history = [{"date": str(d), "count": c} for d, c in rows]

        counts = [c for _, c in rows]
        window = min(5, len(counts))
        moving_avg = sum(counts[-window:]) / window

        return {"history": history, "predicted_next_day": round(moving_avg)}

    @app.get("/api/analytics/resource_optimization")
    def resource_optimization():
        rows = (
            db.session.query(Bill.Treatment, func.avg(Bill.Total_Amount))
            .group_by(Bill.Treatment)
            .order_by(func.avg(Bill.Total_Amount).desc())
            .all()
        )

        return {
            "most_expensive_procedures": [
                {"treatment": t, "avg_cost": float(c)} for t, c in rows[:5]
            ]
        }

    return app


app = create_app()

if __name__ == "__main__":
    app.run(port=5001, debug=True)

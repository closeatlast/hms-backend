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

    # SQLite on Render
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///render_temp2.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    CORS(app)
    db.init_app(app)

    # --------------------------------------------------
    # ROOT / HEALTH / CREATE TABLES
    # --------------------------------------------------
    @app.get("/")
    def index():
        return {"message": "Backend is running"}

    @app.get("/create_tables")
    def create_tables():
        with app.app_context():
            db.create_all()
        return {"status": "tables created"}

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

        for field in [
            "SSN", "Name", "Sex", "Contact", "Insurance_Provider",
            "Description", "Admitted", "Discharged", "Room_ID"
        ]:
            if field in d:
                setattr(p, field, d[field])

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
    # EMPLOYEE (ISA parent)
    # --------------------------------------------------
    @app.get("/api/employees")
    def list_employees():
        employees = Employee.query.all()

        output = []
        for e in employees:
            data = {
            "Employee_ID": e.Employee_ID,
            "Name": e.Name,
            "Salary": float(e.Salary) if e.Salary else None,
            "Type": e.Type
            }

            # Include subclass-specific fields
            if isinstance(e, Doctor):
                data["Specialty"] = e.Specialty
                data["Contact"] = e.Contact

            if isinstance(e, Nurse):
                data["Contact"] = e.Contact

            if isinstance(e, Receptionist):
                data["Contact"] = e.Contact
            output.append(data)

        return jsonify(output)


    @app.post("/api/employees")
    def create_employee():
        d = request.json or {}
        e = Employee(Name=d.get("Name"), Salary=d.get("Salary"))
        db.session.add(e)
        db.session.commit()
        return {"created": e.Employee_ID}, 201

    # --------------------------------------------------
    # DOCTOR (ISA Employee) – CORRECTED
    # --------------------------------------------------
    @app.post("/api/doctors")
    def create_doctor():
        d = request.json or {}

        # Because Doctor inherits from Employee, just create the Doctor.
        doctor = Doctor(
            Name=d.get("Name"),
            Salary=d.get("Salary"),
            Specialty=d.get("Specialty"),
            Contact=d.get("Contact")
        )
        db.session.add(doctor)
        db.session.commit()

        return {"created": doctor.Doctor_ID}, 201

    @app.get("/api/doctors")
    def list_doctors():
        rows = Doctor.query.all()
        # include inherited columns too
        result = []
        for doc in rows:
            result.append({
                "Doctor_ID": doc.Doctor_ID,
                "Name": doc.Name,
                "Salary": float(doc.Salary) if doc.Salary is not None else None,
                "Specialty": doc.Specialty,
                "Contact": doc.Contact,
            })
        return jsonify(result)

    @app.put("/api/doctors/<int:did>")
    def update_doctor(did):
        d_obj = Doctor.query.get_or_404(did)
        data = request.json or {}

        for field in ["Name", "Salary", "Specialty", "Contact"]:
            if field in data:
                setattr(d_obj, field, data[field])

        db.session.commit()
        return {
            "Doctor_ID": d_obj.Doctor_ID,
            "Name": d_obj.Name,
            "Salary": float(d_obj.Salary) if d_obj.Salary is not None else None,
            "Specialty": d_obj.Specialty,
            "Contact": d_obj.Contact,
        }

    # --------------------------------------------------
    # NURSE (ISA Employee) – CORRECTED
    # --------------------------------------------------
    @app.post("/api/nurses")
    def create_nurse():
        d = request.json or {}

        nurse = Nurse(
            Name=d.get("Name"),
            Salary=d.get("Salary"),
            Contact=d.get("Contact")
        )
        db.session.add(nurse)
        db.session.commit()

        return {"created": nurse.Nurse_ID}, 201

    @app.get("/api/nurses")
    def list_nurses():
        rows = Nurse.query.all()
        result = []
        for n in rows:
            result.append({
                "Nurse_ID": n.Nurse_ID,
                "Name": n.Name,
                "Salary": float(n.Salary) if n.Salary is not None else None,
                "Contact": n.Contact,
            })
        return jsonify(result)

    # --------------------------------------------------
    # RECEPTIONIST (ISA Employee) – CORRECTED
    # --------------------------------------------------
    @app.post("/api/receptionists")
    def create_receptionist():
        d = request.json or {}

        r = Receptionist(
            Name=d.get("Name"),
            Salary=d.get("Salary"),
            Contact=d.get("Contact")
        )
        db.session.add(r)
        db.session.commit()

        return {"created": r.Receptionist_ID}, 201

    @app.get("/api/receptionists")
    def list_receptionists():
        rows = Receptionist.query.all()
        result = []
        for x in rows:
            result.append({
                "Receptionist_ID": x.Receptionist_ID,
                "Name": x.Name,
                "Salary": float(x.Salary) if x.Salary is not None else None,
                "Contact": x.Contact,
            })
        return jsonify(result)

    # --------------------------------------------------
    # ROOM
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
    # MEDICATION
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
    # BILLS / VISITS / RECOMMENDATIONS / SCHEDULE / RESOURCE
    # --------------------------------------------------
    @app.get("/api/bills")
    def list_bills():
        rows = Bill.query.all()
        return jsonify([{c.name: getattr(r, c.name) for c in r.__table__.columns} for r in rows])

    @app.get("/api/patients/<int:pid>/bills")
    def bills_for_patient(pid):
        rows = Bill.query.filter_by(Patient_ID=pid).all()
        return jsonify([{c.name: getattr(b, c.name) for c in b.__table__.columns} for b in rows])

    @app.post("/api/visits")
    def create_visit():
        d = request.json or {}
        v = Visit(
            Patient_ID=d["Patient_ID"],
            Doctor_ID=d["Doctor_ID"],
            VisitDate=datetime.fromisoformat(d["VisitDate"]).date(),
            Notes=d.get("Notes")
        )
        db.session.add(v)
        db.session.commit()
        return {"created": v.Visit_ID}, 201

    @app.get("/api/visits/<int:pid>")
    def get_visits(pid):
        rows = Visit.query.filter_by(Patient_ID=pid).all()
        return jsonify([{c.name: getattr(v, c.name) for c in v.__table__.columns} for v in rows])

    @app.post("/api/recommendations")
    def create_recommendation():
        d = request.json or {}
        r = Recommendation(Patient_ID=d["Patient_ID"], Text=d["Text"])
        db.session.add(r)
        db.session.commit()
        return {"created": r.Rec_ID}, 201

    @app.get("/api/recommendations/<int:pid>")
    def get_recommendations(pid):
        rows = Recommendation.query.filter_by(Patient_ID=pid).all()
        return jsonify([{c.name: getattr(x, c.name) for c in x.__table__.columns} for x in rows])

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

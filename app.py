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
        return jsonify([
            {c.name: getattr(p, c.name) for c in p.__table__.columns}
            for p in rows
        ])

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

            if e.Type == "Doctor":
                doc = Doctor.query.get(e.Employee_ID)
                data["Specialty"] = doc.Specialty
                data["Contact"] = doc.Contact

            elif e.Type == "Nurse":
                nurse = Nurse.query.get(e.Employee_ID)
                data["Contact"] = nurse.Contact

            elif e.Type == "Receptionist":
                rec = Receptionist.query.get(e.Employee_ID)
                data["Contact"] = rec.Contact

            output.append(data)

        return jsonify(output)

    # --------------------------------------------------
    # DOCTOR CRUD (ISA)
    # --------------------------------------------------
    @app.post("/api/doctors")
    def create_doctor():
        d = request.json or {}
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
        return jsonify([
            {
                "Doctor_ID": d.Doctor_ID,
                "Name": d.Name,
                "Salary": float(d.Salary) if d.Salary else None,
                "Specialty": d.Specialty,
                "Contact": d.Contact
            }
            for d in rows
        ])

    @app.get("/api/doctors/<int:did>")
    def get_doctor(did):
        d = Doctor.query.get_or_404(did)
        return {
            "Doctor_ID": d.Doctor_ID,
            "Name": d.Name,
            "Salary": float(d.Salary) if d.Salary else None,
            "Specialty": d.Specialty,
            "Contact": d.Contact
        }

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
            "Salary": float(d_obj.Salary) if d_obj.Salary else None,
            "Specialty": d_obj.Specialty,
            "Contact": d_obj.Contact
        }

    @app.delete("/api/doctors/<int:did>")
    def delete_doctor(did):
        d = Doctor.query.get_or_404(did)
        db.session.delete(d)
        db.session.commit()
        return {"deleted": did}

    # --------------------------------------------------
    # NURSE CRUD (ISA)
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
        return jsonify([
            {
                "Nurse_ID": n.Nurse_ID,
                "Name": n.Name,
                "Salary": float(n.Salary) if n.Salary else None,
                "Contact": n.Contact
            }
            for n in rows
        ])

    @app.get("/api/nurses/<int:nid>")
    def get_nurse(nid):
        n = Nurse.query.get_or_404(nid)
        return {
            "Nurse_ID": n.Nurse_ID,
            "Name": n.Name,
            "Salary": float(n.Salary) if n.Salary else None,
            "Contact": n.Contact
        }

    @app.put("/api/nurses/<int:nid>")
    def update_nurse(nid):
        n_obj = Nurse.query.get_or_404(nid)
        data = request.json or {}

        for field in ["Name", "Salary", "Contact"]:
            if field in data:
                setattr(n_obj, field, data[field])

        db.session.commit()

        return {
            "Nurse_ID": n_obj.Nurse_ID,
            "Name": n_obj.Name,
            "Salary": float(n_obj.Salary) if n_obj.Salary else None,
            "Contact": n_obj.Contact
        }

    @app.delete("/api/nurses/<int:nid>")
    def delete_nurse(nid):
        n = Nurse.query.get_or_404(nid)
        db.session.delete(n)
        db.session.commit()
        return {"deleted": nid}

    # --------------------------------------------------
    # RECEPTIONIST CRUD (ISA)
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
        return jsonify([
            {
                "Receptionist_ID": x.Receptionist_ID,
                "Name": x.Name,
                "Salary": float(x.Salary) if x.Salary else None,
                "Contact": x.Contact
            }
            for x in rows
        ])

    @app.get("/api/receptionists/<int:rid>")
    def get_receptionist(rid):
        r = Receptionist.query.get_or_404(rid)
        return {
            "Receptionist_ID": r.Receptionist_ID,
            "Name": r.Name,
            "Salary": float(r.Salary) if r.Salary else None,
            "Contact": r.Contact
        }

    @app.put("/api/receptionists/<int:rid>")
    def update_receptionist(rid):
        r_obj = Receptionist.query.get_or_404(rid)
        data = request.json or {}

        for field in ["Name", "Salary", "Contact"]:
            if field in data:
                setattr(r_obj, field, data[field])

        db.session.commit()

        return {
            "Receptionist_ID": r_obj.Receptionist_ID,
            "Name": r_obj.Name,
            "Salary": float(r_obj.Salary) if r_obj.Salary else None,
            "Contact": r_obj.Contact
        }

    @app.delete("/api/receptionists/<int:rid>")
    def delete_receptionist(rid):
        r = Receptionist.query.get_or_404(rid)
        db.session.delete(r)
        db.session.commit()
        return {"deleted": rid}

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
        return jsonify([
            {c.name: getattr(r, c.name) for c in r.__table__.columns}
            for r in rows
        ])

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
        return jsonify([
            {c.name: getattr(m, c.name) for c in m.__table__.columns}
            for m in rows
        ])

    # --------------------------------------------------
    # BILLS / VISITS / RECOMMENDATIONS / SCHEDULE / RESOURCE
    # --------------------------------------------------
    @app.get("/api/bills")
    def list_bills():
        rows = Bill.query.all()
        return jsonify([
            {c.name: getattr(r, c.name) for c in r.__table__.columns}
            for r in rows
        ])

    @app.get("/api/patients/<int:pid>/bills")
    def bills_for_patient(pid):
        rows = Bill.query.filter_by(Patient_ID=pid).all()
        return jsonify([
            {c.name: getattr(b, c.name) for c in b.__table__.columns}
            for b in rows
        ])

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
        return jsonify([
            {c.name: getattr(v, c.name) for c in v.__table__.columns}
            for v in rows
        ])

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
        return jsonify([
            {c.name: getattr(x, c.name) for c in x.__table__.columns}
            for x in rows
        ])

    @app.get("/api/schedule/<int:eid>")
    def get_schedule(eid):
        rows = Schedule.query.filter_by(Employee_ID=eid).all()
        return jsonify([
            {c.name: getattr(s, c.name) for c in s.__table__.columns}
            for s in rows
        ])

    @app.get("/api/resources")
    def get_resources():
        rows = Resource.query.all()
        return jsonify([
            {c.name: getattr(r, c.name) for c in r.__table__.columns}
            for r in rows
        ])

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
                {"treatment": t, "avg_cost": float(c)}
                for t, c in rows[:5]
            ]
        }

    # --------------------------------------------------
    # ROOM SHORTAGE FORECAST (ADVANCED ANALYTICS)
    # --------------------------------------------------
    @app.get("/api/analytics/room_shortage_forecast")
    def room_shortage_forecast():
        total_rooms = Room.query.count()
        occupied_rooms = Room.query.filter_by(Status="Occupied").count()
        available_rooms = total_rooms - occupied_rooms

        admission_rows = (
            db.session.query(Patient.AdmissionDate, func.count(Patient.Patient_ID))
            .filter(Patient.AdmissionDate.isnot(None))
            .group_by(Patient.AdmissionDate)
            .order_by(Patient.AdmissionDate)
            .all()
        )

        if not admission_rows:
            return {"error": "Not enough admission data to forecast."}

        counts = [c for _, c in admission_rows]
        window = min(5, len(counts))
        predicted_next_day = sum(counts[-window:]) / window

        los_rows = (
            db.session.query(
                func.avg(
                    func.julianday(Patient.DischargeDate)
                    - func.julianday(Patient.AdmissionDate)
                )
            )
            .filter(Patient.DischargeDate.isnot(None))
            .all()
        )

        avg_los = los_rows[0][0] if los_rows and los_rows[0][0] else 3

        if predicted_next_day == 0:
            projected_shortage_days = None
        else:
            projected_shortage_days = available_rooms / predicted_next_day

        if projected_shortage_days is None:
            risk = "LOW"
        elif projected_shortage_days < 1:
            risk = "CRITICAL"
        elif projected_shortage_days < 3:
            risk = "HIGH"
        else:
            risk = "MODERATE"

        return {
            "total_rooms": total_rooms,
            "occupied_rooms": occupied_rooms,
            "available_rooms": available_rooms,
            "predicted_next_day_admissions": round(predicted_next_day, 2),
            "average_length_of_stay_days": round(avg_los, 2),
            "projected_shortage_in_days": round(projected_shortage_days, 2) if projected_shortage_days else None,
            "risk": risk
        }

    return app


app = create_app()

if __name__ == "__main__":
    app.run(port=5001, debug=True)

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Employee(db.Model):
    __tablename__ = "EMPLOYEE"

    Employee_ID = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(100))
    Salary = db.Column(db.Numeric(12, 2))

    Type = db.Column(db.String(50))

    __mapper_args__ = {
        "polymorphic_identity": "Employee",
        "polymorphic_on": Type
    }


class Doctor(Employee):
    __tablename__ = "DOCTOR"

    Doctor_ID = db.Column(
        db.Integer,
        db.ForeignKey("EMPLOYEE.Employee_ID"),
        primary_key=True
    )

    Specialty = db.Column(db.String(100))
    Contact = db.Column(db.String(100))

    __mapper_args__ = {
        "polymorphic_identity": "Doctor"
    }


class Nurse(Employee):
    __tablename__ = "NURSE"

    Nurse_ID = db.Column(
        db.Integer,
        db.ForeignKey("EMPLOYEE.Employee_ID"),
        primary_key=True
    )

    Contact = db.Column(db.String(100))

    __mapper_args__ = {
        "polymorphic_identity": "Nurse"
    }


class Receptionist(Employee):
    __tablename__ = "RECEPTIONIST"

    Receptionist_ID = db.Column(
        db.Integer,
        db.ForeignKey("EMPLOYEE.Employee_ID"),
        primary_key=True
    )

    Contact = db.Column(db.String(100))

    __mapper_args__ = {
        "polymorphic_identity": "Receptionist"
    }


class Room(db.Model):
    __tablename__ = "ROOM"

    Room_ID = db.Column(db.Integer, primary_key=True)
    Room_Number = db.Column(db.String(20))
    Room_Type = db.Column(db.String(50))
    Status = db.Column(db.String(50))  # Available / Occupied

    Nurse_ID = db.Column(db.Integer, db.ForeignKey("NURSE.Nurse_ID"))


class Patient(db.Model):
    __tablename__ = "PATIENT"

    Patient_ID = db.Column(db.Integer, primary_key=True)
    SSN = db.Column(db.String(20))
    Name = db.Column(db.String(100))
    DOB = db.Column(db.Date)
    Sex = db.Column(db.String(10))
    Contact = db.Column(db.String(100))
    Insurance_Provider = db.Column(db.String(100))
    Admitted = db.Column(db.Boolean, default=False)
    Description = db.Column(db.Text)
    Discharged = db.Column(db.Boolean, default=False)
    AdmissionDate = db.Column(db.Date, nullable=True)
    DischargeDate = db.Column(db.Date, nullable=True)

    Room_ID = db.Column(db.Integer, db.ForeignKey("ROOM.Room_ID"))


class Medication(db.Model):
    __tablename__ = "MEDICATION"

    Medication_ID = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(100))
    Dosage = db.Column(db.String(100))
    Patient_ID = db.Column(db.Integer, db.ForeignKey("PATIENT.Patient_ID"))


class Bill(db.Model):
    __tablename__ = "BILL"

    Bill_ID = db.Column(db.Integer, primary_key=True)
    Patient_ID = db.Column(db.Integer)
    Treatment = db.Column(db.Text)
    Total_Amount = db.Column(db.Numeric(12, 2))


class Visit(db.Model):
    __tablename__ = "VISIT"

    Visit_ID = db.Column(db.Integer, primary_key=True)
    Patient_ID = db.Column(db.Integer)
    Doctor_ID = db.Column(db.Integer)
    VisitDate = db.Column(db.Date)
    Notes = db.Column(db.Text)


class Recommendation(db.Model):
    __tablename__ = "RECOMMENDATION"

    Rec_ID = db.Column(db.Integer, primary_key=True)
    Patient_ID = db.Column(db.Integer)
    Text = db.Column(db.Text)


class Schedule(db.Model):
    __tablename__ = "SCHEDULE"

    Schedule_ID = db.Column(db.Integer, primary_key=True)
    Employee_ID = db.Column(db.Integer)
    WorkDate = db.Column(db.Date)
    Shift = db.Column(db.String(50))


class Resource(db.Model):
    __tablename__ = "RESOURCE"

    Resource_ID = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(100))
    Quantity = db.Column(db.Integer)
    Status = db.Column(db.String(50))

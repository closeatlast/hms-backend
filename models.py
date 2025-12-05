from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# --------------------------------------------------
# PATIENT TABLE
# --------------------------------------------------
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

    # NEW FOR STAGE 5
    AdmissionDate = db.Column(db.Date, nullable=True)
    DischargeDate = db.Column(db.Date, nullable=True)


# --------------------------------------------------
# DOCTOR TABLE
# --------------------------------------------------
class Doctor(db.Model):
    __tablename__ = "DOCTOR"

    Doctor_ID = db.Column(db.Integer, primary_key=True)
    Employee_ID = db.Column(db.Integer)
    Name = db.Column(db.String(100))
    Specialty = db.Column(db.String(100))
    Contact = db.Column(db.String(100))


# --------------------------------------------------
# BILL TABLE
# --------------------------------------------------
class Bill(db.Model):
    __tablename__ = "BILL"

    Bill_ID = db.Column(db.Integer, primary_key=True)
    Patient_ID = db.Column(db.Integer)
    Treatment = db.Column(db.Text)
    Total_Amount = db.Column(db.Numeric(12, 2))


# --------------------------------------------------
# VISIT TABLE — (Stage 5: Patient Visits)
# --------------------------------------------------
class Visit(db.Model):
    __tablename__ = "VISIT"

    Visit_ID = db.Column(db.Integer, primary_key=True)
    Patient_ID = db.Column(db.Integer)
    Doctor_ID = db.Column(db.Integer)
    VisitDate = db.Column(db.Date)
    Notes = db.Column(db.Text)


# --------------------------------------------------
# RECOMMENDATIONS — (Stage 5: Personalized Care)
# --------------------------------------------------
class Recommendation(db.Model):
    __tablename__ = "RECOMMENDATION"

    Rec_ID = db.Column(db.Integer, primary_key=True)
    Patient_ID = db.Column(db.Integer)
    Text = db.Column(db.Text)


# --------------------------------------------------
# EMPLOYEE SCHEDULE — (Stage 5: Staff Tools)
# --------------------------------------------------
class Schedule(db.Model):
    __tablename__ = "SCHEDULE"

    Schedule_ID = db.Column(db.Integer, primary_key=True)
    Employee_ID = db.Column(db.Integer)
    WorkDate = db.Column(db.Date)
    Shift = db.Column(db.String(50))


# --------------------------------------------------
# RESOURCE TABLE — (Stage 5: Resource Optimization)
# --------------------------------------------------
class Resource(db.Model):
    __tablename__ = "RESOURCE"

    Resource_ID = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(100))
    Quantity = db.Column(db.Integer)
    Status = db.Column(db.String(50))  # e.g., Available, In Use, Low Stock

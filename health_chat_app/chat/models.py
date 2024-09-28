# chat/models.py

from django.db import models

class Patient(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    date_of_birth = models.DateField()
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()
    medical_condition = models.CharField(max_length=100)
    medication_regimen = models.TextField()
    last_appointment = models.DateTimeField()
    next_appointment = models.DateTimeField()
    doctor_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Message(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    sender = models.CharField(max_length=10)  # 'patient' or 'bot'
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender}: {self.text[:50]}"

class AppointmentChangeRequest(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    requested_time = models.DateTimeField()
    timestamp = models.DateTimeField(auto_now_add=True)
    reviewed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.patient.first_name} requested appointment change to {self.requested_time}"

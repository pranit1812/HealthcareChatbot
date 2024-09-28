# chat/admin.py

from django.contrib import admin
from .models import Patient, Message, AppointmentChangeRequest

admin.site.register(Patient)
admin.site.register(Message)
admin.site.register(AppointmentChangeRequest)

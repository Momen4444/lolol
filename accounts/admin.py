from django.contrib import admin
from . models import *

# Register your models here.
admin.site.register(User)
admin.site.register(Patient)
admin.site.register(Doctor)
admin.site.register(Admin)
admin.site.register(Appointment)
admin.site.register(Report)
admin.site.register(Billing)
admin.site.register(PrescriptionGlasses)
admin.site.register(PasswordResetCode)
from django.utils import timezone
from django.conf import settings
from django.db import connection, models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    USER_TYPE_CHOICES = [
        ('Patient', 'Patient'),
        ('Doctor', 'Doctor'),
        ('Admin', 'Admin'),
    ]
    
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

class Patient(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    address = models.TextField()
    emergency_contact_name = models.CharField(max_length=100)
    emergency_contact_phone = models.CharField(max_length=20)
    general_medical_history = models.TextField(blank=True,default='')
    insurance_provider = models.CharField(max_length=100, blank=True, default='')
    photo = models.URLField(blank=True,default='')

    @staticmethod
    def patients_without_upcoming_appointments():
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT p.user_id, u.first_name, u.last_name
                FROM accounts_patient p
                JOIN auth_user u ON p.user_id = u.id
                WHERE NOT EXISTS (
                    SELECT 1 FROM accounts_appointment a
                    WHERE a.patient_id = p.user_id
                    AND a.appointment_date > %s
                )
            """, [timezone.now()])
            return cursor.fetchall()
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} (Patient)"

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    license_number = models.CharField(max_length=100,)
    specialization = models.CharField(max_length=100,default='General' ,blank=True)
    about = models.TextField(blank=True, default='')
    rating = models.FloatField(default=0.0,editable=False)
    photo = models.URLField(blank=True,default='')
    first_visit = models.FloatField(default=0.0)
    follow_up = models.FloatField(default=0.0)
    education = models.TextField(blank=True, default='')
    experiences = models.TextField(blank=True, default='')

    @staticmethod
    def top_doctors_by_appointments(limit=5):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT d.user_id, u.first_name, u.last_name, COUNT(a.appointment_id) as total_appointments
                FROM accounts_doctor d
                JOIN accounts_appointment a ON d.user_id = a.doctor_id
                JOIN auth_user u ON d.user_id = u.id
                GROUP BY d.user_id, u.first_name, u.last_name
                ORDER BY total_appointments DESC
                LIMIT %s
            """, [limit])
            return cursor.fetchall()


class Admin(models.Model):
    ROLE_CHOICES = [
        ('SuperAdmin', 'Super Admin'),
        ('Manager', 'Manager'),
        ('Staff', 'Staff'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    last_login = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} ({self.role})"

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('Scheduled', 'Scheduled'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
        ('No-show', 'No-show'),
    ]
    
    VISIT_TYPE_CHOICES = [
        ('Routine', 'Routine'),
        ('Follow-up', 'Follow-up'),
    ]
    
    appointment_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    appointment_date = models.DateTimeField()
    duration = models.IntegerField(help_text="Duration in minutes")
    reason = models.TextField(default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Scheduled')
    covered_by_insurance = models.BooleanField(default=False)
    visit_type = models.CharField(max_length=20, choices=VISIT_TYPE_CHOICES, default='Routine')

    @staticmethod
    def appointment_status_summary():
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT status, COUNT(*) as count
                FROM accounts_appointment
                GROUP BY status
            """)
            return dict(cursor.fetchall())
    
    def __str__(self):
        return f"Appointment #{self.appointment_id} - {self.patient} with {self.doctor}"

class PrescriptionGlasses(models.Model):
    TYPE_CHOICES = [
        ('Distance', 'Distance'),
        ('Read', 'Read'),
    ]
    
    prescription_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    left_sphere = models.FloatField()
    left_cylinder = models.FloatField()
    left_axis = models.IntegerField()
    right_sphere = models.FloatField()
    right_cylinder = models.FloatField()
    right_axis = models.IntegerField()
    prescription_date = models.DateField()
    expiration_date = models.DateField()
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Prescription #{self.prescription_id} for {self.patient}"

class Report(models.Model):
    report_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True)
    diagnosis_summary = models.TextField()
    recommendations = models.TextField()
    follow_up_date = models.DateField(blank=True, null=True)

    @staticmethod
    def reports_per_doctor():
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT d.user_id, u.first_name, u.last_name, COUNT(r.report_id) AS total_reports
                FROM accounts_report r
                JOIN accounts_doctor d ON r.doctor_id = d.user_id
                JOIN auth_user u ON d.user_id = u.id
                GROUP BY d.user_id, u.first_name, u.last_name
                ORDER BY total_reports DESC
            """)
            return cursor.fetchall()
    
    def __str__(self):
        return f"Report #{self.report_id} for {self.patient}"

class Billing(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('Cash', 'Cash'),
        ('Credit', 'Credit'),
        ('Insurance', 'Insurance'),
        ('Check', 'Check'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('Paid', 'Paid'),
        ('Pending', 'Pending'),
        ('Denied', 'Denied'),
    ]
    
    billing_id = models.AutoField(primary_key=True)
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    insurance_coverage = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='Pending')
    billing_date = models.DateField()

    @staticmethod
    def total_paid_revenue():
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT SUM(amount)
                FROM accounts_billing
                WHERE payment_status = %s
            """, ['Paid'])
            result = cursor.fetchone()
        return result[0] if result and result[0] is not None else 0.0
    
    def __str__(self):
        return f"Billing #{self.billing_id} - {self.payment_status}"
    
class PasswordResetCode(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
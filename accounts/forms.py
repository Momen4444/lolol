from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Patient, Doctor, Admin, Appointment, PrescriptionGlasses, Report, Billing
from django.core.validators import RegexValidator

class UserForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(
        max_length=20,
        required=False,
        validators=[RegexValidator(r'^\+?\d{7,20}$', message="Enter a valid phone number.")]
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'phone_number', 'password1', 'password2', 'user_type')


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(
        max_length=20,
        required=False,
        validators=[RegexValidator(r'^\+?\d{7,20}$', message="Enter a valid phone number.")]
    )
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone_number')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'password1' in self.fields:
            del self.fields['password1']
        if 'password2' in self.fields:
            del self.fields['password2']

class PatientForm(forms.ModelForm):
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    emergency_contact_phone = forms.CharField(
        max_length=20,
        validators=[RegexValidator(r'^\+?\d{7,20}$', message="Enter a valid emergency contact number.")]
    )

    class Meta:
        model = Patient
        fields = [
            'date_of_birth', 'gender', 'address', 
            'emergency_contact_name', 'emergency_contact_phone',
            'general_medical_history', 'insurance_provider', 'photo'
        ]
        widgets = {
            'general_medical_history': forms.Textarea(attrs={'rows': 3}),
            'address': forms.Textarea(attrs={'rows': 2}),
        }


class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = [
            'license_number', 'specialization', 
            'about', 'photo', 'first_visit', 'follow_up',
            'education', 'experiences'
        ]
        widgets = {
            'about': forms.Textarea(attrs={'rows': 3}),
            'education': forms.Textarea(attrs={'rows': 3}),
            'experiences': forms.Textarea(attrs={'rows': 3}),
        }


class AdminForm(forms.ModelForm):
    class Meta:
        model = Admin
        fields = ['role']


class AppointmentForm(forms.ModelForm):
    appointment_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M']
    )

    class Meta:
        model = Appointment
        fields = [
            'patient', 'doctor', 'appointment_date', 'duration',
            'reason', 'status', 'covered_by_insurance', 'visit_type'
        ]
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 3}),
        }


class PrescriptionGlassesForm(forms.ModelForm):
    prescription_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    expiration_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = PrescriptionGlasses
        fields = [
            'patient', 'doctor', 'type', 'left_sphere', 'left_cylinder',
            'left_axis', 'right_sphere', 'right_cylinder', 'right_axis',
            'prescription_date', 'expiration_date', 'notes'
        ]
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }


class ReportForm(forms.ModelForm):
    follow_up_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )

    class Meta:
        model = Report
        fields = [
            'patient', 'doctor', 'appointment', 'diagnosis_summary',
            'recommendations', 'follow_up_date'
        ]
        widgets = {
            'diagnosis_summary': forms.Textarea(attrs={'rows': 4}),
            'recommendations': forms.Textarea(attrs={'rows': 4}),
        }


class BillingForm(forms.ModelForm):
    billing_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Billing
        fields = [
            'report', 'amount', 'insurance_coverage', 'payment_method',
            'payment_status', 'billing_date'
        ]


# Password Reset 
class EmailForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        }),
        label="Email Address"
    )

class CodeVerificationForm(forms.Form):
    code = forms.CharField(
        max_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter 6-digit code'
        }),
        label="Verification Code"
    )

class PasswordResetForm(forms.Form):
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'New password'
        }),
        label="New Password"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm new password'
        }),
        label="Confirm Password"
    )
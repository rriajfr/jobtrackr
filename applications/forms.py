from django import forms
from .models import Application, Interview, Contact

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = [
            'company', 'role', 'job_link', 'location', 'job_type', 
            'salary', 'date_applied', 'follow_up_date', 'status', 'notes'
        ]
        widgets = {
            'date_applied': forms.DateInput(attrs={'type': 'date'}),
            'follow_up_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = 'form-select'
            else:
                field.widget.attrs['class'] = 'form-control'

class InterviewForm(forms.ModelForm):
    class Meta:
        model = Interview
        fields = ['round_type', 'date_time', 'mode', 'meeting_link', 'notes', 'result']
        widgets = {
            'date_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = 'form-select'
            else:
                field.widget.attrs['class'] = 'form-control'

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'designation', 'email', 'phone', 'linkedin']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
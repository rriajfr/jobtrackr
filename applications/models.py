from django.db import models
from django.contrib.auth.models import User

class Application(models.Model):
    # Define the status choices (Wishlist -> Applied -> Interview -> Offer -> Rejected)
    STATUS_CHOICES = [
        ('wishlist', 'Wishlist'),
        ('applied', 'Applied'),
        ('interview', 'Interview'),
        ('offer', 'Offer'),
        ('rejected', 'Rejected'),
    ]

    # Link this application to the user who created it
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Basic job details
    company = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    job_link = models.URLField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    
    # Job type choices
    JOB_TYPE_CHOICES = [
        ('full_time', 'Full-time'),
        ('internship', 'Internship'),
    ]
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, default='full_time')
    
    salary = models.CharField(max_length=50, blank=True, null=True)
    date_applied = models.DateField()
    follow_up_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='wishlist')
    notes = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company} - {self.role}"


class Interview(models.Model):
    ROUND_CHOICES = [
        ('hr', 'HR Round'),
        ('technical', 'Technical Round'),
        ('managerial', 'Managerial Round'),
    ]
    MODE_CHOICES = [
        ('online', 'Online'),
        ('offline', 'Offline (In-person)'),
    ]
    
    # Link to the Application
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='interviews')
    round_type = models.CharField(max_length=20, choices=ROUND_CHOICES)
    date_time = models.DateTimeField()
    mode = models.CharField(max_length=10, choices=MODE_CHOICES, default='online')
    meeting_link = models.URLField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    result = models.CharField(max_length=50, blank=True, null=True) # e.g., "Cleared", "Rejected"

    def __str__(self):
        return f"{self.get_round_type_display()} - {self.application.company}"

class Contact(models.Model):
    # Link to the Application
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='contacts')
    name = models.CharField(max_length=100)
    designation = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.application.company})"
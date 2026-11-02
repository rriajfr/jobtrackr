from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db.models import Count  # <--- ADD THIS LINE
from django.db.models.functions import TruncMonth # <--- ADD THIS LINE
import json

from .models import Application, Interview, Contact
from .forms import ApplicationForm, InterviewForm, ContactForm

# Dashboard View
@login_required
def dashboard(request):
    user_apps = Application.objects.filter(user=request.user)
    
    total_apps = user_apps.count()
    interviews = user_apps.filter(status='interview').count()
    offers = user_apps.filter(status='offer').count()
    rejections = user_apps.filter(status='rejected').count()

    recent_apps = user_apps.order_by('-created_at')[:5]

    # --- CHART DATA ---
    # 1. Status Breakdown (Doughnut Chart)
    status_counts = user_apps.values('status').annotate(count=Count('id'))
    # Create a dictionary mapping status keys to labels (e.g., 'wishlist': 'Wishlist')
    status_labels_map = dict(Application.STATUS_CHOICES)
    
    status_data = []
    status_labels = []
    for entry in status_counts:
        status_labels.append(status_labels_map.get(entry['status'], entry['status']))
        status_data.append(entry['count'])

    # 2. Applications per Month (Bar Chart)
    monthly_counts = user_apps.annotate(month=TruncMonth('date_applied')).values('month').annotate(count=Count('id')).order_by('month')
    month_labels = []
    month_data = []
    for entry in monthly_counts:
        if entry['month']:
            month_labels.append(entry['month'].strftime('%b %Y'))
            month_data.append(entry['count'])

    context = {
        'total_apps': total_apps,
        'interviews': interviews,
        'offers': offers,
        'rejections': rejections,
        'recent_apps': recent_apps,
        # Convert Python lists to JSON so JavaScript can read them
        'status_labels': json.dumps(status_labels),
        'status_data': json.dumps(status_data),
        'month_labels': json.dumps(month_labels),
        'month_data': json.dumps(month_data),
    }
    return render(request, 'applications/dashboard.html', context)

# Application List View
class ApplicationListView(LoginRequiredMixin, ListView):
    model = Application
    template_name = 'applications/application_list.html'
    context_object_name = 'applications'

    def get_queryset(self):
        # 1. Get only the logged-in user's applications
        queryset = Application.objects.filter(user=self.request.user).order_by('-date_applied')
        
        # 2. Get the search query and status from the URL
        search_query = self.request.GET.get('q')
        status_filter = self.request.GET.get('status')

        # 3. Apply filters if they exist
        if search_query:
            queryset = queryset.filter(company__icontains=search_query) | queryset.filter(role__icontains=search_query)
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset

    def get_context_data(self, **kwargs):
        # Pass the current search/status back to the template so we can keep the form filled
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        context['status_filter'] = self.request.GET.get('status', '')
        return context

# Application Create View
class ApplicationCreateView(LoginRequiredMixin, CreateView):
    model = Application
    form_class = ApplicationForm
    template_name = 'applications/application_form.html'
    success_url = reverse_lazy('application_list')

    # Automatically attach the logged-in user to the new application
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

# Application Update View
class ApplicationUpdateView(LoginRequiredMixin, UpdateView):
    model = Application
    form_class = ApplicationForm
    template_name = 'applications/application_form.html'
    success_url = reverse_lazy('application_list')

    # Security: Ensure users can only edit their OWN applications
    def get_queryset(self):
        return Application.objects.filter(user=self.request.user)

# Application Delete View
class ApplicationDeleteView(LoginRequiredMixin, DeleteView):
    model = Application
    template_name = 'applications/application_confirm_delete.html'
    success_url = reverse_lazy('application_list')

    # Security: Ensure users can only delete their OWN applications
    def get_queryset(self):
        return Application.objects.filter(user=self.request.user)


# --- INTERVIEW VIEWS ---
class InterviewCreateView(LoginRequiredMixin, CreateView):
    model = Interview
    form_class = InterviewForm
    template_name = 'applications/interview_form.html'

    def form_valid(self, form):
        # Get the application ID from the URL
        application = Application.objects.get(id=self.kwargs['app_id'], user=self.request.user)
        form.instance.application = application
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('application_detail', kwargs={'pk': self.kwargs['app_id']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['app'] = Application.objects.get(id=self.kwargs['app_id'])
        return context

# --- CONTACT VIEWS ---
class ContactCreateView(LoginRequiredMixin, CreateView):
    model = Contact
    form_class = ContactForm
    template_name = 'applications/contact_form.html'

    def form_valid(self, form):
        application = Application.objects.get(id=self.kwargs['app_id'], user=self.request.user)
        form.instance.application = application
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('application_detail', kwargs={'pk': self.kwargs['app_id']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['app'] = Application.objects.get(id=self.kwargs['app_id'])
        return context

class ApplicationDetailView(LoginRequiredMixin, DetailView):
    model = Application
    template_name = 'applications/application_detail.html'
    context_object_name = 'app'

    def get_queryset(self):
        # Security: Users can only view their own applications
        return Application.objects.filter(user=self.request.user)

from django.views.generic import DetailView

class ApplicationDetailView(LoginRequiredMixin, DetailView):
    model = Application
    template_name = 'applications/application_detail.html'
    context_object_name = 'app'

    def get_queryset(self):
        # Security: Users can only view their own applications
        return Application.objects.filter(user=self.request.user)


# 1. The View that shows the Kanban Board
@login_required
def kanban_board(request):
    applications = Application.objects.filter(user=request.user)
    return render(request, 'applications/kanban.html', {'applications': applications})

# 2. The AJAX Endpoint that updates the status when you drop a card
@login_required
def update_status_ajax(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        app_id = data.get('app_id')
        new_status = data.get('status')

        try:
            # Security: Make sure the user owns this application
            application = Application.objects.get(id=app_id, user=request.user)
            application.status = new_status
            application.save()
            return JsonResponse({'success': True})
        except Application.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Application not found'}, status=404)
            
    return JsonResponse({'success': False}, status=400)
@login_required
def skill_matcher(request):
    result = None
    job_desc = ""
    
    # Check if the form was submitted
    if request.method == 'POST':
        job_desc = request.POST.get('job_description', '').lower()
        
        # Only process if there is actual text
        if job_desc.strip():
            my_skills = ['python', 'django', 'html', 'css', 'javascript', 'react', 'sql', 'git', 'bootstrap']
            
            found = []
            missing = []
            
            for skill in my_skills:
                if skill in job_desc:
                    found.append(skill.title())
                else:
                    missing.append(skill.title())
                    
            score = 0
            if len(found) > 0:
                score = int((len(found) / len(my_skills)) * 100)

            result = {
                'score': score,
                'found': ', '.join(found) if found else "None",
                'missing': ', '.join(missing) if missing else "None"
            }

    return render(request, 'applications/matcher.html', {'result': result, 'job_desc': job_desc})
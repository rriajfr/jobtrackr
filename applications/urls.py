from django.urls import path
from . import views  # <--- This belongs here

urlpatterns = [
    path('list/', views.ApplicationListView.as_view(), name='application_list'),
    path('add/', views.ApplicationCreateView.as_view(), name='application_add'),
    path('edit/<int:pk>/', views.ApplicationUpdateView.as_view(), name='application_edit'),
    path('delete/<int:pk>/', views.ApplicationDeleteView.as_view(), name='application_delete'),
    path('<int:pk>/', views.ApplicationDetailView.as_view(), name='application_detail'),
    path('<int:app_id>/interview/add/', views.InterviewCreateView.as_view(), name='interview_add'),
    path('<int:app_id>/contact/add/', views.ContactCreateView.as_view(), name='contact_add'),
    path('kanban/', views.kanban_board, name='kanban_board'),
    path('update-status/', views.update_status_ajax, name='update_status_ajax'),
    path('skill-matcher/', views.skill_matcher, name='skill_matcher'), # <--- Make sure this is here
]
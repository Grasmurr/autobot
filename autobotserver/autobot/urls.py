from django.urls import path
from . import views
from .views import ApplicantsView

urlpatterns = [
    path('applicant/', views.ApplicantsView.as_view(), name='create_applicant'),
    path('urls/<int:user_id>/', views.ApplicantUpdateView.as_view(), name='update_applicant_data'),

    path('applicants/', views.ApplicantsView.as_view(), name='get_all_applicants'),
    path('get_applicant/<int:user_id>/', views.ApplicantsView.as_view(), name='get_applicant')
    ]
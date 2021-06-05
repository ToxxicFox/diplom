from django.urls import path
from . import views


urlpatterns = [
    path('register/',
            views.StudentRegistrationView.as_view(),
            name='student_registration'),
    path('enroll-internship/',
            views.StudentEnrollInternshipView.as_view(),
            name='student_enroll_internship'),
    path('internships/',
             views.StudentInternshipListView.as_view(),
             name='student_internship_list'),
    path('internship/<pk>/',
             views.StudentInternshipDetailView.as_view(),
             name='student_internship_detail'),
    path('internship/<pk>/<module_id>/',
             views.StudentInternshipDetailView.as_view(),
             name='student_internship_detail_module'),
]

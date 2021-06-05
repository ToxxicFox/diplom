from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import InternshipEnrollForm
from django.views.generic.list import ListView
from internship.models import Internship
from django.views.generic.detail import DetailView


class StudentRegistrationView(CreateView):
    template_name = 'students/student/registration.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('student_internship_list')

    def form_valid(self, form):
        result = super(StudentRegistrationView, self).form_valid(form)
        cd = form.cleaned_data
        user = authenticate(username=cd['username'],
                            password=cd['password1'])
        login(self.request, user)
        return result


class StudentEnrollInternshipView(LoginRequiredMixin, FormView):
    internship = None
    form_class = InternshipEnrollForm

    def form_valid(self, form):
        self.internship = form.cleaned_data['internship']
        self.internship.students.add(self.request.user)
        return super(StudentEnrollInternshipView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('student_internship_detail', args=[self.internship.id])


class StudentInternshipListView(LoginRequiredMixin, ListView):
    model = Internship
    template_name = 'students/internship/list.html'

    def get_queryset(self):
        qs = super(StudentInternshipListView, self).get_queryset()
        return qs.filter(students__in=[self.request.user])


class StudentInternshipDetailView(DetailView):
    model = Internship
    template_name = 'students/internship/detail.html'

    def get_queryset(self):
        qs = super(StudentInternshipDetailView, self).get_queryset()
        return qs.filter(students__in=[self.request.user])

    def get_context_data(self, **kwargs):
        context = super(StudentInternshipDetailView, self).get_context_data()
        internship = self.get_object()
        if 'module_id' in self.kwargs:
            context['module'] = internship.modules.get(id=self.kwargs['module_id'])
        else:
            context['module'] = internship.modules.all()[0]
        return context
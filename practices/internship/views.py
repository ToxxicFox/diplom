#from practices import internship
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.views.generic.base import TemplateResponseMixin, View
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.forms.models import modelform_factory
from django.apps import apps
from braces.views import CsrfExemptMixin, JsonRequestResponseMixin
from django.db.models import Count
from django.views.generic.detail import DetailView

from students.forms import InternshipEnrollForm

from .models import Module, Content
from .models import Internship
from .models import Area
from .forms import ModuleFormSet


class OwnerMixin(object):
    def get_queryset(self):
        qs = super(OwnerMixin, self).get_queryset()
        return qs.filter(owner=self.request.user)


class OwnerEditMixin(object):
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super(OwnerEditMixin, self).form_valid(form)


class OwnerInternshipMixin(OwnerMixin, LoginRequiredMixin):
    model = Internship
    fields = ['area', 'title', 'slug', 'overview']
    success_url = reverse_lazy('manage_internship_list')


class OwnerInternshipEditMixin(OwnerInternshipMixin, OwnerEditMixin):
    fields = ['area', 'title', 'slug', 'overview']
    success_url = reverse_lazy('manage_internship_list')
    template_name = 'internships/manage/internship/form.html'


class ManageInternshipListView(OwnerInternshipMixin, ListView):
    template_name = 'internships/manage/internship/list.html'


class InternshipCreateView(PermissionRequiredMixin, 
                            OwnerInternshipEditMixin, 
                            CreateView):
    permission_required = 'internship.add_internship'


class InternshipUpdateView(PermissionRequiredMixin, 
                            OwnerInternshipEditMixin, 
                            UpdateView):
    permission_required = 'internship.change_internship'


class InternshipDeleteView(PermissionRequiredMixin, 
                            OwnerInternshipMixin, 
                            DeleteView):
    template_name = 'internships/manage/internship/delete.html'
    success_url = reverse_lazy('manage_internship_list')
    permission_required = 'internship.delete_internship'


class InternshipModuleUpdateView(TemplateResponseMixin, View):
    template_name = 'internships/manage/module/formset.html'
    internship = None

    def get_formset(self, data=None):
        return ModuleFormSet(instance=self.internship, data=data)

    def dispatch(self, request, pk):
        self.internship = get_object_or_404(Internship,
                                                id=pk,
                                                owner=request.user)
        return super(InternshipModuleUpdateView, self).dispatch(request, pk)

    def get(self, request, *args, **kwargs):
        formset = self.get_formset()
        return self.render_to_response({'internship': self.internship, 'formset': formset})

    def post(self, request, *args, **kwargs):
        formset = self.get_formset(data=request.POST)
        if formset.is_valid():
            formset.save()
            return redirect('manage_internship_list')
        return self.render_to_response({'internship': self.internship, 'formset': formset})


class ContentCreateUpdateView(TemplateResponseMixin, View):
    module = None
    model = None
    obj = None
    template_name = 'internships/manage/content/form.html'

    def get_model(self, model_name):
        if model_name in ['text', 'video', 'image', 'file']:
            return apps.get_model(app_label='internship', model_name=model_name)
            return None

    def get_form(self, model, *args, **kwargs):
        Form = modelform_factory(model, exclude=['owner',
                                                 'order',
                                                 'created',
                                                 'updated'])
        return Form(*args, **kwargs)

    def dispatch(self, request, module_id, model_name, id=None):
        self.module = get_object_or_404(Module, 
                                        id=module_id,
                                        internship__owner=request.user)
        self.model = self.get_model(model_name)
        if id:
            self.obj = get_object_or_404(self.model,
                                         id=id,
                                         owner=request.user)
        return super(ContentCreateUpdateView, self).dispatch(request, module_id, model_name, id)

    def get(self, request, module_id, model_name, id=None):
        form = self.get_form(self.model, instance=self.obj)
        return self.render_to_response({'form': form, 'object': self.obj})

    def post(self, request, module_id, model_name, id=None):
        form = self.get_form(self.model, instance=self.obj, data=request.POST, files=request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.save()
            if not id:
                #Создаем новый объект
                Content.objects.create(module=self.module, item=obj)
            return redirect('module_content_list', self.module.id)
        return self.render_to_response({'form': form, 'object': self.obj})


class ContentDeleteView(View):

    def post(self, request, id):
        content = get_object_or_404(Content,
                                    id=id,
                                    module__internship__owner=request.user)
        module = content.module
        content.item.delete()
        content.delete()
        return redirect('module_content_list', module.id)


class ModuleContentListView(TemplateResponseMixin, View):
    template_name = 'internships/manage/module/content_list.html'

    def get(self, request, module_id):
        module = get_object_or_404(Module,
                                    id=module_id,
                                    internship__owner=request.user)
        return self.render_to_response({'module': module})


class ModuleOrderView(CsrfExemptMixin, JsonRequestResponseMixin, View):
    def post(self, request):
        for id, order in self.request_json.items():
            Module.objects.filter(id=id,
                        internship__owner=request.user).update(order=order)
        return self.render_json_response({'saved': 'OK'})


class ContentOrderView(CsrfExemptMixin, JsonRequestResponseMixin, View):
    def post(self, request):
        for id, order in self.request_json.items():
            Content.objects.filter(id=id,
                    module__internship__owner=request.user).update(order=order)
        return self.render_json_response({'saved': 'OK'})


class InternshipListView(TemplateResponseMixin, View):
    model = Internship
    template_name = 'internships/internship/list.html'

    def get(self, request, area=None):
        areas = Area.objects.annotate(
            total_internships=Count('internships')
        )
        internships = Internship.objects.annotate(total_modules=Count('modules'))
        if area:
            area = get_object_or_404(Area, slug=area)
            internships = internships.filter(area=area)
        return self.render_to_response({'areas': areas,
                                        'area': area,
                                        'internships': internships})


class InternshipDetailView(DetailView):
    model = Internship
    template_name = 'internships/internship/detail.html'

    def get_context_data(self, **kwargs):
        context = super(InternshipDetailView, self).get_context_data(**kwargs)
        context['enroll_form'] = InternshipEnrollForm(
            initial={'internship': self.object})
        return context
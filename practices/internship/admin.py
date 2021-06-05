from django.contrib import admin
from .models import Area, Internship, Module


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug']
    prepopulated_fields = {'slug': ('title',)}


class ModelInline(admin.StackedInline):
    model = Module


@admin.register(Internship)
class InternshipAdmin(admin.ModelAdmin):
    list_display = ['title', 'area', 'created']
    list_filter = ['created', 'area']
    search_fields = ['title', 'overview']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ModelInline]
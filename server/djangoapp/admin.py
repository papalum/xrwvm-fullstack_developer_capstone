from django.contrib import admin
from .models import CarMake, CarModel

# CarModelInline class to allow inline editing of CarModels in CarMakeAdmin
class CarModelInline(admin.TabularInline):  # or admin.StackedInline for a different layout
    model = CarModel
    extra = 1  # Number of empty CarModel forms to display

# CarMakeAdmin class with CarModelInline
class CarMakeAdmin(admin.ModelAdmin):
    inlines = [CarModelInline]
    list_display = ('name', 'description')  # Optional: improve list view
    search_fields = ['name']  # Optional: add search capability

# CarModelAdmin class for individual CarModel admin
class CarModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'car_make', 'type', 'year')
    list_filter = ('type', 'year', 'car_make')
    search_fields = ['name']

# Register models here
admin.site.register(CarMake, CarMakeAdmin)
admin.site.register(CarModel, CarModelAdmin)

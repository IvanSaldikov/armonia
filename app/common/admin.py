from django.contrib import admin


@admin.action(description="Duplicate selected record")
def duplicate_action(modeladmin, request, queryset):
    for object in queryset:
        object.id = None
        object.save()

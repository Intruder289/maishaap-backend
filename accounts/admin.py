from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.admin.sites import NotRegistered

# If another app (or Django itself) already registered Group, unregister it first
# This prevents "AlreadyRegistered: The model Group is already registered" errors
try:
	admin.site.unregister(Group)
except NotRegistered:
	pass


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
	search_fields = ('name',)
	filter_horizontal = ('permissions',)
	list_display = ('name',)

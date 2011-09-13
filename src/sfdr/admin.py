"""
Created on 13. juni 2011

@author: "Christoffer Viken"
"""
from django.contrib import admin
from sfdr.models import Service

class ServiceAdmin(admin.ModelAdmin):
    pass

admin.site.register(Service, ServiceAdmin)

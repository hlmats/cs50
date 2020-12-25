from django.contrib import admin
from .models import User, Hotels, Reservations, Comments

# Register your models here.
admin.site.register(User)
admin.site.register(Hotels)
admin.site.register(Reservations)
admin.site.register(Comments)

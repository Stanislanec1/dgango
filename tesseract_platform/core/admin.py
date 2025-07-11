from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Document, UserToDocument, Price, Cart

admin.site.register(Document)
admin.site.register(UserToDocument)
admin.site.register(Price)
admin.site.register(Cart)

from django.contrib import admin

from .models import Post, Tag 

admin.site.register(Post)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

# Register your models here.

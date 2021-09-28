from django.contrib import admin
from .models import Post, Comments


class PostAdmin(admin.ModelAdmin):
    prepopulated_fields = {'url': ('title',)}


admin.site.register(Post, PostAdmin)


class CommentAdmin(admin.ModelAdmin):
    list_display = ('username', 'post', 'text', 'created_date')
    list_filter = ('username', 'created_date')
    search_fields = ('username', 'text')


admin.site.register(Comments, CommentAdmin)

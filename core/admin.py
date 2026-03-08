from django.contrib import admin
from .models import Category, Document, Comment, Notification


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'document_count', 'created_at']
    search_fields = ['name']

    def document_count(self, obj):
        return obj.document_set.count()
    document_count.short_description = 'Documents'


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display  = ['title', 'uploader', 'category', 'uploaded_at', 'download_count', 'is_active']
    list_filter   = ['is_active', 'category', 'uploaded_at']
    search_fields = ['title', 'uploader__username']
    actions       = ['remove_and_notify']

    def remove_and_notify(self, request, queryset):
        count = 0
        for doc in queryset:
            Notification.objects.create(
                recipient=doc.uploader,
                notification_type='removal',
                message=f'Your document "{doc.title}" was removed by an administrator.',
            )
            doc.delete()
            count += 1
        self.message_user(request, f'{count} document(s) removed. Uploaders notified.')
    remove_and_notify.short_description = 'Remove selected & notify uploaders'

    def delete_model(self, request, obj):
        Notification.objects.create(
            recipient=obj.uploader,
            notification_type='removal',
            message=f'Your document "{obj.title}" was removed by an administrator.',
        )
        super().delete_model(request, obj)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display  = ['author', 'document', 'created_at']
    search_fields = ['author__username', 'content']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'notification_type', 'is_read', 'created_at']
    list_filter  = ['notification_type', 'is_read']


admin.site.site_header = '📚 KnowledgeShare Admin'
admin.site.site_title  = 'KnowledgeShare'
admin.site.index_title = 'Platform Administration'

from django.db import models
from django.contrib.auth.models import User
import os


class Category(models.Model):
    name        = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon        = models.CharField(max_length=10, default='📁')
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def document_count(self):
        return self.document_set.count()


class Document(models.Model):
    title          = models.CharField(max_length=200)
    description    = models.TextField()
    file           = models.FileField(upload_to='documents/%Y/%m/')
    category       = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    uploader       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    uploaded_at    = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)
    download_count = models.PositiveIntegerField(default=0)
    is_active      = models.BooleanField(default=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.title

    def get_file_extension(self):
        _, ext = os.path.splitext(self.file.name)
        return ext.lower().strip('.')

    def get_file_size(self):
        try:
            size = self.file.size
            if size < 1024:
                return f"{size} B"
            elif size < 1024 * 1024:
                return f"{size/1024:.1f} KB"
            else:
                return f"{size/(1024*1024):.1f} MB"
        except Exception:
            return "N/A"

    def get_file_icon(self):
        icons = {
            'pdf': '📄', 'doc': '📝', 'docx': '📝',
            'xls': '📊', 'xlsx': '📊', 'ppt': '📊',
            'pptx': '📊', 'txt': '📃',
        }
        return icons.get(self.get_file_extension(), '📎')

    def comment_count(self):
        return self.comments.count()


class Comment(models.Model):
    document   = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='comments')
    author     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content    = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.author.username} on {self.document.title}"


class Notification(models.Model):
    TYPE_CHOICES = [
        ('comment', 'New Comment'),
        ('removal', 'Document Removed'),
        ('system',  'System'),
    ]
    recipient         = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='system')
    message           = models.TextField()
    is_read           = models.BooleanField(default=False)
    created_at        = models.DateTimeField(auto_now_add=True)
    document          = models.ForeignKey(Document, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"To {self.recipient.username}: {self.message[:40]}"

    def get_icon(self):
        return {'comment': '💬', 'removal': '🗑️', 'system': 'ℹ️'}.get(self.notification_type, 'ℹ️')

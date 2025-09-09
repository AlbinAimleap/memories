from django.db import models
from django.contrib.auth import get_user_model
from accounts.models import Child
import uuid

User = get_user_model()

class BedtimeStory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='bedtime_stories')
    title = models.CharField(max_length=200)
    story_content = models.TextField()
    prompt_used = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    is_favorite = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} for {self.child.name}"

class AITask(models.Model):
    TASK_TYPES = [
        ('caption', 'Photo Caption'),
        ('bedtime_story', 'Bedtime Story'),
        ('transcription', 'Audio Transcription'),
        ('year_review', 'Year in Review'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task_type = models.CharField(max_length=20, choices=TASK_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    input_data = models.JSONField(default=dict)
    output_data = models.JSONField(default=dict)
    error_message = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_task_type_display()} - {self.status}"
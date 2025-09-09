from django.db import models
from django.contrib.auth import get_user_model
from accounts.models import Child
from memories.models import Memory
import uuid

User = get_user_model()

class Album(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='albums')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    cover_memory = models.ForeignKey(Memory, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    is_private = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.child.name}"
    
    @property
    def memory_count(self):
        return self.memories.count()

class AlbumMemory(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='album_memories')
    memory = models.ForeignKey(Memory, on_delete=models.CASCADE, related_name='albums')
    order = models.IntegerField(default=0)
    added_at = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ['album', 'memory']
        ordering = ['order', 'added_at']
    
    def __str__(self):
        return f"{self.memory.title} in {self.album.title}"
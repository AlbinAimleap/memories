from django.db import models
from django.contrib.auth import get_user_model
from accounts.models import Child
from PIL import Image
import uuid

User = get_user_model()

class Memory(models.Model):
    MEMORY_TYPES = [
        ('photo', 'Photo'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('text', 'Text Note'),
        ('drawing', 'Drawing'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='memories')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_memories')
    
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    memory_type = models.CharField(max_length=10, choices=MEMORY_TYPES, default='text')
    
    # Media files
    image = models.ImageField(upload_to='memories/images/', blank=True, null=True)
    video = models.FileField(upload_to='memories/videos/', blank=True, null=True)
    audio = models.FileField(upload_to='memories/audio/', blank=True, null=True)
    
    # Thumbnails (auto-generated)
    thumbnail = models.ImageField(upload_to='memories/thumbnails/', blank=True, null=True)
    
    # Metadata
    memory_date = models.DateTimeField(help_text="When this memory happened")
    tags = models.CharField(max_length=500, blank=True, help_text="Comma-separated tags")
    location = models.CharField(max_length=200, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    
    # AI Features
    ai_caption = models.TextField(blank=True, help_text="AI-generated caption")
    transcription = models.TextField(blank=True, help_text="Audio transcription")
    
    # System fields
    is_milestone = models.BooleanField(default=False)
    is_private = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-memory_date', '-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.child.name}"
    
    def get_tags_list(self):
        """Return tags as a list"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',')]
        return []
    
    def save(self, *args, **kwargs):
        # Generate thumbnail for images
        if self.image and not self.thumbnail:
            self.create_thumbnail()
        super().save(*args, **kwargs)
    
    def create_thumbnail(self):
        """Create thumbnail for image"""
        if not self.image:
            return
        
        try:
            image = Image.open(self.image)
            image.thumbnail((300, 300), Image.Resampling.LANCZOS)
            
            # Save thumbnail
            thumb_filename = f"thumb_{self.image.name.split('/')[-1]}"
            thumb_path = f"memories/thumbnails/{thumb_filename}"
            
            # TODO: Save thumbnail to storage
            # This would need proper file handling for production
            
        except Exception as e:
            print(f"Error creating thumbnail: {e}")

class MemoryReaction(models.Model):
    REACTIONS = [
        ('❤️', 'Love'),
        ('😍', 'Adore'),
        ('😊', 'Happy'),
        ('🤗', 'Hugs'),
        ('👏', 'Clap'),
        ('🎉', 'Celebrate'),
        ('😢', 'Emotional'),
        ('🥰', 'Cute'),
    ]
    
    memory = models.ForeignKey(Memory, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reaction = models.CharField(max_length=10, choices=REACTIONS)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['memory', 'user', 'reaction']
    
    def __str__(self):
        return f"{self.user.username} reacted {self.reaction} to {self.memory.title}"

class MemoryComment(models.Model):
    memory = models.ForeignKey(Memory, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.user.username} on {self.memory.title}"
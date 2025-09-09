from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('family', 'Family Member'),
        ('child', 'Child'),
    ]
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='family')
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.username
    
    @property
    def is_owner(self):
        return self.role == 'owner'
    
    @property
    def is_family_member(self):
        return self.role == 'family'
    
    @property
    def is_child(self):
        return self.role == 'child'

class Child(models.Model):
    name = models.CharField(max_length=100)
    birth_date = models.DateField()
    birth_time = models.TimeField(blank=True, null=True)
    birth_location = models.CharField(max_length=200, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_children')
    family_members = models.ManyToManyField(User, related_name='children', blank=True)
    child_user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='child_profile')
    avatar = models.ImageField(upload_to='child_avatars/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    @property
    def age_in_years(self):
        """Calculate age in years"""
        today = timezone.now().date()
        return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
    
    @property
    def age_in_months(self):
        """Calculate age in months"""
        today = timezone.now().date()
        return (today.year - self.birth_date.year) * 12 + today.month - self.birth_date.month
    
    @property
    def age_in_days(self):
        """Calculate age in days"""
        today = timezone.now().date()
        return (today - self.birth_date).days
    
    def get_unlocked_features(self):
        """Return list of unlocked features based on age"""
        age = self.age_in_years
        features = ['memories', 'basic_milestones']
        
        if age >= 1:
            features.extend(['milestones', 'growth_chart', 'ai_captions'])
        if age >= 2:
            features.append('memory_map')
        if age >= 3:
            features.append('bedtime_stories')
        if age >= 5:
            features.extend(['voice_notes', 'drawings'])
        if age >= 13:
            features.extend(['guestbook', 'journaling'])
        if age >= 18:
            features.extend(['ownership_transfer', 'full_export'])
            
        return features
    
    def has_feature(self, feature_name):
        """Check if a specific feature is unlocked"""
        return feature_name in self.get_unlocked_features()

class Invitation(models.Model):
    email = models.EmailField()
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='invitations')
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=User.ROLE_CHOICES, default='family')
    token = models.CharField(max_length=100, unique=True)
    is_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    def __str__(self):
        return f"Invitation to {self.email} for {self.child.name}"
    
    @property
    def is_expired(self):
        return timezone.now() > self.expires_at
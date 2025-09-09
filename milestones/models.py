from django.db import models
from accounts.models import Child
from django.contrib.auth import get_user_model

User = get_user_model()

class MilestoneCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=7, default='#3B82F6')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class PredefinedMilestone(models.Model):
    category = models.ForeignKey(MilestoneCategory, on_delete=models.CASCADE, related_name='milestones')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    typical_age_months_min = models.IntegerField(help_text="Minimum typical age in months")
    typical_age_months_max = models.IntegerField(help_text="Maximum typical age in months")
    is_major = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'typical_age_months_min']
    
    def __str__(self):
        return self.title

class ChildMilestone(models.Model):
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='milestones')
    predefined_milestone = models.ForeignKey(PredefinedMilestone, on_delete=models.CASCADE, blank=True, null=True)
    custom_title = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    achieved_date = models.DateTimeField()
    age_at_achievement = models.CharField(max_length=50, blank=True)  # e.g., "6 months, 2 weeks"
    recorded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    notes = models.TextField(blank=True)
    photo = models.ImageField(upload_to='milestones/', blank=True, null=True)
    is_custom = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['achieved_date']
    
    def __str__(self):
        title = self.custom_title if self.is_custom else self.predefined_milestone.title
        return f"{self.child.name}: {title}"
    
    @property
    def title(self):
        return self.custom_title if self.is_custom else self.predefined_milestone.title

class GrowthRecord(models.Model):
    MEASUREMENT_TYPES = [
        ('height', 'Height'),
        ('weight', 'Weight'),
        ('head_circumference', 'Head Circumference'),
    ]
    
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='growth_records')
    measurement_type = models.CharField(max_length=20, choices=MEASUREMENT_TYPES)
    value = models.DecimalField(max_digits=6, decimal_places=2)  # in cm for height, kg for weight
    measurement_date = models.DateTimeField()
    age_at_measurement = models.CharField(max_length=50, blank=True)
    recorded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['measurement_date']
        unique_together = ['child', 'measurement_type', 'measurement_date']
    
    def __str__(self):
        return f"{self.child.name}: {self.measurement_type} - {self.value}"
from django import forms
from accounts.models import Child

class BedtimeStoryForm(forms.Form):
    THEME_CHOICES = [
        ('adventure', 'Adventure'),
        ('friendship', 'Friendship'),
        ('animals', 'Animals'),
        ('magic', 'Magic & Fantasy'),
        ('family', 'Family'),
        ('learning', 'Learning & Education'),
        ('bedtime', 'Sleepy & Calming'),
    ]
    
    LENGTH_CHOICES = [
        ('short', 'Short (2-3 minutes)'),
        ('medium', 'Medium (5-7 minutes)'),
        ('long', 'Long (10+ minutes)'),
    ]
    
    child = forms.ModelChoiceField(queryset=Child.objects.none())
    theme = forms.ChoiceField(choices=THEME_CHOICES, required=False)
    story_length = forms.ChoiceField(choices=LENGTH_CHOICES, initial='medium')
    story_prompt = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 4,
            'placeholder': 'Describe what you want the story to be about...'
        }),
        help_text="Describe characters, setting, or specific elements you'd like in the story"
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            if user.is_owner:
                children = Child.objects.filter(owner=user)
            else:
                children = user.children.all()
            
            # Only show children who have bedtime stories unlocked
            unlocked_children = [child for child in children if child.has_feature('bedtime_stories')]
            self.fields['child'].queryset = Child.objects.filter(id__in=[c.id for c in unlocked_children])
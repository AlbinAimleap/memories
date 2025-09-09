from django import forms
from .models import Memory, MemoryComment
from accounts.models import Child

class MemoryForm(forms.ModelForm):
    class Meta:
        model = Memory
        fields = [
            'child', 'title', 'content', 'memory_type', 'memory_date',
            'image', 'video', 'audio', 'tags', 'location', 'is_milestone', 'is_private'
        ]
        widgets = {
            'memory_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'content': forms.Textarea(attrs={'rows': 4}),
            'tags': forms.TextInput(attrs={'placeholder': 'birthday, first steps, cute'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            if user.is_owner:
                self.fields['child'].queryset = Child.objects.filter(owner=user)
            else:
                self.fields['child'].queryset = user.children.all()

class MemoryCommentForm(forms.ModelForm):
    class Meta:
        model = MemoryComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Add a comment...'})
        }
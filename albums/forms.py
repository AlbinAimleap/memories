from django import forms
from .models import Album
from accounts.models import Child
from memories.models import Memory

class AlbumForm(forms.ModelForm):
    class Meta:
        model = Album
        fields = ['child', 'title', 'description', 'is_private']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            if user.is_owner:
                self.fields['child'].queryset = Child.objects.filter(owner=user)
            else:
                self.fields['child'].queryset = user.children.all()

class AddMemoriesToAlbumForm(forms.Form):
    memories = forms.ModelMultipleChoiceField(
        queryset=Memory.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    
    def __init__(self, *args, **kwargs):
        available_memories = kwargs.pop('available_memories', Memory.objects.none())
        super().__init__(*args, **kwargs)
        self.fields['memories'].queryset = available_memories
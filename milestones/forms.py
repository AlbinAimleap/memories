from django import forms
from .models import ChildMilestone, GrowthRecord
from accounts.models import Child

class ChildMilestoneForm(forms.ModelForm):
    class Meta:
        model = ChildMilestone
        fields = [
            'child', 'predefined_milestone', 'custom_title', 'description', 
            'achieved_date', 'notes', 'photo'
        ]
        widgets = {
            'achieved_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            if user.is_owner:
                self.fields['child'].queryset = Child.objects.filter(owner=user)
            else:
                self.fields['child'].queryset = user.children.all()
        
        # Make predefined_milestone optional when custom_title is provided
        self.fields['predefined_milestone'].required = False
        self.fields['custom_title'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        predefined_milestone = cleaned_data.get('predefined_milestone')
        custom_title = cleaned_data.get('custom_title')
        
        if not predefined_milestone and not custom_title:
            raise forms.ValidationError(
                "Either select a predefined milestone or provide a custom title."
            )
        
        if custom_title:
            cleaned_data['is_custom'] = True
        
        return cleaned_data

class GrowthRecordForm(forms.ModelForm):
    class Meta:
        model = GrowthRecord
        fields = ['child', 'measurement_type', 'value', 'measurement_date', 'notes']
        widgets = {
            'measurement_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            if user.is_owner:
                self.fields['child'].queryset = Child.objects.filter(owner=user)
            else:
                self.fields['child'].queryset = user.children.all()
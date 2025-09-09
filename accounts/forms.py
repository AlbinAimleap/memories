from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from .models import User, Child, Invitation

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
    
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if username and password:
            self.user = authenticate(username=username, password=password)
            if not self.user:
                raise forms.ValidationError('Invalid username or password.')
        return self.cleaned_data
    
    def get_user(self):
        return self.user

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'avatar', 'birth_date']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }

class ChildForm(forms.ModelForm):
    class Meta:
        model = Child
        fields = ['name', 'birth_date', 'birth_time', 'birth_location', 'avatar']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'birth_time': forms.TimeInput(attrs={'type': 'time'}),
        }

class InviteForm(forms.ModelForm):
    class Meta:
        model = Invitation
        fields = ['email', 'child', 'role']
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['child'].queryset = Child.objects.filter(owner=user)
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.utils import timezone
from datetime import timedelta
import secrets

from .models import User, Child, Invitation
from .forms import CustomUserCreationForm, LoginForm, ProfileForm, InviteForm, ChildForm

class LoginView(TemplateView):
    template_name = 'accounts/login.html'
    
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('core:dashboard')
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = LoginForm()
        return context
    
    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('core:dashboard')
        return render(request, self.template_name, {'form': form})

class LogoutView(LoginRequiredMixin, TemplateView):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('accounts:login')

class RegisterView(TemplateView):
    template_name = 'accounts/register.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_form'] = CustomUserCreationForm()
        context['child_form'] = ChildForm()
        return context
    
    def post(self, request):
        user_form = CustomUserCreationForm(request.POST, request.FILES)
        child_form = ChildForm(request.POST, request.FILES)
        
        if user_form.is_valid() and child_form.is_valid():
            user = user_form.save(commit=False)
            user.role = 'owner'
            user.save()
            
            child = child_form.save(commit=False)
            child.owner = user
            child.save()
            
            login(request, user)
            messages.success(request, f"Welcome! {child.name}'s memory album has been created.")
            return redirect('core:dashboard')
        
        return render(request, self.template_name, {
            'user_form': user_form,
            'child_form': child_form
        })

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ProfileForm(instance=self.request.user)
        return context
    
    def post(self, request):
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('accounts:profile')
        return render(request, self.template_name, {'form': form})

class InviteView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/invite.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = InviteForm()
        context['children'] = Child.objects.filter(owner=self.request.user)
        return context
    
    def post(self, request):
        form = InviteForm(request.POST)
        if form.is_valid():
            invitation = form.save(commit=False)
            invitation.invited_by = request.user
            invitation.token = secrets.token_urlsafe(32)
            invitation.expires_at = timezone.now() + timedelta(days=7)
            invitation.save()
            
            # TODO: Send email with invitation link
            messages.success(request, f"Invitation sent to {invitation.email}")
            return redirect('accounts:invite')
        
        return render(request, self.template_name, {'form': form})

class AcceptInviteView(TemplateView):
    template_name = 'accounts/accept_invite.html'
    
    def get(self, request, token):
        invitation = get_object_or_404(Invitation, token=token)
        
        if invitation.is_expired:
            messages.error(request, "This invitation has expired.")
            return redirect('accounts:login')
        
        if invitation.is_accepted:
            messages.info(request, "This invitation has already been used.")
            return redirect('accounts:login')
        
        return render(request, self.template_name, {'invitation': invitation})
    
    def post(self, request, token):
        invitation = get_object_or_404(Invitation, token=token)
        
        if invitation.is_expired or invitation.is_accepted:
            return redirect('accounts:login')
        
        # Create user account or link existing account
        user, created = User.objects.get_or_create(
            email=invitation.email,
            defaults={
                'username': invitation.email.split('@')[0],
                'role': invitation.role,
                'is_verified': True
            }
        )
        
        # Add user to child's family members
        invitation.child.family_members.add(user)
        invitation.is_accepted = True
        invitation.save()
        
        login(request, user)
        messages.success(request, f"Welcome to {invitation.child.name}'s memory album!")
        return redirect('core:dashboard')
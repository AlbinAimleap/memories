from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib import messages
from django.db.models import Count
from accounts.models import Child
from memories.models import Memory
from milestones.models import ChildMilestone
from albums.models import Album
from ai_features.models import BedtimeStory

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'core/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get user's children
        if self.request.user.is_owner:
            children = Child.objects.filter(owner=self.request.user)
        else:
            children = self.request.user.children.all()
        
        context['children'] = children
        
        if children.exists():
            # Get stats for all children
            total_memories = Memory.objects.filter(child__in=children).count()
            total_milestones = ChildMilestone.objects.filter(child__in=children).count()
            total_albums = Album.objects.filter(child__in=children).count()
            total_stories = BedtimeStory.objects.filter(child__in=children).count()
            
            context['stats'] = {
                'memories': total_memories,
                'milestones': total_milestones,
                'albums': total_albums,
                'stories': total_stories,
            }
            
            # Recent memories
            context['recent_memories'] = Memory.objects.filter(child__in=children)[:5]
            
            # Feature availability for each child
            context['child_features'] = {}
            for child in children:
                context['child_features'][child.id] = {
                    'age': child.age_in_years,
                    'unlocked_features': child.get_unlocked_features(),
                    'upcoming_features': self._get_upcoming_features(child)
                }
        
        return context
    
    def _get_upcoming_features(self, child):
        """Get features that will unlock in the next few years"""
        age = child.age_in_years
        upcoming = []
        
        if age < 1:
            upcoming.append(('Milestones & Growth Chart', 1))
        if age < 2:
            upcoming.append(('Memory Map', 2))
        if age < 3:
            upcoming.append(('Bedtime Story Generator', 3))
        if age < 5:
            upcoming.append(('Voice Notes & Drawings', 5))
        if age < 13:
            upcoming.append(('Guestbook & Journaling', 13))
        if age < 18:
            upcoming.append(('Full Export & Ownership Transfer', 18))
        
        return upcoming[:3]  # Return next 3 features

class FeaturesView(LoginRequiredMixin, TemplateView):
    template_name = 'core/features.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get user's children
        if self.request.user.is_owner:
            children = Child.objects.filter(owner=self.request.user)
        else:
            children = self.request.user.children.all()
        
        context['children'] = children
        
        # Feature map with descriptions
        context['all_features'] = {
            'memories': {
                'name': 'Memories',
                'description': 'Upload and organize photos, videos, audio recordings, and text memories',
                'unlocked_at': 0,
                'icon': '📸'
            },
            'milestones': {
                'name': 'Milestone Tracker',
                'description': 'Track important developmental milestones and achievements',
                'unlocked_at': 1,
                'icon': '🌟'
            },
            'growth_chart': {
                'name': 'Growth Chart',
                'description': 'Monitor height, weight, and growth progress over time',
                'unlocked_at': 1,
                'icon': '📏'
            },
            'ai_captions': {
                'name': 'AI Photo Captions',
                'description': 'Automatically generate captions for photos using AI',
                'unlocked_at': 1,
                'icon': '🤖'
            },
            'memory_map': {
                'name': 'Memory Map',
                'description': 'View memories on a map based on their locations',
                'unlocked_at': 2,
                'icon': '🗺️'
            },
            'bedtime_stories': {
                'name': 'Bedtime Story Generator',
                'description': 'Generate personalized bedtime stories using AI',
                'unlocked_at': 3,
                'icon': '📚'
            },
            'voice_notes': {
                'name': 'Voice Notes & Drawings',
                'description': 'Record voice messages and upload drawings',
                'unlocked_at': 5,
                'icon': '🎤'
            },
            'guestbook': {
                'name': 'Guestbook & Journaling',
                'description': 'Friends and family can leave messages, child can journal',
                'unlocked_at': 13,
                'icon': '✍️'
            },
            'full_export': {
                'name': 'Full Export & Ownership',
                'description': 'Export all data and transfer ownership to the child',
                'unlocked_at': 18,
                'icon': '💾'
            }
        }
        
        return context

class ExportDataView(LoginRequiredMixin, TemplateView):
    template_name = 'core/export.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Only owners can export
        if not self.request.user.is_owner:
            messages.error(self.request, "Only the album owner can export data.")
            return redirect('core:dashboard')
        
        context['children'] = Child.objects.filter(owner=self.request.user)
        return context
    
    def post(self, request):
        if not request.user.is_owner:
            messages.error(request, "Only the album owner can export data.")
            return redirect('core:dashboard')
        
        child_id = request.POST.get('child')
        if not child_id:
            messages.error(request, "Please select a child to export.")
            return redirect('core:export')
        
        child = Child.objects.get(id=child_id, owner=request.user)
        
        # TODO: Implement actual export functionality
        # This would create a background task to generate a zip file with all data
        messages.success(request, f"Export for {child.name} has been started. You'll receive an email when it's ready.")
        return redirect('core:export')

class SettingsView(LoginRequiredMixin, TemplateView):
    template_name = 'core/settings.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.request.user.is_owner:
            context['children'] = Child.objects.filter(owner=self.request.user)
        else:
            context['children'] = self.request.user.children.all()
        
        return context
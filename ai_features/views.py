from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, ListView
from django.contrib import messages
from django.http import JsonResponse
from accounts.models import Child
from .models import BedtimeStory, AITask
from .forms import BedtimeStoryForm
from .tasks import generate_bedtime_story, generate_photo_caption, transcribe_audio_file

class BedtimeStoriesView(LoginRequiredMixin, ListView):
    model = BedtimeStory
    template_name = 'ai_features/stories_list.html'
    context_object_name = 'stories'
    paginate_by = 12
    
    def get_queryset(self):
        child_id = self.request.GET.get('child')
        queryset = BedtimeStory.objects.all()
        
        # Filter by child access permissions
        if self.request.user.is_owner:
            children = Child.objects.filter(owner=self.request.user)
        else:
            children = self.request.user.children.all()
        
        queryset = queryset.filter(child__in=children)
        
        if child_id:
            queryset = queryset.filter(child_id=child_id)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_owner:
            context['children'] = Child.objects.filter(owner=self.request.user)
        else:
            context['children'] = self.request.user.children.all()
        context['current_child'] = self.request.GET.get('child')
        return context

class CreateBedtimeStoryView(LoginRequiredMixin, TemplateView):
    template_name = 'ai_features/create_story.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = BedtimeStoryForm(user=self.request.user)
        
        # Check if any child has bedtime stories unlocked
        if self.request.user.is_owner:
            children = Child.objects.filter(owner=self.request.user)
        else:
            children = self.request.user.children.all()
        
        unlocked_children = [child for child in children if child.has_feature('bedtime_stories')]
        
        if not unlocked_children:
            messages.info(self.request, "Bedtime story generator will unlock when your child turns 3 years old!")
            return redirect('core:dashboard')
        
        return context
    
    def post(self, request):
        form = BedtimeStoryForm(request.POST, user=request.user)
        if form.is_valid():
            child = form.cleaned_data['child']
            
            # Check if bedtime stories feature is unlocked
            if not child.has_feature('bedtime_stories'):
                messages.error(request, "Bedtime story generator is not yet available for this child.")
                return redirect('ai_features:stories')
            
            # Create AI task for story generation
            task = AITask.objects.create(
                task_type='bedtime_story',
                created_by=request.user,
                input_data={
                    'child_id': str(child.id),
                    'prompt': form.cleaned_data['story_prompt'],
                    'child_name': child.name,
                    'theme': form.cleaned_data.get('theme', ''),
                    'length': form.cleaned_data.get('story_length', 'medium')
                }
            )
            
            # Trigger async task
            generate_bedtime_story.delay(str(task.id))
            
            messages.success(request, "Your bedtime story is being generated! Check back in a few moments.")
            return redirect('ai_features:stories')
        
        return render(request, self.template_name, {'form': form})

class BedtimeStoryDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'ai_features/story_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        story = get_object_or_404(BedtimeStory, pk=kwargs['pk'])
        
        # Check permissions
        user = self.request.user
        if not ((user.is_owner and story.child.owner == user) or 
                story.child in user.children.all()):
            messages.error(self.request, "You don't have permission to view this story.")
            return redirect('ai_features:stories')
        
        context['story'] = story
        return context

class GenerateCaptionView(LoginRequiredMixin, TemplateView):
    def post(self, request):
        memory_id = request.POST.get('memory_id')
        
        if not memory_id:
            return JsonResponse({'error': 'Memory ID required'}, status=400)
        
        # Create AI task for caption generation
        task = AITask.objects.create(
            task_type='caption',
            created_by=request.user,
            input_data={'memory_id': memory_id}
        )
        
        # Trigger async task
        generate_photo_caption.delay(str(task.id))
        
        return JsonResponse({'task_id': str(task.id), 'status': 'processing'})

class TranscribeAudioView(LoginRequiredMixin, TemplateView):
    def post(self, request):
        memory_id = request.POST.get('memory_id')
        
        if not memory_id:
            return JsonResponse({'error': 'Memory ID required'}, status=400)
        
        # Create AI task for transcription
        task = AITask.objects.create(
            task_type='transcription',
            created_by=request.user,
            input_data={'memory_id': memory_id}
        )
        
        # Trigger async task
        transcribe_audio_file.delay(str(task.id))
        
        return JsonResponse({'task_id': str(task.id), 'status': 'processing'})
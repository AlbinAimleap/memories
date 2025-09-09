from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, ListView
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from accounts.models import Child
from .models import Memory, MemoryReaction, MemoryComment
from .forms import MemoryForm, MemoryCommentForm

class MemoryListView(LoginRequiredMixin, ListView):
    model = Memory
    template_name = 'memories/list.html'
    context_object_name = 'memories'
    paginate_by = 20
    
    def get_queryset(self):
        child_id = self.request.GET.get('child')
        queryset = Memory.objects.all()
        
        # Filter by child access permissions
        if self.request.user.is_owner:
            children = Child.objects.filter(owner=self.request.user)
        else:
            children = self.request.user.children.all()
        
        queryset = queryset.filter(child__in=children)
        
        if child_id:
            queryset = queryset.filter(child_id=child_id)
        
        # Search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(content__icontains=search) |
                Q(tags__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_owner:
            context['children'] = Child.objects.filter(owner=self.request.user)
        else:
            context['children'] = self.request.user.children.all()
        context['current_child'] = self.request.GET.get('child')
        context['search_query'] = self.request.GET.get('search', '')
        return context

class MemoryDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'memories/detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        memory = get_object_or_404(Memory, pk=kwargs['pk'])
        
        # Check permissions
        if not self._has_permission(memory):
            messages.error(self.request, "You don't have permission to view this memory.")
            return redirect('memories:list')
        
        context['memory'] = memory
        context['reactions'] = memory.reactions.all()
        context['comments'] = memory.comments.all()
        context['comment_form'] = MemoryCommentForm()
        context['user_reactions'] = memory.reactions.filter(user=self.request.user)
        return context
    
    def _has_permission(self, memory):
        user = self.request.user
        return (user.is_owner and memory.child.owner == user) or \
               memory.child in user.children.all()

class AddMemoryView(LoginRequiredMixin, TemplateView):
    template_name = 'memories/add.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = MemoryForm(user=self.request.user)
        return context
    
    def post(self, request):
        form = MemoryForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            memory = form.save(commit=False)
            memory.created_by = request.user
            memory.save()
            
            messages.success(request, "Memory added successfully!")
            return redirect('memories:detail', pk=memory.pk)
        
        return render(request, self.template_name, {'form': form})

class EditMemoryView(LoginRequiredMixin, TemplateView):
    template_name = 'memories/edit.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        memory = get_object_or_404(Memory, pk=kwargs['pk'])
        context['memory'] = memory
        context['form'] = MemoryForm(instance=memory, user=self.request.user)
        return context
    
    def post(self, request, pk):
        memory = get_object_or_404(Memory, pk=pk)
        form = MemoryForm(request.POST, request.FILES, instance=memory, user=request.user)
        
        if form.is_valid():
            form.save()
            messages.success(request, "Memory updated successfully!")
            return redirect('memories:detail', pk=memory.pk)
        
        return render(request, self.template_name, {
            'memory': memory,
            'form': form
        })

class DeleteMemoryView(LoginRequiredMixin, TemplateView):
    def post(self, request, pk):
        memory = get_object_or_404(Memory, pk=pk)
        
        # Check permissions - only owner or creator can delete
        if not (request.user == memory.created_by or 
                (request.user.is_owner and memory.child.owner == request.user)):
            messages.error(request, "You don't have permission to delete this memory.")
            return redirect('memories:detail', pk=pk)
        
        memory.delete()
        messages.success(request, "Memory deleted successfully.")
        return redirect('memories:list')

class ReactToMemoryView(LoginRequiredMixin, TemplateView):
    def post(self, request, pk):
        memory = get_object_or_404(Memory, pk=pk)
        reaction = request.POST.get('reaction')
        
        if not reaction:
            return JsonResponse({'error': 'No reaction provided'}, status=400)
        
        # Toggle reaction
        existing_reaction = MemoryReaction.objects.filter(
            memory=memory, 
            user=request.user, 
            reaction=reaction
        ).first()
        
        if existing_reaction:
            existing_reaction.delete()
            action = 'removed'
        else:
            MemoryReaction.objects.create(
                memory=memory,
                user=request.user,
                reaction=reaction
            )
            action = 'added'
        
        # Get updated reaction counts
        reaction_counts = {}
        for r in memory.reactions.values('reaction').distinct():
            reaction_counts[r['reaction']] = memory.reactions.filter(reaction=r['reaction']).count()
        
        return JsonResponse({
            'action': action,
            'reaction_counts': reaction_counts
        })

class AddCommentView(LoginRequiredMixin, TemplateView):
    def post(self, request, pk):
        memory = get_object_or_404(Memory, pk=pk)
        form = MemoryCommentForm(request.POST)
        
        if form.is_valid():
            comment = form.save(commit=False)
            comment.memory = memory
            comment.user = request.user
            comment.save()
            
            if request.headers.get('HX-Request'):
                return render(request, 'memories/partials/comment.html', {
                    'comment': comment
                })
            
            messages.success(request, "Comment added!")
        
        return redirect('memories:detail', pk=pk)

class TimelineView(LoginRequiredMixin, TemplateView):
    template_name = 'memories/timeline.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get child parameter
        child_id = self.request.GET.get('child')
        child = None
        
        if child_id:
            if self.request.user.is_owner:
                child = get_object_or_404(Child, id=child_id, owner=self.request.user)
            else:
                child = get_object_or_404(Child, id=child_id, family_members=self.request.user)
        else:
            # Default to first accessible child
            if self.request.user.is_owner:
                child = Child.objects.filter(owner=self.request.user).first()
            else:
                child = self.request.user.children.first()
        
        if child:
            memories = Memory.objects.filter(child=child).order_by('-memory_date')
            context['memories'] = memories
            context['child'] = child
        
        # Available children for switcher
        if self.request.user.is_owner:
            context['children'] = Child.objects.filter(owner=self.request.user)
        else:
            context['children'] = self.request.user.children.all()
        
        return context
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, ListView
from django.contrib import messages
from django.db.models import Q
from accounts.models import Child
from memories.models import Memory
from .models import Album, AlbumMemory
from .forms import AlbumForm, AddMemoriesToAlbumForm

class AlbumListView(LoginRequiredMixin, ListView):
    model = Album
    template_name = 'albums/list.html'
    context_object_name = 'albums'
    paginate_by = 12
    
    def get_queryset(self):
        child_id = self.request.GET.get('child')
        queryset = Album.objects.all()
        
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

class CreateAlbumView(LoginRequiredMixin, TemplateView):
    template_name = 'albums/create.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = AlbumForm(user=self.request.user)
        return context
    
    def post(self, request):
        form = AlbumForm(request.POST, user=request.user)
        if form.is_valid():
            album = form.save(commit=False)
            album.created_by = request.user
            album.save()
            
            messages.success(request, "Album created successfully!")
            return redirect('albums:detail', pk=album.pk)
        
        return render(request, self.template_name, {'form': form})

class AlbumDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'albums/detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        album = get_object_or_404(Album, pk=kwargs['pk'])
        
        # Check permissions
        if not self._has_permission(album):
            messages.error(self.request, "You don't have permission to view this album.")
            return redirect('albums:list')
        
        context['album'] = album
        context['album_memories'] = album.album_memories.all()
        return context
    
    def _has_permission(self, album):
        user = self.request.user
        return (user.is_owner and album.child.owner == user) or \
               album.child in user.children.all()

class EditAlbumView(LoginRequiredMixin, TemplateView):
    template_name = 'albums/edit.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        album = get_object_or_404(Album, pk=kwargs['pk'])
        context['album'] = album
        context['form'] = AlbumForm(instance=album, user=self.request.user)
        return context
    
    def post(self, request, pk):
        album = get_object_or_404(Album, pk=pk)
        form = AlbumForm(request.POST, instance=album, user=request.user)
        
        if form.is_valid():
            form.save()
            messages.success(request, "Album updated successfully!")
            return redirect('albums:detail', pk=album.pk)
        
        return render(request, self.template_name, {
            'album': album,
            'form': form
        })

class DeleteAlbumView(LoginRequiredMixin, TemplateView):
    def post(self, request, pk):
        album = get_object_or_404(Album, pk=pk)
        
        # Check permissions - only owner or creator can delete
        if not (request.user == album.created_by or 
                (request.user.is_owner and album.child.owner == request.user)):
            messages.error(request, "You don't have permission to delete this album.")
            return redirect('albums:detail', pk=pk)
        
        album.delete()
        messages.success(request, "Album deleted successfully.")
        return redirect('albums:list')

class AddMemoriesToAlbumView(LoginRequiredMixin, TemplateView):
    template_name = 'albums/add_memories.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        album = get_object_or_404(Album, pk=kwargs['pk'])
        context['album'] = album
        
        # Get memories not already in this album
        existing_memory_ids = album.album_memories.values_list('memory_id', flat=True)
        available_memories = Memory.objects.filter(child=album.child).exclude(id__in=existing_memory_ids)
        
        context['form'] = AddMemoriesToAlbumForm(available_memories=available_memories)
        return context
    
    def post(self, request, pk):
        album = get_object_or_404(Album, pk=pk)
        
        existing_memory_ids = album.album_memories.values_list('memory_id', flat=True)
        available_memories = Memory.objects.filter(child=album.child).exclude(id__in=existing_memory_ids)
        
        form = AddMemoriesToAlbumForm(request.POST, available_memories=available_memories)
        
        if form.is_valid():
            memories = form.cleaned_data['memories']
            for memory in memories:
                AlbumMemory.objects.create(
                    album=album,
                    memory=memory,
                    added_by=request.user
                )
            
            messages.success(request, f"Added {len(memories)} memories to the album!")
            return redirect('albums:detail', pk=album.pk)
        
        return render(request, self.template_name, {
            'album': album,
            'form': form
        })
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, ListView
from django.contrib import messages
from accounts.models import Child
from .models import ChildMilestone, PredefinedMilestone, GrowthRecord, MilestoneCategory
from .forms import ChildMilestoneForm, GrowthRecordForm

class MilestoneListView(LoginRequiredMixin, TemplateView):
    template_name = 'milestones/list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get child
        child_id = self.request.GET.get('child')
        child = None
        
        if child_id:
            if self.request.user.is_owner:
                child = get_object_or_404(Child, id=child_id, owner=self.request.user)
            else:
                child = get_object_or_404(Child, id=child_id, family_members=self.request.user)
        else:
            if self.request.user.is_owner:
                child = Child.objects.filter(owner=self.request.user).first()
            else:
                child = self.request.user.children.first()
        
        if child:
            # Check if milestones feature is unlocked
            if not child.has_feature('milestones'):
                messages.info(self.request, "Milestone tracking will unlock when your child turns 1 year old!")
                return redirect('core:dashboard')
            
            context['child'] = child
            context['achieved_milestones'] = ChildMilestone.objects.filter(child=child)
            context['categories'] = MilestoneCategory.objects.all()
            
            # Get available milestones to achieve
            achieved_milestone_ids = context['achieved_milestones'].values_list(
                'predefined_milestone_id', flat=True
            )
            context['available_milestones'] = PredefinedMilestone.objects.exclude(
                id__in=achieved_milestone_ids
            )
        
        # Available children
        if self.request.user.is_owner:
            context['children'] = Child.objects.filter(owner=self.request.user)
        else:
            context['children'] = self.request.user.children.all()
        
        return context

class AddMilestoneView(LoginRequiredMixin, TemplateView):
    template_name = 'milestones/add.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ChildMilestoneForm(user=self.request.user)
        return context
    
    def post(self, request):
        form = ChildMilestoneForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            milestone = form.save(commit=False)
            milestone.recorded_by = request.user
            
            # Calculate age at achievement
            child = milestone.child
            age_in_months = (milestone.achieved_date.date() - child.birth_date).days // 30
            milestone.age_at_achievement = f"{age_in_months} months old"
            
            milestone.save()
            messages.success(request, "Milestone recorded successfully!")
            return redirect('milestones:list')
        
        return render(request, self.template_name, {'form': form})

class EditMilestoneView(LoginRequiredMixin, TemplateView):
    template_name = 'milestones/edit.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        milestone = get_object_or_404(ChildMilestone, pk=kwargs['pk'])
        context['milestone'] = milestone
        context['form'] = ChildMilestoneForm(instance=milestone, user=self.request.user)
        return context
    
    def post(self, request, pk):
        milestone = get_object_or_404(ChildMilestone, pk=pk)
        form = ChildMilestoneForm(request.POST, request.FILES, instance=milestone, user=request.user)
        
        if form.is_valid():
            form.save()
            messages.success(request, "Milestone updated successfully!")
            return redirect('milestones:list')
        
        return render(request, self.template_name, {
            'milestone': milestone,
            'form': form
        })

class GrowthChartView(LoginRequiredMixin, TemplateView):
    template_name = 'milestones/growth_chart.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get child
        child_id = self.request.GET.get('child')
        child = None
        
        if child_id:
            if self.request.user.is_owner:
                child = get_object_or_404(Child, id=child_id, owner=self.request.user)
            else:
                child = get_object_or_404(Child, id=child_id, family_members=self.request.user)
        else:
            if self.request.user.is_owner:
                child = Child.objects.filter(owner=self.request.user).first()
            else:
                child = self.request.user.children.first()
        
        if child:
            # Check if growth chart feature is unlocked
            if not child.has_feature('growth_chart'):
                messages.info(self.request, "Growth chart will unlock when your child turns 1 year old!")
                return redirect('core:dashboard')
            
            context['child'] = child
            context['height_records'] = GrowthRecord.objects.filter(
                child=child, measurement_type='height'
            )
            context['weight_records'] = GrowthRecord.objects.filter(
                child=child, measurement_type='weight'
            )
            context['head_records'] = GrowthRecord.objects.filter(
                child=child, measurement_type='head_circumference'
            )
        
        # Available children
        if self.request.user.is_owner:
            context['children'] = Child.objects.filter(owner=self.request.user)
        else:
            context['children'] = self.request.user.children.all()
        
        return context

class AddGrowthRecordView(LoginRequiredMixin, TemplateView):
    template_name = 'milestones/add_growth.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = GrowthRecordForm(user=self.request.user)
        return context
    
    def post(self, request):
        form = GrowthRecordForm(request.POST, user=request.user)
        if form.is_valid():
            growth_record = form.save(commit=False)
            growth_record.recorded_by = request.user
            
            # Calculate age at measurement
            child = growth_record.child
            age_in_months = (growth_record.measurement_date.date() - child.birth_date).days // 30
            growth_record.age_at_measurement = f"{age_in_months} months old"
            
            growth_record.save()
            messages.success(request, "Growth record added successfully!")
            return redirect('milestones:growth_chart')
        
        return render(request, self.template_name, {'form': form})
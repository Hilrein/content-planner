from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from .models import ContentPlan, ContentItem, ContentCategory, UserProfile
from .forms import ContentPlanForm, ContentItemForm, ContentCategoryForm, UserProfileForm, UserProfileImageForm

def home(request):
    if request.user.is_authenticated:
        recent_plans = ContentPlan.objects.filter(owner=request.user).order_by('-updated_at')[:5]
        upcoming_items = ContentItem.objects.filter(
            content_plan__owner=request.user, 
            scheduled_date__gte=timezone.now(),
            status='scheduled'
        ).order_by('scheduled_date')[:10]
        
        context = {
            'recent_plans': recent_plans,
            'upcoming_items': upcoming_items,
        }
        return render(request, 'planner/dashboard.html', context)
    return render(request, 'planner/home.html')

@login_required
def content_plan_list(request):
    plans = ContentPlan.objects.filter(owner=request.user).order_by('-updated_at')
    
    for plan in plans:
        plan.published_count = plan.content_items.filter(status='published').count()
        plan.scheduled_count = plan.content_items.filter(status='scheduled').count()
        plan.total_count = plan.content_items.count()
        
        if plan.total_count > 0:
            plan.published_percent = int((plan.published_count / plan.total_count) * 100)
            plan.scheduled_percent = int((plan.scheduled_count / plan.total_count) * 100)
        else:
            plan.published_percent = 0
            plan.scheduled_percent = 0
            
    return render(request, 'planner/content_plan_list.html', {'plans': plans})

@login_required
def content_plan_detail(request, pk):
    """Детальная информация о плане контента"""
    plan = get_object_or_404(ContentPlan, pk=pk, owner=request.user)
    items = plan.content_items.all().order_by('scheduled_date')
    
    status_filter = request.GET.get('status')
    category_filter = request.GET.get('category')
    
    if status_filter:
        items = items.filter(status=status_filter)
    if category_filter:
        items = items.filter(category_id=category_filter)
    
    context = {
        'plan': plan,
        'items': items,
        'categories': ContentCategory.objects.all(),
        'status_choices': ContentItem.STATUS_CHOICES,
    }
    return render(request, 'planner/content_plan_detail.html', context)

@login_required
def content_plan_create(request):
    if request.method == 'POST':
        form = ContentPlanForm(request.POST)
        if form.is_valid():
            plan = form.save(commit=False)
            plan.owner = request.user
            plan.save()
            messages.success(request, 'План контента успешно создан!')
            return redirect('content_plan_detail', pk=plan.pk)
    else:
        form = ContentPlanForm()
    
    return render(request, 'planner/content_plan_form.html', {'form': form, 'is_create': True})

@login_required
def content_plan_edit(request, pk):
    plan = get_object_or_404(ContentPlan, pk=pk, owner=request.user)
    
    if request.method == 'POST':
        form = ContentPlanForm(request.POST, instance=plan)
        if form.is_valid():
            form.save()
            messages.success(request, 'План контента успешно обновлен!')
            return redirect('content_plan_detail', pk=plan.pk)
    else:
        form = ContentPlanForm(instance=plan)
    
    return render(request, 'planner/content_plan_form.html', {'form': form, 'is_create': False, 'plan': plan})

@login_required
def content_plan_delete(request, pk):
    plan = get_object_or_404(ContentPlan, pk=pk, owner=request.user)
    
    if request.method == 'POST':
        plan.delete()
        messages.success(request, 'План контента успешно удален!')
        return redirect('content_plan_list')
    
    return render(request, 'planner/content_plan_confirm_delete.html', {'plan': plan})

@login_required
def content_item_create(request, plan_pk):
    plan = get_object_or_404(ContentPlan, pk=plan_pk, owner=request.user)
    
    if request.method == 'POST':
        form = ContentItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.content_plan = plan
            item.save()
            messages.success(request, 'Элемент контента успешно создан!')
            return redirect('content_plan_detail', pk=plan.pk)
    else:
        form = ContentItemForm()
    
    return render(request, 'planner/content_item_form.html', {
        'form': form, 
        'plan': plan,
        'is_create': True
    })

@login_required
def content_item_edit(request, pk):
    item = get_object_or_404(ContentItem, pk=pk, content_plan__owner=request.user)
    
    if request.method == 'POST':
        form = ContentItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Элемент контента успешно обновлен!')
            return redirect('content_plan_detail', pk=item.content_plan.pk)
    else:
        form = ContentItemForm(instance=item)
    
    return render(request, 'planner/content_item_form.html', {
        'form': form, 
        'plan': item.content_plan,
        'item': item,
        'is_create': False
    })

@login_required
def content_item_delete(request, pk):
    item = get_object_or_404(ContentItem, pk=pk, content_plan__owner=request.user)
    plan_pk = item.content_plan.pk
    
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Элемент контента успешно удален!')
        return redirect('content_plan_detail', pk=plan_pk)
    
    return render(request, 'planner/content_item_confirm_delete.html', {'item': item})

@login_required
def content_calendar(request):
    items = ContentItem.objects.filter(
        content_plan__owner=request.user
    ).order_by('scheduled_date')
    
    status_filter = request.GET.get('status')
    category_filter = request.GET.get('category')
    plan_filter = request.GET.get('plan')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if status_filter:
        items = items.filter(status=status_filter)
    if category_filter:
        items = items.filter(category_id=category_filter)
    if plan_filter:
        items = items.filter(content_plan_id=plan_filter)
    if date_from:
        items = items.filter(scheduled_date__gte=date_from)
    if date_to:
        items = items.filter(scheduled_date__lte=date_to)
    
    context = {
        'items': items,
        'categories': ContentCategory.objects.all(),
        'plans': ContentPlan.objects.filter(owner=request.user),
        'status_choices': ContentItem.STATUS_CHOICES,
        'status_filter': status_filter,
        'category_filter': category_filter,
        'plan_filter': plan_filter,
        'date_from': date_from,
        'date_to': date_to
    }
    return render(request, 'planner/content_calendar.html', context)

@login_required
def categories_list(request):
    categories = ContentCategory.objects.all()
    
    if request.method == 'POST':
        form = ContentCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Категория успешно создана!')
            return redirect('categories_list')
    else:
        form = ContentCategoryForm()
    
    return render(request, 'planner/categories_list.html', {
        'categories': categories,
        'form': form
    })

@login_required
def category_delete(request, pk):
    category = get_object_or_404(ContentCategory, pk=pk)
    
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Категория успешно удалена!')
        return redirect('categories_list')
    
    return render(request, 'planner/category_confirm_delete.html', {'category': category})

@login_required
def user_profile(request):
    user = request.user
    
    try:
        profile = user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=user)
    
    content_plans_count = ContentPlan.objects.filter(owner=user).count()
    content_items_count = ContentItem.objects.filter(content_plan__owner=user).count()
    published_items_count = ContentItem.objects.filter(
        content_plan__owner=user, 
        status='published'
    ).count()
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user)
        image_form = UserProfileImageForm(request.POST, request.FILES, instance=profile)
        
        old_password = request.POST.get('old_password')
        if old_password:
            password_form = PasswordChangeForm(user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user) 
                messages.success(request, 'Пароль успешно изменен!')
        
        if form.is_valid() and image_form.is_valid():
            form.save()
            image_form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('user_profile')
    else:
        form = UserProfileForm(instance=user)
        image_form = UserProfileImageForm(instance=profile)
    
    context = {
        'form': form,
        'image_form': image_form,
        'content_plans_count': content_plans_count,
        'content_items_count': content_items_count,
        'published_items_count': published_items_count,
    }
    return render(request, 'planner/profile.html', context)

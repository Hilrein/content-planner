from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class ContentCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Категории контента"

class ContentPlan(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='content_plans')
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name_plural = "Планы контента"

class ContentItem(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('scheduled', 'Запланировано'),
        ('published', 'Опубликовано'),
        ('cancelled', 'Отменено'),
    ]
    
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    content_plan = models.ForeignKey(ContentPlan, on_delete=models.CASCADE, related_name='content_items')
    category = models.ForeignKey(ContentCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='content_items')
    scheduled_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='content_images/', blank=True, null=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name_plural = "Элементы контента"
        ordering = ['-scheduled_date']

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    
    def __str__(self):
        return f"Профиль пользователя {self.user.username}"

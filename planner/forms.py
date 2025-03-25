from django import forms
from django.utils import timezone
from django.contrib.auth.models import User
from .models import ContentPlan, ContentItem, ContentCategory, UserProfile

class ContentPlanForm(forms.ModelForm):
    class Meta:
        model = ContentPlan
        fields = ['title', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'title': 'Название',
            'description': 'Описание',
        }

class ContentItemForm(forms.ModelForm):
    class Meta:
        model = ContentItem
        fields = ['title', 'content', 'category', 'status', 'scheduled_date', 'image']
        widgets = {
            'scheduled_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'content': forms.Textarea(attrs={'rows': 6}),
        }
        labels = {
            'title': 'Название',
            'content': 'Содержание',
            'category': 'Категория',
            'status': 'Статус',
            'scheduled_date': 'Дата публикации',
            'image': 'Изображение',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'instance' in kwargs and kwargs['instance']:
            self.fields['scheduled_date'].initial = kwargs['instance'].scheduled_date.strftime('%Y-%m-%dT%H:%M')
        else:
            self.fields['scheduled_date'].initial = timezone.now().strftime('%Y-%m-%dT%H:%M')

class ContentCategoryForm(forms.ModelForm):
    class Meta:
        model = ContentCategory
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'name': 'Название',
            'description': 'Описание',
        }

class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=False, label="Имя")
    last_name = forms.CharField(max_length=30, required=False, label="Фамилия")
    email = forms.EmailField(required=False, label="Email")
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError('Пользователь с таким Email уже существует.')
        return email

class UserProfileImageForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_image']
        labels = {
            'profile_image': 'Фотография профиля',
        }
        widgets = {
            'profile_image': forms.FileInput(attrs={'class': 'form-control'}),
        } 
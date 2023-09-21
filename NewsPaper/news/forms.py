from django.forms import ModelForm
from .models import Post
from django import forms


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['type', 'title', 'textPost', 'author', 'category']
        labels = {
            'type': 'Нововсть/статья',
            'title': 'Заголовок',
            'textPost': 'Текст новости/статьи',
            'author': 'Автор',
            'category': 'Категория'
        }
        widgets = {
            'type': forms.Select(attrs={
                'class': 'form-control',
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите заголовок'
            }),
            'textPost': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Текст вашей нововсти или статьи'
            }),
            'author': forms.Select(attrs={
                'class': 'form-control',
            }),
        }

from django import forms
from django.core.exceptions import ValidationError

from posts.models import Group


class PostForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea)
    group = forms.CharField(max_length=200)

    def clean_group(self):
        data = self.cleaned_data['group']
        if not Group.objects.filter(title=data).exists():
            raise ValidationError('Не существует такой группы')
        return data

from django import forms
from django.core.exceptions import ValidationError

from posts.models import Group


class PostForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea)
    group = forms.CharField(max_length=200, required=False)

    def clean_group(self):
        if not self.cleaned_data['group']:
            return
        data = self.cleaned_data['group']
        if not Group.objects.filter(title=data).exists():
            raise ValidationError('Не существует такой группы')
        return data

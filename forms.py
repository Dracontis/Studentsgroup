# ~*~ coding: utf-8 ~*~
from django import forms
from engine_models.models import Comment
from admin_models.models import Registration
from engine_models.optimization import validate_not_spaces

class CommentForm(forms.ModelForm):
    nickname = forms.CharField(widget = forms.HiddenInput())
    text = forms.CharField(widget = forms.Textarea(attrs = {'cols': 100, 'rows': 7}),validators = [validate_not_spaces])
    rel_message = forms.IntegerField(widget = forms.HiddenInput())

    class Meta:
        exclude = ('rel_message',)
        model = Comment

class RegistrationForm(forms.ModelForm):
    class Meta:
        model = Registration
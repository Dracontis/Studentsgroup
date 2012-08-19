# ~*~ coding: utf-8 ~*~
from models import SubCategory
from django.forms import ValidationError

def validate_not_spaces(value):
    if value.strip() == '':
        raise ValidationError(u"You must provide more than just whitespace.")
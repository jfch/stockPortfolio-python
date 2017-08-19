from __future__ import unicode_literals

from django.db import models
from pygments.lexers import get_all_lexers
from pygments.styles import get_all_styles

from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.forms import EmailField
from django.utils.translation import ugettext_lazy as _

LEXERS = [item for item in get_all_lexers() if item[1]]
LANGUAGE_CHOICES = sorted([(item[1][0], item[0]) for item in LEXERS])
STYLE_CHOICES = sorted((item, item) for item in get_all_styles())


# Create your models here.
class UserCreationForm(UserCreationForm):
    email = EmailField(label=_("Email address"), required=True,
        help_text=_("Required."))

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
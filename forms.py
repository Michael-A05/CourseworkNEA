from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import CustomUser, Allergen, Choice


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email')


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email')


class AllergenChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = []

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(AllergenChoiceForm, self).__init__(*args, **kwargs)
        allergens = Allergen.objects.all()
        for allergen in allergens:
            field_name = 'allergen_%s' % allergen.id
            self.fields[field_name] = forms.BooleanField(label=allergen.name, required=False)

    def save(self, commit=True, **kwargs):
        user = kwargs.pop('user')
        for field_name, value in self.cleaned_data.items():
            if value:
                allergen_id = int(field_name.split('_')[-1])
                allergen = Allergen.objects.get(id=allergen_id)
                choice, created = Choice.objects.get_or_create(user=user, allergen=allergen)
                choice.chosen = True
                if commit:
                    choice.save()
        return self.instance

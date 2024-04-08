from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.contrib.auth.decorators import login_required

from .forms import CustomUserCreationForm, AllergenChoiceForm
from .models import Choice, Allergen


# Create your views here.

def profile(request):
    return render(request, 'user_home.html')


@login_required
def choose_allergens(request):
    user_choices = Choice.objects.filter(user=request.user, chosen=True)
    if request.method == 'POST':
        form = AllergenChoiceForm(request.POST, user=request.user)
        if form.is_valid():
            form.save(user=request.user)
            return redirect(reverse_lazy('user_page'))
    else:
        form = AllergenChoiceForm(user=request.user)
    return render(request, 'choose_allergens.html', {'form': form, 'user_choices': user_choices})


def remove_allergen(request, choice_id):
    choice = get_object_or_404(Choice, id=choice_id, user=request.user)
    choice.delete()
    return redirect('choose_allergens')

class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

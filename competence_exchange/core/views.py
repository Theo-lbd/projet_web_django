from django.shortcuts import render,redirect
from .models import Slot
from .models import Competence
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User


def available_slots(request):
    slots = Slot.objects.filter(is_available=True)
    return render(request, 'core/available_slots.html', {'slots': slots})


def competence_list(request):
    competences = Competence.objects.all()
    return render(request, 'core/competence_list.html', {'competences': competences})


@login_required
def user_competences(request):
    if request.method == 'POST':
        selected_competences = request.POST.getlist('competences')
        user = request.user
        user.profile.competences.set(selected_competences)  # Assurez-vous d'avoir un champ compétences dans le profil utilisateur
        return redirect('available_slots')
    else:
        competences = Competence.objects.all()
        return render(request, 'core/user_competences.html', {'competences': competences})
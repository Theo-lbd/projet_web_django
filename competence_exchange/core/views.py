from django.shortcuts import render,redirect
from .models import Slot, Profile
from django.utils import timezone
from datetime import timedelta
from .models import Competence
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404


def available_slots(request):
    slots = Slot.objects.filter(is_available=True, purpose='aid')
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


@login_required
def add_slot(request):
    user_profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        date = request.POST.get('date')
        competence_id = request.POST.get('competence')
        purpose = request.POST.get('purpose')
        competence = Competence.objects.get(id=competence_id)

        # Créer un créneau avec les informations fournies
        Slot.objects.create(date=date, competence=competence, user=request.user, is_available=True, purpose=purpose)
        return redirect('my_slots')

    else:
        competences = user_profile.competences.all()
        return render(request, 'core/add_slot.html', {'competences': competences})


@login_required
def my_slots(request):
    slots = Slot.objects.filter(user=request.user)
    return render(request, 'core/my_slots.html', {'slots': slots})


@login_required
def delete_slot(request, slot_id):
    slot = get_object_or_404(Slot, id=slot_id, user=request.user)
    slot.delete()
    return redirect('my_slots')
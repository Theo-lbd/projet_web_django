from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Slot, Profile, Competence, Activity

def available_slots(request):
    """
    Affiche la liste des créneaux disponibles pour l'aide, sans informations personnelles.

    Args:
        request (HttpRequest): La requête HTTP reçue par le serveur.

    Returns:
        HttpResponse: La page affichant les créneaux disponibles.
    """
    slots = Slot.objects.filter(is_available=True, purpose='aid')
    return render(request, 'core/available_slots.html', {'slots': slots})


def competence_list(request):
    """
    Affiche la liste des compétences disponibles pour l'échange.

    Args:
        request (HttpRequest): La requête HTTP reçue par le serveur.

    Returns:
        HttpResponse: La page affichant la liste des compétences.
    """
    competences = Competence.objects.all()
    return render(request, 'core/competence_list.html', {'competences': competences})


@login_required
def user_competences(request):
    """
    Permet à l'utilisateur de sélectionner les compétences qu'il possède.

    Args:
        request (HttpRequest): La requête HTTP reçue par le serveur.

    Returns:
        HttpResponse: La page permettant de sélectionner les compétences, ou une redirection.
    """
    if request.method == 'POST':
        selected_competences = request.POST.getlist('competences')
        request.user.profile.competences.set(selected_competences)
        return redirect('available_slots')
    competences = Competence.objects.all()
    return render(request, 'core/user_competences.html', {'competences': competences})


@login_required
def add_slot(request):
    """
    Permet à l'utilisateur de créer un créneau pour offrir ou demander de l'aide.

    Args:
        request (HttpRequest): La requête HTTP reçue par le serveur.

    Returns:
        HttpResponse: La page d'ajout de créneau ou une redirection vers 'my_slots'.
    """
    user_profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        # Récupérer les données du formulaire
        date = request.POST.get('date')
        competence_id = request.POST.get('competence')
        purpose = request.POST.get('purpose')
        competence = Competence.objects.get(id=competence_id)
        description = request.POST.get('description') if purpose == 'request' else None

        # Créer le créneau
        slot = Slot.objects.create(date=date, competence=competence, user=request.user, is_available=True,
                                   purpose=purpose)

        # Si c'est une demande d'aide, créer une activité avec la description
        if purpose == 'request' and description:
            Activity.objects.create(description=description, requester=request.user, competence_needed=competence,
                                    slot=slot)

        return redirect('my_slots')

    competences = user_profile.competences.all()
    return render(request, 'core/add_slot.html', {'competences': competences})

@login_required
def my_slots(request):
    """
    Affiche les créneaux de l'utilisateur, avec la possibilité de les supprimer.

    Args:
        request (HttpRequest): La requête HTTP reçue par le serveur.

    Returns:
        HttpResponse: La page listant les créneaux de l'utilisateur.
    """
    slots = Slot.objects.filter(user=request.user)
    return render(request, 'core/my_slots.html', {'slots': slots})


@login_required
def delete_slot(request, slot_id):
    """
    Supprime un créneau spécifique de l'utilisateur.

    Args:
        request (HttpRequest): La requête HTTP reçue par le serveur.
        slot_id (int): L'identifiant du créneau à supprimer.

    Returns:
        HttpResponseRedirect: Redirection vers 'my_slots' après suppression du créneau.
    """
    slot = get_object_or_404(Slot, id=slot_id, user=request.user)
    slot.delete()
    return redirect('my_slots')


@login_required
def help_requests(request):
    """
    Affiche les demandes d'aide d'autres utilisateurs dans une compétence que l'utilisateur actuel possède.

    Args:
        request (HttpRequest): La requête HTTP reçue par le serveur.

    Returns:
        HttpResponse: La page listant les demandes d'aide d'autres utilisateurs.
    """
    user_competences = request.user.profile.competences.all()
    help_requests = Activity.objects.filter(competence_needed__in=user_competences).exclude(requester=request.user)
    return render(request, 'core/help_requests.html', {'help_requests': help_requests})


@login_required
def my_requests(request):
    """
    Affiche les demandes d'aide créées par l'utilisateur connecté.

    Args:
        request (HttpRequest): La requête HTTP reçue par le serveur.

    Returns:
        HttpResponse: La page listant les demandes d'aide de l'utilisateur.
    """
    user_requests = Activity.objects.filter(requester=request.user)
    return render(request, 'core/my_requests.html', {'user_requests': user_requests})


@login_required
def available_help(request):
    """
    Affiche les créneaux disponibles où un autre utilisateur propose de l'aide dans une compétence que l'utilisateur actuel ne possède pas.

    Args:
        request (HttpRequest): La requête HTTP reçue par le serveur.

    Returns:
        HttpResponse: La page listant les créneaux d'aide disponibles.
    """
    user_competences = request.user.profile.competences.all()
    available_slots = Slot.objects.filter(is_available=True, purpose='aid').exclude(competence__in=user_competences)
    return render(request, 'core/available_help.html', {'available_slots': available_slots})


@login_required
def volunteer_for_help(request, activity_id):
    """
    Permet à l'utilisateur de se proposer pour aider sur une demande spécifique.

    Args:
        request (HttpRequest): La requête HTTP reçue par le serveur.
        activity_id (int): L'identifiant de la demande d'aide.

    Returns:
        HttpResponseRedirect: Redirection vers 'help_requests'.
    """
    activity = get_object_or_404(Activity, id=activity_id)
    activity.slot.is_available = False
    activity.slot.save()
    return redirect('help_requests')

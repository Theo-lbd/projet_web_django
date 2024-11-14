from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Slot, Profile, Competence, Activity, Category
from datetime import date


def available_slots(request):
    """
    Affiche la liste des créneaux disponibles pour l'aide, sans informations personnelles.

    Args:
        request (HttpRequest) : La requête HTTP reçue par le serveur.

    Returns :
        HttpResponse : La page affichant les créneaux disponibles.
    """
    slots = Slot.objects.filter(is_available=True, purpose='aid', date__gte=date.today())
    return render(request, 'core/available_slots.html', {'slots': slots})


def competence_list(request):
    """
    Affiche la liste des compétences regroupées par catégorie.

    Args:
        request (HttpRequest) : La requête HTTP reçue par le serveur.

    Returns :
        HttpResponse : La page affichant la liste des compétences par catégorie.
    """
    categories = Category.objects.all()
    return render(request, 'core/competence_list.html', {'categories': categories})


@login_required
def user_competences(request):
    """
    Permet à l'utilisateur de sélectionner les compétences qu'il possède.

    Args:
        request (HttpRequest) : La requête HTTP reçue par le serveur.

    Returns :
        HttpResponse : La page permettant de sélectionner les compétences, ou une redirection.
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
        request (HttpRequest) : La requête HTTP reçue par le serveur.

    Returns :
        HttpResponse : La page d'ajout de créneau ou une redirection vers 'my_slots'.
    """
    user_profile, created = Profile.objects.get_or_create(user=request.user)
    # Compétences que l'utilisateur possède
    competences = user_profile.competences.all()

    if request.method == 'POST':
        # Récupérer les données du formulaire
        date = request.POST.get('date')
        competence_id = request.POST.get('competence')
        purpose = request.POST.get('purpose')
        competence = get_object_or_404(Competence, id=competence_id)
        description = request.POST.get('description') if purpose == 'request' else None

        # Créer le créneau
        slot = Slot.objects.create(
            date=date,
            competence=competence,
            user=request.user,
            is_available=True,
            purpose=purpose
        )

        # Si c'est une demande d'aide, créer une activité avec la description
        if purpose == 'request' and description:
            Activity.objects.create(
                description=description,
                requester=request.user,
                competence_needed=competence,
                slot=slot
            )

        return redirect('my_slots')

    return render(request, 'core/add_slot.html', {'competences': competences})

@login_required
def my_slots(request):
    """
    Affiche les créneaux de l'utilisateur, avec la possibilité de les supprimer.

    Args:
        request (HttpRequest) : La requête HTTP reçue par le serveur.

    Returns :
        HttpResponse : La page listant les créneaux de l'utilisateur.
    """
    slots = Slot.objects.filter(user=request.user)
    return render(request, 'core/my_slots.html', {'slots': slots})


@login_required
def delete_slot(request, slot_id):
    """
    Supprime un créneau spécifique de l'utilisateur.

    Args:
        request (HttpRequest) : La requête HTTP reçue par le serveur.
        Slot_id (int): L'identifiant du créneau à supprimer.

    Returns :
        HttpResponseRedirect : Redirection vers 'my_slots' après suppression du créneau.
    """
    slot = get_object_or_404(Slot, id=slot_id, user=request.user)
    slot.delete()
    return redirect('my_slots')


from django.db.models import Q

@login_required
def help_requests(request):
    """
    Affiche les demandes d'aide d'autres utilisateurs dans une compétence que l'utilisateur actuel possède.

    Args:
        request (HttpRequest): La requête HTTP reçue par le serveur.

    Returns :
        HttpResponse : La page listant les demandes d'aide d'autres utilisateurs.
    """

    # Compétences que l'utilisateur possède
    user_competences = request.user.profile.competences.all()
    print(f"Compétences de l'utilisateur : {[comp.name for comp in user_competences]}")

    # Filtre les demandes d'aide disponibles ou celles où l'utilisateur est déjà volontaire
    help_requests = Activity.objects.filter(
        competence_needed__in=user_competences,
        slot__purpose='request',  # Vérifie que le créneau est une demande d'aide
    ).filter(
        Q(slot__is_available=True) | Q(volunteer=request.user)  # Inclut les créneaux disponibles ou où l'utilisateur est volontaire
    ).exclude(requester=request.user)

    print(f"Nombre de demandes d'aide récupérées : {help_requests.count()}")

    return render(request, 'core/help_requests.html', {'help_requests': help_requests})



@login_required
def my_requests(request):
    """
    Affiche les demandes d'aide créées par l'utilisateur connecté.

    Args:
        request (HttpRequest): La requête HTTP reçue par le serveur.

    Returns :
        HttpResponse : La page listant les demandes d'aide de l'utilisateur.
    """
    user_requests = Activity.objects.filter(requester=request.user)
    return render(request, 'core/my_requests.html', {'user_requests': user_requests})


@login_required
def available_help(request):
    """
    Affiche les créneaux disponibles où un autre utilisateur propose de l'aide dans une compétence que l'utilisateur actuel ne possède pas.

    Args:
        request (HttpRequest): La requête HTTP reçue par le serveur.

    Returns :
        HttpResponse : La page listant les créneaux d'aide disponibles.
    """

    # Compétences que l'utilisateur possède
    user_competences = request.user.profile.competences.all()

    # Créneaux disponibles pour des compétences que l'utilisateur ne possède pas
    available_slots = Slot.objects.filter(
        is_available=True,
        purpose='aid'
    ).exclude(competence__in=user_competences).exclude(user=request.user)

    return render(request, 'core/available_help.html', {'available_slots': available_slots})


@login_required
def volunteer_for_help(request, activity_id):
    """
    Permet à l'utilisateur de se proposer pour aider sur une demande spécifique.

    Args:
        request (HttpRequest): La requête HTTP reçue par le serveur.
        Activity_id (int): L'identifiant de l'activité pour laquelle l'utilisateur souhaite se proposer.

    Returns :
        HttpResponseRedirect : Redirection vers la page des demandes d'aide.
    """
    activity = get_object_or_404(Activity, id=activity_id)

    # Vérifie que l'utilisateur possède la compétence requise
    if activity.competence_needed not in request.user.profile.competences.all():
        return HttpResponseForbidden("Vous ne possédez pas la compétence requise pour cette activité.")

    # Enregistre l'utilisateur comme volontaire et rend le créneau indisponible
    activity.slot.is_available = False
    activity.slot.save()
    activity.volunteer = request.user
    activity.save()

    return redirect('help_requests')


@login_required
def contact_info(request, activity_id):
    """
    Affiche les informations de contact de l'autre utilisateur impliqué dans un créneau d'aide.

    Args:
        request (HttpRequest): La requête HTTP reçue par le serveur.
        Activity_id (int): L'identifiant de l'activité pour laquelle on souhaite afficher les informations de contact.

    Returns :
        HttpResponse: La page affichant les informations de contact de l'autre utilisateur.
        HttpResponseForbidden : Si l'utilisateur actuel n'est pas impliqué dans l'activité.
    """
    activity = get_object_or_404(Activity, id=activity_id)

    # Vérifie que l'utilisateur est impliqué dans l'activité
    if request.user != activity.requester and request.user != activity.volunteer:
        return HttpResponseForbidden("Vous n'avez pas accès à ces informations.")

    # Détermine l'autre utilisateur impliqué dans l'activité
    other_user = activity.volunteer if request.user == activity.requester else activity.requester
    return render(request, 'core/contact_info.html', {'other_user': other_user})

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings


class Category(models.Model):
    """
    Modèle représentant une catégorie de compétence.

    Attributes :
        name (CharField): Le nom de la catégorie.
    """
    name = models.CharField("Nom de la catégorie", max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"


class Competence(models.Model):
    """
    Modèle représentant une compétence.

    Attributes :
        name (CharField): Le nom de la compétence.
        Category (ForeignKey): La catégorie associée à cette compétence.
    """
    name = models.CharField("Nom de la compétence", max_length=100, unique=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='competences')

    def __str__(self):
        return self.name


class Slot(models.Model):
    """
    Modèle représentant un créneau de disponibilité d'un utilisateur.

    Attributes:
        date (DateField): La date du créneau.
        user (ForeignKey): L'utilisateur qui propose ou demande de l'aide.
        competence (ForeignKey): Compétence liée au créneau.
        is_available (BooleanField): Indicateur de disponibilité du créneau.
        purpose (CharField): Indique si le créneau est pour aider ou pour demander de l'aide.
    """
    PURPOSE_CHOICES = [
        ('aid', 'Pour aider'),
        ('request', 'Demande d’aide'),
    ]

    date = models.DateField("Date du créneau")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='slots')
    competence = models.ForeignKey('Competence', on_delete=models.CASCADE, related_name='slots')
    is_available = models.BooleanField("Disponible", default=True)
    purpose = models.CharField("Objectif", max_length=10, choices=PURPOSE_CHOICES, default='aid')

    def __str__(self):
        return f"{self.date} - {self.competence.name} - {'Disponible' if self.is_available else 'Indisponible'} - {self.get_purpose_display()}"


class Activity(models.Model):
    """
    Modèle représentant une activité pour laquelle un utilisateur peut demander de l'aide.

    Attributes:
        description (TextField): La description de l'activité.
        requester (ForeignKey): L'utilisateur demandant l'aide.
        competence_needed (ForeignKey): Compétence requise pour cette activité.
        slot (ForeignKey): Le créneau associé à la demande d'aide.
        volunteer (ForeignKey): L'utilisateur qui se propose pour aider.
    """
    description = models.TextField("Description de l'activité")
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requested_activities')
    competence_needed = models.ForeignKey(Competence, on_delete=models.CASCADE, related_name='activities')
    slot = models.ForeignKey('Slot', on_delete=models.CASCADE)
    volunteer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='volunteered_activities',
        verbose_name="Utilisateur qui se propose pour aider"
    )

    def __str__(self):
        return f"Activité : {self.description} - Compétence requise : {self.competence_needed.name}"

    class Meta:
        verbose_name = "Activité"
        verbose_name_plural = "Activités"


class Profile(models.Model):
    """
    Modèle représentant le profil d'un utilisateur, incluant ses compétences.

    Attributes:
        user (OneToOneField): L'utilisateur lié à ce profil.
        competences (ManyToManyField): Compétences que l'utilisateur possède et est prêt à offrir.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    competences = models.ManyToManyField('Competence', blank=True, related_name='profiles')

    def __str__(self):
        return f"Profil de {self.user.username}"


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Signal unique pour créer ou mettre à jour le profil de l'utilisateur.
    """
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()

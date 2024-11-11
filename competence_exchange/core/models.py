from django.db import models
from django.contrib.auth.models import User


class Competence(models.Model):
    name = models.CharField("Nom de la compétence", max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Compétence"
        verbose_name_plural = "Compétences"


class Slot(models.Model):
    date = models.DateField("Date du créneau")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='slots')
    competence = models.ForeignKey(Competence, on_delete=models.CASCADE, related_name='slots')
    is_available = models.BooleanField("Disponible", default=True)

    def __str__(self):
        return f"{self.date} - {self.competence.name} - {'Disponible' if self.is_available else 'Indisponible'}"

    class Meta:
        verbose_name = "Créneau"
        verbose_name_plural = "Créneaux"


class Activity(models.Model):
    description = models.TextField("Description de l'activité")
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requested_activities')
    competence_needed = models.ForeignKey(Competence, on_delete=models.CASCADE, related_name='activities')
    slot = models.ForeignKey(Slot, on_delete=models.CASCADE)

    def __str__(self):
        return f"Activité : {self.description} - Compétence requise : {self.competence_needed.name}"

    class Meta:
        verbose_name = "Activité"
        verbose_name_plural = "Activités"

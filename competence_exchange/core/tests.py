from django.test import TestCase
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from .models import Competence, Slot, Activity, Profile, Category, create_user_profile
from datetime import date


class CompetenceModelTest(TestCase):
    """
    Classe de test pour le modèle Competence.
    """

    def setUp(self):
        """
        Configuration initiale pour les tests du modèle Competence.
        """
        self.competence = Competence.objects.create(name="Informatique")

    def test_competence_creation(self):
        """
        Vérifie que la compétence est correctement créée avec le bon nom.
        """
        self.assertEqual(self.competence.name, "Informatique")

    def test_str_method(self):
        """
        Test de la méthode __str__ pour Competence.
        """
        self.assertEqual(str(self.competence), "Informatique")


class SlotModelTest(TestCase):
    """
    Classe de test pour le modèle Slot.
    """

    def setUp(self):
        """
        Configuration initiale pour les tests du modèle Slot.
        """
        self.user = User.objects.create_user(username="testuser")
        self.competence = Competence.objects.create(name="Jardinage")
        self.slot = Slot.objects.create(
            date=date.today(),
            user=self.user,
            competence=self.competence,
            is_available=True,
            purpose="aid"
        )

    def test_slot_creation(self):
        """
        Vérifie que le créneau est créé avec les bonnes informations.
        """
        self.assertEqual(self.slot.date, date.today())
        self.assertEqual(self.slot.user, self.user)
        self.assertEqual(self.slot.competence, self.competence)
        self.assertTrue(self.slot.is_available)
        self.assertEqual(self.slot.purpose, "aid")

    def test_str_method(self):
        """
        Test de la méthode __str__ pour Slot.
        """
        expected_str = f"{self.slot.date} - {self.competence.name} - Disponible - Pour aider"
        self.assertEqual(str(self.slot), expected_str)


class ActivityModelTest(TestCase):
    """
    Classe de test pour le modèle Activity.
    """

    def setUp(self):
        """
        Configuration initiale pour les tests du modèle Activity.
        """
        self.user_requester = User.objects.create_user(username="requester")
        self.competence_needed = Competence.objects.create(name="Bricolage")
        self.slot = Slot.objects.create(
            date=date.today(),
            user=self.user_requester,
            competence=self.competence_needed,
            is_available=True,
            purpose="request"
        )
        self.activity = Activity.objects.create(
            description="Réparation d'une étagère",
            requester=self.user_requester,
            competence_needed=self.competence_needed,
            slot=self.slot
        )

    def test_activity_creation(self):
        """
        Vérifie que l'activité est créée avec les bonnes informations.
        """
        self.assertEqual(self.activity.description, "Réparation d'une étagère")
        self.assertEqual(self.activity.requester, self.user_requester)
        self.assertEqual(self.activity.competence_needed, self.competence_needed)
        self.assertEqual(self.activity.slot, self.slot)

    def test_str_method(self):
        """
        Test de la méthode __str__ pour Activity.
        """
        expected_str = f"Activité : {self.activity.description} - Compétence requise : {self.competence_needed.name}"
        self.assertEqual(str(self.activity), expected_str)


class ProfileModelTest(TestCase):
    """
    Classe de test pour le modèle Profile.
    Teste la création de profils et l'ajout de compétences pour un utilisateur.
    """

    def setUp(self):
        """
        Configuration initiale pour chaque test de la classe ProfileModelTest.
        Crée un utilisateur et vérifie si un profil existe déjà pour cet utilisateur
        avant de créer ou d'ajouter des compétences au profil.
        """
        # Crée un utilisateur
        self.user = User.objects.create_user(username="profileuser")

        # Récupère ou crée un profil pour l'utilisateur
        self.profile, created = Profile.objects.get_or_create(user=self.user)

        # Crée une compétence et l'ajoute au profil
        self.competence = Competence.objects.create(name="Cuisine")
        self.profile.competences.add(self.competence)

    def test_profile_creation(self):
        """
        Vérifie que le profil est associé à l'utilisateur et est correctement créé.
        """
        self.assertEqual(self.profile.user, self.user)

    def test_add_competence(self):
        """
        Vérifie que les compétences peuvent être ajoutées au profil.
        """
        self.assertIn(self.competence, self.profile.competences.all())

    def test_str_method(self):
        """
        Test de la méthode __str__ pour Profile.
        Vérifie que la représentation sous forme de chaîne du profil est correcte.
        """
        expected_str = f"Profil de {self.user.username}"
        self.assertEqual(str(self.profile), expected_str)


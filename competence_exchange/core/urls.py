from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('creaneaux-disponibles/', views.available_slots, name='available_slots'),
    path('competences/', views.competence_list, name='competence_list'),
    path('connexion/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('deconnexion/', auth_views.LogoutView.as_view(), name='logout'),
    path('mes-competences/', views.user_competences, name='user_competences'),
    path('mes-creneaux/', views.my_slots, name='my_slots'),
    path('supprimer-creneau/<int:slot_id>/', views.delete_slot, name='delete_slot'),
    path('ajouter-creneau/', views.add_slot, name='add_slot'),
    path('demandes-aide/', views.help_requests, name='help_requests'),
    path('mes-demandes/', views.my_requests, name='my_requests'),
    path('aide-disponible/', views.available_help, name='available_help'),
    path('contact-info/<int:activity_id>/', views.contact_info, name='contact_info'),
    path('se-proposer-aide/<int:activity_id>/', views.volunteer_for_help, name='volunteer_for_help'),

]


from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('creaneaux-disponibles/', views.available_slots, name='available_slots'),
    path('competences/', views.competence_list, name='competence_list'),
    path('connexion/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('deconnexion/', auth_views.LogoutView.as_view(), name='logout'),
    path('mes-competences/', views.user_competences, name='user_competences'),

]


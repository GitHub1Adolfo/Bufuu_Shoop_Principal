from django.urls import path
from . import views

urlpatterns = [
     path('boleta/', views.boleta_view, name='boleta'),
]

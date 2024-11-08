from django.urls import path
from .views import get_countries, get_states, get_cities

urlpatterns = [
    path('countries/', get_countries, name='get_countries'),
    path('states/<str:country_code>/', get_states, name='get_states'),
    path('cities/<str:state_code>/', get_cities, name='get_cities'),
]

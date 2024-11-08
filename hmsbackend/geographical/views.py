from django.shortcuts import render
import requests
from django.http import JsonResponse


def get_countries(request):
    response = requests.get('https://restcountries.com/v3.1/all')
    countries = response.json()
    country_list = [{"name": country["name"]["common"],
                     "code": country["cca2"]} for country in countries]
    return JsonResponse(country_list, safe=False)


def get_states(request, country_code):
    # You'll need a method to fetch states; this data isn't available from the REST Countries API.
    # Consider a static list or another API.
    return JsonResponse([])  # Placeholder for now.


def get_cities(request, state_code):
    # Similar to states, you'll need to find a source for cities.
    return JsonResponse([])  # Placeholder for now.

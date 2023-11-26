import requests
from geopy.distance import distance
from django.conf import settings


def fetch_coordinates(address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": settings.YANDEX_GEOCODER_API_TOKEN,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lat, lon


def calculate_distance(place_from, place_to):
    place_from = fetch_coordinates(place_from)
    place_to = fetch_coordinates(place_to)
    if place_from is None or place_to is None:
        return None
    return distance(place_from, place_to).kilometers

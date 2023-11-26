import requests
from django.conf import settings

from location.models import Location


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


def get_coordinates(address, locations):
    for location in locations:
        if address == location.address:
            lat, lon = location.lat, location.lon
            return lat, lon

    location = fetch_coordinates(address)

    if location is None:
        return None
    else:
        lat, lon = location[0], location[1]
        Location.objects.create(address=address, lat=lat, lon=lon)
        return lat, lon

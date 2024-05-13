#Création de la classe Capteur

import orekit
from orekit.pyhelpers import setup_orekit_curdir, download_orekit_data_curdir
from org.orekit.frames import FramesFactory, TopocentricFrame
from org.orekit.bodies import OneAxisEllipsoid, GeodeticPoint
from org.orekit.utils import Constants, IERSConventions
import math
from pytz import timezone as pytz_timezone

# Initialisation de Orekit
orekit.initVM()

# Définition du référentiel
ITRF = FramesFactory.getITRF(IERSConventions.IERS_2010, True)
earth = OneAxisEllipsoid(Constants.WGS84_EARTH_EQUATORIAL_RADIUS,Constants.WGS84_EARTH_FLATTENING,ITRF)

class Capteur:
    def __init__(self, latitude, longitude, altitude, aperture, focal_ratio, max_speed, max_acceleration, timezone_name, name):
        # Conversion des coordonnées en radians
        self.latitude = math.radians(latitude)
        self.longitude = math.radians(longitude)
        self.altitude = altitude  # Stockage de l'altitude

        # Ajout des nouveaux attributs
        self.aperture = aperture
        self.focal_ratio = focal_ratio
        self.max_speed = max_speed
        self.max_acceleration = max_acceleration

        # Ajout du fuseau horaire
        self.timezone_name = timezone_name

        self.name = name

    def get_altitude(self):
        # Retourne l'altitude en mètres
        return self.altitude

    def get_latitude(self):
        # Retourne la latitude en radians
        return self.latitude

    def get_longitude(self):
        # Retourne la longitude en radians
        return self.longitude

    def get_aperture(self):
        # Retourne l'ouverture en mètres
        return self.aperture

    def get_focal_ratio(self):
        # Retourne le rapport de focale
        return self.focal_ratio

    def get_max_speed(self):
        # Retourne la vitesse maximale en degrés par seconde
        return self.max_speed

    def get_max_acceleration(self):
        # Retourne l'accélération maximale en degrés par seconde carrée
        return self.max_acceleration

    def get_timezone(self):
        # Retourne le fuseau horaire
        return self.timezone

    def get_name(self):
        # Retourne le nom
        return self.name

    def to_dict(self):
        return {
            "name": self.name,
            "lon": math.degrees(self.longitude),
            "lat": math.degrees(self.latitude),
            "alt": self.altitude,
            "timezone": self.timezone_name,
            "aperture": self.aperture,
            "focal_ratio": self.focal_ratio,
            "max_speed": self.max_speed,
            "max_acceleration": self.max_acceleration
        }

# Création d'une instance de Capteur
capteur = Capteur(48.8534, 2.3488, 35.0, 0.25, 3.2, 60, 120, "Europe/Paris", "Paris"),
#print(capteur.get_altitude())
#print(capteur.get_latitude())
#print(capteur.get_longitude())
#print(capteur.get_aperture())
#print(capteur.get_focal_ratio())
#print(capteur.get_max_speed())
#print(capteur.get_max_acceleration())

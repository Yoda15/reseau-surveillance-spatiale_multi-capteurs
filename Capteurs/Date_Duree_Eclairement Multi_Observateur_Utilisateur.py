import math
from math import radians, degrees, pi
import orekit
import pytz
from astral import LocationInfo
from astral.sun import sun as astral_sun
from orekit.pyhelpers import setup_orekit_curdir, download_orekit_data_curdir
from org.hipparchus.geometry.euclidean.threed import Vector3D
from org.orekit.frames import FramesFactory, TopocentricFrame
from org.orekit.bodies import OneAxisEllipsoid, GeodeticPoint, CelestialBodyFactory
from org.orekit.utils import Constants, IERSConventions
from org.orekit.time import AbsoluteDate, TimeScalesFactory, DateComponents, TimeComponents
from org.orekit.propagation.analytical.tle import TLE, TLEPropagator
from org.orekit.propagation.events import EclipseDetector
from datetime import datetime, timedelta, timezone
from pytz import timezone as pytz_timezone

# Initialisation de Orekit
orekit.initVM()

# Configuration d'Orekit et téléchargement des données
setup_orekit_curdir()
download_orekit_data_curdir()

def calculate_angular_velocity(observer_frame, pv_provider, orekit_date, delta_t):
    # Get the position of the satellite at two different times
    pv1 = pv_provider.getPVCoordinates(orekit_date, observer_frame)
    pv2 = pv_provider.getPVCoordinates(orekit_date.shiftedBy(delta_t), observer_frame)

    # Calculate the directional vectors
    direction_vector1 = pv1.getPosition()
    direction_vector2 = pv2.getPosition()

    # Check if either of the directional vectors is a zero vector
    if direction_vector1.getNorm() == 0 or direction_vector2.getNorm() == 0:
        return 0

    # Calculate the angle between the two direction vectors (in radians)
    dot_product = Vector3D.dotProduct(direction_vector1, direction_vector2)
    magnitude_product = direction_vector1.getNorm() * direction_vector2.getNorm()
    cos_angle = dot_product / magnitude_product
    angle_radians = math.acos(cos_angle)

    # Convert the angle from radians to degrees
    angle_degrees = angle_radians * 180.0 / pi

    # Calculate the angular velocity (degrees per second)
    angular_velocity = angle_degrees / delta_t

    return angular_velocity

# Définition du référentiel
ITRF = FramesFactory.getITRF(IERSConventions.IERS_2010, True)
earth = OneAxisEllipsoid(Constants.WGS84_EARTH_EQUATORIAL_RADIUS, Constants.WGS84_EARTH_FLATTENING, ITRF)

# Heures de début et de fin d'observation pour chaque jour (en heures locales)
observation_times = {
    0: (0.0, 23.99),
    1: (0.0, 23.99),
    2: (0.0, 23.99),
}

from Automatic_TLE_Injector import fetch_and_propagate_tle

norad_number = 25544  # ISS
propagator = fetch_and_propagate_tle(norad_number)

# Création du détecteur d'éclipse
sun = CelestialBodyFactory.getSun()
eclipse_detector = EclipseDetector(sun, Constants.SUN_RADIUS, earth)

from Classe_Telescope import Capteur

# Demander à l'utilisateur le nombre de capteurs
num_sensors = int(input("Entrez le nombre de capteurs : "))

# Créer une liste pour stocker les capteurs
capteurs = []

# Demander à l'utilisateur les détails de chaque capteur
for i in range(num_sensors):
    name = input(f"Entrez le nom du capteur {i + 1} : ")
    lon = float(input(f"Entrez la longitude du capteur {i + 1} : "))
    lat = float(input(f"Entrez la latitude du capteur {i + 1} : "))
    alt = float(input(f"Entrez l'altitude du capteur {i + 1} : "))
    aperture = float(input(f"Entrez l'ouverture du capteur {i + 1} : "))
    focal_ratio = float(input(f"Entrez le rapport de focale du capteur {i + 1} : "))
    max_speed = float(input(f"Entrez la vitesse maximale du capteur {i + 1} : "))
    max_acceleration = float(input(f"Entrez l'accélération maximale du capteur {i + 1} : "))
    timezone_name = input(f"Entrez le fuseau horaire du capteur {i + 1} (Ex: Europe/Paris ou America/New_York): ")

    # Créer un nouvel objet Capteur et l'ajouter à la liste
    capteurs.append(Capteur(lat, lon, alt, aperture, focal_ratio, max_speed, max_acceleration, timezone_name, name))

# Conversion des capteurs en observateurs
observers = [capteur.to_dict() for capteur in capteurs]

# Affichage des observateurs
for observer in observers:
    print(observer)


for observer in observers:
    # Définition de l'observateur
    observer_lon = observer["lon"]
    observer_lat = observer["lat"]
    observer_alt = observer["alt"]
    observer_point = GeodeticPoint(radians(observer_lat), radians(observer_lon), observer_alt)
    observer["frame"] = TopocentricFrame(earth, observer_point, observer["name"])
    observer_timezone = pytz.timezone(observer["timezone"])
    location = LocationInfo("custom", "region", observer_timezone, observer_lat, observer_lon)
    s = astral_sun(location.observer, date=datetime.now(timezone.utc))


# Liste pour stocker les durées d'observabilité pour chaque jour de la semaine
pass_times = {observer["name"]: {day: [] for day in range(3)} for observer in observers}

# Création de la date actuelle
current_datetime = datetime.now(timezone.utc)

# Définition de l'échelle de temps UTC pour Orekit
utc = TimeScalesFactory.getUTC()

# Parcourir plusieurs jours
for day_of_week in range(3):
    observation_start_hour, observation_end_hour = observation_times[day_of_week]

    # Définir l'heure de début et de fin pour la journée actuelle
    start_of_day = current_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
    observation_start_time = start_of_day + timedelta(hours=observation_start_hour)
    observation_end_time = start_of_day + timedelta(hours=observation_end_hour)

    # Convertir la date de début Python en date Orekit
    date_comp = DateComponents(observation_start_time.year, observation_start_time.month, observation_start_time.day)
    time_comp = TimeComponents(observation_start_time.hour, observation_start_time.minute,
                               observation_start_time.second + observation_start_time.microsecond / 1e6)
    observation_start_date = AbsoluteDate(date_comp, time_comp, utc)

    # Convertir la date de fin Python en date Orekit
    end_date_comp = DateComponents(observation_end_time.year, observation_end_time.month, observation_end_time.day)
    end_time_comp = TimeComponents(observation_end_time.hour, observation_end_time.minute,
                                   observation_end_time.second + observation_end_time.microsecond / 1e6)
    observation_end_date = AbsoluteDate(end_date_comp, end_time_comp, utc)

    # Propagation and elevation event detection for the current day
    orekit_date = observation_start_date
    while orekit_date.compareTo(observation_end_date) <= 0:
        state = propagator.propagate(orekit_date)
        position = state.getPVCoordinates().getPosition()
        frame = state.getFrame()

        # Check if the satellite is illuminated by the sun
        is_eclipsed = eclipse_detector.g(state) <= 0

        for observer in observers:
            elevation = observer["frame"].getElevation(position, frame, orekit_date) * 180.0 / pi

            # Check if the observer is in darkness
            observer_timezone = pytz.timezone(observer["timezone"])
            location = LocationInfo("custom", "region", observer_timezone, observer["lat"], observer["lon"])
            s = astral_sun(location.observer, date=datetime.fromtimestamp(
                orekit_date.toDate(TimeScalesFactory.getUTC()).getTime() / 1000.0))
            orekit_date_datetime = datetime.fromtimestamp(
                orekit_date.toDate(TimeScalesFactory.getUTC()).getTime() / 1000.0, tz=pytz_timezone('UTC'))
            is_night = s['sunset'] <= orekit_date_datetime or orekit_date_datetime <= s['sunrise']

            # Calculate the angular velocity
            delta_t = 1.0  # Time interval between two positions (in seconds)
            angular_velocity = calculate_angular_velocity(observer["frame"], propagator, orekit_date, delta_t)

            # Check if the angular velocity and acceleration are within limits
            if elevation >= 10 and not is_eclipsed and is_night and angular_velocity <= observer["max_speed"]:
                pass_times[observer["name"]][day_of_week].append(orekit_date)
                # print("angular velocity =", angular_velocity, "deg/s")

        # Update the Orekit date here
        orekit_date = orekit_date.shiftedBy(10.0)


    # Mise à jour de la date actuelle pour chaque nouveau jour
    current_datetime = current_datetime + timedelta(days=1)

    # Afficher les heures de passage pour chaque jour de la semaine
for observer in observers:
    print(f"{observer['name']}:")

    for day, times in pass_times[observer["name"]].items():
        print(f"Jour {day}: Heures de passage =")
        if times:
            start_time = times[0]
            end_time = start_time
            for time in times[1:]:
                if (time.durationFrom(end_time)) > (timedelta(
                        minutes=2).total_seconds()):  # Vérifie si la durée entre les passages est supérieure à 2 minutes
                    duration_seconds = end_time.durationFrom(start_time)
                    duration_minutes, duration_seconds = divmod(duration_seconds, 60)
                    duration_hours, duration_minutes = divmod(duration_minutes, 60)
                    print(
                        f"Début : {start_time.toString()} - Fin : {end_time.toString()} - Durée : {int(duration_hours)}:{int(duration_minutes):02}:{int(duration_seconds)}")
                    start_time = time
                end_time = time

            duration_seconds = end_time.durationFrom(start_time)
            duration_minutes, duration_seconds = divmod(duration_seconds, 60)
            duration_hours, duration_minutes = divmod(duration_minutes, 60)
            print(
                f"Début : {start_time.toString()} - Fin : {end_time.toString()} - Durée : {int(duration_hours)}:{int(duration_minutes):02}:{int(duration_seconds)}")

        print()



# Créer une liste pour stocker toutes les durées d'observation
all_pass_times = []

# Convertir AbsoluteDate en datetime
def absolute_date_to_datetime(absolute_date):
    return datetime.fromtimestamp(absolute_date.toDate(TimeScalesFactory.getUTC()).getTime() / 1000.0, tz=pytz_timezone('UTC'))

# Ajouter les durées d'observation à all_pass_times
for day_of_week in range(3):
    for observer in observers:
        times = pass_times[observer["name"]][day_of_week]
        if times:
            start_time = times[0]
            end_time = start_time
            for time in times[1:]:
                if (time.durationFrom(end_time)) > (timedelta(minutes=2).total_seconds()):
                    all_pass_times.append((absolute_date_to_datetime(start_time), absolute_date_to_datetime(end_time), observer["name"], day_of_week))
                    start_time = time
                end_time = time
            all_pass_times.append((absolute_date_to_datetime(start_time), absolute_date_to_datetime(end_time), observer["name"], day_of_week))

# Trier toutes les durées d'observation par heure de début
all_pass_times.sort(key=lambda x: x[0])

# Afficher toutes les durées d'observation
for day_of_week in range(3):
    print(f"Jour {day_of_week}: Heures de passage =")
    for start_time, end_time, observer_name, day in all_pass_times:
        if day == day_of_week:
            duration = end_time - start_time
            duration_seconds = duration.total_seconds()
            duration_minutes, duration_seconds = divmod(duration_seconds, 60)
            duration_hours, duration_minutes = divmod(duration_minutes, 60)
            print(f"Début : {start_time.isoformat()} - Fin : {end_time.isoformat()} - Durée : {int(duration_hours)}:{int(duration_minutes):02}:{int(duration_seconds)}  ({observer_name})")
    print()

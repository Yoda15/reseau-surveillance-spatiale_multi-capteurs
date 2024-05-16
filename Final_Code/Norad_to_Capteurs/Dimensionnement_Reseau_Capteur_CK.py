import math
from math import radians, degrees, pi
import orekit
import pytz
import xlrd
from astral import LocationInfo
from astral.sun import sun as astral_sun
from matplotlib import pyplot as plt
from orekit.pyhelpers import setup_orekit_curdir, download_orekit_data_curdir
from org.hipparchus.geometry.euclidean.threed import Vector3D
from org.orekit.frames import FramesFactory, TopocentricFrame
from org.orekit.bodies import OneAxisEllipsoid, GeodeticPoint, CelestialBodyFactory
from org.orekit.propagation.analytical import KeplerianPropagator
from org.orekit.utils import Constants, IERSConventions
from org.orekit.time import AbsoluteDate, TimeScalesFactory, DateComponents, TimeComponents
from org.orekit.propagation.analytical.tle import TLE, TLEPropagator
from org.orekit.propagation.events import EclipseDetector
from datetime import datetime, timedelta, timezone
from pytz import timezone as pytz_timezone

# Initialisation de Orekit
orekit.initVM()

# Configuration d'Orekit et téléchargement des données
# download_orekit_data_curdir()
setup_orekit_curdir()

def calculate_angular_velocity(observer_frame, pv_provider, orekit_date, delta_t):
    # Récuperer les positions du satellites à 2 moments différents
    pv1 = pv_provider.getPVCoordinates(orekit_date, observer_frame)
    pv2 = pv_provider.getPVCoordinates(orekit_date.shiftedBy(delta_t), observer_frame)

    # Calculer le vecteur directionel
    direction_vector1 = pv1.getPosition()
    direction_vector2 = pv2.getPosition()

    # Vérifier si 1 vecteur est nul
    if direction_vector1.getNorm() == 0 or direction_vector2.getNorm() == 0:
        return 0

    # Calculer en rad l'angle entre vecteurs
    dot_product = Vector3D.dotProduct(direction_vector1, direction_vector2)
    magnitude_product = direction_vector1.getNorm() * direction_vector2.getNorm()
    cos_angle = dot_product / magnitude_product
    angle_radians = math.acos(cos_angle)

    angle_degrees = angle_radians * 180.0 / pi

    # Calculer la vitesse angulaire
    angular_velocity = angle_degrees / delta_t

    return angular_velocity

# Définition du référentiel
ITRF = FramesFactory.getITRF(IERSConventions.IERS_2010, True)
earth = OneAxisEllipsoid(Constants.WGS84_EARTH_EQUATORIAL_RADIUS, Constants.WGS84_EARTH_FLATTENING, ITRF)

# Définition du nombre de jours
num_days = 3

# Heures de début et de fin d'observation pour chaque jour (en heures locales)
observation_times = {}
for day in range(num_days):
    observation_times[day] = (0.0, 23.99)

from Automatic_CK_Injector import fetch_and_propagate_CK
norad_number = 25544  # ISS
#norad_number = 39070 #TDRS 11 (GEO)
#norad_number = 43567 #Galileo
propagator = fetch_and_propagate_CK(norad_number)

# Création du détecteur d'éclipse
sun = CelestialBodyFactory.getSun()
eclipse_detector = EclipseDetector(sun, Constants.SUN_RADIUS, earth)

from Classe_Telescope import Capteur

# Définition des capteurs
capteurs = [
    Capteur(48.8534, 2.3488, 35.0, 0.25, 3.2, 60, 120, "Europe/Paris", "Paris"),
    Capteur(52.5200, 13.4050, 35.0, 0.25, 3.2, 60, 120, "Europe/Berlin", "Berlin"),
    Capteur(55.7558, 37.6176, 35.0, 0.25, 3.2, 60, 120, "Europe/Moscow", "Moscow"),
    Capteur(30.0444, 31.2357, 35.0, 0.25, 3.2, 60, 120, "Africa/Cairo", "Cairo"),
    Capteur(40.7128, -74.0060, 35.0, 0.25, 3.2, 60, 120, "America/New_York", "New York"),
    Capteur(-33.8688, 151.2093, 35.0, 0.25, 3.2, 60, 120, "Australia/Sydney", "Sydney"),
    Capteur(-23.5475, -46.6361, 35.0, 0.25, 3.2, 60, 120, "America/Sao_Paulo", "Sao Paulo"),
    Capteur(28.6139, 77.2090, 35.0, 0.25, 3.2, 60, 120, "Asia/Kolkata", "Kolkata"),
    Capteur(35.6895, 139.6917, 35.0, 0.25, 3.2, 60, 120, "Asia/Tokyo", "Tokyo"),
    Capteur(-34.6037, -58.3816, 35.0, 0.25, 3.2, 60, 120, "America/Argentina/Buenos_Aires", "Buenos Aires"),
    Capteur(25.0330, 121.5654, 35.0, 0.25, 3.2, 60, 120, "Asia/Taipei", "Taipei"),
    Capteur(-18.1423, -70.2350, 35.0, 0.25, 3.2, 60, 120, "America/Lima", "Lima"),
    Capteur(51.5074, -0.1278, 35.0, 0.25, 3.2, 60, 120, "Europe/London", "London"),
    Capteur(36.0999, 101.4238, 35.0, 0.25, 3.2, 60, 120, "Asia/Shanghai", "Shanghai"),
    Capteur(-25.7463, 28.1953, 35.0, 0.25, 3.2, 60, 120, "Africa/Johannesburg", "Johannesburg"),
    Capteur(37.7749, -122.4194, 35.0, 0.25, 3.2, 60, 120, "America/Los_Angeles", "Los Angeles"),
    Capteur(55.6761, 12.5683, 35.0, 0.25, 3.2, 60, 120, "Europe/Copenhagen", "Copenhagen"),
    Capteur(-36.8485, 174.7633, 35.0, 0.25, 3.2, 60, 120, "Pacific/Auckland", "Auckland"),
    Capteur(1.2833, 103.8333, 35.0, 0.25, 3.2, 60, 120, "Asia/Singapore", "Singapore"),
    Capteur(-34.9287, -56.1645, 35.0, 0.25, 3.2, 60, 120, "America/Montevideo", "Montevideo"),
    Capteur(56.1304, 106.3468, 35.0, 0.25, 3.2, 60, 120, "Asia/Novosibirsk", "Novosibirsk"),
    Capteur(-12.0464, -77.0428, 35.0, 0.25, 3.2, 60, 120, "America/Lima", "Lima"),
    Capteur(32.0853, 34.7818, 35.0, 0.25, 3.2, 60, 120, "Asia/Jerusalem", "Jerusalem"),
    Capteur(37.5665, 126.9780, 35.0, 0.25, 3.2, 60, 120, "Asia/Seoul", "Seoul"),
    Capteur(24.8864, 67.0211, 35.0, 0.25, 3.2, 60, 120, "Asia/Karachi", "Karachi"),
    Capteur(-23.5505, -46.6333, 35.0, 0.25, 3.2, 60, 120, "America/Sao_Paulo", "Sao Paulo"),
    Capteur(43.7728, 11.2564, 35.0, 0.25, 3.2, 60, 120, "Europe/Rome", "Rome"),
    Capteur(22.3193, 114.1694, 35.0, 0.25, 3.2, 60, 120, "Asia/Hong_Kong", "Hong Kong"),
    Capteur(23.1291, 113.2644, 35.0, 0.25, 3.2, 60, 120, "Asia/Macau", "Macau"),
    Capteur(14.5995, -90.6720, 35.0, 0.25, 3.2, 60, 120, "America/Guatemala", "Guatemala City")
]
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
pass_times = {observer["name"]: {day: [] for day in range(num_days)} for observer in observers}

# Création de la date actuelle
current_datetime = datetime.now(timezone.utc)

# Définition de l'échelle de temps UTC pour Orekit
utc = TimeScalesFactory.getUTC()

# Parcourir plusieurs jours
for day_of_week in range(num_days):
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

        # Vérifier si le satellite est éclairé par le soleil
        is_eclipsed = eclipse_detector.g(state) <= 0

        for observer in observers:
            elevation = observer["frame"].getElevation(position, frame, orekit_date) * 180.0 / pi

            # Vérifier si l'observateur est à l'ombre
            observer_timezone = pytz.timezone(observer["timezone"])
            location = LocationInfo("custom", "region", observer_timezone, observer["lat"], observer["lon"])
            s = astral_sun(location.observer, date=datetime.fromtimestamp(
                orekit_date.toDate(TimeScalesFactory.getUTC()).getTime() / 1000.0))
            orekit_date_datetime = datetime.fromtimestamp(
                orekit_date.toDate(TimeScalesFactory.getUTC()).getTime() / 1000.0, tz=pytz_timezone('UTC'))
            is_night = s['sunset'] <= orekit_date_datetime or orekit_date_datetime <= s['sunrise']

            # Calculer la vitesse angulaire
            delta_t = 1.0  # Interval entre 2 positions
            angular_velocity = calculate_angular_velocity(observer["frame"], propagator, orekit_date, delta_t)

            # Vérifier que la vitesse angulaire et la position n'est pas hors limite
            if elevation >= 10 and not is_eclipsed and is_night and angular_velocity <= observer["max_speed"]:
                pass_times[observer["name"]][day_of_week].append(orekit_date)

        # Mettre à jour les données orekit
        orekit_date = orekit_date.shiftedBy(10.0)

    # Mise à jour de la date actuelle pour chaque nouveau jour
    current_datetime = current_datetime + timedelta(days=1)

# Afficher les heures de passage pour chaque jour de la semaine
for observer in observers:
    print(f"{observer['name']}:")

    for day, times in pass_times[observer["name"]].items():
        if day < num_days:
            print(f"Jour {day}: Heures de passage =")
            if times:
                start_time = times[0]
                end_time = start_time
                for time in times[1:]:
                    if (time.durationFrom(end_time)) > (timedelta(
                            minutes=2).total_seconds()):  # Vérifie si la durée entre les passages est supérieure à 2 minutes (permet d'avoir des durées de plus de 10s)
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
    return datetime.fromtimestamp(absolute_date.toDate(TimeScalesFactory.getUTC()).getTime() / 1000.0,
                                  tz=pytz_timezone('UTC'))

# Ajouter les durées d'observation à all_pass_times
for day_of_week in range(num_days):
    for observer in observers:
        times = pass_times[observer["name"]][day_of_week]
        if times:
            start_time = times[0]
            end_time = start_time
            for time in times[1:]:
                if (time.durationFrom(end_time)) > (timedelta(minutes=2).total_seconds()):
                    all_pass_times.append((absolute_date_to_datetime(start_time), absolute_date_to_datetime(end_time),
                                           observer["name"], day_of_week))
                    start_time = time
                end_time = time
            all_pass_times.append((absolute_date_to_datetime(start_time), absolute_date_to_datetime(end_time),
                                   observer["name"], day_of_week))

# Trier toutes les durées d'observation par heure de début
all_pass_times.sort(key=lambda x: x[0])

# Afficher toutes les durées d'observation
for day_of_week in range(num_days):
    print(f"Jour {day_of_week}: Heures de passage =")
    for start_time, end_time, observer_name, day in all_pass_times:
        if day == day_of_week:
            duration = end_time - start_time
            duration_seconds = duration.total_seconds()
            duration_minutes, duration_seconds = divmod(duration_seconds, 60)
            duration_hours, duration_minutes = divmod(duration_minutes, 60)
            print(
                f"Début : {start_time.isoformat()} - Fin : {end_time.isoformat()} - Durée : {int(duration_hours)}:{int(duration_minutes):02}:{int(duration_seconds)}  ({observer_name})")
    print()

print("\n---------------------------------------------------------------------Test Dimensionnement---------------------------------------------------")


def display_pass_times_fixed_periods(all_pass_times, period_duration):
    # Trier toutes les durées d'observation par heure de début
    all_pass_times.sort(key=lambda x: x[0])

    # Afficher toutes les durées d'observation
    for day_of_week in range(num_days):
        print(f"Jour {day_of_week % 7}:")

        # Définir les heures de début et de fin de la journée
        start_of_day = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=day_of_week)
        end_of_day = start_of_day + timedelta(days=1)

        # Diviser la journée en périodes
        period_start_time = start_of_day
        while period_start_time < end_of_day:
            period_end_time = period_start_time + period_duration
            period_observers = {}

            for start_time, end_time, observer_name, day in all_pass_times:
                if day == day_of_week % 7 and start_time < period_end_time and end_time > period_start_time:
                    # Cette observation est dans la période actuelle
                    if observer_name not in period_observers:
                        period_observers[observer_name] = []
                    # Vérifier si le passage actuel est déjà dans la liste des passages du capteur
                    if (start_time, end_time) not in period_observers[observer_name]:
                        period_observers[observer_name].append((start_time, end_time))

            # Afficher la période actuelle
            print(f"Période {period_start_time} à {period_end_time}:")
            print(f"Nombre de capteurs disponibles : {len(period_observers)} ({', '.join(period_observers.keys())})")
            for observer_name, times in period_observers.items():
                for start, end in times:
                    duration = end - start
                    print(f"{observer_name}: Début : {start.isoformat()} - Fin : {end.isoformat()} - Durée : {duration}")
            print()

            # Passer à la période suivante
            period_start_time = period_end_time

display_pass_times_fixed_periods(all_pass_times, timedelta(hours=6))



print("\n----------------------------------------------------------------------Liste capteur nécessaire----------------------------------------------------")


from itertools import combinations

def find_minimal_sensors_per_day(all_pass_times, period_duration):
    # Trier toutes les durées d'observation par heure de début
    all_pass_times.sort(key=lambda x: x[0])

    # Afficher toutes les durées d'observation
    for day_of_week in range(num_days):
        #print(f"\nJour {day_of_week % 7}:")
        f.write("\nJour" + str(day_of_week % 7) )

        # Définir les heures de début et de fin de la journée
        start_of_day = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=day_of_week)
        end_of_day = start_of_day + timedelta(days=1)

        # Diviser la journée en périodes
        period_start_time = start_of_day
        periods = []
        while period_start_time < end_of_day:
            period_end_time = period_start_time + period_duration
            periods.append((period_start_time, period_end_time))

            # Passer à la période suivante
            period_start_time = period_end_time

        # Trouver toutes les combinaisons de capteurs pour cette journée
        all_sensors = set([observer_name for _, _, observer_name, _ in all_pass_times])
        for num_sensors in range(1, len(periods) + 1):  # Change here to limit the number of sensors to the number of periods
            for sensors in combinations(all_sensors, num_sensors):
                # Vérifier si ces capteurs peuvent couvrir toutes les périodes
                can_cover_all_periods = True
                for period_start_time, period_end_time in periods:
                    can_cover_period = False
                    for start_time, end_time, observer_name, day in all_pass_times:
                        if day == day_of_week % 7 and observer_name in sensors and start_time < period_end_time and end_time > period_start_time:
                            can_cover_period = True
                            break
                    if not can_cover_period:
                        can_cover_all_periods = False
                        break

                if can_cover_all_periods:
                    f.write("\n" + str(num_sensors) + " capteur(s) nécessaire(s) : "+ str(sensors))


# find_minimal_sensors_per_day(all_pass_times, timedelta(hours=6))

#Fichier txt
nom = 'Capteur nécessaire.txt'
f=open(nom,'w')


CP = find_minimal_sensors_per_day(all_pass_times, timedelta(hours=6))


#Fermeture du txt
f.close()


#dimensioner le reseau en fonction du nombre de capteurs minimum en fonction du timedelta
print("\n----------------------------------------------------------------------Dimensionnement Reseau----------------------------------------------------")

def find_minimal_sensors_per_day(all_pass_times, period_duration):
    # Trier toutes les durées d'observation par heure de début
    all_pass_times.sort(key=lambda x: x[0])

    # Liste pour stocker le nombre minimum de capteurs pour chaque jour
    min_sensors_per_day = []

    # Parcourir chaque jour
    for day_of_week in range(num_days):
        # Définir les heures de début et de fin de la journée
        start_of_day = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=day_of_week)
        end_of_day = start_of_day + timedelta(days=1)

        # Diviser la journée en périodes
        period_start_time = start_of_day
        periods = []
        while period_start_time < end_of_day:
            period_end_time = period_start_time + period_duration
            periods.append((period_start_time, period_end_time))
            period_start_time = period_end_time

        # Trouver toutes les combinaisons de capteurs pour cette journée
        all_sensors = set([observer_name for _, _, observer_name, _ in all_pass_times])
        min_sensors = float('inf')
        for num_sensors in range(1, len(periods) + 1):
            for sensors in combinations(all_sensors, num_sensors):
                # Vérifier si ces capteurs peuvent couvrir toutes les périodes
                can_cover_all_periods = True
                for period_start_time, period_end_time in periods:
                    can_cover_period = False
                    for start_time, end_time, observer_name, day in all_pass_times:
                        if day == day_of_week % 7 and observer_name in sensors and start_time < period_end_time and end_time > period_start_time:
                            can_cover_period = True
                            break
                    if not can_cover_period:
                        can_cover_all_periods = False
                        break

                if can_cover_all_periods:
                    # Ajouter le nombre de capteurs à la liste et arrêter de chercher d'autres combinaisons pour ce jour
                    min_sensors = min(min_sensors, num_sensors)
                    break  # arrête la boucle dès qu'une combinaison valide est trouvée
        min_sensors_per_day.append(min_sensors)
    return min_sensors_per_day


# Durées entre deux observations
time_deltas = [2, 4, 6, 8, 12, 24]  # en heures

# Liste pour stocker le nombre minimum de capteurs pour chaque durée
min_sensors = []

# Calculer le nombre minimum de capteurs pour chaque durée
for delta in time_deltas:
    # Convertir la durée en timedelta
    period_duration = timedelta(hours=delta)

    sensors_needed = find_minimal_sensors_per_day(all_pass_times, period_duration)

    # Ajouter le nombre de capteurs à la liste
    min_sensors.append(sensors_needed)

# Créer le graphique
plt.figure(figsize=(10, 6))
plt.plot(time_deltas, min_sensors, marker='o')
plt.title('Nombre minimum de capteurs en fonction de la durée entre deux observations')
plt.xlabel('Durée entre deux observations (heures)')
plt.ylabel('Nombre minimum de capteurs')
plt.grid(True)
plt.show()

print("\n----------------------------------------------------------------------FIN----------------------------------------------------")

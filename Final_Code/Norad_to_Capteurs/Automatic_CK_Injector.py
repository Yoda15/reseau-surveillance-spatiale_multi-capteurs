import requests
import orekit
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import math

from org.orekit.frames import FramesFactory
from org.orekit.orbits import KeplerianOrbit, PositionAngleType
from org.orekit.propagation.analytical import KeplerianPropagator
from org.orekit.time import AbsoluteDate, TimeScalesFactory, DateComponents, TimeComponents
from org.orekit.utils import Constants

# Initialize Orekit
orekit.initVM()



def fetch_and_propagate_CK(norad_number):
    # Construction de l'URL du site n2yo
    url = f"https://www.n2yo.com/satellite/?s={norad_number}"

    # Envoyer une requête GET pour récupérer le contenu de la page
    response = requests.get(url)

    # Vérifier si la requête a réussi
    if response.status_code == 200:

        # Analyser le contenu HTML de la page
        soup = BeautifulSoup(response.content, "html.parser")

        # Recherche de la balise <div> avec id="satinfo"
        sat_info_div = soup.find("div", id="satinfo")

        # Récupération du texte brut à l'intérieur de la balise <div id="satinfo">
        text = sat_info_div.get_text()

        # Initialisation des variables
        perigee = None
        apogee = None
        inclination = None
        semi_major_axis = None

        # Parcourir les lignes de texte et extraire les valeurs appropriées
        lines = text.split("\n")
        for line in lines:
            if "Perigee" in line:
                parts = line.split(":")
                if len(parts) > 1:
                    perigee = float(parts[1].strip().split()[0])
            elif "Apogee" in line:
                parts = line.split(":")
                if len(parts) > 1:
                    apogee = float(parts[1].strip().split()[0])
            elif "Inclination" in line:
                parts = line.split(":")
                if len(parts) > 1:
                    inclination = float(parts[1].strip().split()[0])
            elif "Semi major axis" in line:
                parts = line.split(":")
                if len(parts) > 1:
                    semi_major_axis = float(parts[1].strip().split()[0])

        # Vérifier si les valeurs ont été récupérées avec succès
        if perigee is not None and apogee is not None and inclination is not None:
            # Calcul de l'excentricité
            eccentricity: float = (apogee - perigee) / (apogee + perigee)

            # Affichage des valeurs récupérées
            print("Perigee:", perigee, "km")
            print("Apogee:", apogee, "km")
            print("Semi Major Axis:", semi_major_axis, "km")
            print("Inclination:", inclination, "degrees")
            print("Eccentricity:", eccentricity)

        # Séparer les lignes de la réponse en une liste
        lines = response.text.splitlines()

        # Filtrer les lignes TLE en recherchant celles qui commencent par "1 " et "2 "
        tle_lines = [line.strip() for line in lines if line.startswith("1 ") or line.startswith("2 ")]

        # Vérifier si au moins deux lignes TLE ont été récupérées
        if len(tle_lines) >= 2:
            tle_line1 = tle_lines[0]
            tle_line2 = tle_lines[1]

            # Extract the epoch year and day from the first TLE line
            epoch_year = int(tle_line1[18:20])
            epoch_day = float(tle_line1[20:32])

            # The epoch year is given as a two-digit number. If it is less than 57, it is in the 2000s. Otherwise, it is in the 1900s.
            if epoch_year < 57:
                epoch_year += 2000
            else:
                epoch_year += 1900

            # Convert the epoch day to a datetime object
            epoch = datetime(epoch_year, 1, 1) + timedelta(epoch_day - 1)

            # Créer des objets DateComponents et TimeComponents à partir de l'objet datetime
            date_comp = DateComponents(epoch.year, epoch.month, epoch.day)
            seconds = float(epoch.second)
            time_comp = TimeComponents(epoch.hour, epoch.minute, seconds)

            utc=TimeScalesFactory.getUTC()

            # Convertir les objets DateComponents et TimeComponents en AbsoluteDate
            absolute_date = AbsoluteDate(date_comp, time_comp, utc)

            # Print the TLE epoch
            print("TLE Epoch: Year", epoch_year, "Day", epoch_day)

            omega = float(tle_line2[34:42])  # perigee argument
            raan = float(tle_line2[17:25])  # right ascension of ascending node
            lM = float(tle_line2[43:51])  # mean anomaly

            print("omega =", omega, "degrees")
            print("raan =", raan, "degrees")
            print("lM =", lM, "degrees")

            a = semi_major_axis*1000
            i = math.radians( inclination)
            omegaR = math.radians( omega)
            raanR = math.radians(raan)
            lMR = math.radians(lM)

                    # Utilisez cette date comme epoch pour votre orbite
            initialOrbit = KeplerianOrbit(a, eccentricity, i, omegaR, raanR, lMR, PositionAngleType.MEAN, FramesFactory.getEME2000(),absolute_date, Constants.WGS84_EARTH_MU)

            # Créer un propagateur keplerien à partir de l'orbite keplerienne
            propagator = KeplerianPropagator(initialOrbit)


            return  propagator


            # Maintenant, vous pouvez utiliser ce propagateur pour propager l'orbite du satellite comme dans votre code existant
        else:
            print("Erreur: Les lignes TLE n'ont pas été trouvées sur la page.")

    else:
        print("Erreur: Impossible de récupérer les données depuis le site Web.")


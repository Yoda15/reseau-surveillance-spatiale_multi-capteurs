import orekit
#from orekit.pyhelpers import setup_orekit_curdir, download_orekit_data_curdir
from org.orekit.propagation.analytical.tle import TLE, TLEPropagator
import requests

# Initialize Orekit
orekit.initVM()

# Setup Orekit and download data
#setup_orekit_curdir()
#download_orekit_data_curdir()

def fetch_and_propagate_tle(norad_number):
    # Build the URL for n2yo site
    url = f"https://www.n2yo.com/satellite/?s={norad_number}"

    # Send a GET request to fetch the page content
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Split the response lines into a list
        lines = response.text.splitlines()

        # Filter TLE lines by looking for lines that start with "1 " and "2 "
        tle_lines = [line.strip() for line in lines if line.startswith("1 ") or line.startswith("2 ")]

        # Check if at least two TLE lines were fetched
        if len(tle_lines) >= 2:
            tle_line1 = tle_lines[0]
            tle_line2 = tle_lines[1]

            # Afficher les lignes TLE récupérées
            print("Ligne 1 TLE:", tle_line1)
            print("Ligne 2 TLE:", tle_line2)

            # Create a TLE object
            tle = TLE(tle_line1, tle_line2)

            # Create a TLEPropagator object
            propagator = TLEPropagator.selectExtrapolator(tle)

            return propagator
        else:
            print("Erreur: Les lignes TLE n'ont pas été trouvées sur la page.")
    else:
        print("Erreur: Impossible de récupérer les données TLE depuis le site n2yo.")



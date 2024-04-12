#Ce code permet de lire le fichier txt ephemerides et d'en resortir avec des coordonnées kepleirienne
#J'utilise la date et la position XYZ pour obtenir la vitesse
#Une fois la date, la position XYZ et la vitesse obtenue, je peux avoir une orbite créée avec une orbite cartesienne
#Ensuite je transforme cette orbite cartésienne en orbite keplerienne
#Je renvoie ensuite tout les paramètres de mon orbite kepleirienne
#On ne peux pas créér une orbite a partir des coordonnées AEI puisque celle-ci ne donne aucune info sur la position du satellite
#Pour cela il faudrais également avoir Raan/Omega/lM dans les ephemerides pour avoir une coordonéee en 3D.
import math

import orekit
from orekit.pyhelpers import setup_orekit_curdir, download_orekit_data_curdir
from org.hipparchus.geometry.euclidean.threed import Vector3D
from org.orekit.orbits import KeplerianOrbit, CartesianOrbit
from org.orekit.frames import  FramesFactory
from org.orekit.utils import Constants, PVCoordinates
from org.orekit.time import AbsoluteDate, TimeScalesFactory

# Initialisation de Orekit
orekit.initVM()

# Configuration d'Orekit et téléchargement des données
setup_orekit_curdir()
download_orekit_data_curdir()



import pandas as pd


def read_ephemeris_file(file_name):
    ephemeris_data = []
    last_position = None
    last_date = None
    with open(file_name, 'r') as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            values = line.split(' ')
            date_str = ' '.join(values[2:4])  # Remove extra spaces
            try:
                # Parse the date string with the correct format
                date = pd.to_datetime(date_str)
                # Convert pandas Timestamp to python datetime
                date = date.to_pydatetime()
                # Remove timezone information
                date = date.replace(tzinfo=None)
                # Convert python datetime to orekit AbsoluteDate
                date = AbsoluteDate(date.year, date.month, date.day, date.hour, date.minute,
                                    date.second + date.microsecond / 1e6, TimeScalesFactory.getUTC())
                x = float(values[6].replace('x = ', ''))
                y = float(values[9].replace('y = ', ''))
                z = float(values[12].replace('z = ', ''))
                a = float(values[15].replace('a = ', '')) #Techniquement inutile
                e = float(values[18].replace('e = ', '')) #Techniquement inutile
                i = float(values[21].replace('i = ', '')) #Techniquement inutile

                position = Vector3D(x, y, z)

                if last_position is not None:
                    # Calculate the velocity vector
                    delta_t = date.durationFrom(last_date)
                    velocity = (position.subtract(last_position)).scalarMultiply(1.0 / delta_t)
                else:
                    # For the first data point, we don't have a velocity yet
                    velocity = None

                ephemeris_data.append((date, position, velocity, a, e, i))

                last_position = position
                last_date = date
            except Exception as e:
                print(f"Erreur lors de la conversion de la date : {e}")

    # Set the velocity of the first data point to be the same as the second data point
    if len(ephemeris_data) > 1:
        ephemeris_data[0] = (
        ephemeris_data[0][0], ephemeris_data[0][1], ephemeris_data[1][2], ephemeris_data[0][3], ephemeris_data[0][4],
        ephemeris_data[0][5])

    return ephemeris_data






def ephemeris_to_cartesian(ephemeris_data):
    cartesian_orbits = []
    for data in ephemeris_data:
        date, position, velocity, a, e, i = data
        # Create a PVCoordinates object
        pv_coordinates = PVCoordinates(position, velocity)
        # Create the CartesianOrbit
        cartesian_orbit = CartesianOrbit(pv_coordinates, FramesFactory.getEME2000(), date, Constants.WGS84_EARTH_MU)
        #cartesian_orbits.append(cartesian_orbit)
        cartesian_orbits.append((cartesian_orbit, a, e, i,position))
    return cartesian_orbits

def cartesian_to_keplerian(cartesian_orbits):
    keplerian_orbits = []
    for cartesian_orbit, a, e, i, position in cartesian_orbits:
        # Create the KeplerianOrbit
        keplerian_orbit = KeplerianOrbit(
            cartesian_orbit.getPVCoordinates(),
            cartesian_orbit.getFrame(),
            cartesian_orbit.getDate(),
            Constants.WGS84_EARTH_MU
        )
        #keplerian_orbits.append(keplerian_orbit)
        keplerian_orbits.append((keplerian_orbit, a, e, i))
    return keplerian_orbits

file_name = 'E:\PyCharm Community Edition 2023.3.3\TestV1\ephemeride'

def print_first_lines(file_name):
    with open(file_name, 'r') as file:
        for i, line in enumerate(file):
            print(line)
            if i >= 2:
                break

# Call the function to print the first 10 lines of the file
print_first_lines('ephemeride')

ephemeris_data = read_ephemeris_file(file_name)
cartesian_orbits = ephemeris_to_cartesian(ephemeris_data)
keplerian_orbits = cartesian_to_keplerian(cartesian_orbits)

#for (cartesian_orbit, a, e, i, position) in cartesian_orbits:
    #print(f"Imported position: position={position}")
    #print(cartesian_orbit)

for (keplerian_orbit, a, e, i) in keplerian_orbits:
    print(f"Imported AEI: a={a}, e={e}, i={i}")
    print(f"Calculated AEI: a={keplerian_orbit.getA()}, e={keplerian_orbit.getE()}, i={math.degrees(keplerian_orbit.getI())}")


import matplotlib.pyplot as plt


# Get the imported AEI values
a_imported = [a for date, position, velocity, a, e, i in ephemeris_data]
e_imported = [e for date, position, velocity, a, e, i in ephemeris_data]
i_imported = [i for date, position, velocity, a, e, i in ephemeris_data]

# Get the calculated AEI values
a_calculated = [orbit.getA() for orbit, a, e, i in keplerian_orbits]
e_calculated = [orbit.getE() for orbit, a, e, i in keplerian_orbits]
i_calculated = [math.degrees(orbit.getI()) for orbit, a, e, i in keplerian_orbits]

# Create subplots
fig, axs = plt.subplots(3)

# Plot semi-major axis (a)
axs[0].plot(a_imported, label='Imported a')
axs[0].plot(a_calculated, label='Calculated a')
axs[0].set_ylabel('Semi-major axis (a)')
axs[0].legend()

# Plot eccentricity (e)
axs[1].plot(e_imported, label='Imported e')
axs[1].plot(e_calculated, label='Calculated e')
axs[1].set_ylabel('Eccentricity (e)')
axs[1].legend()

# Plot inclination (i)
axs[2].plot(i_imported, label='Imported i')
axs[2].plot(i_calculated, label='Calculated i')
axs[2].set_ylabel('Inclination (i)')
axs[2].legend()

# Show the plot
plt.show()
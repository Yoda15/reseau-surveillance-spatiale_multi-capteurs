#Ce code permet de lire le fichier txt ephemerides et d'en resortir avec des coordonnées kepleirienne
#J'utilise la date et la position XYZ pour obtenir la vitesse
#Une fois la date, la position XYZ et la vitesse obtenue, je peux avoir une orbite créée avec une orbite cartesienne
#Ensuite je transforme cette orbite cartésienne en orbite keplerienne
#Je renvoie ensuite tout les paramètres de mon orbite kepleirienne
#On ne peux pas créér une orbite a partir des coordonnées AEI puisque celle-ci ne donne aucune info sur la position du satellite
#Pour cela il faudrais également avoir Raan/Omega/lM dans les ephemerides pour avoir une coordonéee en 3D.
import math

import orekit
import xlrd
from orekit.pyhelpers import setup_orekit_curdir, download_orekit_data_curdir
from org.hipparchus.geometry.euclidean.threed import Vector3D
from org.orekit.orbits import KeplerianOrbit, CartesianOrbit
from org.orekit.frames import FramesFactory
from org.orekit.propagation.analytical import KeplerianPropagator
from org.orekit.utils import Constants, PVCoordinates
from org.orekit.time import AbsoluteDate, TimeScalesFactory

# Initialisation de Orekit
orekit.initVM()

# Configuration d'Orekit et téléchargement des données
# download_orekit_data_curdir()
setup_orekit_curdir()




import pandas as pd

def ephemeris_to_cartesian(ephemeris_databrut):
    ###Transformer des éphéméris en une Orbite Cartésienne###
    cartesian_orbits = []
    date = []
    for i in range(1,int(ephemeris_databrut.cell_value(0, 13))):
        dates = pd.to_datetime(str(ephemeris_databrut.cell_value(i, 0)))
        # Convertir l'horodatage pandas en datetime python
        dates = dates.to_pydatetime()
        # Supprimer les informations de fuseau horaire
        dates = dates.replace(tzinfo=None)
        # Convertir python datetime en orekit AbsoluteDate
        dates = AbsoluteDate(dates.year, dates.month, dates.day, dates.hour, dates.minute,
                             dates.second + dates.microsecond / 1e6, TimeScalesFactory.getUTC())
        date.append(dates)
        #Recuperation de la position, Vitesse et Acceleration pour créé notre PVCoordinates
        XYZ = [float(ephemeris_databrut.cell_value(i, 1)), float(ephemeris_databrut.cell_value(i, 2)),float(ephemeris_databrut.cell_value(i, 3))]
        VXYZ = [float(ephemeris_databrut.cell_value(i, 7)), float(ephemeris_databrut.cell_value(i, 8)),float(ephemeris_databrut.cell_value(i, 9))]
        AXYZ = [float(ephemeris_databrut.cell_value(i, 10)), float(ephemeris_databrut.cell_value(i, 11)),float(ephemeris_databrut.cell_value(i, 12))]
        pv_coordinates = PVCoordinates(Vector3D(XYZ), Vector3D(VXYZ), Vector3D(AXYZ))
        # Créer l'orbite cartésienne
        cartesian_orbit = CartesianOrbit(pv_coordinates, FramesFactory.getEME2000(), dates, Constants.WGS84_EARTH_MU)
        cartesian_orbits.append((cartesian_orbit, ephemeris_databrut.cell_value(i, 4),ephemeris_databrut.cell_value(i, 5), ephemeris_databrut.cell_value(i, 6), XYZ))
    return cartesian_orbits


def cartesian_to_keplerian(cartesian_orbits):
    ###Transformer une orbite cartésienne en képlérienne###
    keplerian_orbits = []
    for cartesian_orbit, a, e, i, position in cartesian_orbits:
        # Créer la KeplerianOrbit
        keplerian_orbit = KeplerianPropagator(KeplerianOrbit(
            CartesianOrbit(cartesian_orbit)
        ))
        keplerian_orbits.append([keplerian_orbit,a,e,i])
    return keplerian_orbits

#Ouverture de l'Excel
workbook = xlrd.open_workbook('ephemeride.xls')
ephemeris_databrute = workbook.sheet_by_index(0)  # Sélectionner la première feuille
cartesian_orbits = ephemeris_to_cartesian(ephemeris_databrute)
keplerian_orbits = cartesian_to_keplerian(cartesian_orbits)

import matplotlib.pyplot as plt


# Récupérer les valeurs importées
a_imported = [float(ephemeris_databrute.cell_value(row, 4)) for row in range(1,ephemeris_databrute.nrows)]
e_imported = [float(ephemeris_databrute.cell_value(row, 5)) for row in range(1,ephemeris_databrute.nrows)]
i_imported = [float(ephemeris_databrute.cell_value(row, 6)) for row in range(1,ephemeris_databrute.nrows)]


# Récupérer les valeurs calculées
a_calculated = [float(a) for orbit, a, e, i in keplerian_orbits]
e_calculated = [float(e) for orbit, a, e, i in keplerian_orbits]
i_calculated = [float(i) for orbit, a, e, i in keplerian_orbits]


fig, axs = plt.subplots(3)

# Tracer (a)
axs[0].plot(a_imported, label='Imported a')
axs[0].plot(a_calculated, label='Calculated a')
axs[0].set_ylabel('Semi-major axis (a)')
axs[0].legend()

# Tracer (e)
axs[1].plot(e_imported, label='Imported e')
axs[1].plot(e_calculated, label='Calculated e')
axs[1].set_ylabel('Eccentricity (e)')
axs[1].legend()

# Tracer (i)
axs[2].plot(i_imported, label='Imported i')
axs[2].plot(i_calculated, label='Calculated i')
axs[2].set_ylabel('Inclination (i)')
axs[2].legend()

plt.show()
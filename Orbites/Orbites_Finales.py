#Essaye de faire une manœuvre 


from math import radians, degrees
import matplotlib.pyplot as plt
import pandas as pd

# First, check the version

import orekit
from org.hipparchus.geometry.euclidean.threed import Vector3D, Rotation
from org.hipparchus.util import FastMath
from org.orekit.attitudes import LofOffset
from org.orekit.forces.maneuvers.propulsion import BasicConstantThrustPropulsionModel
from org.orekit.forces.maneuvers.trigger import DateBasedManeuverTriggers
from org.orekit.propagation.events import NodeDetector, EventEnablingPredicateFilter
from org.orekit.propagation.events.handlers import StopOnIncreasing
from org.orekit.frames import Frame, Transform

vm = orekit.initVM()
print('Java version:', vm.java_version)
print('Orekit version:', orekit.VERSION)

# Second, download files and import useful functions

from orekit.pyhelpers import setup_orekit_curdir, download_orekit_data_curdir

# download_orekit_data_curdir()
setup_orekit_curdir()

from org.orekit.orbits import KeplerianOrbit, PositionAngleType, CircularOrbit, EquinoctialOrbit, OrbitType
from org.orekit.propagation.analytical import KeplerianPropagator
from org.orekit.time import AbsoluteDate, TimeScalesFactory, DateComponents, TimeComponents
from org.orekit.utils import Constants, PVCoordinates, AngularCoordinates
from org.orekit.frames import FramesFactory, LOFType

from org.orekit.propagation.numerical import NumericalPropagator
from org.hipparchus.ode.nonstiff import DormandPrince853Integrator
from org.orekit.propagation import SpacecraftState
from org.orekit.bodies import OneAxisEllipsoid
from org.orekit.utils import IERSConventions
from org.orekit.forces.gravity.potential import GravityFieldFactory
from org.orekit.forces.gravity import HolmesFeatherstoneAttractionModel
from org.orekit.forces.maneuvers import Maneuver, ImpulseManeuver
from orekit import JArray_double


def initialisation_orbite(a, i, e, raan, w, anomaly):
    ###initialiser l'orbite et le satellite###

    # passer en radians
    i = radians(i)
    raan = radians(raan)
    w = radians(w)
    anomaly = radians(anomaly)

    # définir le référentiel de travail (à demander)
    referentiel_terre = FramesFactory.getEME2000()

    utc = TimeScalesFactory.getUTC()

    # Date de création de l'orbite (problème possible)
    Date_Debut = AbsoluteDate(2023, 12, 25, 10, 23, 00.000, utc)  # Annee,Mois,jour,heure,minutes,seconde,type

    # Création de l'orbite
    if e == 0 and i != 0:
        orbite = CircularOrbit(a, 0.0, 0.0, i, raan, w, PositionAngleType.TRUE, referentiel_terre, Date_Debut,
                               Constants.WGS84_EARTH_MU)
    else:
        orbite = KeplerianOrbit(a, e, i, w, raan, anomaly, PositionAngleType.TRUE, referentiel_terre, Date_Debut,
                                Constants.WGS84_EARTH_MU)

    return orbite


def initialisation_satellite(orbite, masse):
    return (SpacecraftState(orbite, masse))


def propagation_orbite(orbite, duree, frequence, satellite):
    ###Propagation de l'orbite###
    faultposition = 1.0
    # Pourquoi Minimum et Maximum
    pasMin = 0.001
    pasMax = 1000.0
    initStep = 10.0
    tolerances = NumericalPropagator.tolerances(faultposition, orbite,
                                                orbite.getType())  # Erreurs Poisition, orbite étudié, type de celle-ci
    integrateur = DormandPrince853Integrator(pasMin, pasMax, JArray_double.cast_(tolerances[0]),
                                             JArray_double.cast_(tolerances[1]))  # Pourquoi JArray
    integrateur.setInitialStepSize(initStep)  # Pourquoi initStep = 60.0 ?

    # Propagation de l'orbite
    propagation = NumericalPropagator(integrateur)
    propagation.setInitialState(satellite)  # Initialisation du satellite sur l'orbite

    # Création modele terrestre
    gravite = GravityFieldFactory.getNormalizedProvider(10, 10)
    propagation.addForceModel(
        HolmesFeatherstoneAttractionModel(FramesFactory.getITRF(IERSConventions.IERS_2010, True), gravite))

    ephemeride = []
    Date = orbite.getDate()  # Recuperation de la date de l'orbite
    DateFinal = Date.shiftedBy(duree)  # Date Final
    while (Date.compareTo(DateFinal) <= 0.0):
        orbite = propagation.getPVCoordinates(Date, FramesFactory.getEME2000())  # Nouvelle orbite à T+t
        # Position Sat
        x = orbite.getPosition().getX()
        y = orbite.getPosition().getY()
        z = orbite.getPosition().getZ()
        orbit_kepl = KeplerianOrbit(orbite, FramesFactory.getEME2000(), Date, Constants.WGS84_EARTH_MU)
        i = degrees(orbit_kepl.getI())
        a = orbit_kepl.getA()
        e = orbit_kepl.getE()
        date = pd.to_datetime(Date.toString())
        ephemeride.append([date, x, y, z, a, e, i])
        f.write("\n date : " + str(date) + " x = " + str(x) + " y = " + str(y) + " z = " + str(z) + " a = " + str(
            a) + " e = " + str(e) + " i = " + str(i))
        Date = Date.shiftedBy(frequence)
    ephemeride = pd.DataFrame(ephemeride, columns=['date', 'x', 'y', 'z', 'a', 'e', 'i'])
    return ephemeride


# MAIN
a = 400E3 + Constants.WGS84_EARTH_EQUATORIAL_RADIUS
i = 45
e = 0.1
raan = 0
w = 90
anomaly = 0
orbite = initialisation_orbite(a, i, e, raan, w, anomaly)
print(orbite)
masse = 4500.0  # Masse sat

# Creation satellite
satellite = initialisation_satellite(orbite, masse)

# Fichier txt
nom = 'ephemeride'
f = open(nom, 'w')

# Orbite Initial
frequence = 10.0  # Echantillonage
duree = 3600 * 12.0  # Seconde
ephemeride = propagation_orbite(orbite, duree, frequence, satellite)
print(ephemeride)
Avant_maneuvre = ephemeride

orbitType = orbite.getType()

faultposition = 1.0
pasMin = 0.001
pasMax = 1000.0
initStep = 60.0
utc = TimeScalesFactory.getUTC()
Date_Debut = AbsoluteDate(2023, 12, 25, 10, 23, 00.000, utc)
Date_Fin = AbsoluteDate(2023, 12, 25, 22, 23, 00.000, utc)

tolerances = NumericalPropagator.tolerances(faultposition, orbite, orbite.getType())
integrator = DormandPrince853Integrator(pasMin, pasMax, JArray_double.cast_(tolerances[0]), JArray_double.cast_(tolerances[1]))
integrator.setInitialStepSize(initStep)
propagator = NumericalPropagator(integrator)
propagator.setOrbitType(orbitType)
propagator.setInitialState(satellite)
propagator.setAttitudeProvider(LofOffset(FramesFactory.getEME2000(), LOFType.VNC))
direction = Vector3D(radians(-7.4978), radians(351))
rotation = Rotation(direction, Vector3D.PLUS_I)


# Créez une vitesse angulaire (zéro dans cet exemple)
angularRate = Vector3D.ZERO

# Créez des AngularCoordinates avec la rotation et la vitesse angulaire
angularCoordinates = AngularCoordinates(rotation, angularRate)

# Appliquez les AngularCoordinates pour créer un nouveau Transform
new_transform = Transform(Date_Debut, angularCoordinates)

# Créez un nouveau frame avec le Transform modifié
frame = Frame(FramesFactory.getEME2000(), new_transform, "myFrame")

attitudeOverride = frame


firingDate = AbsoluteDate(DateComponents(2023, 12, 25), TimeComponents(12, 23, 00.000), TimeScalesFactory.getUTC())
duration = 4.0
triggers = DateBasedManeuverTriggers(firingDate, duration)
thrust = 420.0
isp = 318.0
propulsionModel = BasicConstantThrustPropulsionModel(thrust, isp, Vector3D.PLUS_I, "apogee-engine")

# Utilisez le frame EME2000 pour l'AttitudeProvider
attitudeProvider = LofOffset(FramesFactory.getEME2000(), LOFType.VNC)

# Store the state of the satellite before the maneuver
state_before = propagator.propagate(Date_Debut)

# Apply the maneuver
propagator.addForceModel(Maneuver(attitudeProvider, triggers, propulsionModel))

# Store the state of the satellite after the maneuver
state_after = propagator.propagate(Date_Fin)

ephemeride = []


propagator.propagate(Date_Debut, Date_Fin)
Date = orbite.getDate()
DateFinal = Date.shiftedBy(duree)
while Date.compareTo(DateFinal) <= 0.0:
    orbite = propagator.getPVCoordinates(Date, FramesFactory.getEME2000())
    x = orbite.getPosition().getX()
    y = orbite.getPosition().getY()
    z = orbite.getPosition().getZ()
    orbit_kepl = KeplerianOrbit(orbite, FramesFactory.getEME2000(), Date, Constants.WGS84_EARTH_MU)
    i = degrees(orbit_kepl.getI())
    a = orbit_kepl.getA()
    e = orbit_kepl.getE()
    date = pd.to_datetime(Date.toString())
    ephemeride.append([date, x, y, z, a, e, i])
    f.write("\n date : " + str(date) + " x = " + str(x) + " y = " + str(y) + " z = " + str(z) + " a = " + str(
        a) + " e = " + str(e) + " i = " + str(i))
    Date = Date.shiftedBy(frequence)
ephemeride = pd.DataFrame(ephemeride, columns=['date', 'x', 'y', 'z', 'a', 'e', 'i'])


print(ephemeride)

Apres_maneuvre=ephemeride
#Fermeture du txt
f.close()

# Ajoutez une visualisation 2D à la fin de votre script
import matplotlib.pyplot as plt


fig, axs = plt.subplots(3, 2, figsize=(15, 15))

# Comparaison des valeurs X avant et après la manœuvre
axs[0, 0].plot(Avant_maneuvre['date'], Avant_maneuvre['x'], label='x avant')
axs[0, 0].plot(Apres_maneuvre['date'], Apres_maneuvre['x'], label='x après')
axs[0, 0].set_title('Comparaison des valeurs X avant et après la manœuvre')
axs[0, 0].legend()

# Comparaison des valeurs Y avant et après la manœuvre
axs[0, 1].plot(Avant_maneuvre['date'], Avant_maneuvre['y'], label='y avant')
axs[0, 1].plot(Apres_maneuvre['date'], Apres_maneuvre['y'], label='y après')
axs[0, 1].set_title('Comparaison des valeurs Y avant et après la manœuvre')
axs[0, 1].legend()

# Comparaison des valeurs Z avant et après la manœuvre
axs[1, 0].plot(Avant_maneuvre['date'], Avant_maneuvre['z'], label='z avant')
axs[1, 0].plot(Apres_maneuvre['date'], Apres_maneuvre['z'], label='z après')
axs[1, 0].set_title('Comparaison des valeurs Z avant et après la manœuvre')
axs[1, 0].legend()

# Comparaison des valeurs A avant et après la manœuvre
axs[1, 1].plot(Avant_maneuvre['date'], Avant_maneuvre['a'], label='a avant')
axs[1, 1].plot(Apres_maneuvre['date'], Apres_maneuvre['a'], label='a après')
axs[1, 1].set_title('Comparaison des valeurs A avant et après la manœuvre')
axs[1, 1].legend()

# Comparaison des valeurs E avant et après la manœuvre
axs[2, 0].plot(Avant_maneuvre['date'], Avant_maneuvre['e'], label='e avant')
axs[2, 0].plot(Apres_maneuvre['date'], Apres_maneuvre['e'], label='e après')
axs[2, 0].set_title('Comparaison des valeurs E avant et après la manœuvre')
axs[2, 0].legend()

# Comparaison des valeurs I avant et après la manœuvre
axs[2, 1].plot(Avant_maneuvre['date'], Avant_maneuvre['i'], label='i avant')
axs[2, 1].plot(Apres_maneuvre['date'], Apres_maneuvre['i'], label='i après')
axs[2, 1].set_title('Comparaison des valeurs I avant et après la manœuvre')
axs[2, 1].legend()

plt.tight_layout()
plt.show()

# Affichez la figure et bloquez l'exécution jusqu'à ce que la fenêtre de la figure soit fermée
plt.show(block=True)


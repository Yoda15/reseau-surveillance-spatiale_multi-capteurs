from math import radians, degrees
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from mpl_toolkits.basemap import Basemap

import orekit
from org.hipparchus.geometry.euclidean.threed import Vector3D, Rotation
from org.orekit.attitudes import LofOffset
from org.orekit.forces.maneuvers.propulsion import BasicConstantThrustPropulsionModel
from org.orekit.forces.maneuvers.trigger import DateBasedManeuverTriggers
from org.orekit.frames import Frame, Transform

vm = orekit.initVM()
print('Java version:', vm.java_version)
print('Orekit version:', orekit.VERSION)

from orekit.pyhelpers import setup_orekit_curdir, download_orekit_data_curdir

# download_orekit_data_curdir()
setup_orekit_curdir()

from org.orekit.orbits import KeplerianOrbit, PositionAngleType, CircularOrbit
from org.orekit.time import AbsoluteDate, TimeScalesFactory, DateComponents, TimeComponents
from org.orekit.utils import Constants, AngularCoordinates
from org.orekit.frames import FramesFactory, LOFType

from org.orekit.propagation.numerical import NumericalPropagator
from org.hipparchus.ode.nonstiff import DormandPrince853Integrator
from org.orekit.propagation import SpacecraftState
from org.orekit.bodies import OneAxisEllipsoid
from org.orekit.utils import IERSConventions
from org.orekit.forces.gravity.potential import GravityFieldFactory
from org.orekit.forces.gravity import HolmesFeatherstoneAttractionModel
from org.orekit.forces.maneuvers import Maneuver
from orekit import JArray_double
import xlwt

def initialisation_orbite(a, i, e, raan, w, anomaly,Annee_Debut,Mois_Debut,Jour_Debut,Heure_Debut,Minute_Debut,Seconde_Debut):
    ###initialiser l'orbite et le satellite###

    # passer en radians
    i = radians(i)
    raan = radians(raan)
    w = radians(w)
    anomaly = radians(anomaly)

    # définir le référentiel de travail
    referentiel_terre = FramesFactory.getEME2000()

    utc = TimeScalesFactory.getUTC()

    # Date de création de l'orbite
    Date_Debut = AbsoluteDate(Annee_Debut, Mois_Debut, Jour_Debut, Heure_Debut, Minute_Debut, Seconde_Debut, utc)  # Annee,Mois,jour,heure,minutes,seconde,type

    # Création de l'orbite
    if e == 0 and i != 0:
        orbite = CircularOrbit(a, 0.0, 0.0, i, raan, w, PositionAngleType.TRUE, referentiel_terre, Date_Debut,Constants.WGS84_EARTH_MU)
    else:
        orbite = KeplerianOrbit(a, e, i, w, raan, anomaly, PositionAngleType.TRUE, referentiel_terre, Date_Debut,Constants.WGS84_EARTH_MU)

    return orbite


def initialisation_satellite(orbite, masse):
    ###initialiser le satellite###
    return (SpacecraftState(orbite, masse))

p = []
def propagation_orbite(orbite, duree, frequence, satellite):
    ###Propagation de l'orbite###
    faultposition = 1.0
    # Pourquoi Minimum et Maximum
    pasMin = 0.001
    pasMax = 1000.0
    initStep = 10.0
    nbi =0
    tolerances = NumericalPropagator.tolerances(faultposition, orbite,orbite.getType())  # Erreurs Poisition, orbite étudié, type de celle-ci
    integrateur = DormandPrince853Integrator(pasMin, pasMax, JArray_double.cast_(tolerances[0]),JArray_double.cast_(tolerances[1]))  # Pourquoi JArray
    integrateur.setInitialStepSize(initStep)

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
        PVA = orbit_kepl.getPVCoordinates()
        ephemeride.append([date, x, y, z, a, e, i])
        # ws.write(nbi + 1, 0, str(date))
        # ws.write(nbi + 1, 1, str(x))
        # ws.write(nbi + 1, 2, str(y))
        # ws.write(nbi + 1, 3, str(z))
        # ws.write(nbi + 1, 4, str(a))
        # ws.write(nbi + 1, 5, str(e))
        # ws.write(nbi + 1, 6, str(i))
        # ws.write(nbi + 1, 7, str(PVA.getVelocity().getX()))
        # ws.write(nbi + 1, 8, str(PVA.getVelocity().getY()))
        # ws.write(nbi + 1, 9, str(PVA.getVelocity().getZ()))
        # ws.write(nbi + 1, 10, str(PVA.getAcceleration().getX()))
        # ws.write(nbi + 1, 11, str(PVA.getAcceleration().getY()))
        # ws.write(nbi + 1, 12, str(PVA.getAcceleration().getZ()))
        Date = Date.shiftedBy(frequence)
        # nbi = nbi+1
    ephemeride = pd.DataFrame(ephemeride, columns=['date', 'x', 'y', 'z', 'a', 'e', 'i'])
    return ephemeride,nbi

ITRF = FramesFactory.getITRF(IERSConventions.IERS_2010, True)
earth = OneAxisEllipsoid(Constants.WGS84_EARTH_EQUATORIAL_RADIUS,
                             Constants.WGS84_EARTH_FLATTENING,
                             ITRF)



#########################################################################################################
###########################################VALEURS MODIFIABLES###########################################
#########################################################################################################
a = 4000E3 + Constants.WGS84_EARTH_EQUATORIAL_RADIUS
i = 45
e = 0.001
raan = 0
w = 90
anomaly = 0
masse = 4500.0  # Masse sat

#Date/Horaire Debut
Annee_Debut = 2024
Mois_Debut = 10
Jour_Debut = 8
Heure_Debut = 10
Minute_Debut = 23
Seconde_Debut = 00.000

#Date/Horaire Fin
Annee_Fin = 2024
Mois_Fin = 10
Jour_Fin = 8
Heure_Fin = 22
Minute_Fin = 23
Seconde_Fin = 00.000

#Date/Horaire Manoeuvre
Annee_Manoeuvre = 2024
Mois_Manoeuvre = 10
Jour_Manoeuvre = 8
Heure_Manoeuvre = 12
Minute_Manoeuvre = 23
Seconde_Manoeuvre = 00.000

#Caractéristique Manoeuvre
duration = 480.0
thrust = 20.0
isp = 318.0

#Ces valeurs n'ont ajourd'hui aucunes incidences sur l'orbite, mais permettent normalement de changer l'orientation du satellite
alpha = -7.4978
delta = 351

#########################################################################################################
#########################################################################################################
#########################################################################################################




orbite = initialisation_orbite(a, i, e, raan, w, anomaly,Annee_Debut,Mois_Debut,Jour_Debut,Heure_Debut,Minute_Debut,Seconde_Debut)
print(orbite)

nbi = 0
# Creation satellite
satellite = initialisation_satellite(orbite, masse)

# Fichier excel
nom = 'ephemeride.xls'
wb = xlwt.Workbook()
ws = wb.add_sheet('Data')
ws.write(0, 0, 'date :')
ws.write(0, 1, 'x =')
ws.write(0, 2, 'y =')
ws.write(0, 3, 'z =')
ws.write(0, 4, 'a =')
ws.write(0, 5, 'e =')
ws.write(0, 6, 'i =')
ws.write(0, 7, 'VitesseX =')
ws.write(0, 8, 'VitesseY =')
ws.write(0, 9, 'VitesseZ =')
ws.write(0, 10, 'AccélérationX =')
ws.write(0, 11, 'AccélérationY =')
ws.write(0, 12, 'AccélérationZ =')

# Orbite Initial
frequence = 10.0  # Echantillonage
duree = 3600 * 12.0  # Seconde
[ephemeride,nbi] = propagation_orbite(orbite, duree, frequence, satellite)
print(ephemeride)
Avant_maneuvre = ephemeride

orbitType = orbite.getType()

faultposition = 1.0
pasMin = 0.001
pasMax = 1000.0
initStep = 60.0
utc = TimeScalesFactory.getUTC()
Date_Debut = AbsoluteDate(Annee_Debut, Mois_Debut, Jour_Debut, Heure_Debut, Minute_Debut, Seconde_Debut, utc)
Date_Fin = AbsoluteDate(Annee_Fin, Mois_Fin, Jour_Fin, Heure_Fin, Minute_Fin, Seconde_Fin, utc)

t = [Date_Debut.shiftedBy(float(dt)) \
         for dt in np.arange(0, duree, frequence)]
tl = np.linspace(0, duree, len(t))

tolerances = NumericalPropagator.tolerances(faultposition, orbite, orbite.getType())
integrator = DormandPrince853Integrator(pasMin, pasMax, JArray_double.cast_(tolerances[0]), JArray_double.cast_(tolerances[1]))
integrator.setInitialStepSize(initStep)
propagator = NumericalPropagator(integrator)
propagator.setOrbitType(orbitType)
propagator.setInitialState(satellite)
propagator.setAttitudeProvider(LofOffset(FramesFactory.getEME2000(), LOFType.VNC))
direction = Vector3D(radians(alpha), radians(delta))
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


firingDate = AbsoluteDate(DateComponents(Annee_Manoeuvre, Mois_Manoeuvre, Jour_Manoeuvre), TimeComponents(Heure_Manoeuvre, Minute_Manoeuvre, Seconde_Manoeuvre), TimeScalesFactory.getUTC())

triggers = DateBasedManeuverTriggers(firingDate, duration)

propulsionModel = BasicConstantThrustPropulsionModel(thrust, isp, Vector3D.PLUS_I, "apogee-engine")

# Utilisez le frame EME2000 pour l'AttitudeProvider
attitudeProvider = LofOffset(FramesFactory.getEME2000(), LOFType.VNC)

# Stocker l'état du satellite avant la manœuvre
state_before = propagator.propagate(Date_Debut)

# Faire la Manoeuvre
propagator.addForceModel(Maneuver(attitudeProvider, triggers, propulsionModel))

# Stocker l'état du satellite après la manœuvre
state_after = propagator.propagate(Date_Fin)

ephemeride = []


propagator.propagate(Date_Debut, Date_Fin)
Date = orbite.getDate()
DateFinal = Date.shiftedBy(duree)
print(p)
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
    PVA = orbit_kepl.getPVCoordinates()

    p.append(PVA.getPosition())
    ws.write(nbi + 1, 0, str(date))
    ws.write(nbi + 1, 1, str(x))
    ws.write(nbi + 1, 2, str(y))
    ws.write(nbi + 1, 3, str(z))
    ws.write(nbi + 1, 4, str(a))
    ws.write(nbi + 1, 5, str(e))
    ws.write(nbi + 1, 6, str(i))
    ws.write(nbi + 1, 7, str(PVA.getVelocity().getX()))
    ws.write(nbi + 1, 8, str(PVA.getVelocity().getY()))
    ws.write(nbi + 1, 9, str(PVA.getVelocity().getZ()))
    ws.write(nbi + 1, 10, str(PVA.getAcceleration().getX()))
    ws.write(nbi + 1, 11, str(PVA.getAcceleration().getY()))
    ws.write(nbi + 1, 12, str(PVA.getAcceleration().getZ()))
    Date = Date.shiftedBy(frequence)
    nbi = nbi + 1
ephemeride = pd.DataFrame(ephemeride, columns=['date', 'x', 'y', 'z', 'a', 'e', 'i'])

print(ephemeride)

#création des graphes visuelle comprenant la manoeuvre

subpoint = [earth.transform(tp, FramesFactory.getEME2000(), tt) for tt, tp in zip(t, p)]
lat = np.degrees([gp.getLatitude() for gp in subpoint])
lon = np.degrees([gp.getLongitude() for gp in subpoint])
m = Basemap(projection='cyl',
                resolution='l',
                area_thresh=None)

m.drawmapboundary()
m.fillcontinents(color='#dadada', lake_color='white')
m.drawmeridians(np.arange(-180, 180, 30), color='gray')
m.drawparallels(np.arange(-90, 90, 30), color='gray');

m.scatter(lon, lat, alpha=0.3, color='red', zorder=3, marker='.', linewidth=0.5);

fig, long =plt.subplots()# affichage longitude en fonction du temps
long.plot(lon, tl)
long.invert_yaxis()
long.set_xlabel('longitude (°)')
long.set_ylabel('temps (s)')
long.set_title('Evolution de la longitude en fonction du temps')
plt.show()



Apres_maneuvre=ephemeride
#Fermeture du Excel
ws.write(0, 13, str(nbi))
wb.save('ephemeride.xls')

# Ajoute de la visualisation 2D à la fin du script
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

# Afficher la figure et bloquez l'exécution jusqu'à ce que la fenêtre de la figure soit fermée
plt.show(block=True)


fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
u = np.linspace(0, 2 * np.pi, 100)
v = np.linspace(0, np.pi, 100)
x = Constants.WGS84_EARTH_EQUATORIAL_RADIUS * np.outer(np.cos(u), np.sin(v))
y = Constants.WGS84_EARTH_EQUATORIAL_RADIUS * np.outer(np.sin(u), np.sin(v))
z = Constants.WGS84_EARTH_EQUATORIAL_RADIUS * np.outer(np.ones(np.size(u)), np.cos(v))

#Derterminer les échelles
x_range= np.ptp(x)
y_range = np.ptp(y)
z_range = np.ptp(z)
max_val = max(x_range,y_range,z_range)
# print(max_val)
min_val = -1*min(x_range,y_range,z_range)
# print(min_val)
ax.set_xlim([min_val,max_val])
ax.set_ylim([min_val,max_val])
ax.set_zlim([min_val,max_val])

ax.plot_surface(x, y, z, color='b')
ax.plot(ephemeride['x'], ephemeride['y'], ephemeride['z'])
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_box_aspect([1, 1, 1])
plt.show()


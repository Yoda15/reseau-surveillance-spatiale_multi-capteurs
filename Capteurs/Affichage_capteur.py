import imageio
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from mayavi import mlab



# Liste des coordonnées des capteurs (latitude, longitude)
capteurs = [
    (48.8534, 2.3488),
    (52.5200, 13.4050),
    (55.7558, 37.6176),
    (30.0444, 31.2357),
    (40.7128, -74.0060),
    (-33.8688, 151.2093),
    (-23.5475, -46.6361),
    (28.6139, 77.2090),
    (35.6895, 139.6917),
    (-34.6037, -58.3816),
    (25.0330, 121.5654),
    (-18.1423, -70.2350),
    (51.5074, -0.1278),
    (36.0999, 101.4238),
    (-25.7463, 28.1953),
    (37.7749, -122.4194),
    (55.6761, 12.5683),
    (-36.8485, 174.7633),
    (1.2833, 103.8333),
    (-34.9287, -56.1645),
    (56.1304, 106.3468),
    (-12.0464, -77.0428),
    (32.0853, 34.7818),
    (37.5665, 126.9780),
    (24.8864, 67.0211),
    (-23.5505, -46.6333),
    (43.7728, 11.2564),
    (22.3193, 114.1694),
    (23.1291, 113.2644),
    (14.5995, -90.6720)
]

# Conversion des coordonnées en radians
capteurs_rad = [(np.deg2rad(lat), np.deg2rad(lon)) for lat, lon in capteurs]

# Rayon de la Terre (en mètres)
R = 6371

# Créer une sphère
phi, theta = np.mgrid[0:np.pi:101j, 0:2*np.pi:101j]
x = R * np.sin(phi) * np.cos(theta)
y = R * np.sin(phi) * np.sin(theta)
z = R * np.cos(phi)

# Création de la figure 3D
mlab.figure(size=(700, 700))

# Dessiner la sphère (Terre)
mlab.mesh(x, y, z, color=(0, 0, 1))  # Utiliser une couleur bleue pour tous les points

# Ajout des points sur le globe (capteurs)
for lat, lon in capteurs_rad:
    x = R * np.cos(lat) * np.cos(lon)
    y = R * np.cos(lat) * np.sin(lon)
    z = R * np.sin(lat)
    mlab.points3d(x, y, z, color=(1, 0, 0), scale_factor=100)  # Utiliser une couleur rouge pour les capteurs

# Affichage de la figure
mlab.show()

# Charger l'image
img = imageio.v2.imread('earth.jpg')

# Créer une figure
fig, ax = plt.subplots()

# Afficher l'image
ax.imshow(img, extent=[-180, 180, -90, 90])

# Ajouter les positions des capteurs
for lat, lon in capteurs:
    ax.plot(lon, lat, 'ro')  # Utiliser une couleur rouge pour les capteurs

# Afficher la figure
plt.show()
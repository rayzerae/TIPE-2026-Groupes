import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
from mpl_toolkits.mplot3d import Axes3D

# --- CONFIGURATION ---
FRAMES = 120         # Nombre d'images (plus = plus fluide mais plus long)
FPS = 30             # Images par seconde
RES = 50             # Résolution de la grille (densité des points)

# --- FONCTIONS MATHÉMATIQUES ---

def inverse_stereographic(z):
    """Projette le plan complexe sur la sphère."""
    denom = np.abs(z)**2 + 1
    x = 2 * np.real(z) / denom
    y = 2 * np.imag(z) / denom
    z_coord = (np.abs(z)**2 - 1) / denom
    return x, y, z_coord

def moebius_transform(z, M):
    """Applique la matrice M = [[a,b],[c,d]] au point z."""
    a, b = M[0,0], M[0,1]
    c, d = M[1,0], M[1,1]
    # On évite la division par zéro avec un petit epsilon
    denom = c*z + d
    denom[denom == 0] = 1e-9
    return (a*z + b) / denom

# --- PRÉPARATION DE LA SCÈNE ---

# 1. Création de la grille (Latitudes / Longitudes)
# C'est ça qui va donner l'aspect "maillage" à la sphère
theta = np.linspace(0, 2*np.pi, RES)
phi = np.linspace(-np.pi/2 + 0.1, np.pi/2 - 0.1, RES) # On évite les pôles exacts
THETA, PHI = np.meshgrid(theta, phi)

# On crée des lignes de longitude (cercles passant par les pôles)
longitudes_z = []
for t in np.linspace(0, np.pi, 12): # 12 méridiens
    r_line = np.tan(np.linspace(-1.5, 1.5, RES))
    z_line = r_line * np.exp(1j * t)
    longitudes_z.append(z_line)

# On crée des lignes de latitude (cercles parallèles à l'équateur)
latitudes_z = []
for p in np.linspace(0.1, 5, 10): # 10 parallèles
    t_line = np.linspace(0, 2*np.pi, RES)
    z_line = p * np.exp(1j * t_line)
    latitudes_z.append(z_line)

# 2. Initialisation du graphique 3D
fig = plt.figure(figsize=(10, 8), facecolor='black')
ax = fig.add_subplot(111, projection='3d', facecolor='black')
ax.set_axis_off() # On cache les axes pour le style
ax.set_xlim(-1, 1); ax.set_ylim(-1, 1); ax.set_zlim(-1, 1)

# Ces listes contiendront les objets graphiques (les lignes 3D)
lines_long = [ax.plot([], [], [], color='cyan', linewidth=1, alpha=0.6)[0] for _ in longitudes_z]
lines_lat = [ax.plot([], [], [], color='magenta', linewidth=1, alpha=0.6)[0] for _ in latitudes_z]

# --- LA MATRICE QUI BOUGE (Le Cœur du TIPE) ---
# On définit une transformation qui évolue avec le temps 't'.
# Ici : une "loxodromie" (mélange de rotation et de dilatation).
def get_matrix_at_time(t_norm):
    """
    t_norm varie de 0 à 1.
    La transformation : z -> k * exp(i*theta) * z
    C'est une rotation combinée à une dilatation.
    """
    angle_rotation = 2 * np.pi * t_norm # Un tour complet
    dilatation = 1 + 0.5 * np.sin(2 * np.pi * t_norm) # Ça "respire" entre 0.5 et 1.5
    
    multiplicateur = dilatation * np.exp(1j * angle_rotation)
    
    # Matrice correspondante [[m, 0], [0, 1]] correspond à z -> mz
    M = np.array([[multiplicateur, 0], [0, 1]], dtype=complex)
    return M

# --- BOUCLE D'ANIMATION ---

def update(frame):
    # 1. Où en est-on dans le temps ? (entre 0 et 1)
    t_norm = frame / FRAMES
    
    # 2. Quelle est la matrice à cet instant ?
    M = get_matrix_at_time(t_norm)
    
    # 3. On met à jour les longitudes
    for i, z_line in enumerate(longitudes_z):
        # a. Appliquer la transfo dans le plan
        z_transformed = moebius_transform(z_line, M)
        # b. Projeter sur la sphère
        X, Y, Z = inverse_stereographic(z_transformed)
        # c. Mettre à jour le dessin
        lines_long[i].set_data(X, Y)
        lines_long[i].set_3d_properties(Z)
        
    # 4. On met à jour les latitudes (idem)
    for i, z_line in enumerate(latitudes_z):
        z_transformed = moebius_transform(z_line, M)
        X, Y, Z = inverse_stereographic(z_transformed)
        lines_lat[i].set_data(X, Y)
        lines_lat[i].set_3d_properties(Z)
        
    # On fait tourner un peu la caméra pour que ce soit plus dynamique
    ax.view_init(elev=30, azim=frame*2)
    
    if frame % 10 == 0: print(f"Rendu frame {frame}/{FRAMES}...")
    return lines_long + lines_lat

# --- LANCER LE RENDU ---
print(f"Début du rendu 3D sur le Mac M2 ({FRAMES} frames)...")
ani = animation.FuncAnimation(fig, update, frames=FRAMES, interval=1000/FPS, blit=False)

# Sauvegarde en vidéo MP4 (Nécessite ffmpeg, souvent déjà là sur Mac)
output_file = 'journal/images/sphere_moebius.mp4'
try:
    ani.save(output_file, writer='ffmpeg', fps=FPS, dpi=150)
    print(f"✅ Vidéo terminée : {output_file}")
    print("Ouvre-la avec QuickTime pour voir le résultat !")
except Exception as e:
    print(f"❌ Erreur lors de la sauvegarde vidéo : {e}")
    print("Essaye d'installer ffmpeg : 'brew install ffmpeg' dans le terminal.")
    # En cas d'échec vidéo, on montre juste la dernière image
    plt.show()
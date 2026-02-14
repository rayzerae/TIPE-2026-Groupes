import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle

# --- CONFIGURATION (MODE M2 TURBO) ---
# Sur ton Mac M2, tu peux monter à 8 ou 9 sans problème.
# Sur Codespace, reste à 6 ou 7.
PROFONDEUR_RECURSION = 8  
SEUIL_VISIBILITE = 0.0001 # On garde les cercles même très petits

def inversion_cercle(cercle_source, cercle_inversor):
    z, r = cercle_source
    z0, r0 = cercle_inversor
    denom = abs(z - z0)**2 - r**2
    if denom == 0: return (0, 0)
    facteur = r0**2 / denom
    nouveau_centre = z0 + facteur * (z - z0)
    nouveau_rayon = abs(facteur) * r
    return (nouveau_centre, nouveau_rayon)

def generer_cercles(liste_cercles_base, profondeur):
    tous_les_cercles = []
    file_attente = [(c, i) for i, c in enumerate(liste_cercles_base)]
    tous_les_cercles.extend(liste_cercles_base)

    current_depth = 0
    while current_depth < profondeur:
        nouvelle_generation = []
        for cercle_courant, index_parent in file_attente:
            for i, cercle_base in enumerate(liste_cercles_base):
                if i == index_parent: continue
                
                nouveau_cercle = inversion_cercle(cercle_courant, cercle_base)
                
                if nouveau_cercle[1] > SEUIL_VISIBILITE: 
                    nouvelle_generation.append((nouveau_cercle, i))
                    tous_les_cercles.append(nouveau_cercle)
        
        file_attente = nouvelle_generation
        current_depth += 1
        print(f"Profondeur {current_depth} calculée... ({len(tous_les_cercles)} cercles)")
        
    return tous_les_cercles

# --- MAIN ---
r0 = 1/2
cercles_base = [
    (1 + 0j, r0), (-1 + 0j, r0), (0 + 1j, r0), (0 - 1j, r0)
]

resultat = generer_cercles(cercles_base, PROFONDEUR_RECURSION)

# Affichage Haute Qualité
fig, ax = plt.subplots(figsize=(12, 12)) # Grande image
ax.set_aspect('equal')
ax.set_facecolor('black')

print("Génération du graphique...")
for (centre, rayon) in resultat:
    # ASTUCE PRO : L'épaisseur du trait (linewidth) dépend du rayon !
    # Plus le cercle est petit, plus le trait est fin.
    epaisseur = 0.8 * (rayon / r0) ** 0.6 
    c = Circle((centre.real, centre.imag), rayon, color='royalblue', fill=False, linewidth=max(epaisseur, 0.05))
    ax.add_patch(c)

limit = 1.2
ax.set_xlim(-limit, limit)
ax.set_ylim(-limit, limit)
ax.axis('off')

# SAUVEGARDE EN PDF (VECTORIEL)
# C'est ça qui permet le zoom infini sans pixelisation
nom_fichier = 'journal/images/perles_indra_hd.pdf'
plt.savefig(nom_fichier, facecolor='black', edgecolor='none')
print(f"Terminé ! Image vectorielle sauvegardée sous : {nom_fichier}")

# On génère aussi un PNG haute déf pour l'aperçu rapide
plt.savefig('journal/images/perles_indra_preview.png', dpi=300, facecolor='black')
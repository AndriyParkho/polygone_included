#!/usr/bin/env python3
"""
fichier principal pour la detection des inclusions.
ce fichier est utilise pour les tests automatiques.
attention donc lors des modifications.
"""
import sys
from tycat import read_instance
from tycat import tycat
from geo.point import Point
from geo.polygon import Polygon
from tri_fusion import tri_fusion_polygone, tri_fusion
from inclusion_points import dans_polygon1, dans_polygon2
from itertools import combinations
import time

def trouve_inclusions_naif(polygones):
    longueur = len(polygones)
    liste_resultat = [-1]*longueur
    for i in range(longueur): # On parcours tout les polygones
        polygones_sup = []                # Liste pour stocker tout les polygones dans le quel le ième polygone est inclus
        point_test = polygones[i].points[0]     # On choisit un point test
        for j in range(longueur):           # On parcourt tout les polygones
            if j != i:                      # sauf le ième pour verifier si ils contiennent ce dernier
                if dans_polygon1(point_test, polygones[j]):
                    polygones_sup += [j]
        if polygones_sup != []:
        # Détermine le polygone avec l'air la plus petite
            min_air, i_petit_poly = abs(polygones[polygones_sup[0]].area()), polygones_sup[0]
            for indice_poly in polygones_sup[1:]:
                air_poly = abs(polygones[indice_poly].area())
                if air_poly <= min_air:
                    min_air, i_petit_poly = air_poly, indice_poly
            liste_resultat[i] = i_petit_poly   # On stock l'indice du plus petit polygone dans les résultats
    return liste_resultat


def trouve_inclusions(polygones):
    liste_resultat = [-1]*len(polygones)
    liste_indices = list(range(0, len(polygones)))
    #on trie les polygones par aire. On donne aussi l'ordre dans lequel ils sont ordonnés
    polygones, liste_indices = tri_fusion_polygone(polygones, liste_indices)

    for i in range(len(polygones)): #on parcourt chacun des polygones
        point_test = polygones[i].points[0] #on choisit un point test
        quadrant_contenu = polygones[i].bounding_quadrant()
        for j in range(i+1, len(polygones)): #pour tous les polygones ayant une aire supérieure
            quadrant_contenant = polygones[j].bounding_quadrant()
            # On vérifie déjà si les quadrants s'intersectent
            if quadrant_contenu.intersect(quadrant_contenant):
                # On verifie si le point_test est dans le quadrant
                if point_test.quadrant_inclusion(quadrant_contenant):
                    #si le point est dans le polygone (donc si le polygone auquel il appartient est dans le polygone)
                    if dans_polygon1(point_test, polygones[j]):
                        #print("on a reconnu l'inclusion de " +str(liste_indices[i])+ " dans "+ str(liste_indices[j]))
                        liste_resultat[liste_indices[i]] = (liste_indices[j]) #on ajoute l'indice du polygone a la liste résultat
                        break

    return liste_resultat


# Pareil que le précédent mais avec l'autre tri fusion
def trouve_inclusions_bis(polygones):
    liste_resultat = [-1]*len(polygones)
    #on trie les polygones par aire. On donne aussi l'ordre dans lequel ils sont ordonnés
    liste_indices = tri_fusion([abs(poly.area()) for poly in polygones], list(range(0, len(polygones))))
    for i in range(len(polygones) - 1, -1, -1): #on parcourt chacun des polygones en partant du plus grand
        point_test = polygones[liste_indices[i]].points[0] #on choisit un point test
        quadrant_contenu = polygones[liste_indices[i]].bounding_quadrant()
        for j in range(i+1, len(polygones)): #pour tous les polygones ayant une aire supérieure
            quadrant_contenant = polygones[liste_indices[j]].bounding_quadrant()
            # On vérifie déjà si les quadrants s'intersectent
            if quadrant_contenu.intersect(quadrant_contenant):
                # On verifie si le point_test est dans le quadrant
                if point_test.quadrant_inclusion(quadrant_contenant):
                    #si le point est dans le polygone (donc si le polygone auquel il appartient est dans le polygone)
                    if dans_polygon1(point_test, polygones[liste_indices[j]]):
                        #print("on a reconnu l'inclusion de " +str(liste_indices[i])+ " dans "+ str(liste_indices[j]))
                        liste_resultat[liste_indices[i]] = (liste_indices[j]) #on ajoute l'indice du polygone a la liste résultat
                        break

    return liste_resultat



def main():
    """
    charge chaque fichier .poly donne
    trouve les inclusions
    affiche l'arbre en format texte
    """
    for fichier in sys.argv[1:]:
        polygones = read_instance(fichier)
        inclusions = trouve_inclusions(polygones)
        print(inclusions)
    # for fichier in sys.argv[1:]:
    #     polygones = read_instance(fichier)
    #     start_time = time.time()
    #     inclusions_bis = trouve_inclusions_bis(polygones)
    #     temps_bis = time.time() - start_time
    #     print("Résultats algo bis:", inclusions_bis)
    #     print("Temps algo bis:", temps_bis)
    #     start_time = time.time()
    #     inclusions = trouve_inclusions(polygones)
    #     temps = time.time() - start_time
    #     print("Résultats algo normal:", inclusions)
    #     print("Temps algo normal:", temps)


if __name__ == "__main__":
    main()

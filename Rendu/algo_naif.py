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
from geo.segment import Segment


def point_intersection(point, segment):
    """
    Vérifie si la semi-droite verticale tracée vers le haut
    à partir du point intersecte le segment
    """
    x_point = point.coordinates[0]
    x1, x2 = segment.endpoints[0].coordinates[0], segment.endpoints[1].coordinates[0]
    if segment.is_vertical() or x_point < min(x1, x2) or x_point >= max(x1, x2):
        return False

    if segment.endpoints[0].coordinates[1] < point.coordinates[1] and segment.endpoints[1].coordinates[1] < point.coordinates[1]:
        return True

    coeff, oao = segment.eq_droite()
    y_inter = coeff*x_point + oao
    if point.coordinates[1] > y_inter:
        return True
    return False


def point_dans_polygone(point, polygone):
    """
    utilise l'algorithme du raycast fourni avec amélioration pour savoir si un point est dans un polygone
    """
    count = 0                                                                   # Compteur du nombre de segments traversés

    for segment in polygone.segments():

        if point_intersection(point, segment):
            count += 1
    return bool(count%2)                                                    #on renvoie True si le nombre est impair, False si il est pair


def trouve_inclusions_naif(polygones):
    longueur = len(polygones)
    liste_resultat = [-1]*longueur
    for i in range(longueur): # On parcours tout les polygones
        polygones_sup = []                # Liste pour stocker tout les polygones dans le quel le ième polygone est inclus
        point_test = polygones[i].points[0]     # On choisit un point test
        for j in range(longueur):           # On parcourt tout les polygones
            if j != i:                      # sauf le ième pour verifier si ils contiennent ce dernier
                if point_dans_polygone(point_test, polygones[j]):
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


def main():
    """
    charge chaque fichier .poly donne
    trouve les inclusions
    affiche l'arbre en format texte
    """
    for fichier in sys.argv[1:]:
        polygones = read_instance(fichier)
        inclusions = trouve_inclusions_naif(polygones)
        print(inclusions)


if __name__ == "__main__":
    main()

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


def air_poly_liste(polygones):
    """
    Renvoie une liste de triplet (indice, polygones, air du polygone)
    """
    return [[i, abs(polygones[i].area())] for i in range(len(polygones))]

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


def trouve_inclusions_air_quadrant(polygones):
    nb_polygones = len(polygones)
    liste_resultat = [-1]*nb_polygones
    #on trie les polygones par aire. En renvoyant la liste des triplet
    air_liste = sorted(air_poly_liste(polygones), key = lambda triplet: triplet[1])
    quadrant_liste = [poly.bounding_quadrant() for poly in polygones]
    for i in range(nb_polygones - 1, -1, -1): #on parcourt chacun des polygones
        point_test = polygones[air_liste[i][0]].points[0] #on choisit un point test
        for j in range(i+1, nb_polygones): #pour tous les polygones ayant une aire supérieure
            # On vérifie si les aires ne sont pas égales
            if air_liste[i][1] < air_liste[j][1]:
                # On vérifie déjà si les quadrants s'intersectent
                if quadrant_liste[air_liste[i][0]].intersect(quadrant_liste[air_liste[j][0]]):
                    # On vérifie si le point est dans le polygone
                    if point_dans_polygone(point_test, polygones[air_liste[j][0]]):
                        liste_resultat[air_liste[i][0]] = air_liste[j][0] # On ajoute l'indice du polygone a la liste résultat
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
        inclusions = trouve_inclusions_air_quadrant(polygones)
        print(inclusions)


if __name__ == "__main__":
    main()

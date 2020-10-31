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
from geo.quadrant import Quadrant
from itertools import combinations
import time

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

        y_min = min(point.coordinates[1] for point in segment.endpoints)
        if y_min < point.coordinates[1]:
            if point_intersection(point, segment):
                count += 1
    return bool(count%2)                                                    #on renvoie True si le nombre est impair, False si il est pair

def taille_diagonale_quadrant(quadrant):
    """
    renvoie la taille de la diagonale d'une quadrant
    """
    point_mini = Point(quadrant.min_coordinates)
    point_maxi = Point(quadrant.max_coordinates)
    return point_mini.distance_to(point_maxi)



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


def trouve_inclusions(polygones):
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

def trouve_inclusion_quadrant(polygones):
    nb_polygones = len(polygones)
    liste_resultat = [-1] * nb_polygones
    polygones_caracteristiques = [[polygones[i], i, polygones[i].bounding_quadrant(), taille_diagonale_quadrant(polygones[i].bounding_quadrant())] for i in range(nb_polygones)]
    polygones_caracteristiques.sort(key=lambda polygone_cara : polygone_cara[3])
    #desormais tries
    for i in range(nb_polygones -1):
        point_test = polygones_caracteristiques[i][0].points[0] #premier point du polygone

        for j in range(i + 1, nb_polygones):
            if polygones_caracteristiques[i][2].intersect(polygones_caracteristiques[j][2]):
                if polygones_caracteristiques[i][3] < polygones_caracteristiques[j][3]:
                    if point_dans_polygone(point_test, polygones_caracteristiques[j][0]):
                        liste_resultat[polygones_caracteristiques[i][1]] = polygones_caracteristiques[j][1]
                        break

    return liste_resultat

def main():
    """
    charge chaque fichier .poly donne
    trouve les inclusions
    affiche l'arbre en format texte
    """
    # for fichier in sys.argv[1:]:
    #     polygones = read_instance(fichier)
    #     inclusions = trouve_inclusion_quadrant(polygones)
    #     tycat(polygones)
    #     print(inclusions)
    somme = 0
    for i in range(10):
        for fichier in sys.argv[1:]:
            polygones = read_instance(fichier)
            start_time = time.time()
            inclusions = trouve_inclusions(polygones)
            temps_normal = time.time() - start_time
            #print("Résultats algo de base:", inclusions)
            print("Temps algo de base:", temps_normal)
            start_time = time.time()
            inclusions_test = trouve_inclusion_quadrant(polygones)
            temps_test = time.time() - start_time
            #print("Résultats algo normal:", inclusions_test)
            print("Temps algo nouveau: ", temps_test)
            somme += temps_test - temps_normal
    print('moyenne : ', somme/10)

if __name__ == "__main__":
    main()

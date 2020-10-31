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
import time
import numpy as np
import matplotlib.pyplot as plt
import csv

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


def taille_diagonale_quadrant(quadrant):
    """
    renvoie la taille de la diagonale d'une quadrant
    """
    point_mini = Point(quadrant.min_coordinates)
    point_maxi = Point(quadrant.max_coordinates)
    return point_mini.distance_to(point_maxi)

def poly_indice_quadrant_diagonale(polygone, i):
    """
    Renvoie le couple quadrant et diagonale de quadrant
    """
    rectangle = polygone.bounding_quadrant()
    return [polygone, i, rectangle, taille_diagonale_quadrant(rectangle)]


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

def trouve_inclusions_quadrant(polygones):
    nb_polygones = len(polygones)
    liste_resultat = [-1] * nb_polygones
    polygones_caracteristiques = [poly_indice_quadrant_diagonale(polygones[i], i) for i in range(nb_polygones)]
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


def intersection_ligne(x_ligne, segment):
    """
    Retourne l'ordonnée du point d'intersection s'il y a intersection
    """
    coeff, oao = segment.eq_droite()
    y_inter = coeff*x_ligne + oao
    return y_inter

def orientation(segment):
    if segment.endpoints[0].coordinates[0] < segment.endpoints[1].coordinates[0]:
        return 1
    else:
        return -1

def polygones_quadrant(polygones):
    return [[polygone, polygone.bounding_quadrant()] for polygone in polygones]


def liste_intersection(x_ligne, polygones):
    """
    Retourne la liste des couples (y_intersection, indice_poly, Bool_ajout)
    """
    liste_intersec = []
    for i, (polygone, quadrant) in enumerate(polygones):
        if x_ligne < quadrant.min_coordinates[0] or x_ligne > quadrant.max_coordinates[0]:
            continue
        orientation_prec = 0
        for segment in polygone.segments():
            x1, x2 = segment.endpoints[0].coordinates[0], segment.endpoints[1].coordinates[0]
            if segment.is_vertical() or min(x1, x2) > x_ligne or max(x1, x2) < x_ligne:
                continue
            y0, y1 = segment.endpoints[0].coordinates[1], segment.endpoints[1].coordinates[1]
            if x_ligne == segment.endpoints[0].coordinates[0]:
                orientation_actuelle = orientation(segment)
                if orientation_prec == 0:
                    orientation_prec = orientation_actuelle
                elif orientation_prec == -1:
                    if orientation_actuelle == -1:
                        liste_intersec += [[y0, i, True]]
                    else:
                        liste_intersec += [[y0, i, False]]
                    orientation_prec = 0
                else:
                    if orientation_actuelle == -1:
                        liste_intersec += [[y0, i, False]]
                    else:
                        liste_intersec += [[y0, i, True]]
                    orientation_prec = 0
            elif x_ligne == segment.endpoints[1].coordinates[0]:
                orientation_actuelle = orientation(segment)
                if orientation_prec == 0:
                    orientation_prec = orientation_actuelle
                elif orientation_prec == -1:
                    if orientation_actuelle == -1:
                        liste_intersec += [[y1, i, True]]
                    else:
                        liste_intersec += [[y1, i, False]]
                    orientation_prec = 0
                else:
                    if orientation_actuelle == -1:
                        liste_intersec += [[y1, i, False]]
                    else:
                        liste_intersec += [[y1, i, True]]
                    orientation_prec = 0
            else:
                liste_intersec += [[intersection_ligne(x_ligne, segment), i, True]]
    return liste_intersec


def trouve_inclusions_ligne(polygones):
    nb_polygones = len(polygones)
    poly_croise = [False]*nb_polygones
    liste_resultat = [-1]*nb_polygones
    polygone_quadrant = polygones_quadrant(polygones)
    j = 0
    while j < nb_polygones and not(poly_croise[j]):
        liste_intersec = sorted(liste_intersection(polygones[j].points[0].coordinates[0], polygone_quadrant), key = lambda triplet: triplet[0])
        liste_eponge = []
        for y_intersec, i, ajout in liste_intersec:
            if liste_eponge == []:
                poly_croise[i] = True
                if ajout:
                    liste_eponge.append(i)
            else:
                if i == liste_eponge[-1]:
                    if ajout:
                        liste_eponge.pop()
                else:
                    liste_resultat[i] = liste_eponge[-1]
                    poly_croise[i] = True
                    if ajout:
                        liste_eponge.append(i)
        j += 1
        while j < nb_polygones and poly_croise[j]:
            j += 1
    return liste_resultat



def tests_temps(function):
    """
    Renvoie les temps selon le nombre de polygones
    """
    nb_polygones = [500, 1000, 1500, 2000, 2500, 3000, 3500, 4000,\
                    10000, 20000, 30000, 40000]
    temps = []
    for nb in nb_polygones:
        fichier = "tests/polygons/" + sys.argv[1] + "-" + str(nb) + ".poly"
        polygones = read_instance(fichier)
        start_time = time.time()
        function(polygones)
        temps += [time.time() - start_time]
    return(nb_polygones, temps)


def tests_temps_csv():
    """
    Renvoie les temps en les cherchant dans le .csv
    """
    fname = sys.argv[1]
    file = open(fname, "r")
    temps = []
    nb_polygones = []
    reader = csv.reader(file)
    next(reader)
    for ligne in reader:
        valeur = ligne[0].split('-')[1]
        nb, ok, tmps = valeur.split(';')
        nb_polygones.append(int(nb))
        temps.append(float(tmps))
    file.close()
    return (nb_polygones, temps)


def trace_graphique():
    x, y1 = tests_temps_csv()
    # y2 = tests_temps(trouve_inclusions_naif)[1]
    # y3 = tests_temps(trouve_inclusion_test)[1]
    plt.plot(x, y1, label="avec aires")
    # plt.plot(x, y2, label="Naif")
    # plt.plot(x, y3, label="sans aires")
    plt.title("Mesure de performances")
    plt.xlabel("Nombre de polygones")
    plt.ylabel("Temps")
    plt.legend()
    plt.show()


def main():
    """
    charge chaque fichier .poly donne
    trouve les inclusions
    affiche l'arbre en format texte
    """
    # trace_graphique()
    for fichier in sys.argv[1:]:
        polygones = read_instance(fichier)
        # inclusions = trouve_inclusions_ligne(polygones)
        tycat(polygones)
        # print(inclusions)
    # for fichier in sys.argv[1:]:
    #     polygones = read_instance(fichier)
    #     start_time = time.time()
    #     inclusions_bis = trouve_inclusions_bis(polygones)
    #     temps_bis = time.time() - start_time
    #     print("Résultats algo bis:", inclusions_bis)
    #     print("Temps algo bis:", temps_bis)
        # start_time = time.time()
        # inclusions = trouve_inclusions_quadrant(polygones)
        # temps = time.time() - start_time
        # print("Résultats algo normal:", inclusions)
        # print("Temps algo normal:", temps)


if __name__ == "__main__":
    main()

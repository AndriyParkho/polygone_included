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


def trouve_inclusions_quadrant(polygones):
    nb_polygones = len(polygones)
    #initialisation de la liste des résultats
    liste_resultat = [-1] * nb_polygones
    #on stocke les triplets polygone, indice, quadrant, taille de la diagonale du quadrant
    polygones_caracteristiques = [poly_indice_quadrant_diagonale(polygones[i], i) for i in range(nb_polygones)]
    #on trie la liste en fonction des tailles de diagonale
    polygones_caracteristiques.sort(key=lambda polygone_cara : polygone_cara[3])

    for i in range(nb_polygones - 1):
        point_test = polygones_caracteristiques[i][0].points[0] #premier point du polygone

        for j in range(i + 1, nb_polygones): #pour les polygones ayant une diagonale plus grande que le polygone considere
            if polygones_caracteristiques[i][2].intersect(polygones_caracteristiques[j][2]): #si les quadrants ont une zone en commun
                if polygones_caracteristiques[i][3] < polygones_caracteristiques[j][3]: #si la diagonale est strictement inférieure (enleve polygones identiques par exemple)
                    if point_dans_polygone(point_test, polygones_caracteristiques[j][0]): #on teste sur l'inclusion du point dans le polygone
                        liste_resultat[polygones_caracteristiques[i][1]] = polygones_caracteristiques[j][1] #on ajoute le polygone parent a la liste resultat
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
        inclusions = trouve_inclusions_quadrant(polygones)
        print(inclusions)


if __name__ == "__main__":
    main()

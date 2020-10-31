#!/usr/bin/env python3

from geo.point import Point
from geo.segment import Segment
from tycat import tycat
from random import randint
from geo.polygon import Polygon

def intersection_with_vertical(point_ref, segment):
    """
    renvoie si un segment intersecte un segment vertical au dessus du point
    """
    #point de reference
    x_point_ref, y_point_ref = point_ref.coordinates
    #points du segment
    point1, point2 = segment.endpoints

    x_point1, y_point1 = point1.coordinates
    x_point2, y_point2 = point2.coordinates

    if x_point1 == x_point2 :
        #print("Vertical")
        return False #si vertical

    if y_point1 > y_point_ref and y_point2 > y_point_ref:
        #print("On est en dessous")
        return False #si les deux points sont en dessous, ça n'intersecte pas

    if not(min(x_point1, x_point2) <= x_point_ref and max(x_point1, x_point2) >= x_point_ref):
        #print("Du meme cote")
        return False #si les deux point sont du même coté non plus

    if y_point1 <= y_point_ref and y_point2 <= y_point_ref:
        #print("Cote different et au dessus")
        return True #si les deux points sont de coté différents et au dessus du point, ça intersecte

    #dernier cas à traiter : cote different mais un au dessus, un en dessous : on compare les pentes
    point_a_gauche = point1 if x_point1 <= x_point2 else point2
    point_a_droite = point2 if point_a_gauche == point1 else point1

    pente_ref = (y_point_ref - point_a_gauche.coordinates[1])/(x_point_ref - point_a_gauche.coordinates[0])
    pente = (point_a_droite.coordinates[1] - point_a_gauche.coordinates[1])/(point_a_droite.coordinates[0] - point_a_gauche.coordinates[0])

    #print("pente", pente)
    #print("pente ref", pente_ref)
    if pente <= pente_ref:
        #print("pente <= pente_ref")
        return True
    else:
        #print("pente > pente_ref")
        return False



def segment_aleatoire(x_min, x_max, y_min, y_max):
    point1 = Point([randint(x_min, x_max), randint(y_min, y_max)])
    point2 = Point([randint(x_min, x_max), randint(y_min, y_max)])
    return Segment((point1, point2))

def main():
    point_ref = Point([3, 3])
    segments = []
    carre = Polygon.square(0, 0, 6)
    while True:
        input("Nouveau segment, appuyez sur entrée : ")
        segment = segment_aleatoire(0, 6, 0, 6)

        tycat(carre, point_ref, segment.endpoints)
        print(intersection_with_vertical(point_ref, segment))

if __name__ == '__main__':
    main()

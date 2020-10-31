"""
vérifie si le point est inclus dans le polygone
"""

from geo.point  import Point
from geo.polygon import Polygon
from geo.segment import Segment
from tycat import tycat

def dans_polygon1(point, polygon):
    """
    utilise l'algorithme du raycast fourni avec amélioration pour savoir si un point est dans un polygone
    """
    count = 0                                                                   # Compteur du nombre de segments traversés
    quadrant = polygon.bounding_quadrant()                                      # On créer le plus petit quadrant contenant le polygon
    segment_test = Segment([point, Point([point.coordinates[0], quadrant.min_coordinates[1] - 5])])           # On choisit comme segment pour le raycast le segment
                                                                                # vertical partant du point vers le haut


    for segment in polygon.segments():

        x_max = max(point.coordinates[0] for point in segment.endpoints)
        x_min = min(point.coordinates[0] for point in segment.endpoints)
        y_min = min(point.coordinates[1] for point in segment.endpoints)
        if not(x_min < point.coordinates[0] <= x_max and y_min <= point.coordinates[1]):
            continue
        i = segment_test.intersection_with(segment)                         # Point d'intersection entre le segment pour le raycast et segment du polygone
        if i is not None:
            count += 1
    return bool(count%2)                                                    #on renvoie True si le nombre est impair, False si il est pair



def dans_polygon2(point, polygon):
    """
    utilise l'algorithme du raycast modifié fourni pour savoir si un point est dans un polygone
    """
    new_point = Point((point.coordinates[0], point.coordinates[1]))
    count = 0                                                                                   #compteur du nombre de segments traversés
    pas = Point((1e-6, 0))

    for segment in polygon.segments():                                                          #on parcout les extremités des segments, et on retourne True si on est à un bout

        for extremite in segment.endpoints:
            if extremite.coordinates == new_point.coordinates:
                return True

        if segment.contains(new_point):                                                         #si le point est sur le segment, on renvoie direct true
            return True


        #On regarde le rectange dans lequel est contenu le segment

        x_max = max(point.coordinates[0] for point in segment.endpoints)
        y_max = max(point.coordinates[1] for point in segment.endpoints)
        x_min = min(point.coordinates[0] for point in segment.endpoints)
        y_min = min(point.coordinates[1] for point in segment.endpoints)

        if new_point.coordinates[0] <= x_max and y_min <= new_point.coordinates[1] <= y_max:    #si le point est pas a droite du rectangle, et dans les limites de hauteur

            point_0 = Point((max(x_min, new_point.coordinates[0]), new_point.coordinates[1]))   #on place le point avec lequel on va faire le raycast soit sur la gauche du rectangle, soit sur le point lui meme
            while point_0.coordinates[0] <= x_max:                                              # tant qu'on est a gauche du rectangle
                if segment.contains(point_0):                                                   #on regarde si le point est sur le segment
                    count += 1                                                                  #si c'est le cas, on rajoutte 1 au compteur
                    break                                                                       #on passe au segment suivant
                point_0 += pas                                                                  #sinon, on passe au point suivant

    return bool(count%2)                                                                        #on renvoie True si le nombre est impair, False si il est pair

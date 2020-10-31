#!/usr/bin/env python3
"""
Programme principal de l'algo utilisant une droite verticale pour déterminer
l'inclusion des polygones
"""
import sys
from tycat import read_instance
from tycat import tycat
from geo.point import Point
from geo.polygon import Polygon
from geo.segment import Segment


def intersection_droite(x_droite, segment):
    """
    Retourne l'ordonnée du point d'intersection s'il y a intersection
    """
    coeff, oao = segment.eq_droite()
    y_inter = coeff*x_droite + oao
    return y_inter

def orientation(segment):
    """
    Retourne l'orientation du segment avec 1 = droite et -1 = gauche
    """
    if segment.endpoints[0].coordinates[0] < segment.endpoints[1].coordinates[0]:
        return 1
    else:
        return -1

def polygones_quadrant(polygones):
    """
    Retourne la liste des couples (polygone, quadrant)
    """
    return [[polygone, polygone.bounding_quadrant()] for polygone in polygones]


def liste_intersection(x_droite, polygones):
    """
    Retourne la liste des couples (y_intersection, indice_poly, Bool_ajout)
    """
    liste_intersec = []
    for i, (polygone, quadrant) in enumerate(polygones):
        # Si la droite se situe à droite ou à gauche de la droite verticale on ne regarde pas le polygone
        if x_droite < quadrant.min_coordinates[0] or x_droite > quadrant.max_coordinates[0]:
            continue
        orientation_prec = 0    # On sauvegarde l'orientation du segment précédent,
                                # 0 signifie que l'orientation ne nous interesse pas
        for segment in polygone.segments():
            x1, x2 = segment.endpoints[0].coordinates[0], segment.endpoints[1].coordinates[0]
            # Si le segment est vertical on ne fait rien et on garde l'orientation
            # du segment précédent. De plus, si la droite se situe à droite ou
            # à gauche de la droite verticale on ne regarde pas le polygone
            if segment.is_vertical() or min(x1, x2) > x_droite or max(x1, x2) < x_droite:
                continue
            y0, y1 = segment.endpoints[0].coordinates[1], segment.endpoints[1].coordinates[1]
            # Si le début du segment intersecte la droite on a un cas particulier
            if x_droite == segment.endpoints[0].coordinates[0]:
                orientation_actuelle = orientation(segment)
                # Si l'orientation du seg précédent ne nous interessait pas on ne fait rien
                if orientation_prec == 0:
                    orientation_prec = orientation_actuelle
                # Si le segment prec est dirigé vers la gauche...
                elif orientation_prec == -1:
                    # ...et l'actuelle aussi cela signifie que le polygone reste
                    # "ouvert" dans la droite donc on aura un autre point d'intersection avec ce polygone
                    # on ajoutera ce point d'intersection à la liste tampon
                    if orientation_actuelle == -1:
                        liste_intersec += [[y0, i, True]]
                    # ...et l'actuelle vers la droite alors le polygone se "referme"
                    # donc on aura pas d'autre point pour le polygone, on ajoutera pas
                    # le point à la liste_tampon au risque de compter ce polygone
                    # comme le père d'une autre alors que non
                    else:
                        liste_intersec += [[y0, i, False]]
                    orientation_prec = 0
                # Si le segment prec. est dirigé vers la droite on a le symétrique du cas précédent
                else:
                    if orientation_actuelle == -1:
                        liste_intersec += [[y0, i, False]]
                    else:
                        liste_intersec += [[y0, i, True]]
                    orientation_prec = 0
            # Si la fin du segment intersecte la droite on a un autre cas particulier
            elif x_droite == segment.endpoints[1].coordinates[0]:
                orientation_actuelle = orientation(segment)
                # Si l'orientation du seg précédent ne nous interessait pas on ne fait rien
                if orientation_prec == 0:
                    orientation_prec = orientation_actuelle
                # Les deux cas qui suivent surviennent lorsqu'on a commencé à parcourir notre polygone
                # à partir d'un segment dont le début s'intersecte avec la droite verticale
                # on garde l'orientation de ce premier segment jusqu'à retombé sur le
                # segment qui "referme" sur la droite verticale, on a alors les même cas
                # que précédemment.
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
                liste_intersec += [[intersection_droite(x_droite, segment), i, True]]
    return liste_intersec


def trouve_inclusions_droite(polygones):
    """
    Retourne la liste des inclusions par l'algorithme de la droite vertical (imaginaire)
    """
    nb_polygones = len(polygones)
    poly_croise = [False]*nb_polygones
    liste_resultat = [-1]*nb_polygones
    polygone_quadrant = polygones_quadrant(polygones) # On récupère les quadrant de nos polygones
    j = 0
    # Tant qu'il reste des polygones qui n'ont pas été croisé par une droite verticale on boucle
    while j < nb_polygones and not(poly_croise[j]):
        liste_intersec = sorted(liste_intersection(polygones[j].points[0].coordinates[0], polygone_quadrant), key = lambda triplet: triplet[0])
        liste_tampon = []
        for y_intersec, i, ajout in liste_intersec:
            # Si la liste_tampon est vide le père du polygone i est -1 mais vu qu'on initialise
            # à -1 on ne fait rien à part ajouté le polygone à la liste tampon
            if liste_tampon == []:
                poly_croise[i] = True
                if ajout:
                    liste_tampon.append(i)
            else:
                # Si le dernier element est le polygone i et qu'on était censé ajouté
                # le polygone i on retire ce dernier élément si on était censé ajouté
                if i == liste_tampon[-1]:
                    if ajout:
                        liste_tampon.pop()
                # Sinon le père du polygone i est le dernier élément de la liste_tampon
                else:
                    liste_resultat[i] = liste_tampon[-1]
                    poly_croise[i] = True
                    if ajout:
                        liste_tampon.append(i)
        j += 1
        # On regarde quels polygones n'ont pas été croisé par une droite verticale
        while j < nb_polygones and poly_croise[j]:
            j += 1
    return liste_resultat


def main():
    """
    charge chaque fichier .poly donne
    trouve les inclusions
    affiche l'arbre en format texte
    """
    for fichier in sys.argv[1:]:
        polygones = read_instance(fichier)
        inclusions = trouve_inclusions_droite(polygones)
        print(inclusions)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3

from geo.polygon import Polygon


def fusion(polygones1, polygones2, liste_indices1, liste_indices2):

    n1 = len(polygones1)
    n2 = len(polygones2)

    i1 = 0
    i2 = 0


    polygones_tries = [None]*(n1+n2)
    liste_indices_tries = [None]*(n1+n2)

    while i1 < n1 and i2 < n2:
        if abs(polygones1[i1].area()) < abs(polygones2[i2].area()):
            polygones_tries[i1+i2] = polygones1[i1]
            liste_indices_tries[i1+i2] = liste_indices1[i1]
            i1 += 1
        else:
            polygones_tries[i1+i2] = polygones2[i2]
            liste_indices_tries[i1+i2] = liste_indices2[i2]
            i2 += 1
    if i1 == n1:
        while i2 < n2:
            polygones_tries[i2+i1] = polygones2[i2]
            liste_indices_tries[i1+i2] = liste_indices2[i2]
            i2 +=1
    else:
        while i1 < n1:
            polygones_tries[i2+i1] = polygones1[i1]
            liste_indices_tries[i1+i2] = liste_indices1[i1]
            i1 +=1
    return polygones_tries, liste_indices_tries

def tri_fusion_polygone(polygones, liste_indices):
    """
    tri fusion sur les polygones en fontion de leur aire
    """
    if len(polygones) <= 1:
        return polygones, liste_indices
    else:
        polygones1, liste_indices1 = tri_fusion_polygone(polygones[:len(polygones)//2], liste_indices[:len(polygones)//2])
        polygones2, liste_indices2 = tri_fusion_polygone(polygones[len(polygones)//2:], liste_indices[len(polygones)//2:])

        return fusion(polygones1, polygones2, liste_indices1, liste_indices2)

# Un autre tri fusion meilleur en terme de perf mais qui plante si n trop grand...

def fusion2(polygones_air, indices1, indices2):
    """
    Fusion des deux listes de façon à les trier
    """
    if indices1 == []:
        return indices2
    elif indices2 == []:
        return indices1
    elif polygones_air[indices1[0]] < polygones_air[indices2[0]]:
        return [indices1[0]] + fusion2(polygones_air, indices1[1:], indices2)
    else:
        return [indices2[0]] + fusion2(polygones_air, indices1, indices2[1:])

def tri_fusion(polygones_air, indices):
    n = len(indices)
    if n < 2:
        return indices
    else:
        m = n // 2
        return fusion2(polygones_air ,tri_fusion(polygones_air, indices[:m]), tri_fusion(polygones_air, indices[m:]))

#!/usr/bin/env python3
"""
permet de tester les fonctions sur un fichier .poly rentré en argument
"""

from tycat import read_instance
import sys
from tycat import tycat
from geo.point import Point
from inclusion_points_bis import dans_polygon
from tri_fusion import tri_fusion_polygone

polygones = read_instance(sys.argv[1])
liste_indices = list(range(0, len(polygones)))
for polygone in polygones:
    print(polygone.area())
polygones, liste_indices = tri_fusion_polygone(polygones, liste_indices)
print("liste triee :")
for polygone in polygones:
    print(polygone.area())
print(liste_indices)

#dans le cas d'un carré, on place un point au centre


points = [Point((3, 1))]

coord = [0, 1, 2]
for x in coord:
    for y in coord:
        points.append(Point((x, y)))

tycat(points, polygones)

print("Test point exterieur")
print(dans_polygon(points[0], polygones[0]))

print("Test points supposés dedans (centre, sur coins/segments)")
for point in points[1:]:
    print(point, " : ", dans_polygon(point, polygones[0]),)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
affichage d'intersection de segments
"""
from geo.segment import Segment
from itertools import combinations
from geo.point import Point
from random import random

def point_aleatoire():
    """
    renvoie un point du plan de coordonnees aleatoires
    entre 0 et 800
    """
    return (random()*800, random()*800)


def segment_aleatoire():
    """
    renvoie un segment du plan de coordonnees aleatoires
    entre 0 et 800
    """
    return Segment([Point(point_aleatoire()), Point(point_aleatoire())])

def affiche_point(p):
    print('<circle cx="{}" cy="{}" r="3" fill="red"/>'.format(p.coordinates[0], p.coordinates[1]))

def main():
    segments = [segment_aleatoire() for _ in range(10)]
    segments.append(Segment([Point([400, 0]), Point([400, 800])]))
    segments.append(Segment([Point([0, 0]), Point([800, 0])]))
    segments.append(Segment([Point([0, 0]), Point([0, 800])]))
    segments.append(Segment([Point([0, 800]), Point([800, 800])]))

    intersections_brutes = (s1.intersection_with(s2) for s1, s2 in combinations(segments, 2))
    intersections = (i for i in intersections_brutes if i is not None)

#    for i1, s1 in enumerate(segments):
#        for s2 in segments[(i1+1):]:
#            i = s1.intersection(s2)
#            if i is not None:
#                intersections.append(i)

    print('<svg width="800" height="800">')
    for segment in segments:
        segment.svg_content()
    for intersection in intersections:
        affiche_point(intersection)
    print('</svg>')


main()

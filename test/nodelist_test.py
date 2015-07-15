#!/usr/bin/env python
# coding: utf-8

from myworkspace import NodeList


def test_nodelist():
    k1 = 'a/b/c'
    k2 = 'a/b/d'
    k3 = 'e'

    nl = NodeList(k1, k2, k3)
    assert nl.nodes['a']['b']['c'] == []
    assert nl[k1] == []

    nl[k2].append(1)
    assert nl.nodes['a']['b']['d'] == [1]

    nl[k3] = 3
    assert nl.nodes['e'] == 3

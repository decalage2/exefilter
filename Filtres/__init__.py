#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
"""
ExeFilter - Package des filtres de formats.

Le fichier __init__.py sert à dresser dynamiquement la liste des filtres
présents dans ce package Filtres.

Ce fichier fait partie du projet ExeFilter.

@author: U{Philippe Lagadec<mailto:philippe.lagadec(a)laposte.net>}
@author: U{Yannick Bidan}
@organization: DGA/CELAR

@contact: U{Philippe Lagadec<mailto:philippe.lagadec(a)laposte.net>}

@copyright: DGA/CELAR 2004-2007
@license: CeCILL (open-source compatible GPL) - cf. code source ou fichier LICENCE.txt joint

@version: 1.01
@status: beta
"""
__docformat__ = 'epytext en'

__date__      = "06/02/2008"
__version__   = "1.01"

#------------------------------------------------------------------------------
# LICENCE:

# Copyright DGA/CELAR 2004-2007
# Auteurs:
# - Philippe Lagadec (PL) - philippe.lagadec(a)laposte.net
# - Arnaud Kerréneur (AK) - arnaud.kerreneur(a)dga.defense.gouv.fr
# - Tanguy Vinceleux (TV) - tanguy.vinceleux(a)dga.defense.gouv.fr
#
# Ce logiciel est régi par la licence CeCILL soumise au droit français et
# respectant les principes de diffusion des logiciels libres. Vous pouvez
# utiliser, modifier et/ou redistribuer ce programme sous les conditions
# de la licence CeCILL telle que diffusée par le CEA, le CNRS et l'INRIA
# sur le site "http://www.cecill.info". Une copie de cette licence est jointe
# dans les fichiers Licence_CeCILL_V2-fr.html et Licence_CeCILL_V2-en.html.
#
# En contrepartie de l'accessibilité au code source et des droits de copie,
# de modification et de redistribution accordés par cette licence, il n'est
# offert aux utilisateurs qu'une garantie limitée.  Pour les mêmes raisons,
# seule une responsabilité restreinte pèse sur l'auteur du programme,  le
# titulaire des droits patrimoniaux et les concédants successifs.
#
# A cet égard  l'attention de l'utilisateur est attirée sur les risques
# associés au chargement,  à l'utilisation,  à la modification et/ou au
# développement et à la reproduction du logiciel par l'utilisateur étant
# donné sa spécificité de logiciel libre, qui peut le rendre complexe à
# manipuler et qui le réserve donc à des développeurs et des professionnels
# avertis possédant  des  connaissances  informatiques approfondies.  Les
# utilisateurs sont donc invités à charger  et  tester  l'adéquation  du
# logiciel à leurs besoins dans des conditions permettant d'assurer la
# sécurité de leurs systèmes et ou de leurs données et, plus généralement,
# à l'utiliser et l'exploiter dans les mêmes conditions de sécurité.
#
# Le fait que vous puissiez accéder à cet en-tête signifie que vous avez
# pris connaissance de la licence CeCILL, et que vous en avez accepté les
# termes.


#------------------------------------------------------------------------------
# HISTORIQUE:
# 24/05/2005 v0.01 YB: - 1ère version
# 28/05/2005 v0.02 YB: - Mise en conformité de la doc avec epydoc
# 12/10/2005 v0.03 PL: - modif de commentaires
#                      - ajout de classes_filtres(), qui permet d'obtenir plus
#                        simplement une liste des classes de filtres disponibles
# 20/10/2005       PL: - correction d'un commentaire pour epydoc
# 16/01/2006 v0.04 PL: - liste statique de modules si compilation py2exe
# 06/02/2006 v0.05 PL: - chargement optionnel du filtre MIME, qq corrections
# 12/01/2007 v1.00 PL: - version 1.00 officielle
# 06/02/2008 v1.01 PL: - ajout licence CeCILL

# A FAIRE:
# + supprimer liste_filtres si plus utilisé (obsolète)
# ? faire un reload des modules plutôt que import, au cas où les filtres seraient
#   mis à jour depuis le 1er import ?
#------------------------------------------------------------------------------

#=== IMPORTS ==================================================================

import inspect
import sys
import os
import os.path
import glob
import string
import re

from path import path

from commun import *
import Filtres.Filtre

# import direct de modules pour compilation py2exe:
import Filtres.Filtre_AVI
import Filtres.Filtre_BMP
import Filtres.Filtre_GIF
import Filtres.Filtre_HTML
import Filtres.Filtre_JPEG
import Filtres.Filtre_MP3
import Filtres.Filtre_Office
import Filtres.Filtre_PDF
import Filtres.Filtre_PNG
import Filtres.Filtre_RTF
import Filtres.Filtre_Texte
import Filtres.Filtre_WAV
import Filtres.Filtre_Zip
# le filtre MIME est pour l'instant expérimental:
try:
    import Filtres.Filtre_MIME
except:
    pass

#------------------------------------------------------------------------------
# liste_filtres
#---------------------

def liste_filtres():
    """
    Fonction qui charge de façon dynamique les filtres présents dans le package

    Cette fonction retourne également un dictionnaire de description des filtres

    @return: la description des filtres présents dans le package
    @rtype: dict

    """

    # on récupère la liste des fichiers présents dans le répertoire
    chemin_package = os.path.normpath(__path__[0])
    list_dir = glob.glob(chemin_package+"/Filtre_*.py*")
    __liste_filtres__= {}

    # Pour chacun des filtres,
    for filtre in list_dir :
        # on calcule le nom du filtre...
        (head,fichier) = os.path.split(filtre)
        len = fichier.rfind(".")
        fichier_module = fichier[:len]
        module = "Filtres." + fichier_module
        # on vérifie si le module a déjà été chargé
        if __liste_filtres__.has_key(module) : continue
        # si le module n'a pas encore été chargé : on l'importe
        __liste_filtres__[module] = {}
        __import__(module)

        # on charge les infos du module
        for el in sys.modules[module].__dict__ :
            # on essaie de trouver les classes d'objets qui sont décrites
            if inspect.isclass(sys.modules[module].__dict__[el]):
                # si c'est une classe de description de filtre
                if re.match("^Filtre_.*",el) != None:
                    # on commence à charger les infos de la classe de filtre
                    __liste_filtres__[module][module + "." + el] = {}
                    nom = extensions = version = date = ""
                    # charge le nom du filtre
                    if sys.modules[module].__dict__[el].__dict__.has_key("nom") :
                        __liste_filtres__[module][module + "." + el]["nom"] = \
                            sys.modules[module].__dict__[el].__dict__["nom"]
                    else:
                        __liste_filtres__[module][module + "." + el]["nom"] = nom
                    #on charge les extensions gérées par le filtre
                    if sys.modules[module].__dict__[el].__dict__.has_key("extensions") :
                        __liste_filtres__[module][module + "." + el]["extensions"] = \
                            ', '.join(sys.modules[module].__dict__[el].__dict__["extensions"])
                    else:
                        __liste_filtres__[module][module + "." + el]["extensions"] = extensions

                    # on charge la version du filtre
                    if sys.modules[module].__dict__[el].__dict__.has_key("version") :
                         __liste_filtres__[module][module + "." + el]["version"] = \
                             sys.modules[module].__dict__[el].__dict__["version"]
                    else:
                        __liste_filtres__[module][module + "." + el]["version"] = version
                    # on charge la date de mise à jour du filtre
                    if sys.modules[module].__dict__[el].__dict__.has_key("date") :
                        __liste_filtres__[module][module + "." + el]["date"] = \
                            sys.modules[module].__dict__[el].__dict__["date"]
                    else:
                        __liste_filtres__[module][module + "." + el]["date"] = date
    return __liste_filtres__

#------------------------------------------------------------------------------
# classes_filtres
#---------------------

def classes_filtres():
    """
    Fonction qui importe de façon dynamique les modules de filtres présents
    dans le package, et retourne une simple liste des classes de filtres
    disponibles dans ces modules (classes non instanciées).

    @return: liste des classes de filtres présents dans le package
    @rtype: list
    """
    # liste des classes de filtres, vide au départ:
    liste_classes_filtres = []
    # si compilation py2exe, on ne peut faire qu'une liste statique:
    if main_is_frozen():
        liste_classes_filtres = [
            Filtres.Filtre_AVI.Filtre_AVI,
            Filtres.Filtre_BMP.Filtre_BMP,
            Filtres.Filtre_GIF.Filtre_GIF,
            Filtres.Filtre_HTML.Filtre_HTML,
            Filtres.Filtre_JPEG.Filtre_JPEG,
            Filtres.Filtre_MP3.Filtre_MP3,
            Filtres.Filtre_Office.Filtre_Word,
            Filtres.Filtre_Office.Filtre_Excel,
            Filtres.Filtre_Office.Filtre_Powerpoint,
            Filtres.Filtre_PDF.Filtre_PDF,
            Filtres.Filtre_PNG.Filtre_PNG,
            Filtres.Filtre_RTF.Filtre_RTF,
            Filtres.Filtre_Texte.Filtre_Texte,
            Filtres.Filtre_WAV.Filtre_WAV,
            Filtres.Filtre_Zip.Filtre_Zip
        ]
        # le filtre MIME est pour l'instant expérimental:
        try:
            liste_classes_filtres.append(Filtres.Filtre_MIME.Filtre_MIME)
        except:
            pass
        return liste_classes_filtres
    # d'abord, on détermine le répertoire du package Filtres:
    rep_filtres = path(__file__).abspath().dirname()
    #print "repertoire du package Filtres: %s" % rep_filtres
    # on dresse la liste des modules de filtres présents dans le package:
    # (sous forme source *.py ou compilée *.pyc)
    liste_modules = rep_filtres.files('Filtre_*.py')
    if liste_modules == []:
        liste_modules = rep_filtres.files('Filtre_*.pyc')
    # liste des modules importés, vide au départ:
    modules_importes = []
    # Pour chacun des modules, on cherche les classes de filtres:
    for module in liste_modules :
        #print "module filtre: %s" % module
        # on extrait le nom du module du chemin complet:
        nom_module = "Filtres." + module.namebase
        if nom_module not in modules_importes:
            # si le module n'est pas encore importé, on s'en charge:
            #print "nom module: %s" % nom_module
            modules_importes.append(nom_module)
            __import__(nom_module)
            # ensuite on parcourt les objets du module:
            for nom_objet, objet in sys.modules[nom_module].__dict__.iteritems():
                # si l'objet commence par "Filtre_" et est une classe
                if nom_objet.startswith("Filtre_") and inspect.isclass(objet):
                    # ...et si c'est une sous-classe de Filtre
                    if issubclass(objet, Filtres.Filtre.Filtre):
                        # alors on la sélectionne:
                        #print "classe filtre: " + nom_objet
                        liste_classes_filtres.append(objet)
                        #print objet.__name__
    # on a terminé:
    return liste_classes_filtres




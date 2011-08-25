#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
"""
Filtre_XML - ExeFilter

Ce module contient la classe L{Filtre_XML.Filtre_XML} permettant de filtrer
les fichiers de type "document XML".

Ce fichier fait partie du projet ExeFilter.
URL du projet: U{http://www.decalage.info/exefilter}

@author: U{Philippe Lagadec<mailto:philippe.lagadec(a)laposte.net>}

@contact: U{Philippe Lagadec<mailto:philippe.lagadec(a)laposte.net>}

@copyright: Philippe Lagadec 2011

@license: CeCILL (open-source compatible GPL)
          cf. code source ou fichier LICENCE.txt joint

@version: 0.01

@status: alpha
"""
#==============================================================================
__docformat__ = 'epytext en'

__date__    = "2011-08-24"
__version__ = "0.01"

#------------------------------------------------------------------------------
# LICENCE pour le projet ExeFilter:

# Copyright DGA/CELAR 2004-2008
# Copyright NATO/NC3A 2008-2010 (PL changes after ExeFilter v1.1.0)
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
# CHANGELOG:
# 2011-02-21 v0.01 PL: - 1st version
# 2011-08-24       PL: - code cleanup

#------------------------------------------------------------------------------
# TODO:
# + clean xml-stylesheet processing instruction (parameter to enable)

#=== IMPORTS ==================================================================

# modules standards Python:

# XML parser - lxml or ElementTree:
try:
    # lxml: best performance for XML processing
    import lxml.etree as ET
except ImportError:
    try:
        # Python 2.5+: batteries included
        import xml.etree.cElementTree as ET
    except ImportError:
        try:
            # Python <2.5: standalone ElementTree install
            import elementtree.cElementTree as ET
        except ImportError:
            raise ImportError, "lxml or ElementTree are not installed, "\
                +"see http://codespeak.net/lxml "\
                +"or http://effbot.org/zone/element-index.htm"


# modules du projet:
from commun import *
import Resultat, Conteneur
import Filtre


#=== CONSTANTES ===============================================================


#=== CLASSES ==================================================================


class Filtre_XML (Filtre.Filtre):
    """
    classe pour un filtre de fichiers XML.

    un objet Filtre sert à reconnaître le format d'un fichier et à
    nettoyer le code éventuel qu'il contient. La classe Filtre_XML
    correspond aux documents XML.

    @cvar nom: Le nom detaillé du filtre
    @cvar nom_code: nom de code du filtre
    @cvar extensions: liste des extensions de fichiers possibles
    @cvar format_conteneur: indique si c'est un format conteneur
    @cvar extractible: indique si il s'agit d'une archive
    @cvar nettoyable: indique si il est possible de nettoyer avec ce filtre
    @cvar date: date de la derniere modification du filtre
    @cvar version: version du filtre
    """

    nom = _(u"Document XML")
    extensions = [".xml"]
    format_conteneur = False
    extractible = False
    nettoyable = True

    # date et version définies à partir de celles du module
    date = __date__
    version = __version__

    def reconnait_format(self, fichier):
        """
        analyse le format du fichier, et retourne True s'il correspond
        au format recherché, False sinon.
        """
        # Check if the XML file can be parsed without error:
        self.tree = ET.parse(fichier.copie_temp())
        return True

    def nettoyer (self, fichier):
        """
        Analyse et modifie le fichier pour supprimer tout code
        exécutable qu'il peut contenir, si cela est possible.
        Retourne un code résultat suivant l'action effectuée.
        """
        # For now, let's just accept any XML without cleaning:
        return self.resultat_accepte(fichier)


#------------------------------------------------------------------------------
# TESTS
#---------------------
# tests de certaines fonctions si le module est lancé directement et non importé:
if __name__ == '__main__':
    print "----------------------------------------------------------------------------"
    print "Filtre XML v%s du %s - %s" % (__version__, __date__, __author__)
    print "----------------------------------------------------------------------------"
    print ""
    #TODO: test XML parsing and cleaning

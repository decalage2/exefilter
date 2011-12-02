#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
"""
Filtre_OpenXML - ExeFilter

This module contains the class L{Filtre_OpenXML.Filtre_OpenXML},
to scan and clean Open XML files (Microsoft Office 2007 and later).

This file is part of the ExeFilter project.
Project URL: U{http://www.decalage.info/exefilter}

@author: U{Philippe Lagadec<mailto:philippe.lagadec(a)laposte.net>}

@contact: U{Philippe Lagadec<mailto:philippe.lagadec(a)laposte.net>}

@copyright: Philippe Lagadec 2011

@license: CeCILL (open-source compatible GPL)
          cf. code source ou fichier LICENCE.txt joint

@version: 0.02

@status: alpha
"""
#==============================================================================
__docformat__ = 'epytext en'

__date__    = "2011-12-02"
__version__ = "0.02"

#------------------------------------------------------------------------------
# LICENCE pour le projet ExeFilter:

# Copyright DGA/CELAR 2004-2008
# Copyright NATO/NC3A 2008-2010 (PL changes after v1.1.0)
# Auteurs:
# - Philippe Lagadec (PL) - philippe.lagadec(a)laposte.net
# - Arnaud Kerr�neur (AK) - arnaud.kerreneur(a)dga.defense.gouv.fr
# - Tanguy Vinceleux (TV) - tanguy.vinceleux(a)dga.defense.gouv.fr
#
# Ce logiciel est r�gi par la licence CeCILL soumise au droit fran�ais et
# respectant les principes de diffusion des logiciels libres. Vous pouvez
# utiliser, modifier et/ou redistribuer ce programme sous les conditions
# de la licence CeCILL telle que diffus�e par le CEA, le CNRS et l'INRIA
# sur le site "http://www.cecill.info". Une copie de cette licence est jointe
# dans les fichiers Licence_CeCILL_V2-fr.html et Licence_CeCILL_V2-en.html.
#
# En contrepartie de l'accessibilit� au code source et des droits de copie,
# de modification et de redistribution accord�s par cette licence, il n'est
# offert aux utilisateurs qu'une garantie limit�e.  Pour les m�mes raisons,
# seule une responsabilit� restreinte p�se sur l'auteur du programme,  le
# titulaire des droits patrimoniaux et les conc�dants successifs.
#
# A cet �gard  l'attention de l'utilisateur est attir�e sur les risques
# associ�s au chargement,  � l'utilisation,  � la modification et/ou au
# d�veloppement et � la reproduction du logiciel par l'utilisateur �tant
# donn� sa sp�cificit� de logiciel libre, qui peut le rendre complexe �
# manipuler et qui le r�serve donc � des d�veloppeurs et des professionnels
# avertis poss�dant  des  connaissances  informatiques approfondies.  Les
# utilisateurs sont donc invit�s � charger  et  tester  l'ad�quation  du
# logiciel � leurs besoins dans des conditions permettant d'assurer la
# s�curit� de leurs syst�mes et ou de leurs donn�es et, plus g�n�ralement,
# � l'utiliser et l'exploiter dans les m�mes conditions de s�curit�.
#
# Le fait que vous puissiez acc�der � cet en-t�te signifie que vous avez
# pris connaissance de la licence CeCILL, et que vous en avez accept� les
# termes.

#------------------------------------------------------------------------------
# CHANGELOG:
# 2011-02-21 v0.01 PL: - 1st version
# 2011-12-02 v0.02 PL: - added initial support for .rels files

#------------------------------------------------------------------------------
# TODO:
# - complete list of extensions (add dotx, etc)
# - split formats in several filters, one per app: Word, Excel, PowerPoint, etc?
# - filter macros here or in the container class?
# - fix relationships when a file is removed
# - add filters for WMF, EMF, TIFF, etc

#------------------------------------------------------------------------------

#=== IMPORTS ==================================================================

# modules standards Python:

# modules du projet:
from commun import *
import Filtre_Zip
import Filtre_XML

#=== CONSTANTES ===============================================================


#=== CLASSES ==================================================================

class Filtre_OpenXML (Filtre_Zip.Filtre_Zip):
    """
    class to scan and clean Open XML documents (Microsoft Office 2007 and later).

    A Filter object is used to recognize the format of a file, to scan and to
    clean potential active content.
    This class is based on Filtre_Zip.

    Attributes:
    @cvar nom: Le nom detaill� du filtre
    @cvar nom_code: nom de code du filtre
    @cvar extensions: liste des extensions de fichiers possibles
    @cvar format_conteneur: indique si c'est un format conteneur
    @cvar extractible: indique si il s'agit d'une archive
    @cvar nettoyable: indique si il est possible de nettoyer avec ce filtre
    @cvar date: date de la derniere modification du filtre
    @cvar version: version du filtre
    """

    nom = _(u"Open XML document")
    extensions = [".docx", '.docm', '.xlsx', '.xlsm', '.pptx', '.pptm']
    format_conteneur = True
    extractible = True
    nettoyable = True

    # date et version d�finies � partir de celles du module
    date = __date__
    version = __version__

    def reconnait_format(self, fichier):
        """Analyse le format du fichier, et retourne True s'il correspond
        au format recherch�, False sinon.

        @param fichier: fichier � analyser
        @type  fichier: objet L{Fichier.Fichier}
        """
        #TODO: also check if mandatory files are  in the archive?
        return Filtre_Zip.Filtre_Zip.reconnait_format(self, fichier)


class Filtre_OpenXML_rels (Filtre_XML.Filtre_XML):
    """
    class to scan and clean .rels files within Open XML documents (Microsoft
    Office 2007 and later), which are simple XML files.

    A Filter object is used to recognize the format of a file, to scan and to
    clean potential active content.
    This class is based on Filtre_XML.

    Attributes:
    @cvar nom: Le nom detaill� du filtre
    @cvar nom_code: nom de code du filtre
    @cvar extensions: liste des extensions de fichiers possibles
    @cvar format_conteneur: indique si c'est un format conteneur
    @cvar extractible: indique si il s'agit d'une archive
    @cvar nettoyable: indique si il est possible de nettoyer avec ce filtre
    @cvar date: date de la derniere modification du filtre
    @cvar version: version du filtre
    """

    nom = _(u"Open XML .rels file")
    extensions = ['.rels']

    # date et version d�finies � partir de celles du module
    date = __date__
    version = __version__




# coded while listening to Family of the Year's EP "TODO"
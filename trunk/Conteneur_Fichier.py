#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
"""
Conteneur_Fichier - ExeFilter

Module qui contient la classe L{Conteneur_Fichier.Conteneur_Fichier},
pour traiter un conteneur qui correspond � un simple fichier.

Ce fichier fait partie du projet ExeFilter.
URL du projet: U{http://www.decalage.info/exefilter}

@organization: DGA/CELAR
@author: U{Philippe Lagadec<mailto:philippe.lagadec(a)laposte.net>}
@author: U{Arnaud Kerr�neur<mailto:arnaud.kerreneur(a)dga.defense.gouv.fr>}

@contact: U{Philippe Lagadec<mailto:philippe.lagadec(a)laposte.net>}

@copyright: DGA/CELAR 2004-2008
@copyright: NATO/NC3A 2008-2010 (modifications PL apres ExeFilter v1.1.0)

@license: CeCILL (open-source compatible GPL)
          cf. code source ou fichier LICENCE.txt joint

@version: 1.05

@status: beta
"""
#==============================================================================
__docformat__ = 'epytext en'

__date__    = "2010-02-04"
__version__ = "1.05"

#------------------------------------------------------------------------------
# LICENCE pour le projet ExeFilter:

# Copyright DGA/CELAR 2004-2008
# Copyright NATO/NC3A 2008-2010 (PL changes after ExeFilter v1.1.0)
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
# HISTORIQUE:
# 18/05/2005 v0.01 PL: - 1�re version
# 2005-2007     PL,AK: - �volutions
#                      - contributions de Y. Bidan et C. Catherin
# 12/01/2007 v1.00 PL: - version 1.00 officielle
# 2007-11-03 v1.01 PL: - ajout licence CeCILL
# 2008-03-24 v1.02 PL: - ajout de _() pour traduction gettext des chaines
# 2008-04-20 v1.03 PL: - ajout parametre politique a Conteneur_Fichier.__init__
# 2009-11-11 v1.04 PL: - added option to have a filename as destination
# 2010-02-04 v1.05 PL: - fixed temp dir deletion

#------------------------------------------------------------------------------
# A FAIRE:
#------------------------------------------------------------------------------

#=== IMPORTS ==================================================================

import os

# module path.py pour manipuler plus facilement les fichiers/r�pertoires
from path import path

# modules du projet:
from commun import *
import Conteneur
import Conteneur_Repertoire
import Fichier

#=== CONSTANTES ===============================================================


#=== CLASSES ==================================================================
#------------------------------------------------------------------------------
# class CONTENEUR_FICHIER
#----------------------------
class Conteneur_Fichier (Conteneur_Repertoire.Conteneur_Repertoire):
    """
    classe pour analyser un fichier simple (c'est en fait un
    L{Conteneur_Repertoire.Conteneur_Repertoire} qui ne contient qu'un fichier).

    Un objet Conteneur correspond � un r�pertoire ou � un fichier
    Contient un ensemble de fichiers, par exemple une archive Zip.
    La classe Conteneur_Fichier correspond � un simple fichier.
    (n�cessaire quand on ne veut analyser qu'un fichier)
    """

    def __init__(self, nom_fichier, repertoire_destination, rep_relatif_source,
        fichier=None, politique=None, dest_is_a_file=False):
        """
        Constructeur d'objet Conteneur_Fichier.

        @param nom_fichier: le nom du fichier
        @type nom_fichier: str

        @param repertoire_destination: le r�pertoire destination o� copier le
                                       fichier apres transfert
        @type repertoire_destination: str

        @param dest_is_a_file: False if repertoire_destination is a dir (default),
                               True if it's a filename.
        @type dest_is_a_file: bool
        """
        # nom source est le chemin absolu du r�pertoire source:
        chem_source = path(nom_fichier).abspath().normpath().dirname()
        Journal.debug(u"chem_source = %s" % chem_source)
        self.dest_is_a_file = dest_is_a_file
        if dest_is_a_file:
            # if dest is a file, store filename and use its parent dir:
            self.dest_filename = os.path.abspath(repertoire_destination)
            repertoire_destination = os.path.dirname(self.dest_filename)
        # on appelle d'abord le constructeur de base
        #self.type = "Fichier"
        Conteneur.Conteneur.__init__(self, chem_source, repertoire_destination,
            rep_relatif_source, fichier, politique)
        self.type = _(u"Fichier")
        # on sauve le nom de fichier:
        self.nom_fichier = path(nom_fichier).name
        print self


    def lister_fichiers (self):
        """
        retourne la liste contenant l'objet Fichier, qui n'est
        lue qu'une fois au 1er appel.
        """
        # pour le chemin du fichier on ne garde que le
        # chemin relatif par rapport au r�pertoire
        if len(self.liste_fichiers) == 0:
            f = Fichier.Fichier(self.nom_fichier, conteneur=self)
            self.liste_fichiers.append(f)
        return self.liste_fichiers


    def reconstruire (self):
        """
        reconstruit le Conteneur � partir des fichiers nettoy�s.
        """
        # if destination is a directory, use the normal method:
        if not self.dest_is_a_file:
            Conteneur_Repertoire.Conteneur_Repertoire.reconstruire(self)
        # else destination is a file:
        else:
            # check if there's only one file:
            assert(len(self.liste_fichiers) == 1)
            fichier = self.liste_fichiers[0]
            # si le fichier n'est pas refuse, on le recopie a destination:
            if not fichier.resultat_fichier.est_refuse():
                # directory of dest file:
                chem_dest_fich = path(os.path.dirname(self.dest_filename))
##                Journal.debug(u"self.chem_dest = %s" % self.chem_dest)
##                Journal.debug(u"fichier.chemin.parent = %s" % fichier.chemin.parent)
##                Journal.debug(u"fichier.chemin = %s" % fichier.chemin)
##                Journal.debug(u"chem_dest_fich = %s" % chem_dest_fich)
                # create dest dir if it does not exist:
                if not chem_dest_fich.exists():
                    chem_dest_fich.makedirs()
                fichier_dest = self.dest_filename
                Journal.info2(_(u'Copie vers la destination: "%s" -> "%s"...') % (fichier._copie_temp, fichier_dest))
                fichier._copie_temp.copy2(fichier_dest)
                # no archiving in that mode:
##                # Si l'option archivage (archive_after) est activee:
##                if self.politique.parametres['archive_after'].valeur:
##                    # on copie les fichiers nettoy�s vers le r�pertoire archivage
##                    #TODO: code a simplifier
##                    chem_dest_fich = path(self.rep_archive) / path(commun.sous_rep_archive) / self.rep_relatif_source / fichier.chemin.parent
##                    if not chem_dest_fich.exists():
##                        chem_dest_fich.makedirs()
##                    fichier_dest = path(self.rep_archive) / path(commun.sous_rep_archive) / self.rep_relatif_source / fichier.chemin
##                    debug(_(u'Copie: "%s" -> "%s"...') % (fichier._copie_temp, fichier_dest))
##                    fichier._copie_temp.copy2(fichier_dest)

            # puis d�truire le r�pertoire temporaire !
            debug ("Effacement du repertoire temporaire %s" % self.rep_temp_complet)
            self.rep_temp_complet.rmtree()


#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
"""
Conteneur_Repertoire - ExeFilter

Module qui contient la classe L{Conteneur_Repertoire.Conteneur_Repertoire},
pour traiter les fichiers d'un r�pertoire.

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

@version: 1.06

@status: beta
"""
#==============================================================================
__docformat__ = 'epytext en'

__date__    = "2011-04-17"
__version__ = "1.06"

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
# 24/10/2004 v0.01 PL: - 1�re version
# 2004-2007     PL,AK: - nombreuses �volutions
#                      - contributions de Y. Bidan et C. Catherin
# 12/01/2007 v1.00 PL: - version 1.00 officielle
# 2007-11-03 v1.01 PL: - ajout licence CeCILL
# 2008-03-24 v1.02 PL: - ajout de _() pour traduction gettext des chaines
# 2008-04-20 v1.03 PL: - ajout parametre politique a Conteneur_Repertoire.__init__
#                      - archivage en fonction du parametre 'archive_after'
# 2010-02-04 v1.04 PL: - fixed temp dir deletion
# 2010-02-07 v1.05 PL: - removed path import
# 2011-04-17 v1.06 PL: - code to delete temp dir moved to Conteneur


#------------------------------------------------------------------------------
# A FAIRE:
#------------------------------------------------------------------------------

#=== IMPORTS ==================================================================

# modules standards Python
import os, stat

# modules du projet:
from commun import *
import commun
import Conteneur
import Fichier
import Resultat

#=== CONSTANTES ===============================================================


#=== CLASSES ==================================================================

#------------------------------------------------------------------------------
# class CONTENEUR_REPERTOIRE
#----------------------------

class Conteneur_Repertoire (Conteneur.Conteneur):
    """
    classe pour analyser un dossier contenant des fichiers.

    un objet Conteneur correspond � un r�pertoire ou � un fichier
    qui contient un ensemble de fichiers, par exemple une archive Zip.
    La classe Conteneur_Repertoire correspond � un r�pertoire.

    """

    def __init__(self, nom_repertoire, nom_destination, rep_relatif_source,
                fichier=None, politique=None):
        """
        Constructeur d'objet Conteneur_Repertoire.


        @param nom_repertoire: nom du r�pertoire du conteneur source.
        (chemin relatif par rapport au conteneur)
        @type nom_repertoire: str

        @param nom_destination: nom de fichier/r�pertoire du conteneur nettoy�.
        @type nom_destination: str

        @param fichier: objet Fichier du conteneur.
        @type fichier: str

        """
        # nom source est le chemin absolu du r�pertoire source:
        chem_source = path(nom_repertoire).abspath().normpath()
        # on appelle d'abord le constructeur de base
        Conteneur.Conteneur.__init__(self, chem_source, nom_destination,
            rep_relatif_source, fichier, politique)
        self.type = _(u"Repertoire")
        self.taille_rep = 0
        print self


    def lister_fichiers (self):
        """
        retourne la liste des objets Fichier du r�pertoire, qui n'est lue qu'une fois au 1er appel.
        """
        if len(self.liste_fichiers) == 0:
            for fichier in self.chem_src.walkfiles():
                # pour le chemin du fichier on ne garde que le
                # chemin relatif par rapport au r�pertoire
                fichier = self.chem_src.relpathto(fichier)
                f = Fichier.Fichier(fichier, conteneur=self)
                self.liste_fichiers.append(f)
        return self.liste_fichiers


    def compter_taille_rep (self):
        """
        Compte la taille totale des fichiers contenus dans le repertoire.

        @return: taille totale en octets
        @rtype:  int
        """
        if len(self.liste_fichiers) == 0:
            for fichier in self.chem_src.walkfiles():
                self.taille_rep += os.stat(fichier).st_size
        return self.taille_rep


    def copie_temp (self, fichier):
        """
        copie le fichier vers un r�pertoire temporaire, et retourne
        le chemin de la copie. Cette fonction est normalement appel�e
        par Fichier.copie_temp() uniquement au 1er appel.
        """
        # on s'assure d'abord que le r�pertoire relatif du fichier existe
        # (on suppose que fichier.chemin contient un chemin relatif...)
        chem_temp = self.rep_temp_complet / fichier.chemin.parent
        Journal.debug(u"rep_temp : %s" % self.rep_temp_complet)
        Journal.debug (u"fichier.chemin %s" % fichier.chemin)
        Journal.debug(u"chem_temp = %s" % chem_temp)
        if not chem_temp.exists():
            chem_temp.makedirs()
        fichier_temp = self.rep_temp_complet / fichier.chemin
        fichier_source = self.chem_src / fichier.chemin
        Journal.info2(_(u'Copie temporaire: "%s" -> "%s"...') % (fichier_source, fichier_temp))
        fichier_source.copy2(fichier_temp)

        # droit en �criture sur le r�pertoire temporaire pour suppression
        #TODO: est-ce necessaire et sur ??
        os.chmod( path(fichier_temp).abspath().normpath(), stat.S_IRWXU )

        return fichier_temp


    def reconstruire (self):
        """
        reconstruit le Conteneur � partir des fichiers nettoy�s.
        """
        for fichier in self.liste_fichiers:
            # si le fichier n'est pas refuse, on le recopie a destination:
            if not fichier.resultat_fichier.est_refuse():
                #TODO: code a simplifier
                chem_dest_fich = self.chem_dest / self.rep_relatif_source / fichier.chemin.parent
                Journal.debug(u"self.chem_dest = %s" % self.chem_dest)
                Journal.debug(u"fichier.chemin.parent = %s" % fichier.chemin.parent)
                Journal.debug(u"fichier.chemin = %s" % fichier.chemin)
                Journal.debug(u"chem_dest_fich = %s" % chem_dest_fich)
                if not chem_dest_fich.exists():
                    chem_dest_fich.makedirs()
                fichier_dest = self.chem_dest / self.rep_relatif_source / fichier.chemin
                Journal.info2(_(u'Copie vers la destination: "%s" -> "%s"...') % (fichier._copie_temp, fichier_dest))
                fichier._copie_temp.copy2(fichier_dest)

                # Si l'option archivage (archive_after) est activee:
                if self.politique.parametres['archive_after'].valeur:
                    # on copie les fichiers nettoy�s vers le r�pertoire archivage
                    #TODO: code a simplifier
                    chem_dest_fich = path(self.rep_archive) / path(commun.sous_rep_archive) / self.rep_relatif_source / fichier.chemin.parent
                    if not chem_dest_fich.exists():
                        chem_dest_fich.makedirs()
                    fichier_dest = path(self.rep_archive) / path(commun.sous_rep_archive) / self.rep_relatif_source / fichier.chemin
                    debug(_(u'Copie: "%s" -> "%s"...') % (fichier._copie_temp, fichier_dest))
                    fichier._copie_temp.copy2(fichier_dest)

##        # puis d�truire le r�pertoire temporaire !
##        debug ("Effacement du repertoire temporaire %s" % self.rep_temp_complet)
##        self.rep_temp_complet.rmtree()

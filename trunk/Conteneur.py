#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
"""
Conteneur - ExeFilter

Module qui contient la classe L{Conteneur.Conteneur},
pour manipuler des conteneurs g�n�riques de fichiers (repertoire, archive).

Ce fichier fait partie du projet ExeFilter.
URL du projet: U{http://www.decalage.info/exefilter}

@organization: DGA/CELAR
@author: U{Philippe Lagadec<mailto:philippe.lagadec(a)laposte.net>}
@author: U{Arnaud Kerr�neur<mailto:arnaud.kerreneur(a)dga.defense.gouv.fr>}

@contact: U{Philippe Lagadec<mailto:philippe.lagadec(a)laposte.net>}

@copyright: DGA/CELAR 2004-2008
@copyright: NATO/NC3A 2008-2010 (PL changes after ExeFilter v1.1.0)
@license: CeCILL (open-source compatible GPL) - cf. code source ou fichier LICENCE.txt joint

@version: 1.04

@status: beta
"""
#==============================================================================
__docformat__ = 'epytext en'

__date__    = "2010-02-04"
__version__ = "1.04"

#------------------------------------------------------------------------------
# LICENCE pour le projet ExeFilter:

# Copyright DGA/CELAR 2004-2008
# Copyright NATO/NC3A 2008-2010 (modifications PL apres ExeFilter v1.1.0)
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
# 2007-10-28 v1.01 PL: - ajout licence CeCILL
#                      - amelioration portabilite creer_rep_temp avec os.path.join
# 2008-03-24 v1.02 PL: - ajout de _() pour traduction gettext des chaines
# 2008-04-20 v1.03 PL: - ajout parametre politique a Conteneur.__init__
# 2010-02-04 v1.04 PL: - fixed temp dir creation to avoid race conditions

#------------------------------------------------------------------------------
# A FAIRE:
#------------------------------------------------------------------------------

#=== IMPORTS ==================================================================

import tempfile, os, time

# module path.py pour manipuler plus facilement les fichiers/r�pertoires
from path import path

# modules du projet:
import commun
from commun import *
import Resultat
import Journal

#=== CONSTANTES ===============================================================



#=== CLASSES ==================================================================

#------------------------------------------------------------------------------
# class CONTENEUR
#---------------------
class Conteneur:
    """
    Classe pour analyser un conteneur de fichiers (dossier, archive, ...).

    Un objet Conteneur correspond � un r�pertoire ou � un fichier
    qui contient un ensemble de fichiers, par exemple une archive Zip.
    La classe Conteneur est une classe g�n�rique dont h�ritent les
    classes sp�cifique � chaque format de conteneur (r�pertoire, zip,
    tar, ...)

    Attributs d'un objet Conteneur:
        - nom_src: nom de fichier/r�pertoire du conteneur source.
        - nom_destination: nom de fichier/r�pertoire du conteneur nettoy�.
        - chem_src: objet L{path} correspondant � nom_src.
        - chem_dest: objet L{path} correspondant � nom_destination.
        - chemin_complet: chemin complet du conteneur, objet L{path}.
        - fichier: objet L{Fichier.Fichier} correspondant au conteneur.
        - liste_fichiers: liste des fichiers contenus.
        - rep_relatif_source: ??
        - rep_temp: r�pertoire temporaire pour nettoyer le conteneur (L{path}).
        - type: cha�ne (str) d�crivant le type de conteneur.
    """

    def __init__(self, nom_source, nom_destination, rep_relatif_source,
        fichier=None, politique=None):
        """
        Constructeur de la classe abstraite Conteneur.

        @param nom_source: nom de fichier/r�pertoire du conteneur source.
        (chemin relatif par rapport au conteneur)
        @type nom_source : str

        @param nom_destination: nom de fichier/r�pertoire du conteneur nettoy�.
        @type nom_destination : str

        @param fichier: objet Fichier du conteneur, ou bien None si c'est le
                        premier r�pertoire.
        @type  fichier: objet L{Fichier.Fichier} ou  None
        @param politique: objet Politique contenant les parametres.
        @type  fichier: objet L{Politique.Politique} ou  None
        """
        self.nom_src   = nom_source
        self.nom_dest  = nom_destination
        self.chem_src  = path(nom_source)
        self.chem_dest = path(nom_destination)
        self.fichier = fichier
        self.liste_fichiers = []
        self.rep_relatif_source = rep_relatif_source
        #TODO: test a supprimer quand tous les appels sont corriges:
        assert politique != None, 'Conteneur.__init__ requires politique'
        self.politique = politique
        self.rep_temp = politique.parametres['rep_temp'].valeur
        self.rep_archive = politique.parametres['rep_archives'].valeur
        # on construit le chemin complet:
        if fichier == None:
            # on est dans le 1er r�pertoire, le chemin complet est vide:
            self.chemin_complet = path("")
            # si on met le nom du fichier, on a vraiment le chemin complet,
            # mais �a donne un affichage tr�s lourd dans les rapports
            #self.chemin_complet = self.chem_src
        else:
            # sinon on r�cup�re celui du fichier associ� au conteneur:
            self.chemin_complet = fichier.chemin_complet
            Journal.debug(u"chemin_complet = %s" % self.chemin_complet)
        self.creer_rep_temp()
        Journal.debug(u"R�pertoire temporaire = %s" % self.rep_temp_complet)
        self.type = _(u"Conteneur generique")


    def creer_rep_temp(self):
        """Pour initialiser le r�pertoire temporaire n�cessaire � l'analyse du
        conteneur."""
        # create a temp subdir only accessible to current user,
        # without race conditions:
        self.rep_temp_complet = path(tempfile.mkdtemp(dir=self.rep_temp))

        # old code leading to race conditions when running several ExeFilter instances:
##        # rep_temp_complet est la concat�nation de rep_temp, sous_rep_temp et rep_relatif_source
##        # ex: le r�p source est titi. rep_temp_complet devient temp\transfert_19-07-2005_11h30m12s\titi
##        RACINE2 = os.path.join(self.rep_temp, commun.sous_rep_temp, self.rep_relatif_source)
##        if os.path.exists(RACINE2) == False:
##            os.makedirs(RACINE2)
##        self.rep_temp_complet = path(RACINE2)
##        RACINE3 = os.path.join(self.rep_temp, commun.sous_rep_temp)
##        self.rep_temp_partiel = path(RACINE3)


    def __str__(self):
        """
        retourne une repr�sentation du conteneur sous forme de chaine.

        @return: la repr�sentation de l'objet
        @rtype: str
        """
        return self.type+" : "+self.nom_src


    def lister_fichiers (self):
        """
        Retourne la liste des objets Fichier contenus dans le Conteneur.

        @return: liste des fichiers contenus
        @rtype : liste de L{Fichier.Fichier}
        """
        return self.liste_fichiers


    def copie_temp (self, fichier):
        """
        Copie le fichier vers un r�pertoire temporaire, et retourne
        le chemin de la copie.

        @warning: non impl�ment� dans cette classe g�n�rique
        """
        raise NotImplementedError


    def copie_lect (self, fichier):
        """
        fournit une version du fichier accessible en lecture

        soit l'original si c'est possible, soit une copie temporaire s'il
        est dans un conteneur ou si un filtre l'a d�j� modifi�.

        Retourne le chemin de la copie

        @warning: Pas encore impl�ment�

        """
        # En fait ce n'est pas optimal, si plusieurs filtres appellent
        # successivement cette fonction pour relire � chaque fois le
        # fichier sur un support lent comme une disquette ou un CDROM
        # Donc mieux vaut faire une copie temporaire � la 1�re lecture
        raise NotImplementedError


    def fermer (self):
        """
        Ferme le conteneur

        Ferme le conteneur une fois que tous les fichiers inclus ont
        �t� analys�s. (C'est surtout utile pour les archives)
        """
        # par d�faut on ne fait rien:
        pass


    def reconstruire (self):
        """
        reconstruit le Conteneur � partir des fichiers nettoy�s.
        """
        # � impl�menter dans les classes qui h�ritent de Conteneur.
        raise NotImplementedError


    def nettoyer(self, politique):
        """
        Nettoie le Conteneur et tous les fichiers qu'il contient.

        @param politique: politique de filtrage � appliquer, objet L{Politique.Politique}
            ou None. Si None, la politique par d�faut sera appliqu�e.
        @type  politique: objet L{Politique.Politique}
        """
        import Conteneur_Zip # import necessaire plus bas, ne peut etre fait
                             # a l'init du module car reference croisee...
        liste_resultats=[]    # liste des objets Resultat de chaque fichier
        # on commence par lister les fichiers
        self.lister_fichiers()
        for fichier in self.liste_fichiers:
            Journal.info2(_(u"FICHIER: %s") % fichier.chemin_complet)
            # test de l'interruption de transfert par l'utilisateur
            if commun.continuer_transfert == False:
                break
            fichier.nettoyer(politique)
            # on incr�mente le compteur d'avancement sauf pour les conteneurs zip
            #if self.type != "Archive Zip"  : # test incorrect si OS non fr
            if isinstance(self, Conteneur_Zip.Conteneur_Zip):
                commun.compteur_avancement += 1
            # on ajoute le r�sultat � la liste des r�sultats
            liste_resultats.append(fichier.resultat_fichier)
            #if fichier.rejet:
            #if fichier.resultat_fichier.code_resultat == Resultat.REFUSE:
            if fichier.resultat_fichier.est_refuse():
                # on supprime la copie temporaire du fichier si elle existe
                fichier.rejeter()
        # maintenant tous les fichiers ont �t� nettoy�s, on ferme le
        # conteneur:
        self.fermer()
        # on efface les �ventuels r�pertoires vides de conteneur
        if self.rep_relatif_source!= "":
            effacer_rep_vide(self.rep_temp_complet)
        # on reconstruit le conteneur � partir des fichiers temporaires nettoy�s
        self.reconstruire()
        return liste_resultats


    def est_chiffre(self, fichier):
        """Retourne True si le fichier indiqu� est chiffr�, et qu'il ne peut
        pas �tre extrait du conteneur.

        @param fichier: fichier � tester.
        @type  fichier: objet L{Fichier<Fichier.Fichier>}
        """
        # par d�faut un conteneur n'est pas chiffr�:
        return False


    def compter_nb_fichiers(self):
        """
        Renvoie le nombre de fichiers contenus dans le Conteneur

        @return: le nombre de fichier
        @rtype: int
        """
        if len(self.liste_fichiers) == 0:
            self.lister_fichiers()
        return len(self.liste_fichiers)


    def compter_taille_rep (self):
        return self.taille_rep

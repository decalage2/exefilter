#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
"""
Conteneur - ExeFilter

Module qui contient la classe L{Conteneur.Conteneur},
pour manipuler des conteneurs génériques de fichiers (repertoire, archive).

Ce fichier fait partie du projet ExeFilter.
URL du projet: U{http://www.decalage.info/exefilter}

@organization: DGA/CELAR
@author: U{Philippe Lagadec<mailto:philippe.lagadec(a)laposte.net>}
@author: U{Arnaud Kerréneur<mailto:arnaud.kerreneur(a)dga.defense.gouv.fr>}

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
# 24/10/2004 v0.01 PL: - 1ère version
# 2004-2007     PL,AK: - nombreuses évolutions
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

# module path.py pour manipuler plus facilement les fichiers/répertoires
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

    Un objet Conteneur correspond à un répertoire ou à un fichier
    qui contient un ensemble de fichiers, par exemple une archive Zip.
    La classe Conteneur est une classe générique dont héritent les
    classes spécifique à chaque format de conteneur (répertoire, zip,
    tar, ...)

    Attributs d'un objet Conteneur:
        - nom_src: nom de fichier/répertoire du conteneur source.
        - nom_destination: nom de fichier/répertoire du conteneur nettoyé.
        - chem_src: objet L{path} correspondant à nom_src.
        - chem_dest: objet L{path} correspondant à nom_destination.
        - chemin_complet: chemin complet du conteneur, objet L{path}.
        - fichier: objet L{Fichier.Fichier} correspondant au conteneur.
        - liste_fichiers: liste des fichiers contenus.
        - rep_relatif_source: ??
        - rep_temp: répertoire temporaire pour nettoyer le conteneur (L{path}).
        - type: chaîne (str) décrivant le type de conteneur.
    """

    def __init__(self, nom_source, nom_destination, rep_relatif_source,
        fichier=None, politique=None):
        """
        Constructeur de la classe abstraite Conteneur.

        @param nom_source: nom de fichier/répertoire du conteneur source.
        (chemin relatif par rapport au conteneur)
        @type nom_source : str

        @param nom_destination: nom de fichier/répertoire du conteneur nettoyé.
        @type nom_destination : str

        @param fichier: objet Fichier du conteneur, ou bien None si c'est le
                        premier répertoire.
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
            # on est dans le 1er répertoire, le chemin complet est vide:
            self.chemin_complet = path("")
            # si on met le nom du fichier, on a vraiment le chemin complet,
            # mais ça donne un affichage très lourd dans les rapports
            #self.chemin_complet = self.chem_src
        else:
            # sinon on récupère celui du fichier associé au conteneur:
            self.chemin_complet = fichier.chemin_complet
            Journal.debug(u"chemin_complet = %s" % self.chemin_complet)
        self.creer_rep_temp()
        Journal.debug(u"Répertoire temporaire = %s" % self.rep_temp_complet)
        self.type = _(u"Conteneur generique")


    def creer_rep_temp(self):
        """Pour initialiser le répertoire temporaire nécessaire à l'analyse du
        conteneur."""
        # create a temp subdir only accessible to current user,
        # without race conditions:
        self.rep_temp_complet = path(tempfile.mkdtemp(dir=self.rep_temp))

        # old code leading to race conditions when running several ExeFilter instances:
##        # rep_temp_complet est la concaténation de rep_temp, sous_rep_temp et rep_relatif_source
##        # ex: le rép source est titi. rep_temp_complet devient temp\transfert_19-07-2005_11h30m12s\titi
##        RACINE2 = os.path.join(self.rep_temp, commun.sous_rep_temp, self.rep_relatif_source)
##        if os.path.exists(RACINE2) == False:
##            os.makedirs(RACINE2)
##        self.rep_temp_complet = path(RACINE2)
##        RACINE3 = os.path.join(self.rep_temp, commun.sous_rep_temp)
##        self.rep_temp_partiel = path(RACINE3)


    def __str__(self):
        """
        retourne une représentation du conteneur sous forme de chaine.

        @return: la représentation de l'objet
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
        Copie le fichier vers un répertoire temporaire, et retourne
        le chemin de la copie.

        @warning: non implémenté dans cette classe générique
        """
        raise NotImplementedError


    def copie_lect (self, fichier):
        """
        fournit une version du fichier accessible en lecture

        soit l'original si c'est possible, soit une copie temporaire s'il
        est dans un conteneur ou si un filtre l'a déjà modifié.

        Retourne le chemin de la copie

        @warning: Pas encore implémenté

        """
        # En fait ce n'est pas optimal, si plusieurs filtres appellent
        # successivement cette fonction pour relire à chaque fois le
        # fichier sur un support lent comme une disquette ou un CDROM
        # Donc mieux vaut faire une copie temporaire à la 1ère lecture
        raise NotImplementedError


    def fermer (self):
        """
        Ferme le conteneur

        Ferme le conteneur une fois que tous les fichiers inclus ont
        été analysés. (C'est surtout utile pour les archives)
        """
        # par défaut on ne fait rien:
        pass


    def reconstruire (self):
        """
        reconstruit le Conteneur à partir des fichiers nettoyés.
        """
        # à implémenter dans les classes qui héritent de Conteneur.
        raise NotImplementedError


    def nettoyer(self, politique):
        """
        Nettoie le Conteneur et tous les fichiers qu'il contient.

        @param politique: politique de filtrage à appliquer, objet L{Politique.Politique}
            ou None. Si None, la politique par défaut sera appliquée.
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
            # on incrémente le compteur d'avancement sauf pour les conteneurs zip
            #if self.type != "Archive Zip"  : # test incorrect si OS non fr
            if isinstance(self, Conteneur_Zip.Conteneur_Zip):
                commun.compteur_avancement += 1
            # on ajoute le résultat à la liste des résultats
            liste_resultats.append(fichier.resultat_fichier)
            #if fichier.rejet:
            #if fichier.resultat_fichier.code_resultat == Resultat.REFUSE:
            if fichier.resultat_fichier.est_refuse():
                # on supprime la copie temporaire du fichier si elle existe
                fichier.rejeter()
        # maintenant tous les fichiers ont été nettoyés, on ferme le
        # conteneur:
        self.fermer()
        # on efface les éventuels répertoires vides de conteneur
        if self.rep_relatif_source!= "":
            effacer_rep_vide(self.rep_temp_complet)
        # on reconstruit le conteneur à partir des fichiers temporaires nettoyés
        self.reconstruire()
        return liste_resultats


    def est_chiffre(self, fichier):
        """Retourne True si le fichier indiqué est chiffré, et qu'il ne peut
        pas être extrait du conteneur.

        @param fichier: fichier à tester.
        @type  fichier: objet L{Fichier<Fichier.Fichier>}
        """
        # par défaut un conteneur n'est pas chiffré:
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

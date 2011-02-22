#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
"""
Filtre - ExeFilter

Ce module contient la classe L{Filtre.Filtre}. Un Filtre permet d'analyser et
nettoyer un format de fichier specifique. Filtre est une classe generique dont
herite chaque filtre.

Ce fichier fait partie du projet ExeFilter.
URL du projet: U{http://www.decalage.info/exefilter}

@organization: DGA/CELAR
@author: U{Philippe Lagadec<mailto:philippe.lagadec(a)laposte.net>}

@contact: U{Philippe Lagadec<mailto:philippe.lagadec(a)laposte.net>}

@copyright: DGA/CELAR 2004-2008
@copyright: NATO/NC3A 2008 (modifications PL apres v1.1.0)

@license: CeCILL (open-source compatible GPL)
          cf. code source ou fichier LICENCE.txt joint

@version: 1.02

@status: beta
"""
#==============================================================================
__docformat__ = 'epytext en'

__date__    = "2008-03-24"
__version__ = "1.02"

#------------------------------------------------------------------------------
# LICENCE pour le projet ExeFilter:

# Copyright DGA/CELAR 2004-2008
# Copyright NATO/NC3A 2008 (PL changes after v1.1.0)
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
# 2004-2007        PL: - nombreuses évolutions
# 12/01/2007 v1.00 PL: - version 1.00 officielle
# 2007-09-10 v1.01 PL: - ajout licence CeCILL
# 2008-03-24 v1.02 PL: - ajout de _() pour traduction gettext des chaines
#                      - ajout methodes resultat_*() pour simplifier filtres

# A FAIRE:
# - Completer fonctions resultat_*() pour retourner des objets Resultat
#   standards et homogeneiser/simplifier les filtres.
# - ajouter des fonctions communes pour simplifier la gestion des fichiers
#   temporaires lors du nettoyage de fichiers
#------------------------------------------------------------------------------

#=== IMPORTS ==================================================================

# modules du projet:
from commun import *
import Parametres
import Resultat

#=== CONSTANTES ===============================================================


#=== CLASSES ==================================================================

#------------------------------------------------------------------------------
# classe FILTRE
#-------------------
class Filtre:
    """
    classe générique pour un filtre d'un format de fichiers.

    un objet Filtre sert à reconnaître le format d'un fichier et à
    nettoyer le code éventuel qu'il contient. La classe Filtre est
    une classe générique, dont hérite chaque filtre spécifique pour
    un format donné.

    @cvar nom: Le nom detaillé du filtre
    @cvar nom_code: nom de code du filtre
    @cvar extensions: liste des extensions de fichiers possibles
    @cvar format_conteneur: indique si c'est un format conteneur
    @cvar extractible: indique si il s'agit d'une archive
    @cvar nettoyable: indique si il est possible de nettoyer avec ce filtre
    @cvar date: date de la derniere modification du filtre
    @cvar version: version du filtre

    @ivar nom_classe: nom de la classe correspondant à l'objet Filtre
    @ivar politique: politique contenant le filtre
    """

    # attributs de la classe, communs à tous les objets Filtre:
    nom = _(u"Filtre Generique")    # nom détaillé du filtre
    nom_code = "GEN"        # nom de code du filtre
    extensions = []            # liste des extensions de fichiers possibles
    format_conteneur = False    # indique si c'est un format conteneur
    extractible = False
    nettoyable = False
    # date et version définies à partir de celles du module
    date = __date__
    version = __version__

    def __init__ (self, politique, parametres=None):
        """Constructeur d'objet Filtre.

        @param parametres: dictionnaire pour fixer les paramètres du filtre
        @type  parametres: dict

        @param politique: politique contenant ce filtre
        @type  politique: L{Politique.Politique}
        """
        # nom de la classe du filtre, utilisé pour la configuration:
        self.nom_classe = self.__class__.__name__
        # on commence par créer un dictionnaire de paramètres par défaut
        self.parametres = {}
        # le seul paramètre commun à tous les filtres est "format_autorise":
        Parametres.Parametre("format_autorise", bool, nom=_(u"Format autorisé"),
            description=_(u"indique si ce format est autorisé ou non par la politique de filtrage"),
            valeur_defaut=True).ajouter(self.parametres)
        # si des paramètres ont été fournis au constructeur, on les met à jour
        if parametres:
            Parametres.importer (self.parametres, parametres)
        self.politique = politique


    def reconnait_nom (self, fichier):
        """analyse le nom du fichier, et retourne True s'il correspond
        au format recherché, False sinon."""
        # Cette méthode est générique, elle n'a pas besoin d'être
        # surchargée dans les différents filtres
        for extension in extensions:
            if fichier.nom.fnmatch(extension): return True
        return False

    def reconnait_format (self, fichier):
        """analyse le format du fichier, et retourne True s'il correspond
        au format recherché, False sinon."""
        raise NotImplementedError

    def nettoyer (self, fichier):
        """analyse et modifie le fichier pour supprimer tout code
        exécutable qu'il peut contenir, si cela est possible.
        Retourne un code résultat suivant l'action effectuée."""
        raise NotImplementedError


    def resultat_accepte (self, fichier):
        """
        Retourne un objet resultat pour un fichier accepte.

        @param: objet Fichier correspondant
        """
        return Resultat.Resultat(Resultat.ACCEPTE,
            self.nom + _(u" : Pas de contenu actif détecté"), fichier)


    def resultat_nettoye (self, fichier):
        """
        Retourne un objet resultat pour un fichier nettoye.

        @param: objet Fichier correspondant
        """
        return Resultat.Resultat(Resultat.NETTOYE,
            self.nom + _(u" : Contenu actif détecté et nettoyé"), fichier)


    def resultat_format_incorrect (self, fichier, erreur=None):
        """
        Retourne un objet resultat pour un fichier dont le format est incorrect
        ou non supporte. Exemple: voir Filtre_Zip.

        @param: objet Fichier correspondant
        @param erreur: message d'erreur optionnel pour donner plus de details
        """
        msg = self.nom + _(u" : Format de fichier incorrect ou non supporté, ne peut être analysé.")
        if erreur: msg += u"(%s)" % erreur
        Journal.info2(msg)
        return Resultat.Resultat(Resultat.FORMAT_INCORRECT, msg, fichier)


    def resultat_analyse_impossible (self, fichier, raison=None, erreur=None):
        """
        Retourne un objet resultat pour un fichier dont l'analyse est impossible
        a cause d'une erreur survenue lors de l'analyse.

        @param: objet Fichier correspondant
        @param raison: details optionnels sur la raison du refus
        @param erreur: message d'erreur optionnel pour donner plus de details
        """
        msg = self.nom + " : "
        if raison: msg += raison + ", "
        msg += _(u"Analyse impossible.")
        if erreur: msg += u"(%s)" % erreur
        Journal.info2(msg)
        return Resultat.Resultat(Resultat.REFUSE, msg, fichier)


    def resultat_chiffre (self, fichier, erreur=None):
        """
        Retourne un objet resultat pour un fichier dont l'analyse est impossible
        parce que ce fichier est chiffre.

        @param: objet Fichier correspondant
        @param erreur: message d'erreur optionnel pour donner plus de details
        """
        return self.resultat_analyse_impossible(fichier,
            raison=_(u"Fichier chiffré"), erreur=erreur)


    def resultat_nettoyage_impossible (self, fichier, raison=None, erreur=None):
        """
        Retourne un objet resultat pour un fichier dont le nettoyage est
        impossible a cause d'une erreur survenue lors du nettoyage.

        @param: objet Fichier correspondant
        @param raison: details optionnels sur la raison du refus
        @param erreur: message d'erreur optionnel pour donner plus de details
        """
        msg = self.nom + " : "
        if raison: msg += raison + ", "
        msg += _(u"Nettoyage impossible.")
        if erreur: msg += u"(%s)" % erreur
        Journal.info2(msg)
        return Resultat.Resultat(Resultat.REFUSE, msg, fichier)



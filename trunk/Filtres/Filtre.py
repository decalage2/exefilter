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
# 2004-2007        PL: - nombreuses �volutions
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
    classe g�n�rique pour un filtre d'un format de fichiers.

    un objet Filtre sert � reconna�tre le format d'un fichier et �
    nettoyer le code �ventuel qu'il contient. La classe Filtre est
    une classe g�n�rique, dont h�rite chaque filtre sp�cifique pour
    un format donn�.

    @cvar nom: Le nom detaill� du filtre
    @cvar nom_code: nom de code du filtre
    @cvar extensions: liste des extensions de fichiers possibles
    @cvar format_conteneur: indique si c'est un format conteneur
    @cvar extractible: indique si il s'agit d'une archive
    @cvar nettoyable: indique si il est possible de nettoyer avec ce filtre
    @cvar date: date de la derniere modification du filtre
    @cvar version: version du filtre

    @ivar nom_classe: nom de la classe correspondant � l'objet Filtre
    @ivar politique: politique contenant le filtre
    """

    # attributs de la classe, communs � tous les objets Filtre:
    nom = _(u"Filtre Generique")    # nom d�taill� du filtre
    nom_code = "GEN"        # nom de code du filtre
    extensions = []            # liste des extensions de fichiers possibles
    format_conteneur = False    # indique si c'est un format conteneur
    extractible = False
    nettoyable = False
    # date et version d�finies � partir de celles du module
    date = __date__
    version = __version__

    def __init__ (self, politique, parametres=None):
        """Constructeur d'objet Filtre.

        @param parametres: dictionnaire pour fixer les param�tres du filtre
        @type  parametres: dict

        @param politique: politique contenant ce filtre
        @type  politique: L{Politique.Politique}
        """
        # nom de la classe du filtre, utilis� pour la configuration:
        self.nom_classe = self.__class__.__name__
        # on commence par cr�er un dictionnaire de param�tres par d�faut
        self.parametres = {}
        # le seul param�tre commun � tous les filtres est "format_autorise":
        Parametres.Parametre("format_autorise", bool, nom=_(u"Format autoris�"),
            description=_(u"indique si ce format est autoris� ou non par la politique de filtrage"),
            valeur_defaut=True).ajouter(self.parametres)
        # si des param�tres ont �t� fournis au constructeur, on les met � jour
        if parametres:
            Parametres.importer (self.parametres, parametres)
        self.politique = politique


    def reconnait_nom (self, fichier):
        """analyse le nom du fichier, et retourne True s'il correspond
        au format recherch�, False sinon."""
        # Cette m�thode est g�n�rique, elle n'a pas besoin d'�tre
        # surcharg�e dans les diff�rents filtres
        for extension in extensions:
            if fichier.nom.fnmatch(extension): return True
        return False

    def reconnait_format (self, fichier):
        """analyse le format du fichier, et retourne True s'il correspond
        au format recherch�, False sinon."""
        raise NotImplementedError

    def nettoyer (self, fichier):
        """analyse et modifie le fichier pour supprimer tout code
        ex�cutable qu'il peut contenir, si cela est possible.
        Retourne un code r�sultat suivant l'action effectu�e."""
        raise NotImplementedError


    def resultat_accepte (self, fichier):
        """
        Retourne un objet resultat pour un fichier accepte.

        @param: objet Fichier correspondant
        """
        return Resultat.Resultat(Resultat.ACCEPTE,
            self.nom + _(u" : Pas de contenu actif d�tect�"), fichier)


    def resultat_nettoye (self, fichier):
        """
        Retourne un objet resultat pour un fichier nettoye.

        @param: objet Fichier correspondant
        """
        return Resultat.Resultat(Resultat.NETTOYE,
            self.nom + _(u" : Contenu actif d�tect� et nettoy�"), fichier)


    def resultat_format_incorrect (self, fichier, erreur=None):
        """
        Retourne un objet resultat pour un fichier dont le format est incorrect
        ou non supporte. Exemple: voir Filtre_Zip.

        @param: objet Fichier correspondant
        @param erreur: message d'erreur optionnel pour donner plus de details
        """
        msg = self.nom + _(u" : Format de fichier incorrect ou non support�, ne peut �tre analys�.")
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
            raison=_(u"Fichier chiffr�"), erreur=erreur)


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



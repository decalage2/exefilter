#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
"""
Resultat - ExeFilter

Module qui contient la classe L{Resultat.Resultat},
afin de décrire le résultat des filtres appliqués à un fichier.

Ce fichier fait partie du projet ExeFilter.
URL du projet: http://admisource.gouv.fr/projects/exefilter

@organization: DGA/CELAR, NATO/NC3A
@author: U{Philippe Lagadec<mailto:philippe.lagadec(a)laposte.net>}
@author: U{Arnaud Kerréneur<mailto:arnaud.kerreneur(a)dga.defense.gouv.fr>}

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
# 14/01/2005 v0.01 AK: - 1ère version
# 2005-2007     PL,AK: - nombreuses evolutions
# 12/01/2007 v1.00 PL: - version 1.00 officielle
# 2007-09-18 v1.01 PL: - ajout licence CeCILL
# 2008-03-24 v1.02 PL: - ajout de _() pour traduction gettext des chaines

# A FAIRE:
#------------------------------------------------------------------------------

#=== IMPORTS ==================================================================

import sys, copy

# modules du projet:
from commun import *
import Fichier

#=== CONSTANTES ===============================================================

# Codes des Résultats possibles pour l'analyse d'un fichier, par ordre de
# priorité croissante:
#NON_RECONNU      = 0
EXT_NON_AUTORISEE = 0
FORMAT_INCORRECT  = 10
ACCEPTE           = 20
NETTOYE           = 30
ERREUR_LECTURE    = 40
ERREUR_ANALYSE    = 50
REFUSE            = 60
VIRUS             = 70

# résultat détaillé sous forme de chaîne pour chaque code résultat:
resultat_detaille = {
    EXT_NON_AUTORISEE : _(u"Extension non autorisée"),
    FORMAT_INCORRECT :  _(u"Format incorrect ou incompatible avec l'extension"),
    ACCEPTE :           _(u"Fichier accepté"),
    NETTOYE :           _(u"Fichier nettoyé"),
    ERREUR_LECTURE :    _(u"Erreur de lecture"),
    ERREUR_ANALYSE :    _(u"Erreur lors de l'analyse"),
    REFUSE :            _(u"Fichier refusé (analyse ou nettoyage impossible)"),
    VIRUS :             _(u"Fichier infecté par un virus")
    }

# indique pour chaque code résultat s'il s'agit d'un refus du fichier:
resultat_refuse = {
    EXT_NON_AUTORISEE : True,
    FORMAT_INCORRECT :  True,
    ACCEPTE :           False,
    NETTOYE :           False,
    ERREUR_LECTURE :    True,
    ERREUR_ANALYSE :    True,
    REFUSE :            True,
    VIRUS :             True
    }

#------------------------------------------------------------------------------
# Classe Resultat
#-------------------
class Resultat:
    """classe pour afficher le résultat d'une analyse"""

    # NOTE: un objet Resultat NE DOIT PAS contenir une référence à
    # un objet Fichier, car on doit pouvoir conserver une liste
    # globale de résultats pour un transfert, sans que les objets
    # Fichier et Conteneur restent en mémoire. Dans le constructeur
    # ci-dessous, le paramètre fichier sert juste à récupérer le
    # chemin complet.

    def __init__(self, code_resultat=EXT_NON_AUTORISEE, raison="",
        fichier=None):
        """
        Constructeur de la classe Resultat.

        @param code_resultat: code (numéro) associé au résultat, cf. constantes du module L{Resultat}
        @type  code_resultat: int

        @param raison: explique le résultat de l'analyse
        @type  raison: str, unicode

        @param fichier: fichier analysé
        @type  fichier: L{Fichier.Fichier}
        """
        self.code_resultat = code_resultat
        # raison doit être une liste de chaînes unicode.
        self.raison = []
        self.ajouter_raison(raison)
        assert isinstance(fichier, Fichier.Fichier)
        self.chemin_fichier = fichier.chemin_complet

    def ajouter_raison (self, raison):
        """Pour ajouter une raison ou une liste de raisons, en convertissant
        toutes les chaînes str en unicode."""
        # si raison est une chaîne, on la transforme en liste.
        # et si c'est une chaîne vide, la liste doit être vide:
        if isinstance(raison, str) or isinstance(raison, unicode):
            if raison == "":
                raison = []
            else:
                raison = [raison]
        # ensuite on parcourt toutes les chaînes de la liste:
        # (on suppose que c'est une liste, il faudrait peut-être le vérifier)
        for chaine in raison:
            # si c'est une chaîne str, on la tranforme de latin_1 en unicode:
            if isinstance(chaine, str):
                self.raison.append( unicode(chaine, 'latin_1') )
            else:
                self.raison.append(chaine)

    def ajouter (self, resultat):
        """Fusionne avec un autre résultat (en gardant le plus
        prioritaire), et ajoute la raison à la liste déjà présente."""
        # si le code_resultat est le même, on ajoute la raison à la
        # liste des raisons déjà présentes:
        if resultat.code_resultat == self.code_resultat:
            self.ajouter_raison(resultat.raison)
        # sinon on prend le nouveau code_resultat (si > à l'ancien)
        # et on ajoute la raison à la liste déjà présente
        elif resultat.code_resultat > self.code_resultat:
            # si le code_resultat précédent est FORMAT_INCORRECT,
            # alors on supprime la raison précédente, car on vient
            # de trouver un format qui convient:
            if self.code_resultat == FORMAT_INCORRECT:
                self.raison = []
            self.code_resultat = resultat.code_resultat
            self.ajouter_raison(resultat.raison)
        # on ne met à jour chemin_fichier que s'il était vide:
        if self.chemin_fichier == "":
            self.chemin_fichier = resultat.chemin_fichier

    def ajouter_conteneur (self, liste_resultats, type_conteneur="Conteneur"):
        """Ajoute la liste des résultats des fichiers inclus dans un
        conteneur à resultats_conteneur, puis fusionne l'ensemble des
        résultats individuels pour obtenir le résultat global.

        @param liste_resultats: liste d'objets Resultat de chaque fichier du conteneur
        @param type_conteneur: chaîne nommant le type de conteneur
        @type type_conteneur: str, unicode
        """
        # on fusionne l'ensemble des résultats:
        # - accepté si tous les fichiers sont acceptés
        # - nettoyé si au moins 1 accepté et 1 refusé
        # - refusé si tous sont refusés
        nb_acceptes = 0
        nb_refuses  = 0
        nb_nettoyes = 0
        for resultat in liste_resultats:
            if resultat.est_refuse():
                nb_refuses += 1
            else:
                nb_acceptes += 1
            if resultat.code_resultat == NETTOYE:
                nb_nettoyes += 1
        if (nb_acceptes>0 and nb_refuses>0) or nb_nettoyes>0:
            self.code_resultat = NETTOYE
        elif nb_acceptes>0 and nb_refuses==0 and nb_nettoyes==0:
            self.code_resultat = ACCEPTE
        else:
            self.code_resultat = REFUSE
        # pour terminer, on ne garde qu'une raison globale, déduite du résultat obtenu:
        self.raison = [ type_conteneur + ' : ' + self.details() ]

    def details (self):
        "Retourne une chaîne détaillant le code résultat."
        return resultat_detaille[ self.code_resultat ]

    def est_refuse (self):
        "Retourne True si le résultat correspond à un refus."
        return resultat_refuse[ self.code_resultat ]



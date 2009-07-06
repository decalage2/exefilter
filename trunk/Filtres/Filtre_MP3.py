#!/usr/bin/python
# -*- coding: latin-1 -*-
"""
Filtre_MP3 - ExeFilter

Ce module contient la classe L{Filtre_MP3.Filtre_MP3},
pour filtrer les fichiers audio MP3 (MPEG Layer III).

Ce fichier fait partie du projet ExeFilter.
URL du projet: U{http://admisource.gouv.fr/projects/exefilter}

@organization: DGA/CELAR
@author: U{Philippe Lagadec<mailto:philippe.lagadec(a)laposte.net>}
@author: U{Arnaud Kerréneur<mailto:arnaud.kerreneur(a)dga.defense.gouv.fr>}
@author: U{Tanguy Vinceleux<mailto:tanguy.vinceleux(a)dga.defense.gouv.fr>}

@contact: U{Philippe Lagadec<mailto:philippe.lagadec(a)laposte.net>}

@copyright: DGA/CELAR 2004-2007
@license: CeCILL (open-source compatible GPL) - cf. code source ou fichier LICENCE.txt joint

@version: 1.01

@status: beta
"""
__docformat__ = 'epytext en'

__date__      = "2008-02-19"
__version__   = "1.01"

#------------------------------------------------------------------------------
# LICENCE pour le projet ExeFilter:

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
# 22/12/2004 v0.01 AK: - 1ère version
# 2004-2005     AK,PL: - evolutions
# 12/01/2007 v1.00 PL: - version 1.00 officielle
# 2007-09-20 v1.01 PL: - licence CeCILL

# A FAIRE:
# + vérifier s'il y a d'autres tags possibles que ID3 au début d'un fichier mp3
#------------------------------------------------------------------------------

#=== IMPORTS ==================================================================

# modules du projet:
from commun import *
import Filtre, Resultat

#=== CONSTANTES ===============================================================


#=== CLASSES ==================================================================

#------------------------------------------------------------------------------
# classe FILTRE_MP3
#-------------------
class Filtre_MP3 (Filtre.Filtre):
    """
    classe pour un filtre de fichiers son MP3.

    un objet Filtre sert à reconnaître le format d'un fichier et à
    nettoyer le code éventuel qu'il contient. La classe Filtre_Mp3
    correspond aux fichiers son MP3.


    @cvar nom: Le nom detaillé du filtre
    @cvar nom_code: nom de code du filtre
    @cvar extensions: liste des extensions de fichiers possibles
    @cvar format_conteneur: indique si c'est un format conteneur
    @cvar extractible: indique si il s'agit d'une archive
    @cvar nettoyable: indique si il est possible de nettoyer avec ce filtre
    @cvar date: date de la derniere modification du filtre
    @cvar version: version du filtre


    """

    nom = "Fichier Son MP3"
    extensions = [".mp3"]
    format_conteneur = False
    extractible = False
    nettoyable = False

    # date et version définies à partir de celles du module
    date = __date__
    version = __version__

    def reconnait_format(self, fichier):
        """analyse le format du fichier, et retourne True s'il correspond
        au format recherché, False sinon."""
        debut = fichier.lire_debut()
        if debut.startswith("\xFF\xFB") or debut.startswith("ID3"):
            return True

    def nettoyer (self, fichier):
        """analyse et modifie le fichier pour supprimer tout code
        exécutable qu'il peut contenir, si cela est possible.
        Retourne un code résultat suivant l'action effectuée."""
        # Ce format ne contient jamais de code.
        # (sauf bien sûr d'éventuels "exploits" qui sont normalement détectés
        # par l'antivirus)
        return Resultat.Resultat(Resultat.ACCEPTE,
                                 self.nom + " : ne contient pas de code", fichier)




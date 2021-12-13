#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
"""
Filtre_Texte - ExeFilter

Ce module contient la classe L{Filtre_Texte.Filtre_Texte},
pour filtrer les fichiers texte ASCII.

Ce fichier fait partie du projet ExeFilter.
URL du projet: U{http://www.decalage.info/exefilter}

@organization: DGA/CELAR
@author: U{Philippe Lagadec<mailto:philippe.lagadec(a)laposte.net>}
@author: U{Arnaud Kerréneur<mailto:arnaud.kerreneur(a)dga.defense.gouv.fr>}
@author: U{Tanguy Vinceleux<mailto:tanguy.vinceleux(a)dga.defense.gouv.fr>}

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
# 2004-2005        PL: - evolutions
# 12/01/2007 v1.00 PL: - version 1.00 officielle
# 2007-09-20 v1.01 PL: - licence CeCILL
# 2008-03-24 v1.02 PL: - ajout de _() pour traduction gettext des chaines
#                      - simplification dans nettoyer() en appelant resultat_*

# A FAIRE:
# + optimiser la lecture du fichier en lisant des troncons plus longs
# + optimiser l'analyse des caracteres en remplacant la boucle par des
#   fonctions "builtin" plus efficaces comme strip ou translate.
# + ajouter le support d'Unicode, UTF-8 et UTF-7 ? (BOM necessaire, voir
#   Filtre_HTML)
#------------------------------------------------------------------------------

#=== IMPORTS ==================================================================

# modules du projet:
from commun import *
import Filtre, Resultat

#=== CONSTANTES ===============================================================


#=== CLASSES ==================================================================

#------------------------------------------------------------------------------
# classe FILTRE_TEXTE
#-------------------
class Filtre_Texte (Filtre.Filtre):
    """
    classe pour un filtre de fichiers textes ASCII.

    un objet Filtre sert à reconnaître le format d'un fichier et à
    nettoyer le code éventuel qu'il contient. La classe Filtre_Texte
    correspond aux fichiers texte ASCII 8 bits.


    @cvar nom: Le nom detaillé du filtre
    @cvar nom_code: nom de code du filtre
    @cvar extensions: liste des extensions de fichiers possibles
    @cvar format_conteneur: indique si c'est un format conteneur
    @cvar extractible: indique si il s'agit d'une archive
    @cvar nettoyable: indique si il est possible de nettoyer avec ce filtre
    @cvar date: date de la derniere modification du filtre
    @cvar version: version du filtre

    """

    nom = _(u"Fichier Texte ASCII")
    extensions = [".txt", ".doc", "", ".ini", ".inf"]
    format_conteneur = False
    extractible = False
    nettoyable = False

    # date et version définies à partir de celles du module
    date = __date__
    version = __version__

    # table des 256 caractères ASCII autorisés
    table_ascii = 256 * [True]
    table_ascii [0:32] = [False]*32    # caractères non imprimables
    table_ascii [8] = True        # backspace (parfois utilisé ?)
    table_ascii [9] = True        # tab
    table_ascii [10] = True        # saut de ligne
    table_ascii [12] = True        # saut de page
    table_ascii [13] = True        # retour chariot
    # REMARQUE: Mailsweeper est plus restrictif, pour lui les caractères de
    # texte sont seulement 9, 10, 13, 32-126 et 160-255 !

    def reconnait_format(self, fichier):
        """analyse le format du fichier, et retourne True s'il correspond
        au format recherché, False sinon."""
        # on ouvre la copie temporaire du fichier
        f = open(fichier.copie_temp(), 'rb')
        # on lit le fichier 1 octet par un octet
        c = f.read(1)
        # tant qu'on récupère 1 octet on n'est pas à la fin du fichier
        while c != "":
            # on récupère le code ASCII de l'octet
            code_ascii = ord(c)
            # on regarde si c est un caractère texte ASCII
            if code_ascii>255 or not self.table_ascii[code_ascii]:
                # on arrête dès qu'on trouve un caractère non-ASCII
                return False
            # on lit l'octet suivant
            c=f.read(1)
        f.close()
        return True

    def nettoyer (self, fichier):
        """analyse et modifie le fichier pour supprimer tout code
        exécutable qu'il peut contenir, si cela est possible.
        Retourne un code résultat suivant l'action effectuée."""
        # ce format ne contient jamais de code
        return self.resultat_accepte(fichier)


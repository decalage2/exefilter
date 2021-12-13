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
@author: U{Arnaud Kerr�neur<mailto:arnaud.kerreneur(a)dga.defense.gouv.fr>}
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

    un objet Filtre sert � reconna�tre le format d'un fichier et �
    nettoyer le code �ventuel qu'il contient. La classe Filtre_Texte
    correspond aux fichiers texte ASCII 8 bits.


    @cvar nom: Le nom detaill� du filtre
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

    # date et version d�finies � partir de celles du module
    date = __date__
    version = __version__

    # table des 256 caract�res ASCII autoris�s
    table_ascii = 256 * [True]
    table_ascii [0:32] = [False]*32    # caract�res non imprimables
    table_ascii [8] = True        # backspace (parfois utilis� ?)
    table_ascii [9] = True        # tab
    table_ascii [10] = True        # saut de ligne
    table_ascii [12] = True        # saut de page
    table_ascii [13] = True        # retour chariot
    # REMARQUE: Mailsweeper est plus restrictif, pour lui les caract�res de
    # texte sont seulement 9, 10, 13, 32-126 et 160-255 !

    def reconnait_format(self, fichier):
        """analyse le format du fichier, et retourne True s'il correspond
        au format recherch�, False sinon."""
        # on ouvre la copie temporaire du fichier
        f = open(fichier.copie_temp(), 'rb')
        # on lit le fichier 1 octet par un octet
        c = f.read(1)
        # tant qu'on r�cup�re 1 octet on n'est pas � la fin du fichier
        while c != "":
            # on r�cup�re le code ASCII de l'octet
            code_ascii = ord(c)
            # on regarde si c est un caract�re texte ASCII
            if code_ascii>255 or not self.table_ascii[code_ascii]:
                # on arr�te d�s qu'on trouve un caract�re non-ASCII
                return False
            # on lit l'octet suivant
            c=f.read(1)
        f.close()
        return True

    def nettoyer (self, fichier):
        """analyse et modifie le fichier pour supprimer tout code
        ex�cutable qu'il peut contenir, si cela est possible.
        Retourne un code r�sultat suivant l'action effectu�e."""
        # ce format ne contient jamais de code
        return self.resultat_accepte(fichier)


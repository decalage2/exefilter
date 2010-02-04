#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
"""
ExeFilter - Fonctions, constantes et variables communes à tous les modules.

Ce fichier fait partie du projet ExeFilter.
URL du projet: U{http://www.decalage.info/exefilter}

@author: U{Philippe Lagadec<mailto:philippe.lagadec(a)laposte.net>}
@author: U{Arnaud Kerréneur<mailto:arnaud.kerreneur(a)dga.defense.gouv.fr>}
@organization: DGA/CELAR

@contact: U{Philippe Lagadec<mailto:philippe.lagadec(a)laposte.net>}

@copyright: DGA/CELAR 2004-2008
@copyright: NATO/NC3A 2008-2010 (modifications PL apres ExeFilter v1.1.0)

@license: CeCILL (open-source compatible GPL) - cf. code source ou fichier LICENCE.txt joint

@version: 1.02
@status: beta

@var MODE_DEBUG: Activation du mode debug
"""
__docformat__ = 'epytext en'

#__author__    = "Philippe Lagadec, Arnaud Kerréneur (DGA/CELAR)"
__date__      = "2010-02-04"
__version__   = "1.02"


#------------------------------------------------------------------------------
# LICENCE:

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
# 2004-10-24 v0.01 PL: - 1ère version
# 2004-2006     PL,AK: - nombreuses evolutions
# 2007-01-12 v1.00 PL: - version 1.00 officielle
# 2007-07-24       PL: - import plx pour ameliorer la portabilite
# 2007-09-10 v1.01 PL: - ajout licence CeCILL
#                      - conversion tabs en espaces
#                      - amelioration imports
#                      - ajout de display_html_file
# 2010-02-04 v1.02 PL: - disabled sous_rep_temp to avoid race conditions

#------------------------------------------------------------------------------
# A FAIRE:
# - ajouter parametres pour le comportement de chemin_relatif_incorrect()
# - chemin_relatif_incorrect(): ajout verif variable environnement Windows %xy%
# ? chemin_relatif_incorrect(): ajout verif chemin relatif MacOS avec ':' ?

#------------------------------------------------------------------------------

#=== IMPORTS ==================================================================

# import du module path.py pour simplifier la gestion des fichiers/repertoires:
try:
    from path import path
except:
    raise ImportError, "the path module is not installed: "\
                        +"see http://www.jorendorff.com/articles/python/path/"

# module plx pour ameliorer la portabilite
try:
    import plx
except:
    raise ImportError, "the plx module is not installed: "\
                        +"see http://www.decalage.info/python/plx/"

# modules du projet
import Journal

#=== CONSTANTES ===============================================================

MODE_DEBUG = False    # contrôle si les messages de debug() s'affichent

#TODO: a remplacer par attributs de la classe ExeFilter:
nb_fichiers = compteur_avancement = 0
continuer_transfert = True
transfert_commence  = False
##sous_rep_temp       = None
sous_rep_archive    = None
politique           = None


#=== FONCTIONS ================================================================

# fonctions et constantes importees du module plx:
get_username      = plx.get_username
display_html_file = plx.display_html_file
main_is_frozen    = plx.main_is_frozen
get_main_dir      = plx.get_main_dir
print_console = plx.print_console
print_oem     = plx.print_console
str_console   = plx.str_console
str_oem       = plx.str_console
str_lat1      = plx.str_lat1
unistr        = plx.unistr
Popen_timer   = plx.Popen_timer
EXIT_KILL_PTIMER = plx.EXIT_KILL_PTIMER


#------------------------------------------------------------------------------
# mode_debug
#-------------------

def mode_debug(mode=None):
    """
    Pour activer ou désactiver le mode debug, en modifiant la variable
    globale MODE_DEBUG. Retourne la valeur de cette variable.
    """
    global MODE_DEBUG
    if mode!=None:
        MODE_DEBUG = bool(mode)
    return MODE_DEBUG


#------------------------------------------------------------------------------
# DEBUG
#-------------------
def debug(texte):
    """
    pour afficher un texte de débogage si MODE_DEBUG = True

    @param texte: le texte à afficher
    @type texte: str

    """
    if MODE_DEBUG:
        Journal.debug(texte)
        #print_oem ("DEBUG: " + texte)


#------------------------------------------------------------------------------
# DEBUG_PAUSE
#-------------------
def debug_pause(texte=None):
    """
    pour faire une pause si MODE_DEBUG = True, et laisser l'utilisateur
    lire les messages à l'écran.
    """
    if MODE_DEBUG:
        if texte: debug(texte)
        #debug("Appuyer sur Entree pour continuer...")
        print "Appuyer sur Entree pour continuer, ou Ctrl+C pour stopper..."
        attente = raw_input()


#------------------------------------------------------------------------------
# EFFACER_REP_VIDE
#-------------------
def effacer_rep_vide(rep):
    """
    Pour supprimer un repertoire et ses sous-repertoires s'ils ne contiennent
    aucun fichier.
    """
    #TODO: voir si on peut simplifier ce code.
    for sous_rep in rep.dirs():
        if len(sous_rep.dirs()) == 0 and len(sous_rep.files()) == 0:
                sous_rep.rmdir()
        else: effacer_rep_vide(sous_rep)
    if len(rep.dirs()) == 0 and len(rep.files()) == 0:
            rep.rmdir()


#------------------------------------------------------------------------------
# chemin_relatif_incorrect
#--------------------------

def chemin_relatif_incorrect (chemin):
    """
    Vérifie si le chemin relatif de fichier indiqué est incorrect, par exemple
    s'il s'agit d'un chemin absolu, s'il contient "..", un signe "tilde" ou une
    lettre de lecteur MS-DOS/Windows, etc...

    /,\\   : début d'un chemin absolu sous Unix, Windows.
    C:xxx  : lettre de lecteur MS-DOS/Windows
    ..     : répertoire parent (risque de "directory traversal")
    ~      : indique répertoire utilisateur sous Unix
    %xyz%  : variable d'environnement sous Windows (désactivé actuellement)
    $xyz   : variable d'environnement sous Unix
    """
    # est-ce un chemin absolu qui commence par "/", "\", ou ":"  ?
    for c in ['/', '\\']:
        if chemin.startswith(c):
            return True
    # TODO: sur Macintosh c'est l'inverse, un chemin relatif commence par ':'.
    # Est-ce un chemin absolu pour Windows avec une lettre de lecteur ?
    if len(chemin)>=2 and chemin[0].isalpha() and chemin[1]==":":
        return True
    # est-ce qu'il contient ".." ou un tilde ?
    #for c in ['..', '~', '%', '$']:
    for c in ['..', '~', '$']:
        if c in chemin:
            return True
    #TODO: ajouter detection de variable d'environnement Windows %xyz%, mais
    #      attention aux faux positifs. Utiliser une regex intelligente ou bien
    #      verifier avec la liste des variables d'environnement du systeme ?
    #TODO: vérifier si codage unicode, ou autre ??
    # Sinon c'est OK, le chemin est valide:
    return False

#------------------------------------------------------------------------------
# TESTS
#---------------------
# tests de certaines fonctions si le module est lancé directement
# par exemple: python commun.py
if __name__ == "__main__":
    #TODO: a tester sous Linux, MacOSX, BSD
    print 'Tests du module "%s" :' % __file__
    print ''
    print_console('print_console avec accents: éèêëçà')
    print ''

    plx._test_Popen_timer()




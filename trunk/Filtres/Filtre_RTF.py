#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
"""
Filtre_RTF - ExeFilter

Ce module contient la classe L{Filtre_RTF.Filtre_RTF},
pour filtrer les documents RTF.

Ce fichier fait partie du projet ExeFilter.
URL du projet: U{http://admisource.gouv.fr/projects/exefilter}

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
# 2004-2006     PL,AK: - evolutions
# 12/01/2007 v1.00 PL: - version 1.00 officielle
# 2008-02-19 v1.01 PL: - licence CeCILL
#                      - ajout nettoyage objets OLE Package
# 2008-03-24 v1.02 PL: - ajout de _() pour traduction gettext des chaines
#                      - simplification dans nettoyer() en appelant resultat_*

#------------------------------------------------------------------------------
# A FAIRE:
#------------------------------------------------------------------------------

#=== IMPORTS ==================================================================

# modules standards Python:
import os, os.path, re, binascii, tempfile

# modules sp�cifiques:
import RechercherRemplacer

# modules du projet:
from commun import *
import Filtre, Resultat, Parametres

#=== FONCTIONS ================================================================

def _str2hexre (chaine):
    """
    convertit une chaine en regex hexadecimale, case-insensitive.
    (utile pour creer les motifs pour nettoyer les fichiers RTF)
    """
    regex = r''
    for c in chaine:
        code_lower = ord(c.lower())
        code_upper = ord(c.upper())
        regex += r'(?:%02X|%02X)' % (code_lower, code_upper)
    return regex


#=== CONSTANTES ===============================================================

# motif pour detecter et desactiver un objet OLE Package dans RTF:
re_RTF_Package = _str2hexre('Package')
remp_RTF_Package = binascii.hexlify('NoPackg')
motif_RTF = RechercherRemplacer.Motif(case_sensitive=False,
    regex=re_RTF_Package, remplacement=remp_RTF_Package)


#=== CLASSES ==================================================================

#------------------------------------------------------------------------------
# class FILTRE_RTF
#-------------------
class Filtre_RTF (Filtre.Filtre):
    """
    classe pour un filtre de fichiers RTF.

    un objet Filtre sert � reconna�tre le format d'un fichier et �
    nettoyer le code �ventuel qu'il contient. La classe Filtre_RTF
    correspond au format de document RTF de Microsoft.


    @cvar nom: Le nom detaill� du filtre
    @cvar nom_code: nom de code du filtre
    @cvar extensions: liste des extensions de fichiers possibles
    @cvar format_conteneur: indique si c'est un format conteneur
    @cvar extractible: indique si il s'agit d'une archive
    @cvar nettoyable: indique si il est possible de nettoyer avec ce filtre
    @cvar date: date de la derniere modification du filtre
    @cvar version: version du filtre

    """

    nom = _(u"Document RTF")
    extensions = [".rtf", ".doc"]
    # Note: dans certains cas Word peut sauver un fichier RTF avec l'extension .doc
    format_conteneur = False
    extractible = False
    nettoyable = True

    # date et version d�finies � partir de celles du module
    date = __date__
    version = __version__

    def __init__ (self, politique, parametres=None):
        """Constructeur d'objet Filtre_RTF.

        parametres: dictionnaire pour fixer les param�tres du filtre
        """
        # on commence par appeler le constructeur de la classe de base
        Filtre.Filtre.__init__(self, politique, parametres)
        # ensuite on ajoute les param�tres par d�faut
        Parametres.Parametre(u"supprimer_OLE_Package", bool,
            nom=u"Supprimer les objets OLE Package",
            description=u"Supprimer tout objet OLE Package, qui peut camoufler "
                        +"n'importe quel fichier executable.",
            valeur_defaut=True).ajouter(self.parametres)


    def reconnait_format(self, fichier):
        """analyse le format du fichier, et retourne True s'il correspond
        au format recherch�, False sinon."""
        debut = fichier.lire_debut()
        if debut.startswith("{\\rtf"):
            return True

    def nettoyer (self, fichier):
        """analyse et modifie le fichier pour supprimer tout code
        ex�cutable qu'il peut contenir, si cela est possible.
        Retourne un code r�sultat suivant l'action effectu�e."""
        if self.parametres["supprimer_OLE_Package"].valeur == True:
            # creation d'un nouveau fichier temporaire
            f_temp, chem_temp = tempfile.mkstemp(dir=self.politique.parametres['rep_temp'].valeur)
            Journal.info2 (u"Fichier temporaire: %s" % chem_temp)
            f_dest = os.fdopen(f_temp, 'wb')
            # on ouvre le fichier source
            f_src = open(fichier.copie_temp(), 'rb')
            Journal.info2 (u"Nettoyage RTF par remplacement de chaine")
            n = RechercherRemplacer.rechercherRemplacer(motifs=[motif_RTF],
                fich_src=f_src, fich_dest=f_dest, taille_identique=True, controle_apres=True)
            f_src.close()
            f_dest.close()
            if n:
                Journal.info2 (u"Des objets OLE Package ont ete trouves et desactives.")
                # Le fichier nettoye, on remplace la copie temporaire:
                fichier.remplacer_copie_temp(chem_temp)
                return self.resultat_nettoye(fichier)
                #return Resultat.Resultat(Resultat.NETTOYE,
                #    [self.nom + " : objets OLE Package supprim�s"], fichier)
            else:
                # pas de contenu actif
                Journal.info2 (u"Aucun contenu actif n'a ete trouve.")
                # on efface le ficher temporaire:
                os.remove(chem_temp)
                return self.resultat_accepte(fichier)
        else:
            resultat = self.resultat_accepte(fichier)
        return resultat




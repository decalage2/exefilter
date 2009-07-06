#!/usr/bin/python
# -*- coding: latin-1 -*-
"""
Filtre_ZIP - ExeFilter

Ce module contient la classe L{Filtre_Zip.Filtre_Zip},
pour filtrer les archives Zip.

Ce fichier fait partie du projet ExeFilter.
URL du projet: U{http://admisource.gouv.fr/projects/exefilter}

@organization: DGA/CELAR
@author: U{Philippe Lagadec<mailto:philippe.lagadec(a)laposte.net>}
@author: U{Arnaud Kerr�neur<mailto:arnaud.kerreneur(a)dga.defense.gouv.fr>}
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
# 2004-2005     PL,AK: - evolutions
# 12/01/2007 v1.00 PL: - version 1.00 officielle
# 2008-02-25 v1.01 PL: - licence CeCILL

#------------------------------------------------------------------------------
# A FAIRE:

#------------------------------------------------------------------------------

#=== IMPORTS ==================================================================

# modules standards Python:
import zipfile

# modules du projet:
from commun import *
import Filtre, Conteneur_Zip, Resultat

#=== CONSTANTES ===============================================================


#=== CLASSES ==================================================================

#------------------------------------------------------------------------------
# class FILTRE_ZIP
#---------------------
class Filtre_Zip (Filtre.Filtre):
    """
    classe pour un filtre de fichiers Zip.

    un objet Filtre sert � reconna�tre le format d'un fichier et �
    nettoyer le code �ventuel qu'il contient. La classe Filtre_Zip
    correspond aux archives compress�es Zip.


    @cvar nom: Le nom detaill� du filtre
    @cvar nom_code: nom de code du filtre
    @cvar extensions: liste des extensions de fichiers possibles
    @cvar format_conteneur: indique si c'est un format conteneur
    @cvar extractible: indique si il s'agit d'une archive
    @cvar nettoyable: indique si il est possible de nettoyer avec ce filtre
    @cvar date: date de la derniere modification du filtre
    @cvar version: version du filtre
    """

    nom = "Archive Zip"
    extensions = [".zip"]
    format_conteneur = True
    extractible = True
    nettoyable = False

    # date et version d�finies � partir de celles du module
    date = __date__
    version = __version__

    def reconnait_format(self, fichier):
        """Analyse le format du fichier, et retourne True s'il correspond
        au format recherch�, False sinon.

        @param fichier: fichier � analyser
        @type  fichier: objet L{Fichier.Fichier}
        """
        Journal.debug('Verif format Zip pour "%s"' % fichier.nom)
        return zipfile.is_zipfile(str_lat1(fichier.copie_temp()))

    def nettoyer (self, fichier):
        """Analyse et modifie le fichier pour supprimer tout code
        ex�cutable qu'il peut contenir, si cela est possible.
        Retourne un code r�sultat suivant l'action effectu�e.

        @param fichier: fichier � nettoyer
        @type  fichier: objet L{Fichier<Fichier.Fichier>}

        @return: r�sultat du nettoyage
        @rtype : objet L{Resultat<Resultat.Resultat>}
        """
        # ce format ne contient jamais de code en soi, mais comme c'est
        # un conteneur, il faut nettoyer tous les fichiers qu'il contient:
        try:
            conteneur_zip = Conteneur_Zip.Conteneur_Zip (fichier.copie_temp(),
                "", fichier)
        except zipfile.BadZipfile:
            # si on obtient cette exception, c'est que le module zipfile ne
            # supporte pas le format de ce fichier zip.
            erreur = str(sys.exc_info()[1])
            msg = self.nom + u" : Le format de ce fichier est incorrect ou non " \
                +u"support�, il ne peut �tre analys�. (%s)" % erreur
            return Resultat.Resultat(Resultat.ERREUR_ANALYSE, msg , fichier)
            Journal.info2(msg)
        liste_resultats = conteneur_zip.nettoyer(self.politique)
        # on cr�e un objet Resultat par d�faut pour le zip
        resultat_zip = Resultat.Resultat(fichier = fichier)
        # puis on fusionne tous les r�sultats des fichiers inclus
        resultat_zip.ajouter_conteneur(liste_resultats, self.nom)
        return resultat_zip

    def conteneur (self, fichier_conteneur, destination, fichier):
        return Conteneur_Zip.Conteneur_Zip (fichier_conteneur,
            destination, fichier)



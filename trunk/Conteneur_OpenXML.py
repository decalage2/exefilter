#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
"""
Conteneur_OpenXML - ExeFilter

to scan and clean Open XML files (Microsoft Office 2007 and later).

This file is part of the ExeFilter project.
Project URL: U{http://www.decalage.info/exefilter}

@author: U{Philippe Lagadec<mailto:philippe.lagadec(a)laposte.net>}

@contact: U{Philippe Lagadec<mailto:philippe.lagadec(a)laposte.net>}

@copyright: Philippe Lagadec 2011

@license: CeCILL (open-source compatible GPL)
          cf. code source ou fichier LICENCE.txt joint

@version: 0.01

@status: alpha
"""
#==============================================================================
__docformat__ = 'epytext en'

__date__    = "2011-02-21"
__version__ = "0.01"

#------------------------------------------------------------------------------
# LICENCE pour le projet ExeFilter:

# Copyright DGA/CELAR 2004-2008
# Copyright NATO/NC3A 2008-2010 (PL changes after ExeFilter v1.1.0)
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
# CHANGELOG:
# 2011-02-21 v0.01 PL: - 1st version

#------------------------------------------------------------------------------
# TODO:

#=== IMPORTS ==================================================================

# modules standards Python:

# modules du projet:
from commun import *
import Conteneur_Zip


#=== CONSTANTES ===============================================================



#=== CLASSES ==================================================================

class Conteneur_OpenXML (Conteneur_Zip.Conteneur_Zip):
    """
    class to scan and clean Open XML documents (Microsoft Office 2007 and later)
    which are in fact Zip archives.

    A Conteneur object corresponds to a directory or a file which contains a set
    of files, for example a Zip archive.
    Conteneur_OpenXML is based on Conteneur_Zip.
    """

    def __init__(self, nom_archive, nom_destination, fichier, politique):
        """
        Constructeur d'objet Conteneur_OpenXML.

        @warning: Si le format de zip n'est pas supporté, peut lever une exception
        zipfile.BadZipFile ou zipfile.error.

        @param nom_archive: nom de fichier/répertoire du fichier zip source.
                            (chemin relatif par rapport au conteneur)
        @type  nom_archive: str, unicode

        @param nom_destination: nom de fichier/répertoire du conteneur nettoyé.
        @type  nom_destination: str, unicode

        @param fichier: objet Fichier du conteneur, ou bien None si c'est le
                        1er répertoire.
        @type  fichier: objet L{Fichier.Fichier} ou None
        """
        # on appelle d'abord le constructeur de base
        Conteneur_Zip.Conteneur_Zip.__init__(self, nom_archive, nom_destination,
            fichier, politique)
        self.type = _(u"Open XML document")



##    def reconstruire (self):
##        """
##        reconstruit le Conteneur à partir des fichiers nettoyés.
##        """
##        # on commence par établir la liste des fichiers acceptés:
##        liste_fichiers_ok = []
##        for fichier in self.liste_fichiers:
##            if not fichier.resultat_fichier.est_refuse():
##                liste_fichiers_ok.append(fichier)
##        # on ne reconstruit le fichier Zip que s'il y a des fichiers acceptés
##        # (sinon un ZipFile vide provoque une exception bizarre...)
##        if len(liste_fichiers_ok) != 0:
##            Journal.info2(_(u"Recompression du fichier Zip après nettoyage des fichiers..."))
##            # on reconstruit d'abord l'archive Zip dans un fichier temporaire,
##            # puisqu'il faudra remplacer le fichier déjà obtenu par copie_temp.
##            # Obtention d'un nom de fichier zip temporaire:
##            #f_zip_temp, chem_zip_temp = tempfile.mkstemp(suffix=".zip", dir=Conteneur.RACINE_TEMP)
##            #f_zip_temp, chem_zip_temp = tempfile.mkstemp(suffix=".zip", dir=commun.politique.parametres['rep_temp'].valeur)
##            f_zip_temp, chem_zip_temp = newTempFile(suffix=".zip")
##            Journal.debug (u"Fichier Zip temporaire: %s" % chem_zip_temp)
##            # Ouverture en écriture du fichier Zip temporaire:
##            # le mode ZIP_DEFLATED est nécessaire sinon les fichiers ne
##            # seront pas recompressés, juste stockés (ZIP_STORED par défaut)
##            zip_temp = zipfile_PL.ZipFile_PL (chem_zip_temp, 'w', zipfile.ZIP_DEFLATED)
##            # On commence par réinjecter les répertoires qui étaient présents au départ:
##            for zipinfo_rep in self.repertoires:
##                zip_temp.writestr(zipinfo_rep, "")
##            for fichier in self.liste_fichiers:
##                if not fichier.resultat_fichier.est_refuse():
##                    Journal.debug (u'Compression: "%s"...' % fichier.copie_temp())
##                    # on ajoute le fichier dans l'archive :
##                    # le permier argument permet d'ouvrir le fichier à compresser corretement
##                    # le deuxième argument permet l'affichage du fichier dans l'archive avec le
##                    # bon encodage de caractères
##                    # reconstruction de l'archive zip sans le répertoire temp
##                    f = file(fichier.copie_temp(), 'rb')
##                    zip_temp.writestr(fichier.zipinfo, f.read())
##                    f.close()
##                    #zip_temp.write(str_lat1(fichier._copie_temp) , str_oem(fichier.chemin) )
##            # On doit fermer le ZipFile mais aussi le fichier temporaire
##            zip_temp.close()
##            f_zip_temp.close()
##            # on modifie la date du nouveau zip pour correspondre à
##            # celle d'origine:
##            date_zip = os.path.getmtime(self.fichier._copie_temp)
##            os.utime(chem_zip_temp, (date_zip, date_zip))
##            # on remplace la copie temporaire du fichier zip d'origine par
##            # la version nettoyée:
##            # NOTE: sous Windows on est obligé d'effacer d'abord le fichier
##            #       d'origine, alors que sous Unix il serait simplement écrasé
##            self.fichier._copie_temp.remove()
##            #path_zip_temp = path(chem_zip_temp)
##            #path_zip_temp.rename(str_lat1(self.fichier._copie_temp))
##            os.rename(chem_zip_temp, self.fichier._copie_temp)
##        else:
##            Journal.info2(_(u"Aucun fichier accepté dans le Zip: suppression."))
##            self.fichier._copie_temp.remove()
##        # pour finir on détruit le répertoire temporaire:
##        if self.rep_temp_complet.exists():
##            self.rep_temp_complet.rmtree()




# coded while listening to "TODO"
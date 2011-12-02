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

        @warning: Si le format de zip n'est pas support�, peut lever une exception
        zipfile.BadZipFile ou zipfile.error.

        @param nom_archive: nom de fichier/r�pertoire du fichier zip source.
                            (chemin relatif par rapport au conteneur)
        @type  nom_archive: str, unicode

        @param nom_destination: nom de fichier/r�pertoire du conteneur nettoy�.
        @type  nom_destination: str, unicode

        @param fichier: objet Fichier du conteneur, ou bien None si c'est le
                        1er r�pertoire.
        @type  fichier: objet L{Fichier.Fichier} ou None
        """
        # on appelle d'abord le constructeur de base
        Conteneur_Zip.Conteneur_Zip.__init__(self, nom_archive, nom_destination,
            fichier, politique)
        self.type = _(u"Open XML document")



##    def reconstruire (self):
##        """
##        reconstruit le Conteneur � partir des fichiers nettoy�s.
##        """
##        # on commence par �tablir la liste des fichiers accept�s:
##        liste_fichiers_ok = []
##        for fichier in self.liste_fichiers:
##            if not fichier.resultat_fichier.est_refuse():
##                liste_fichiers_ok.append(fichier)
##        # on ne reconstruit le fichier Zip que s'il y a des fichiers accept�s
##        # (sinon un ZipFile vide provoque une exception bizarre...)
##        if len(liste_fichiers_ok) != 0:
##            Journal.info2(_(u"Recompression du fichier Zip apr�s nettoyage des fichiers..."))
##            # on reconstruit d'abord l'archive Zip dans un fichier temporaire,
##            # puisqu'il faudra remplacer le fichier d�j� obtenu par copie_temp.
##            # Obtention d'un nom de fichier zip temporaire:
##            #f_zip_temp, chem_zip_temp = tempfile.mkstemp(suffix=".zip", dir=Conteneur.RACINE_TEMP)
##            #f_zip_temp, chem_zip_temp = tempfile.mkstemp(suffix=".zip", dir=commun.politique.parametres['rep_temp'].valeur)
##            f_zip_temp, chem_zip_temp = newTempFile(suffix=".zip")
##            Journal.debug (u"Fichier Zip temporaire: %s" % chem_zip_temp)
##            # Ouverture en �criture du fichier Zip temporaire:
##            # le mode ZIP_DEFLATED est n�cessaire sinon les fichiers ne
##            # seront pas recompress�s, juste stock�s (ZIP_STORED par d�faut)
##            zip_temp = zipfile_PL.ZipFile_PL (chem_zip_temp, 'w', zipfile.ZIP_DEFLATED)
##            # On commence par r�injecter les r�pertoires qui �taient pr�sents au d�part:
##            for zipinfo_rep in self.repertoires:
##                zip_temp.writestr(zipinfo_rep, "")
##            for fichier in self.liste_fichiers:
##                if not fichier.resultat_fichier.est_refuse():
##                    Journal.debug (u'Compression: "%s"...' % fichier.copie_temp())
##                    # on ajoute le fichier dans l'archive :
##                    # le permier argument permet d'ouvrir le fichier � compresser corretement
##                    # le deuxi�me argument permet l'affichage du fichier dans l'archive avec le
##                    # bon encodage de caract�res
##                    # reconstruction de l'archive zip sans le r�pertoire temp
##                    f = file(fichier.copie_temp(), 'rb')
##                    zip_temp.writestr(fichier.zipinfo, f.read())
##                    f.close()
##                    #zip_temp.write(str_lat1(fichier._copie_temp) , str_oem(fichier.chemin) )
##            # On doit fermer le ZipFile mais aussi le fichier temporaire
##            zip_temp.close()
##            f_zip_temp.close()
##            # on modifie la date du nouveau zip pour correspondre �
##            # celle d'origine:
##            date_zip = os.path.getmtime(self.fichier._copie_temp)
##            os.utime(chem_zip_temp, (date_zip, date_zip))
##            # on remplace la copie temporaire du fichier zip d'origine par
##            # la version nettoy�e:
##            # NOTE: sous Windows on est oblig� d'effacer d'abord le fichier
##            #       d'origine, alors que sous Unix il serait simplement �cras�
##            self.fichier._copie_temp.remove()
##            #path_zip_temp = path(chem_zip_temp)
##            #path_zip_temp.rename(str_lat1(self.fichier._copie_temp))
##            os.rename(chem_zip_temp, self.fichier._copie_temp)
##        else:
##            Journal.info2(_(u"Aucun fichier accept� dans le Zip: suppression."))
##            self.fichier._copie_temp.remove()
##        # pour finir on d�truit le r�pertoire temporaire:
##        if self.rep_temp_complet.exists():
##            self.rep_temp_complet.rmtree()




# coded while listening to "TODO"
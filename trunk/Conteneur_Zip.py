#!/usr/bin/python
# -*- coding: latin-1 -*-
"""
Conteneur_Zip - ExeFilter

Module qui contient la classe L{Conteneur_Zip.Conteneur_Zip},
pour traiter les fichiers d'une archive Zip.

Ce fichier fait partie du projet ExeFilter.
URL du projet: U{http://admisource.gouv.fr/projects/exefilter}

@organization: DGA/CELAR
@author: U{Philippe Lagadec<mailto:philippe.lagadec(a)laposte.net>}
@author: U{Arnaud Kerr�neur<mailto:arnaud.kerreneur(a)dga.defense.gouv.fr>}

@contact: U{Philippe Lagadec<mailto:philippe.lagadec(a)laposte.net>}

@copyright: DGA/CELAR 2004-2007
@license: CeCILL (open-source compatible GPL) - cf. code source ou fichier LICENCE.txt joint

@version: 1.01

@status: beta
"""
#==============================================================================
__docformat__ = 'epytext en'

#__author__  = "Philippe Lagadec, Arnaud Kerr�neur (DGA/CELAR)"
__date__    = "2007-11-02"
__version__ = "1.01"

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
# 2004-2007     PL,AK: - nombreuses �volutions
#                      - contributions de Y. Bidan et C. Catherin
# 12/01/2007 v1.00 PL: - version 1.00 officielle
# 2007-11-03 v1.01 PL: - ajout licence CeCILL

#------------------------------------------------------------------------------
# A FAIRE:
#------------------------------------------------------------------------------

#=== IMPORTS ==================================================================

# modules standards Python:
import zipfile, tempfile, os, os.path , stat

# module path.py pour manipuler plus facilement les fichiers/r�pertoires
from path import path

# modules du projet:
import commun
from commun import *
import Conteneur, Fichier, Resultat
import zipfile_PL


#=== CONSTANTES ===============================================================

# Attributs MSDOS/Windows pour les fichiers:
# constantes extraites de win32con.py, dans les extensions Python Win32:
ATTRIB_READONLY  = 1
ATTRIB_HIDDEN    = 2
ATTRIB_SYSTEM    = 4
ATTRIB_LABEL     = 8    # ajout�, n'�tait pas dans win32con
ATTRIB_DIRECTORY = 16
ATTRIB_ARCHIVE   = 32
ATTRIB_64        = 64   # ajout�, n'�tait pas dans win32con. Attribut inutilis� ?
ATTRIB_NORMAL    = 128  # � quoi sert cet attribut ??

# permissions Unix, d�cal�es de 16 bits dans les fichiers zip: cf. aide du
# module stat, et code source de zipfile.py...
ATTRIB_DIR_UNIX = stat.S_IFDIR << 16L


#=== CLASSES ==================================================================

#------------------------------------------------------------------------------
# class CONTENEUR_ZIP
#---------------------
class Conteneur_Zip (Conteneur.Conteneur):
    """Classe pour analyser une archive Zip contenant des fichiers.

    un objet Conteneur correspond � un r�pertoire ou � un fichier
    qui contient un ensemble de fichiers, par exemple une archive Zip.
    La classe Conteneur_Zip correspond � une archive Zip.
    """
    
    def __init__(self, nom_archive, nom_destination, fichier):
        """
        Constructeur d'objet Conteneur_Zip.
        
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
        Conteneur.Conteneur.__init__(self, nom_archive, nom_destination, "", fichier)
        self.type = "Archive Zip"
        # on ouvre le fichier Zip:
        Journal.info2(u"Ouverture du fichier ZIP gr�ce au module zipfile.")
        self.politique = politique
        self.zip = zipfile_PL.ZipFile_PL(nom_archive)

    
    def creer_rep_temp(self):
        """Pour initialiser le r�pertoire temporaire n�cessaire � l'analyse du
        conteneur."""
        # rep_temp va diff�rer si le conteneur est une archive Zip ou si c'est un r�p
        # r�pertoire temporaire: un nouveau sous-r�pertoire dans RACINE_TEMP
        # mkdtemp permet d'avoir un r�pertoire s�curis�, accessible
        # seulement � l'utilisateur
        #self.rep_temp = path( tempfile.mkdtemp(dir=Conteneur.RACINE_TEMP) )
        self.rep_temp_complet = path( tempfile.mkdtemp(dir=commun.politique.parametres['rep_temp'].valeur) )


    def lister_fichiers (self):
        """Retourne la liste des fichiers de l'archive Zip, qui n'est
        lue qu'une fois au 1er appel.

        @return: liste des fichiers contenus
        @rtype : liste de L{Fichier.Fichier}
        """
        # on ne dresse la liste des fichiers que la premi�re fois:
        if len(self.liste_fichiers) == 0:
            # liste des r�pertoires contenus (objets ZipInfo)
            self.repertoires = []
            Journal.info2(u"Lecture de la liste des fichiers du fichier ZIP:")
            for zipinfo in self.zip.infolist():
                # on convertit le nom de fichier en unicode en utilisant le
                # codec "cp850", car dans un zip les noms de fichiers sont
                # au format OEM (MS-DOS): sinon erreur en cas d'accents
                nom_fichier = unicode(zipinfo.filename, 'cp850')
                Journal.info2(u"- fichier: %s" % nom_fichier)
                Journal.info2(
                    "  zipinfo: flag_bits = %d, internal_attr = %d, external_attr = %d"
                    % (zipinfo.flag_bits, zipinfo.internal_attr, zipinfo.external_attr))
                Journal.info2(
                    "  compress_type = %d, create_system = %d, create_version  = %d"
                    % (zipinfo.compress_type, zipinfo.create_system, zipinfo.create_version))
                Journal.info2(
                    "  extract_version = %d, volume = %d"
                    % (zipinfo.extract_version, zipinfo.volume))
                Journal.info2(
                    "  compress_size = %d, file_size = %d"
                    % (zipinfo.compress_size, zipinfo.file_size))
                # les r�pertoires et labels doivent �tre trait�s � part, ils ne 
                # sont pas dans la liste des fichiers
                if zipinfo.external_attr & (ATTRIB_DIRECTORY | ATTRIB_DIR_UNIX) :
                    # Si c'est un r�pertoire on ajoute le zipinfo � la liste:
                    self.repertoires.append(zipinfo)
                    Journal.info2(u"  R�pertoire.")
                elif zipinfo.external_attr & ATTRIB_LABEL :
                    # Si c'est un label on l'ignore:
                    Journal.info2(u"  Cette entr�e est un label de volume MS-DOS, on l'ignore.")
                else:
                    # C'est un fichier, on l'ajoute � la liste.
                    # si le nom est vide ou "-", ce n'est pas un fichier mais
                    # un texte issu de l'entr�e standard (cf. appnote.iz)
                    # il faut aussi v�rifier que ce n'est pas un chemin absolu, 
                    # et convertir tous les antislashs en slashs
                    f = Fichier.Fichier(nom_fichier, conteneur=self)
                    # on ajoute un nouvel attribut zipinfo au fichier
                    f.zipinfo = zipinfo
                    self.liste_fichiers.append(f)
        return self.liste_fichiers

                
    def copie_temp (self, fichier):
        """copie le fichier vers un r�pertoire temporaire, et retourne
        le chemin de la copie. Cette fonction est normalement appel�e
        par Fichier.copie_temp() uniquement au 1er appel."""
        # on s'assure d'abord que le r�pertoire relatif du fichier existe
        # (on suppose que fichier.chemin contient un chemin relatif...)
        chem_temp = self.rep_temp_complet / fichier.chemin.parent
        if not chem_temp.exists():
            chem_temp.makedirs()
        fichier_temp = self.rep_temp_complet / fichier.chemin
        Journal.info2(u'D�compression: "%s" -> "%s"...' % (fichier.chemin, fichier_temp))
        
        # droit en �criture sur le r�pertoire temporaire pour suppression
##      os.chmod( path(fichier_temp).abspath().normpath(), stat.S_IRWXU )

        f = file(fichier_temp, 'wb')
        # ici on encode le nom de fichier en OEM (cp850) car c'est le format interne zip
        f.write(self.zip.read(fichier.chemin.encode('cp850')))
        f.close()
        return fichier_temp

    
    def fermer (self):
        """
        Ferme le conteneur une fois que tous les fichiers inclus ont
        �t� analys�s.
        """
        self.zip.close()

    
    def reconstruire (self):
        """
        reconstruit le Conteneur � partir des fichiers nettoy�s.
        """
        # on commence par �tablir la liste des fichiers accept�s:
        liste_fichiers_ok = []
        for fichier in self.liste_fichiers:
            if not fichier.resultat_fichier.est_refuse():
                liste_fichiers_ok.append(fichier)
        # on ne reconstruit le fichier Zip que s'il y a des fichiers accept�s
        # (sinon un ZipFile vide provoque une exception bizarre...)
        if len(liste_fichiers_ok) != 0:
            Journal.info2(u"Recompression du fichier Zip apr�s nettoyage des fichiers...")
            # on reconstruit d'abord l'archive Zip dans un fichier temporaire,
            # puisqu'il faudra remplacer le fichier d�j� obtenu par copie_temp.
            # Obtention d'un nom de fichier zip temporaire:
            #f_zip_temp, chem_zip_temp = tempfile.mkstemp(suffix=".zip", dir=Conteneur.RACINE_TEMP)
            f_zip_temp, chem_zip_temp = tempfile.mkstemp(suffix=".zip", dir=commun.politique.parametres['rep_temp'].valeur)
            Journal.debug (u"Fichier Zip temporaire: %s" % chem_zip_temp)
            # Ouverture en �criture du fichier Zip temporaire:
            # le mode ZIP_DEFLATED est n�cessaire sinon les fichiers ne
            # seront pas recompress�s, juste stock�s (ZIP_STORED par d�faut)
            zip_temp = zipfile_PL.ZipFile_PL (chem_zip_temp, 'w', zipfile.ZIP_DEFLATED)
            # On commence par r�injecter les r�pertoires qui �taient pr�sents au d�part:
            for zipinfo_rep in self.repertoires:
                zip_temp.writestr(zipinfo_rep, "")
            for fichier in self.liste_fichiers:
                if not fichier.resultat_fichier.est_refuse():
                    Journal.debug (u'Compression: "%s"...' % fichier.copie_temp())
                    # on ajoute le fichier dans l'archive :
                    # le permier argument permet d'ouvrir le fichier � compresser corretement
                    # le deuxi�me argument permet l'affichage du fichier dans l'archive avec le 
                    # bon encodage de caract�res
                    # reconstruction de l'archive zip sans le r�pertoire temp
                    f = file(fichier.copie_temp(), 'rb')
                    zip_temp.writestr(fichier.zipinfo, f.read())
                    f.close()
                    #zip_temp.write(str_lat1(fichier._copie_temp) , str_oem(fichier.chemin) )
            # On doit fermer le ZipFile mais aussi le fichier temporaire
            zip_temp.close()
            os.close(f_zip_temp)
            # on modifie la date du nouveau zip pour correspondre �
            # celle d'origine:
            date_zip = os.path.getmtime(self.fichier._copie_temp)
            os.utime(chem_zip_temp, (date_zip, date_zip))
            # on remplace la copie temporaire du fichier zip d'origine par
            # la version nettoy�e:
            # NOTE: sous Windows on est oblig� d'effacer d'abord le fichier
            #       d'origine, alors que sous Unix il serait simplement �cras�
            self.fichier._copie_temp.remove()
            #path_zip_temp = path(chem_zip_temp)
            #path_zip_temp.rename(str_lat1(self.fichier._copie_temp))
            os.rename(chem_zip_temp, self.fichier._copie_temp)
        else:
            Journal.info2(u"Aucun fichier accept� dans le Zip: suppression.")
            self.fichier._copie_temp.remove()
        # pour finir on d�truit le r�pertoire temporaire:
        if self.rep_temp_complet.exists():
            self.rep_temp_complet.rmtree()
    

    def est_chiffre(self, fichier):
        """Retourne True si le fichier indiqu� est chiffr�, et qu'il ne peut
        pas �tre extrait du fichier ZIP.
        
        @param fichier: fichier � tester.
        @type  fichier: objet L{Fichier<Fichier.Fichier>}
        """
        # le bit 0 du champ "general purpose bit flag" est normalement
        # positionn� � 1 si le fichier est chiffr�, quel que soit l'algo de
        # chiffrement. (cf. appnote.iz ou appnote.txt)
        if fichier.zipinfo.flag_bits & 1:
            return True
        else:
            return False

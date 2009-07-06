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
@author: U{Arnaud Kerréneur<mailto:arnaud.kerreneur(a)dga.defense.gouv.fr>}

@contact: U{Philippe Lagadec<mailto:philippe.lagadec(a)laposte.net>}

@copyright: DGA/CELAR 2004-2007
@license: CeCILL (open-source compatible GPL) - cf. code source ou fichier LICENCE.txt joint

@version: 1.01

@status: beta
"""
#==============================================================================
__docformat__ = 'epytext en'

#__author__  = "Philippe Lagadec, Arnaud Kerréneur (DGA/CELAR)"
__date__    = "2007-11-02"
__version__ = "1.01"

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
# 24/10/2004 v0.01 PL: - 1ère version
# 2004-2007     PL,AK: - nombreuses évolutions
#                      - contributions de Y. Bidan et C. Catherin
# 12/01/2007 v1.00 PL: - version 1.00 officielle
# 2007-11-03 v1.01 PL: - ajout licence CeCILL

#------------------------------------------------------------------------------
# A FAIRE:
#------------------------------------------------------------------------------

#=== IMPORTS ==================================================================

# modules standards Python:
import zipfile, tempfile, os, os.path , stat

# module path.py pour manipuler plus facilement les fichiers/répertoires
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
ATTRIB_LABEL     = 8    # ajouté, n'était pas dans win32con
ATTRIB_DIRECTORY = 16
ATTRIB_ARCHIVE   = 32
ATTRIB_64        = 64   # ajouté, n'était pas dans win32con. Attribut inutilisé ?
ATTRIB_NORMAL    = 128  # à quoi sert cet attribut ??

# permissions Unix, décalées de 16 bits dans les fichiers zip: cf. aide du
# module stat, et code source de zipfile.py...
ATTRIB_DIR_UNIX = stat.S_IFDIR << 16L


#=== CLASSES ==================================================================

#------------------------------------------------------------------------------
# class CONTENEUR_ZIP
#---------------------
class Conteneur_Zip (Conteneur.Conteneur):
    """Classe pour analyser une archive Zip contenant des fichiers.

    un objet Conteneur correspond à un répertoire ou à un fichier
    qui contient un ensemble de fichiers, par exemple une archive Zip.
    La classe Conteneur_Zip correspond à une archive Zip.
    """
    
    def __init__(self, nom_archive, nom_destination, fichier):
        """
        Constructeur d'objet Conteneur_Zip.
        
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
        Conteneur.Conteneur.__init__(self, nom_archive, nom_destination, "", fichier)
        self.type = "Archive Zip"
        # on ouvre le fichier Zip:
        Journal.info2(u"Ouverture du fichier ZIP grâce au module zipfile.")
        self.politique = politique
        self.zip = zipfile_PL.ZipFile_PL(nom_archive)

    
    def creer_rep_temp(self):
        """Pour initialiser le répertoire temporaire nécessaire à l'analyse du
        conteneur."""
        # rep_temp va différer si le conteneur est une archive Zip ou si c'est un rép
        # répertoire temporaire: un nouveau sous-répertoire dans RACINE_TEMP
        # mkdtemp permet d'avoir un répertoire sécurisé, accessible
        # seulement à l'utilisateur
        #self.rep_temp = path( tempfile.mkdtemp(dir=Conteneur.RACINE_TEMP) )
        self.rep_temp_complet = path( tempfile.mkdtemp(dir=commun.politique.parametres['rep_temp'].valeur) )


    def lister_fichiers (self):
        """Retourne la liste des fichiers de l'archive Zip, qui n'est
        lue qu'une fois au 1er appel.

        @return: liste des fichiers contenus
        @rtype : liste de L{Fichier.Fichier}
        """
        # on ne dresse la liste des fichiers que la première fois:
        if len(self.liste_fichiers) == 0:
            # liste des répertoires contenus (objets ZipInfo)
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
                # les répertoires et labels doivent être traités à part, ils ne 
                # sont pas dans la liste des fichiers
                if zipinfo.external_attr & (ATTRIB_DIRECTORY | ATTRIB_DIR_UNIX) :
                    # Si c'est un répertoire on ajoute le zipinfo à la liste:
                    self.repertoires.append(zipinfo)
                    Journal.info2(u"  Répertoire.")
                elif zipinfo.external_attr & ATTRIB_LABEL :
                    # Si c'est un label on l'ignore:
                    Journal.info2(u"  Cette entrée est un label de volume MS-DOS, on l'ignore.")
                else:
                    # C'est un fichier, on l'ajoute à la liste.
                    # si le nom est vide ou "-", ce n'est pas un fichier mais
                    # un texte issu de l'entrée standard (cf. appnote.iz)
                    # il faut aussi vérifier que ce n'est pas un chemin absolu, 
                    # et convertir tous les antislashs en slashs
                    f = Fichier.Fichier(nom_fichier, conteneur=self)
                    # on ajoute un nouvel attribut zipinfo au fichier
                    f.zipinfo = zipinfo
                    self.liste_fichiers.append(f)
        return self.liste_fichiers

                
    def copie_temp (self, fichier):
        """copie le fichier vers un répertoire temporaire, et retourne
        le chemin de la copie. Cette fonction est normalement appelée
        par Fichier.copie_temp() uniquement au 1er appel."""
        # on s'assure d'abord que le répertoire relatif du fichier existe
        # (on suppose que fichier.chemin contient un chemin relatif...)
        chem_temp = self.rep_temp_complet / fichier.chemin.parent
        if not chem_temp.exists():
            chem_temp.makedirs()
        fichier_temp = self.rep_temp_complet / fichier.chemin
        Journal.info2(u'Décompression: "%s" -> "%s"...' % (fichier.chemin, fichier_temp))
        
        # droit en écriture sur le répertoire temporaire pour suppression
##      os.chmod( path(fichier_temp).abspath().normpath(), stat.S_IRWXU )

        f = file(fichier_temp, 'wb')
        # ici on encode le nom de fichier en OEM (cp850) car c'est le format interne zip
        f.write(self.zip.read(fichier.chemin.encode('cp850')))
        f.close()
        return fichier_temp

    
    def fermer (self):
        """
        Ferme le conteneur une fois que tous les fichiers inclus ont
        été analysés.
        """
        self.zip.close()

    
    def reconstruire (self):
        """
        reconstruit le Conteneur à partir des fichiers nettoyés.
        """
        # on commence par établir la liste des fichiers acceptés:
        liste_fichiers_ok = []
        for fichier in self.liste_fichiers:
            if not fichier.resultat_fichier.est_refuse():
                liste_fichiers_ok.append(fichier)
        # on ne reconstruit le fichier Zip que s'il y a des fichiers acceptés
        # (sinon un ZipFile vide provoque une exception bizarre...)
        if len(liste_fichiers_ok) != 0:
            Journal.info2(u"Recompression du fichier Zip après nettoyage des fichiers...")
            # on reconstruit d'abord l'archive Zip dans un fichier temporaire,
            # puisqu'il faudra remplacer le fichier déjà obtenu par copie_temp.
            # Obtention d'un nom de fichier zip temporaire:
            #f_zip_temp, chem_zip_temp = tempfile.mkstemp(suffix=".zip", dir=Conteneur.RACINE_TEMP)
            f_zip_temp, chem_zip_temp = tempfile.mkstemp(suffix=".zip", dir=commun.politique.parametres['rep_temp'].valeur)
            Journal.debug (u"Fichier Zip temporaire: %s" % chem_zip_temp)
            # Ouverture en écriture du fichier Zip temporaire:
            # le mode ZIP_DEFLATED est nécessaire sinon les fichiers ne
            # seront pas recompressés, juste stockés (ZIP_STORED par défaut)
            zip_temp = zipfile_PL.ZipFile_PL (chem_zip_temp, 'w', zipfile.ZIP_DEFLATED)
            # On commence par réinjecter les répertoires qui étaient présents au départ:
            for zipinfo_rep in self.repertoires:
                zip_temp.writestr(zipinfo_rep, "")
            for fichier in self.liste_fichiers:
                if not fichier.resultat_fichier.est_refuse():
                    Journal.debug (u'Compression: "%s"...' % fichier.copie_temp())
                    # on ajoute le fichier dans l'archive :
                    # le permier argument permet d'ouvrir le fichier à compresser corretement
                    # le deuxième argument permet l'affichage du fichier dans l'archive avec le 
                    # bon encodage de caractères
                    # reconstruction de l'archive zip sans le répertoire temp
                    f = file(fichier.copie_temp(), 'rb')
                    zip_temp.writestr(fichier.zipinfo, f.read())
                    f.close()
                    #zip_temp.write(str_lat1(fichier._copie_temp) , str_oem(fichier.chemin) )
            # On doit fermer le ZipFile mais aussi le fichier temporaire
            zip_temp.close()
            os.close(f_zip_temp)
            # on modifie la date du nouveau zip pour correspondre à
            # celle d'origine:
            date_zip = os.path.getmtime(self.fichier._copie_temp)
            os.utime(chem_zip_temp, (date_zip, date_zip))
            # on remplace la copie temporaire du fichier zip d'origine par
            # la version nettoyée:
            # NOTE: sous Windows on est obligé d'effacer d'abord le fichier
            #       d'origine, alors que sous Unix il serait simplement écrasé
            self.fichier._copie_temp.remove()
            #path_zip_temp = path(chem_zip_temp)
            #path_zip_temp.rename(str_lat1(self.fichier._copie_temp))
            os.rename(chem_zip_temp, self.fichier._copie_temp)
        else:
            Journal.info2(u"Aucun fichier accepté dans le Zip: suppression.")
            self.fichier._copie_temp.remove()
        # pour finir on détruit le répertoire temporaire:
        if self.rep_temp_complet.exists():
            self.rep_temp_complet.rmtree()
    

    def est_chiffre(self, fichier):
        """Retourne True si le fichier indiqué est chiffré, et qu'il ne peut
        pas être extrait du fichier ZIP.
        
        @param fichier: fichier à tester.
        @type  fichier: objet L{Fichier<Fichier.Fichier>}
        """
        # le bit 0 du champ "general purpose bit flag" est normalement
        # positionné à 1 si le fichier est chiffré, quel que soit l'algo de
        # chiffrement. (cf. appnote.iz ou appnote.txt)
        if fichier.zipinfo.flag_bits & 1:
            return True
        else:
            return False

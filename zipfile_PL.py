#!/usr/bin/python
# -*- coding: latin-1 -*-
"""
zipfile_PL

Module qui contient la classe L{ZipFile_PL<zipfile_PL.ZipFile_PL>},
pour améliorer le traitement des archives Zip du module standard zipfile.

URL du projet: U{http://www.decalage.info/python/zipfile}

@author: U{Philippe Lagadec<mailto:philippe.lagadec(a)laposte.net>}

@contact: U{Philippe Lagadec<mailto:philippe.lagadec(a)laposte.net>}

@license: CeCILL (open-source compatible GPL) - cf. code source ou fichier LICENCE.txt joint

@version: 1.01

@status: beta
"""
#==============================================================================
__docformat__ = 'epytext en'

#__author__  = "Philippe Lagadec"
__date__    = "2007-11-02"
__version__ = "1.01"

#------------------------------------------------------------------------------
# LICENCE :

# Copyright Philippe Lagadec 2005-2008 - voir http://www.decalage.info/contact
#
# zipfile_PL est un module Python pour etendre les fonctionnalites du module
# zipfile de la bibliotheque standard Python.
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
# 18/11/2005 v0.01 PL: - 1ère version
# 12/01/2007 v1.00 PL: - version 1.00 officielle
# 2007-11-08 v1.01 PL: - ajout licence CeCILL

#------------------------------------------------------------------------------
# A FAIRE:
#------------------------------------------------------------------------------

#=== IMPORTS ==================================================================

# modules standards Python:
import zipfile

#=== CLASSES ==================================================================

class ZipFile_PL(zipfile.ZipFile):
    """
    Classe qui améliore le traitement des archives Zip par rapport à la
    classe ZipFile standard de Python:
        - Détection des fichiers avec une taille différente du central directory
          une fois décompressés.
    """

    def read(self, name):
        """Pour décompresser le contenu d'un fichier de l'archive Zip dans une
        chaîne.
        Si la taille du fichier décompressé est différente de celle déclarée
        dans le central directory, une exception zipfile.BadZipFile est levée.
        """
        # on appelle d'abord la méthode read() d'origine
        fichier = zipfile.ZipFile.read(self, name)
        zinfo = self.getinfo(name)
        # on vérifie si la taille du fichier décompressé est la même que celle du central directory
        if len(fichier) != zinfo.file_size:
            raise zipfile.BadZipfile, \
                'File size in directory (%d) and header (%d) differ.'\
                % (zinfo.file_size, len(fichier))
        return fichier


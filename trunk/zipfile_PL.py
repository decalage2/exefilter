#!/usr/bin/python
# -*- coding: latin-1 -*-
"""
zipfile_PL

Module qui contient la classe L{ZipFile_PL<zipfile_PL.ZipFile_PL>},
pour am�liorer le traitement des archives Zip du module standard zipfile.

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
# 18/11/2005 v0.01 PL: - 1�re version
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
    Classe qui am�liore le traitement des archives Zip par rapport � la
    classe ZipFile standard de Python:
        - D�tection des fichiers avec une taille diff�rente du central directory
          une fois d�compress�s.
    """

    def read(self, name):
        """Pour d�compresser le contenu d'un fichier de l'archive Zip dans une
        cha�ne.
        Si la taille du fichier d�compress� est diff�rente de celle d�clar�e
        dans le central directory, une exception zipfile.BadZipFile est lev�e.
        """
        # on appelle d'abord la m�thode read() d'origine
        fichier = zipfile.ZipFile.read(self, name)
        zinfo = self.getinfo(name)
        # on v�rifie si la taille du fichier d�compress� est la m�me que celle du central directory
        if len(fichier) != zinfo.file_size:
            raise zipfile.BadZipfile, \
                'File size in directory (%d) and header (%d) differ.'\
                % (zinfo.file_size, len(fichier))
        return fichier


#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
"""
Filtre_PDF - ExeFilter

Ce module contient la classe L{Filtre_PDF.Filtre_PDF},
pour filtrer les documents PDF.

Ce fichier fait partie du projet ExeFilter.
URL du projet: U{http://www.decalage.info/exefilter}

@organization: DGA/CELAR
@author: U{Philippe Lagadec<mailto:philippe.lagadec(a)laposte.net>}
@author: U{Arnaud Kerréneur<mailto:arnaud.kerreneur(a)dga.defense.gouv.fr>}
@author: U{Tanguy Vinceleux<mailto:tanguy.vinceleux(a)dga.defense.gouv.fr>}

@contact: U{Philippe Lagadec<mailto:philippe.lagadec(a)laposte.net>}

@copyright: DGA/CELAR 2004-2008
@copyright: NATO/NC3A 2008-2010 (modifications PL apres ExeFilter v1.1.0)

@license: CeCILL (open-source compatible GPL)
          cf. code source ou fichier LICENCE.txt joint

@version: 1.09

@status: beta
"""
#==============================================================================
__docformat__ = 'epytext en'

__date__    = "2011-02-18"
__version__ = "1.09"

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
# HISTORIQUE:
# 08/06/2005 v0.01 TV: - 1ère version
# 2005-2006  PL,TV,AK: - evolutions
# 12/01/2007 v1.00 PL: - version 1.00 officielle
# 2008-02-19 v1.01 PL: - licence CeCILL
#                      - ajout suppression de mots-cles actifs (Javascript, ...)
# 2008-03-24 v1.02 PL: - ajout de _() pour traduction gettext des chaines
#                      - simplification dans nettoyer() en appelant resultat_*
# 2009-09-30 v1.03 PL: - initial origapy integration, to improve PDF cleaning
# 2009-10-05 v1.04 PL: - added parameters to select clean method
# 2009-10-07 v1.05 PL: - launch origami engine only if policy requires it
#                      - new option to ignore origami errors
# 2009-10-09 v1.06 PL: - added pdfid engine to improve PDF cleaning
# 2010-02-23 v1.07 PL: - updated RechercherRemplacer import
# 2010-05-02 v1.08 PL: - added parameter to disable launch actions with PDFiD
# 2011-02-18 v1.09 PL: - fixed temp file creation using new commun functions

#------------------------------------------------------------------------------
# TODO:
# + when origami fails, include warning text into result, without blocking
# - add options disable_richmedia and detect_cve_2009_xxxx for pdfid
# + improve AA and OpenAction removal to avoid false positives

#------------------------------------------------------------------------------
# REFERENCES:
# http://www.decalage.info/file_formats_security/pdf
# http://www.adobe.com/devnet/pdf/pdf_reference.html
# http://www.adobe.com/devnet/pdf/pdf_reference_archive.html
# http://www.adobe.com/products/acrobat/pdfs/OpenFilenAttach.pdf
# http://www.decalage.info/sstic03
# http://blog.didierstevens.com/2008/04/29/pdf-let-me-count-the-ways/
# http://www.security-labs.org/origami/
# http://michaeldaw.org/md-hacks/backdooring-pdf-files


#=== IMPORTS ==================================================================

import os, tempfile, sys
import thirdparty.RechercherRemplacer.RechercherRemplacer as RechercherRemplacer

# modules du projet:
from commun import *
import Filtre, Resultat, Parametres

# 3rd party modules:
import thirdparty.origapy.origapy as origapy
import thirdparty.pdfid.pdfid_PL as pdfid

#=== CONSTANTES ===============================================================



#=== FONCTIONS ================================================================



#=== CLASSES ==================================================================

#------------------------------------------------------------------------------
# classe FILTRE_PDF
#-------------------
class Filtre_PDF (Filtre.Filtre):
    """
    classe pour un filtre de fichiers PDF.

    un objet Filtre sert à reconnaître le format d'un fichier et à
    nettoyer le code éventuel qu'il contient. La classe Filtre_PDF
    correspond aux fichiers images PDF.

    @cvar nom: Le nom detaillé du filtre
    @cvar nom_code: nom de code du filtre
    @cvar extensions: liste des extensions de fichiers possibles
    @cvar format_conteneur: indique si c'est un format conteneur
    @cvar extractible: indique si il s'agit d'une archive
    @cvar nettoyable: indique si il est possible de nettoyer avec ce filtre
    @cvar date: date de la derniere modification du filtre
    @cvar version: version du filtre
    """

    nom = _(u"Document PDF")
    extensions = [".pdf"]
    format_conteneur = False
    extractible = False
    nettoyable = True

    # date et version définies à partir de celles du module
    date = __date__
    version = __version__

    def __init__ (self, politique, parametres=None):
        """Constructeur d'objet Filtre_PDF.

        parametres: dictionnaire pour fixer les paramètres du filtre
        """
        # on commence par appeler le constructeur de la classe de base
        Filtre.Filtre.__init__(self, politique, parametres)
        # ensuite on ajoute les paramètres par défaut
        # Origami: disabled by default
        Parametres.Parametre(u"use_origami", bool,
            nom=u"Remove active content using Origami engine",
            description=u"Remove all active content using Origami pdfclean "
                        +"engine. (EXPERIMENTAL: not all PDFs are supported yet)",
            valeur_defaut=False).ajouter(self.parametres)
        Parametres.Parametre(u"ignore_origami_errors", bool,
            nom=u"Ignore PDF parsing errors in Origami engine",
            description=u"The current version of Origami does not support all "
                        +"PDF features, and may block legitimate files. "
                        +"With this option ExeFilter will fall back to the "
                        +"simple replace method in case of error.",
            valeur_defaut=True).ajouter(self.parametres)
        # method using pdfid: enabled by default
        Parametres.Parametre(u"use_pdfid", bool,
            nom=u"Remove active content using pdfid",
            description=u"Remove all active content using pdfid. "
                        +"(EXPERIMENTAL: Effective against obfuscated PDFs)",
            valeur_defaut=True).ajouter(self.parametres)
        # Builtin simple replace method: enabled by default
        Parametres.Parametre(u"use_simple_replace", bool,
            nom=u"Remove active content using simple replace",
            description=u"Remove all active content using builtin simple replace "
                        +"method. (Only effective against non obfuscated PDFs)",
            valeur_defaut=True).ajouter(self.parametres)
        Parametres.Parametre(u"disable_javascript", bool,
            nom=u"Disable Javascript",
            description=u"Disable all Javascript code, which may trigger "
                        +"actions without user confirmation. (simple replace, pdfid)",
            valeur_defaut=True).ajouter(self.parametres)
        Parametres.Parametre(u"disable_embeddedfile", bool,
            nom=u"Disable embedded files",
            description=u"Disable all embedded files, which may hide "
                        +"executable code. (simple replace, pdfid)",
            valeur_defaut=True).ajouter(self.parametres)
        Parametres.Parametre(u"disable_fileattachment", bool,
            nom=u"Disable attached files",
            description=u"Disable all file attachments, which may hide "
                        +"executable code. (simple replace, pdfid)",
            valeur_defaut=True).ajouter(self.parametres)
        Parametres.Parametre(u"disable_aa", bool,
            nom=u"Disable AA objects (additional actions)",
            description=u"Disable all AA objects, which may trigger "
                        +"active content. (pdfid)",
            valeur_defaut=True).ajouter(self.parametres)
        Parametres.Parametre(u"disable_openaction", bool,
            nom=u"Disable OpenAction objects",
            description=u"Disable all OpenAction objects, which may trigger "
                        +"active content. (pdfid)",
            valeur_defaut=True).ajouter(self.parametres)
        Parametres.Parametre(u"disable_launch", bool,
            nom=u"Disable Launch objects",
            description=u"Disable all Launch objects, which may launch "
                        "executable files or scripts. (pdfid)",
            valeur_defaut=True).ajouter(self.parametres)
        Parametres.Parametre(u"disable_jbig2decode", bool,
            nom=u"Disable JBIG2Decode objects",
            description=u"Disable all JBIG2Decode objects, subject to vulnerabilities "
                        +"in some applications. (pdfid)",
            valeur_defaut=False).ajouter(self.parametres)
        # Origapy engine, not launched by default:
        self.pdfclean = None

    def reconnait_format(self, fichier):
        """
        analyse le format du fichier, et retourne True s'il correspond
        au format recherché, False sinon.
        """
        debut = fichier.lire_debut()
        # Un fichier PDF bien formé doit obligatoirement commencer par "%PDF-"
        # (en fait Acrobat accepte jusqu'à 1019 caractères quelconques
        # avant, mais ce n'est pas la structure classique d'un PDF...)
        if debut.startswith("%PDF-"):
            return True

    def clean_origami (self, fichier):
        """
        Clean PDF file using origapy/origami.
        To be called from nettoyer() method.
        Return Result object according to result.
        Trigger an exception if an error occurs.
        """
        Journal.info2('Cleaning PDF file with origami')
        if self.pdfclean is None:
            # launching Origapy PDFClean the first time:
            self.pdfclean = origapy.PDF_Cleaner(logger=Journal)
        # source file: temp copy of input file on disk:
        src_path = os.path.abspath(fichier.copie_temp())
        # output file: new temp file
##        f_temp, temp_path = tempfile.mkstemp(dir=self.politique.parametres['rep_temp'].valeur)
        temp_path = newTempFilename()
##        # close file because we only need the file path:
##        os.close(f_temp)
        Journal.info2 (u"Fichier temporaire: %s" % temp_path)
        try:
            result = self.pdfclean.clean(src_path, temp_path)
        except:
            # delete temp file:
            try: os.remove(temp_path)
            except: pass
            # raise exceptions to the caller for the ignore_origami_errors option
            raise
##            # an error occured during PDF parsing by origami
##            erreur=str(sys.exc_info()[1])
##            # delete temp file:
##            try: os.remove(temp_path)
##            except: pass
##            return self.resultat_format_incorrect(fichier, erreur=erreur)
        if result == origapy.CLEANED:
            Journal.info2 (u"Des objets PDF actifs ont ete trouves et desactives.")
            # replace temp copy by cleaned file:
            fichier.remplacer_copie_temp(temp_path)
            return self.resultat_nettoye(fichier)
        else:
            # file is clean
            Journal.info2 (u"Aucun contenu PDF actif n'a ete trouve.")
            # delete temp file:
            os.remove(temp_path)
            return self.resultat_accepte(fichier)


    def clean_pdfid (self, fichier):
        """
        Clean PDF file using pdfid.
        To be called from nettoyer() method.
        Return Result object according to result.
        Trigger an exception if an error occurs.
        """
        Journal.info2('Cleaning PDF file with pdfid')
        # source file: temp copy of input file on disk:
        src_path = os.path.abspath(fichier.copie_temp())
        # output file: new temp file
        temp_path = newTempFilename()
        Journal.info2 (u"Fichier temporaire: %s" % temp_path)
        # default active keywords to be cleaned:
        active_keywords = []
        if self.parametres["disable_javascript"].valeur == True:
            active_keywords += ['/JS', '/JavaScript']
        if self.parametres["disable_embeddedfile"].valeur == True:
            active_keywords += ['/EmbeddedFile', '/EmbeddedFiles']
        if self.parametres["disable_fileattachment"].valeur == True:
            active_keywords.append('/FileAttachment')
        if self.parametres["disable_aa"].valeur == True:
            active_keywords.append('/AA')
        if self.parametres["disable_openaction"].valeur == True:
            active_keywords.append('/OpenAction')
        if self.parametres["disable_launch"].valeur == True:
            active_keywords.append('/Launch')
        if self.parametres["disable_jbig2decode"].valeur == True:
            active_keywords.append('/JBIG2Decode')
        try:
            xmldoc, cleaned = pdfid.PDFiD(src_path, disarm=True,
                output_file=temp_path, raise_exceptions=True,
                return_cleaned=True, active_keywords=active_keywords)
        except:
            # delete temp file:
            try: os.remove(temp_path)
            except: pass
            # raise exceptions to the caller
            raise
##            # an error occured during PDF parsing by pdfid
##            erreur=str(sys.exc_info()[1])
##            # delete temp file:
##            try: os.remove(temp_path)
##            except: pass
##            return self.resultat_format_incorrect(fichier, erreur=erreur)
        if cleaned:
            Journal.info2 (u"Des objets PDF actifs ont ete trouves et desactives.")
            # replace temp copy by cleaned file:
            fichier.remplacer_copie_temp(temp_path)
            return self.resultat_nettoye(fichier)
        else:
            # file is clean
            Journal.info2 (u"Aucun contenu PDF actif n'a ete trouve.")
            # delete temp file:
            os.remove(temp_path)
            return self.resultat_accepte(fichier)


    def clean_simple_replace (self, fichier):
        """
        Clean PDF file using builtin simple replace method.
        To be called from nettoyer() method.
        Return Result object according to result.
        Trigger an exception if an error occurs.
        """
        # liste de motifs pour nettoyer certains mots cles PDF:
        motifs = []
        if self.parametres["disable_javascript"].valeur == True:
            motifs.append( RechercherRemplacer.Motif(case_sensitive=False,
                regex=r'/Javascript', remplacement='/NOjvscript'))
        if self.parametres["disable_embeddedfile"].valeur == True:
            motifs.append( RechercherRemplacer.Motif(case_sensitive=False,
                regex=r'/EmbeddedFile', remplacement='/NO_EmbedFile'))
        if self.parametres["disable_fileattachment"].valeur == True:
            motifs.append( RechercherRemplacer.Motif(case_sensitive=False,
                regex=r'/FileAttachment', remplacement='/NOFileAttachmt'))
        if len(motifs)>0:
            # creation d'un nouveau fichier temporaire
            f_dest, chem_temp = newTempFile()
            Journal.info2 (u"Fichier temporaire: %s" % chem_temp)
            # on ouvre le fichier source
            f_src = open(fichier.copie_temp(), 'rb')
            Journal.info2 (u"Nettoyage PDF par remplacement de chaine")
            n = RechercherRemplacer.rechercherRemplacer(motifs=motifs,
                fich_src=f_src, fich_dest=f_dest, taille_identique=True, controle_apres=True)
            f_src.close()
            f_dest.close()
            if n:
                Journal.info2 (u"Des objets PDF actifs ont ete trouves et desactives.")
                # Le fichier nettoye, on remplace la copie temporaire:
                fichier.remplacer_copie_temp(chem_temp)
                return self.resultat_nettoye(fichier)
                #return Resultat.Resultat(Resultat.NETTOYE,
                #    [self.nom + " : objets PDF actifs supprimés"], fichier)
            else:
                # pas de contenu actif
                Journal.info2 (u"Aucun contenu PDF actif n'a ete trouve.")
                # on efface le ficher temporaire:
                os.remove(chem_temp)
                return self.resultat_accepte(fichier)
        else:
            resultat = self.resultat_accepte(fichier)
        return resultat


    def nettoyer (self, fichier):
        """
        analyse et modifie le fichier pour supprimer tout code
        exécutable qu'il peut contenir, si cela est possible.
        Retourne un code résultat suivant l'action effectuée.
        """
        if self.parametres["use_origami"].valeur == True:
            try:
                return self.clean_origami(fichier)
            except RuntimeError:
                # an error occurred, most likely an origami parsing error:
                if self.parametres["ignore_origami_errors"].valeur == True:
                    # ignore exception, fall back to other methods:
                    Journal.warning("PDF parsing error in Origami: fall back to other methods.")
                    pass
                else:
                    # raise exception to caller (file will be blocked)
                    raise
        if self.parametres["use_pdfid"].valeur == True:
            return self.clean_pdfid(fichier)
        if self.parametres["use_simple_replace"].valeur == True:
            return self.clean_simple_replace(fichier)
        # if no clean method is enabled, return file as is:
        return self.resultat_accepte(fichier)




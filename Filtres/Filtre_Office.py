#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
"""
Filtre_Office - ExeFilter

Ce module contient les différentes classes de filtres correspondant
aux types de documents MS Office: Word, Excel, Powerpoint, ...
(fichiers au format binaire OLE2 / Microsoft Compound File Format)

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

@version: 1.05

@status: beta
"""
#==============================================================================
__docformat__ = 'epytext en'

__date__    = "2011-02-18"
__version__ = "1.05"

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
# 24/10/2004 v0.01 PL: - 1ère version
# 2004-2006        PL: - nombreuses evolutions
#                      - contributions de Y. Bidan et C. Catherin
# 12/01/2007 v1.00 PL: - version 1.00 officielle
# 2007-10-27 v1.01 PL: - ajout licence CeCILL
#                      - ajout methodes suppression macros: win32, remplacer
# 2008-02-06 v1.02 PL: - correction bug dans Infos_OLE.__init__
# 2008-03-24       PL: - ajout de _() pour traduction gettext des chaines
#                      - simplification dans nettoyer() en appelant resultat_*
# 2009-11-02 v1.03 PL: - updated parameters for gettext translation
# 2010-02-23 v1.04 PL: - updated OleFileIO_PL and RechercherRemplacer imports
# 2011-02-18 v1.05 PL: - fixed temp file creation using new commun functions

#------------------------------------------------------------------------------
# A FAIRE:
# + nettoyage de macros avec F-Prot 6
# + nettoyage des objets OLE au lieu de simple détection
# + améliorer la détection des objets OLE: ne pas lire tout le fichier en
#   mémoire, utiliser RechercherRemplacer
# + F-Prot avec l'option /NOFLOPPY pour éviter certaines erreurs
# ? vérification de l'absence effective de macros après nettoyage, en utilisant
#   OleFileIO ?
# ? Extraction d'objets OLE inclus pour approfondir l'analyse ?
#------------------------------------------------------------------------------

#=== IMPORTS ==================================================================

# modules standards Python:
import os, struct, sys, tempfile

# modules win32
if sys.platform == 'win32':
    # pour supprimer_macros_win32
    import pythoncom
    # pour les contantes STGM_*
    # cf. site-packages/win32com/storagecon.py
    from win32com.storagecon import *

# modules spécifiques:
from thirdparty.OleFileIO_PL.OleFileIO_PL import OleFileIO
import thirdparty.RechercherRemplacer.RechercherRemplacer as RechercherRemplacer

# modules du projet:
from commun import *
import Filtre, Resultat, Parametres

#=== CONSTANTES ===============================================================

# types de fichiers Office:
NON_DEFINI = 0
WORD       = 1
EXCEL      = 2
POWERPOINT = 3
ACCESS     = 4
PROJECT    = 5
VISIO      = 6

#=== FONCTIONS ================================================================


#=== CLASSES ==================================================================

#------------------------------------------------------------------------------
# classe Infos_OLE
#---------------------
class Infos_OLE:
    """classe pour lire les infos utiles d'un document OLE.

    Attributs:
    chiffre: vaut True si le document est chiffré.
    application: nom détaillé de l'application qui a créé le document.
    type_doc: type de document (WORD, EXCEL, ... ou NON_DEFINI)
    """

    def __init__(self, fichier_ole):
        "constructeur pour la classe Infos_OLE."
        # initialisation des attributs:
        self.chiffre = False
        self.appname = "Non defini"
        self.type_doc = NON_DEFINI
        sommaire = False    # flag indiquant si le sommaire a été trouvé
        ole = OleFileIO(fichier_ole)
        liste_streams = ole.listdir()
        for f in liste_streams:
            # on cherche le stream SummaryInformation
            if f == ["\x05SummaryInformation"]:
                sommaire = True
                props = ole.getproperties(f)
                # nom de l'application:
                if 0x12 in props:
                    self.appname = props[0x12]
                # on vérifie si le bit 1 du champ security = 1:
                # (attention ce champ est absent pour Powerpoint2000, par exemple)
                if 0x13 in props:
                    if props[0x13] & 1:
                        self.chiffre = True
            if f == ['WordDocument']:
                if self.type_doc != NON_DEFINI:
                    self.type_doc = NON_DEFINI
                else:
                    self.type_doc = WORD
                    s = ole.openstream(["WordDocument"])
                    # on passe 10 octets d'entête
                    s.read(10)
                    temp16 = struct.unpack("H", s.read(2))[0]
                    fEncrypted = (temp16 & 0x0100) >> 8
                    if fEncrypted:
                        self.chiffre = True
                    s.close()
            if f == ['Workbook'] or f == ['Book']:
                if self.type_doc != NON_DEFINI:
                    self.type_doc = NON_DEFINI
                else:
                    self.type_doc = EXCEL
            if f == ['PowerPoint Document']:
                if self.type_doc != NON_DEFINI:
                    self.type_doc = NON_DEFINI
                else:
                    self.type_doc = POWERPOINT

            # BDN PATCH
            # Prise en compte du format Visio
            if f == ['VisioDocument'] :
                if self.type_doc != NON_DEFINI:
                    self.type_doc = NON_DEFINI
                else:
                    self.type_doc = VISIO
            # END BDN PATCH

        # BDN PATCH : si à ce stade on a pas réussi à trouvé le type de fichier,
        # on prend en compte le nom de l'application qui a généré le fichier
        if self.type_doc == NON_DEFINI :
            if self.appname != "Non defini" :
                # on vérifie à partir de quel application le document a été créé
                if self.appname  == "Microsoft PowerPoint" :
                    self.type_doc = POWERPOINT
                elif "Microsoft Word" in self.appname :
                    self.type_doc = WORD
                elif self.appname == "Microsoft Excel":
                    self.type_doc = EXCEL
                elif self.appname == "MSProject":
                    self.type_doc = PROJECT
        # END BDN PATCH

        # si on n'a pas trouvé le sommaire, mieux vaut considérer ce
        # fichier comme incorrect (car on ne peut pas savoir s'il est
        # chiffré). Sauf dans le cas de Word, car pour un doc Word6 créé
        # par WordPad, il n'y a pas de sommaire.
        if sommaire == False and self.type_doc != WORD:
            self.type_doc = NON_DEFINI

        # bugfix 2008-02-06: il faut fermer explicitement le fichier...
        ole.fp.close()


#------------------------------------------------------------------------------
# classe FILTRE_OFFICE
#---------------------
class _Filtre_Office (Filtre.Filtre):
    """
    classe pour un filtre de fichiers Office.


    @cvar nom: Le nom detaillé du filtre
    @cvar nom_code: nom de code du filtre
    @cvar extensions: liste des extensions de fichiers possibles
    @cvar format_conteneur: indique si c'est un format conteneur
    @cvar extractible: indique si il s'agit d'une archive
    @cvar nettoyable: indique si il est possible de nettoyer avec ce filtre
    @cvar date: date de la derniere modification du filtre
    @cvar version: version du filtre
    """

    nom = _(u"Document MS Office generique")
    extensions = []
    format_conteneur = False
    extractible = False
    nettoyable = True

    # date et version définies à partir de celles du module
    date = __date__
    version = __version__

    # Nom du stream OLE contenant les macros VBA a supprimer pour
    # les desactiver, vaut None par defaut pour les autres filtres:
    stream_macros = None

    # motif pour desactiver les macros: a remplacer par un objet motif pour les
    # classes filtres qui le supportent, comme Word et Excel
    # (cf. module RechercherRemplacer)
    # vaut None par defaut pour les autres filtres:
    motif_macros = None

    def __init__ (self, politique, parametres=None):
        """Constructeur d'objet _Filtre_Office.

        parametres: dictionnaire pour fixer les paramètres du filtre
        """
        # on commence par appeler le constructeur de la classe de base
        Filtre.Filtre.__init__(self, politique, parametres)
        # ensuite on ajoute les paramètres par défaut
        Parametres.Parametre(u"detecter_ole_pkg", bool,
            nom=_(u"Détecter les objets OLE Package"),
            description=_(u"Détecter les objets OLE Package, qui peuvent "
                        "contenir des fichiers ou des commandes."),
            valeur_defaut=True).ajouter(self.parametres)
        Parametres.Parametre(u"supprimer_macros", bool,
            nom=_(u"Supprimer les macros VBA"),
            description=_(u"Supprimer toutes les macros VBA des documents."
                        " Voir aussi les parametres macros_xxx pour choisir la"
                        " methode employee. Si aucune methode n'est active, "
                        " une methode simple sera employee. Cette methode est"
                        " portable et rapide, mais ne couvre que Word et Excel."),
            valeur_defaut=True).ajouter(self.parametres)
        if self.stream_macros: Parametres.Parametre(u"macros_win32", bool,
            nom=_(u"Utiliser l'API Win32 pour supprimer les macros"),
            description=_(u"Utiliser les fonctions de Windows pour supprimer"
                        " toutes les macros VBA des documents. Cette methode"
                        " est rapide mais ne couvre que Word et Excel, et ne"
                        " fonctionne que sous Windows."),
            valeur_defaut=True).ajouter(self.parametres)
        Parametres.Parametre(u"macros_fpcmd", bool,
            nom=_(u"Utiliser F-Prot 3 pour supprimer les macros"),
            description=_(u"Utiliser l'antivirus F-Prot 3 (fpcmd) pour supprimer"
                        " toutes les macros VBA des documents. Cette methode"
                        " est lente mais fiable pour Word, Excel et Powerpoint."),
            valeur_defaut=False).ajouter(self.parametres)
        Parametres.Parametre(u"macros_fpscan", bool,
            nom=_(u"Utiliser F-Prot 6 pour supprimer les macros"),
            description=_(u"Utiliser l'antivirus F-Prot 6 (fpscan) pour supprimer"
                        " toutes les macros VBA des documents. Cette methode"
                        " est lente mais fiable pour Word, Excel et Powerpoint."),
            valeur_defaut=False).ajouter(self.parametres)
        # si des paramètres ont été fournis au constructeur, on les met à jour
        if parametres:
            Parametres.importer(self.parametres, parametres)


    def reconnait_format(self, fichier):
        """analyse le format du fichier, et retourne True s'il correspond
        au format recherché, False sinon."""
        debut = fichier.lire_debut()
        # magic très simple sur 2 octets:
        #if debut.startswith("\xD0\xCF"):
        # magic plus précis d'après code trouvé dans wvWare:
        # A VERIFIER: cela marche-t-il pour toutes les versions d'Office ?
        if debut.startswith("\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1"):
            # le magic est OK, on lit alors la structure OLE:
            # copie temporaire
            self.copie_temp = str_lat1(fichier.copie_temp())
            # on lit les infos dans le fichier OLE:
            try:
                self.infos_ole = Infos_OLE(self.copie_temp)
                resultat = True
            except:
                Journal.exception('erreur Infos_OLE')
                resultat = False
        else:
            Journal.debug('Magic incorrect: "%s"' % repr(debut[:8]))
            resultat = False
        return resultat


    def nettoyer (self, fichier):
        """analyse et modifie le fichier pour supprimer tout code
        exécutable qu'il peut contenir, si cela est possible.
        Retourne un code résultat suivant l'action effectuée."""
        # si c'est un fichier chiffré, on ne peut pas l'analyser correctement:
        if self.infos_ole.chiffre:
            return self.resultat_chiffre(fichier)
            #return Resultat.Resultat(Resultat.REFUSE,
            #    self.nom + " : fichier chiffré, non analysable", fichier)
        if self.parametres["detecter_ole_pkg"].valeur == True:
            # détection d'objet OLE Package: A AMELIORER
            # (éviter de lire tout le fichier en mémoire)
            f = file(self.copie_temp, "rb")
            buf = f.read().lower()
            f.close()
            if 'package\x00' in buf or '\x00package' in buf:
                return self.resultat_nettoyage_impossible(fichier,
                    _(u"Contient un objet OLE Package"))
        if self.parametres["supprimer_macros"].valeur == True:
            # On choisit la methode la plus fiable en fonction des parametres:
            if self.parametres["macros_fpcmd"].valeur == True:
                resultat = self.supprimer_macros_fpcmd(fichier)
            elif 'macros_win32' in self.parametres \
                and self.parametres["macros_win32"].valeur == True \
                and sys.platform == 'win32':
                resultat = self.supprimer_macros_win32(fichier)
            else:
                resultat = self.supprimer_macros_remplacer(fichier)
        else:
            resultat = self.resultat_accepte(fichier)
        return resultat


    def supprimer_macros_remplacer (self, fichier):
        """
        Pour supprimer les macros VBA en utilisant un simple remplacement de
        chaine dans le fichier.
        Cette methode est rapide et portable.
        Cependant elle ne fonctionne que pour Word et Excel, et des effets de
        bord sont possible si le fichier contient certains mots cles.
        """
        if self.motif_macros == None:
            # Pour certains formats cette methode simple ne fonctionne pas:
            return self.resultat_accepte(fichier)
        # creation d'un fichier temporaire
##        f_temp, chem_temp = tempfile.mkstemp(dir=self.politique.parametres['rep_temp'].valeur)
        f_dest, chem_temp = newTempFile()
        Journal.info2 (u"Fichier temporaire: %s" % chem_temp)
##        f_dest = os.fdopen(f_temp, 'wb')
        # on ouvre le fichier source
        f_src = open(fichier.copie_temp(), 'rb')
        Journal.info2 (u"Suppression des macros VBA par remplacement de chaine")
        n = RechercherRemplacer.rechercherRemplacer(motifs=[self.motif_macros],
            fich_src=f_src, fich_dest=f_dest, taille_identique=True, controle_apres=True)
        f_src.close()
        f_dest.close()
        if n:
            Journal.info2 (u"Des macros VBA ont ete trouvees et desactivees.")
            # Le fichier nettoye, on remplace la copie temporaire:
            fichier.remplacer_copie_temp(chem_temp)
            return self.resultat_nettoye(fichier)#, _(u"Macro(s) VBA supprimée(s)"))
        else:
            # macros VBA non trouvees
            Journal.info2 (u"Aucune macro VBA n'a ete trouvee.")
            # on efface le ficher temporaire:
            os.remove(chem_temp)
            return self.resultat_accepte(fichier)


    def supprimer_macros_win32 (self, fichier):
        """
        Pour desactiver les macros VBA en utilisant l'API Win32 pour supprimer
        le stream contenant les macros.
        Cette methode est rapide et simple, mais ne fonctionne que sous Windows.
        De plus elle ne fonctionne que pour Word et Excel, et des effets de
        bord sont possible si le fichier contient certains mots cles.
        """
        if self.stream_macros == None:
            # Pour certains formats cette methode simple ne fonctionne pas:
            return Resultat.Resultat(Resultat.ACCEPTE,
                self.nom + " : pas de contenu suspect détecté", fichier)
        Journal.info2 (u"Suppression des macros VBA via l'API Win32")
        mode = STGM_READWRITE|STGM_SHARE_EXCLUSIVE
        istorage = pythoncom.StgOpenStorageEx(fichier.copie_temp(), mode,
               STGFMT_STORAGE, 0, pythoncom.IID_IStorage)
        try:
            istorage.DestroyElement(self.stream_macros)
            Journal.debug (u"Le stream %s a ete supprime." % self.stream_macros)
            Journal.info2 (u"Des macros VBA ont ete trouvees et desactivees.")
            return self.resultat_nettoye(fichier)#, _(u"Macro(s) VBA supprimée(s)"))
        except pythoncom.com_error, details:
            # exception specifique quand le stream n'existe pas
            if details[1] == 'STG_E_FILENOTFOUND':
                # macros VBA non trouvees
                Journal.info2 (u"Aucune macro VBA n'a ete trouvee.")
                return self.resultat_accepte(fichier)
            else:
                # autre erreur pythoncom:
                Journal.exception("Erreur lors du nettoyage des macros")
        except:
            # toute autre erreur:
            Journal.exception("Erreur lors du nettoyage des macros")
        # Dans tous les cas si on arrive ici c'est qu'une erreur s'est produite
        return self.resultat_nettoyage_impossible(fichier,
            _(u"erreur lors du nettoyage des macros VBA"))


    def supprimer_macros_fpcmd (self, fichier):
        """
        Pour supprimer les macros VBA en utilisant l'antivirus F-Prot 3 version
        ligne de commande (fpcmd).
        Cette methode est la plus fiable pour Word, Excel et Powerpoint.
        Cependant le lancement de l'antivirus est relativement long.
        """
        # Nettoyage des macros éventuelles:
        Journal.info2("Lancement de F-Prot 3 (fpcmd) pour supprimer les macros...")
        # on récupère le chemin de F-Prot dans la configuration globale:
        chemin_fprot = self.politique.parametres["fpcmd_executable"].valeur
        args_fprot = [chemin_fprot, '-auto', '-nomem', '-noboot', '-noheur', '-nosub',
            '-old', '-onlymacro', '-removeall', '-type', '-disinf', self.copie_temp]
        # on lance F-Prot avec Popen_timer pour masquer son affichage et
        # limiter le temps d'exécution (cf. commun.py):
        resultat_fprot = Popen_timer(args_fprot)
        if resultat_fprot == 0:
            resultat = self.resultat_accepte(fichier)
        elif resultat_fprot == 6:
            resultat = self.resultat_nettoye(fichier)
        elif resultat_fprot == EXIT_KILL_PTIMER:
            resultat = self.resultat_nettoyage_impossible(fichier,
                _(u"temps dépassé lors du nettoyage des macros VBA"))
        else:
            resultat = self.resultat_nettoyage_impossible(fichier,
                _(u"erreur lors du nettoyage des macros VBA"))
        return resultat

#    F-Prot /ALL /AUTO /DIS /NOB /NOH /NOME /PAR /REMOVEA /SIL /TYP /OLD /REPORT=%s
#
#    Codes retournés par F-Prot:
#    0: OK, aucune macro trouvée.
#    1: NOK, les fichiers de signatures sont obsolètes ou autre erreur.
#    2: NOK, échec lors de l'auto-test.
#    3: NOK, virus fichier ou boot détecté: %LOGTEXT%.
#    4: NOK, virus détecté en mémoire: %LOGTEXT%.
#    5: NOK, programme stoppé par l'utilisateur.
#    6: NOK, %LOGTEXT%. (macro nettoyée)
#    7: NOK, mémoire insuffisante.
#    8: NOK, fichier suspect détecté: %LOGTEXT%.
#    9: code inconnu


#------------------------------------------------------------------------------
# classe FILTRE_WORD
#---------------------
class Filtre_Word (_Filtre_Office):
    """
    classe pour un filtre de documents MS Word.


    @cvar nom: Le nom detaillé du filtre
    @cvar nom_code: nom de code du filtre
    @cvar extensions: liste des extensions de fichiers possibles
    @cvar format_conteneur: indique si c'est un format conteneur
    @cvar extractible: indique si il s'agit d'une archive
    @cvar nettoyable: indique si il est possible de nettoyer avec ce filtre
    @cvar date: date de la derniere modification du filtre
    @cvar version: version du filtre

    """

    nom = _(u"Document MS Word")
    extensions = [".doc", ".wbk", ".dot"]

    # date et version définies à partir de celles du module
    date = __date__
    version = __version__

    # Nom du stream OLE contenant les macros VBA a supprimer pour
    # les desactiver:
    stream_macros = 'Macros'

    # motif pour desactiver les macros:
    # regex du motif a rechercher (r pour raw string):
    # Pour Word, 'Macros' en Unicode:
    regex_VBA = r'M\x00a\x00c\x00r\x00o\x00s'
    # chaine de remplacement: 'MacroX'
    # attention ici ce n'est pas une raw string, sinon les \x00 ne sont pas convertis
    rempl_VBA = 'M\x00a\x00c\x00r\x00o\x00X'
    motif_macros = RechercherRemplacer.Motif(regex=regex_VBA, case_sensitive=False,
                remplacement=rempl_VBA)

    def reconnait_format(self, fichier):
        """analyse le format du fichier, et retourne True s'il correspond
        au format recherché, False sinon."""
        # on vérifie d'abord si c'est un doc Office, et on lit les infos OLE:
        if _Filtre_Office.reconnait_format(self, fichier):
            # puis on vérifie si ces infos OLE indiquent bien un doc Word
            if self.infos_ole.type_doc == WORD:
                return True
            else:
                return False
        else:
            return False


#------------------------------------------------------------------------------
# classe FILTRE_EXCEL
#---------------------
class Filtre_Excel (_Filtre_Office):
    """
    classe pour un filtre de documents MS Excel.


    @cvar nom: Le nom detaillé du filtre
    @cvar nom_code: nom de code du filtre
    @cvar extensions: liste des extensions de fichiers possibles
    @cvar format_conteneur: indique si c'est un format conteneur
    @cvar extractible: indique si il s'agit d'une archive
    @cvar nettoyable: indique si il est possible de nettoyer avec ce filtre
    @cvar date: date de la derniere modification du filtre
    @cvar version: version du filtre


    """

    nom = _(u"Classeur MS Excel")
    extensions = [".xls", '.xlt']

    # date et version définies à partir de celles du module
    date = __date__
    version = __version__

    # Nom du stream OLE contenant les macros VBA a supprimer pour
    # les desactiver:
    stream_macros = '_VBA_PROJECT_CUR'

    # motif pour desactiver les macros:
    # regex du motif a rechercher (r pour raw string):
    # Pour Excel, '_VBA_PROJECT_CUR' en Unicode:
    regex_VBA = r'_\x00V\x00B\x00A\x00'
    # chaine de remplacement: '_VBX'
    # attention ici ce n'est pas une raw string, sinon les \x00 ne sont pas convertis
    rempl_VBA = '_\x00V\x00B\x00X\x00'
    motif_macros = RechercherRemplacer.Motif(regex=regex_VBA, case_sensitive=False,
                remplacement=rempl_VBA)

    def reconnait_format(self, fichier):
        """analyse le format du fichier, et retourne True s'il correspond
        au format recherché, False sinon."""
        # on vérifie d'abord si c'est un doc Office, et on lit les infos OLE:
        if _Filtre_Office.reconnait_format(self, fichier):
            # puis on vérifie si ces infos OLE indiquent bien un doc Excel
            if self.infos_ole.type_doc == EXCEL:
                return True
            else:
                return False
        else:
            return False


#------------------------------------------------------------------------------
# classe FILTRE_POWERPOINT
#---------------------------
class Filtre_Powerpoint (_Filtre_Office):
    """
    classe pour un filtre de documents MS Powerpoint.


    @cvar nom: Le nom detaillé du filtre
    @cvar nom_code: nom de code du filtre
    @cvar extensions: liste des extensions de fichiers possibles
    @cvar format_conteneur: indique si c'est un format conteneur
    @cvar extractible: indique si il s'agit d'une archive
    @cvar nettoyable: indique si il est possible de nettoyer avec ce filtre
    @cvar date: date de la derniere modification du filtre
    @cvar version: version du filtre


    """

    nom = _(u"Presentation MS Powerpoint")
    extensions = [".ppt", ".pps", ".pot"]

    # date et version définies à partir de celles du module
    date = __date__
    version = __version__

    def reconnait_format(self, fichier):
        """analyse le format du fichier, et retourne True s'il correspond
        au format recherché, False sinon."""
        # on vérifie d'abord si c'est un doc Office, et on lit les infos OLE:
        if _Filtre_Office.reconnait_format(self, fichier):
            # puis on vérifie si ces infos OLE indiquent bien un doc Excel
            if self.infos_ole.type_doc == POWERPOINT:
                return True
            else:
                return False
        else:
            return False


#------------------------------------------------------------------------------
# classe FILTRE_VISIO
#---------------------------
class Filtre_Visio (_Filtre_Office):
    """
    classe pour un filtre de documents MS Visio.


    @cvar nom: Le nom detaill? du filtre
    @cvar nom_code: nom de code du filtre
    @cvar extensions: liste des extensions de fichiers possibles
    @cvar format_conteneur: indique si c'est un format conteneur
    @cvar extractible: indique si il s'agit d'une archive
    @cvar nettoyable: indique si il est possible de nettoyer avec ce filtre
    @cvar date: date de la derniere modification du filtre
    @cvar version: version du filtre


    """

    nom = _(u"Dessin MS Visio")
    extensions = [".vsd", ".vst", ".vss"]

    # date et version d?finies ? partir de celles du module
    date = __date__
    version = __version__

    def reconnait_format(self, fichier):
        """analyse le format du fichier, et retourne True s'il correspond
        au format recherch?, False sinon."""
        # on v?rifie d'abord si c'est un doc Office, et on lit les infos OLE:
        if _Filtre_Office.reconnait_format(self, fichier):
            # puis on v?rifie si ces infos OLE indiquent bien un doc Excel
            if self.infos_ole.type_doc == VISIO:
                return True
            else:
                return False
        else:
            return False

#------------------------------------------------------------------------------
# classe FILTRE_PROJECT
#---------------------------
class Filtre_Project (_Filtre_Office):
    """
    classe pour un filtre de documents MS Project.


    @cvar nom: Le nom detaill? du filtre
    @cvar nom_code: nom de code du filtre
    @cvar extensions: liste des extensions de fichiers possibles
    @cvar format_conteneur: indique si c'est un format conteneur
    @cvar extractible: indique si il s'agit d'une archive
    @cvar nettoyable: indique si il est possible de nettoyer avec ce filtre
    @cvar date: date de la derniere modification du filtre
    @cvar version: version du filtre


    """

    nom = _(u"Projet MS Project")
    extensions = [".mpp", ".mpt"]

    # date et version d?finies ? partir de celles du module
    date = __date__
    version = __version__

    def reconnait_format(self, fichier):
        """analyse le format du fichier, et retourne True s'il correspond
        au format recherch?, False sinon."""
        # on v?rifie d'abord si c'est un doc Office, et on lit les infos OLE:
        if _Filtre_Office.reconnait_format(self, fichier):
            # puis on v?rifie si ces infos OLE indiquent bien un doc Excel
            if self.infos_ole.type_doc == PROJECT:
                return True
            else:
                return False
        else:
            return False



#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
"""
Filtre_HTML - ExeFilter

Ce module contient la classe L{Filtre_HTML.Filtre_HTML} permettant de filtrer
les fichiers de type "document HTML".

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

@version: 1.04

@status: beta
"""
#==============================================================================
__docformat__ = 'epytext en'

__date__    = "2011-02-18"
__version__ = "1.04"

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
# 29/10/2004 v0.01 PL: - 1ère version
# 2004-2006     PL,AK: - evolutions
# 12/01/2007 v1.00 PL: - version 1.00 officielle
# 2008-02-24 v1.01 PL: - licence CeCILL
# 2008-03-24 v1.02 PL: - ajout de _() pour traduction gettext des chaines
#                      - simplification dans nettoyer() en appelant resultat_*
# 2010-02-23 v1.03 PL: - updated HTMLParser_PL import
# 2011-02-18 v1.04 PL: - fixed temp file creation using new commun functions

#------------------------------------------------------------------------------
# A FAIRE:
#------------------------------------------------------------------------------

#=== IMPORTS ==================================================================

# modules standards Python:
import os, sys, urlparse, tempfile, codecs, traceback, HTMLParser

# modules du projet:
import commun
from commun import *
import Resultat, Conteneur
import Filtre
import thirdparty.HTMLParser_PL.HTMLParser_PL as HTMLParser_PL


#=== CONSTANTES ===============================================================

# liste des protocoles autorisés dans une URL:
PROTOCOLES_OK = ["file", "http", "https", "ftp", "mailto"]

# liste des balises HTML à supprimer:
BALISES_SUPPR = ['script', 'object', 'embed', 'applet', 'xml', 'iframe']

# Byte-Order Markers utilisés comme entêtes pour les encodages Unicode ou UTF-8:
BOM = {
    'utf_16_be': codecs.BOM_UTF16_BE,
    'utf_16_le': codecs.BOM_UTF16_LE,
    'utf_8'    : codecs.BOM_UTF8
    }

# nombre d'octets lus à chaque lecture du fichier
TAILLE_BUFFER = 65536

#=== CLASSES ==================================================================

# Classe de base pour les parseurs HTML:
# (permet de changer facilement cette classe sans toucher au code)
HTMLParser_base = HTMLParser_PL.HTMLParser_PL
#HTMLParser_base = HTMLParser.HTMLParser

#==============================================================================
# classe HTML_META
#=====================
class HTML_META (HTMLParser_base):
    """Pour analyser un code HTML et déterminer si une balise META indique un
    encodage différent de celui du BOM.

    Après analyse complète du code HTML, le résultat peut être lu dans
    l'attribut encodage_META (None ou nom du codec trouvé).
    Si une incohérence est détectée (encodages META et BOM différents, ou bien
    deux balises META différentes), une exception ValueError est levée.

    @ivar encodage_META: encodage spécifié par une balise META.
    """

    def __init__(self, encodage_BOM=None):
        """constructeur pour un objet HTML_META.

        @param encodage_BOM: nom du codec déduit du BOM, None sinon.
        @type  encodage_BOM: str, None
        """
        # on initialise d'abord avec le constructeur de la classe de base:
        HTMLParser_base.__init__(self)
        # encodage déduit du BOM
        self.encodage_BOM  = encodage_BOM
        # encodage spécifié par balise META
        self.encodage_META = None

    def handle_starttag(self, tag, attrs):
        """Pour traiter une balise HTML ouvrante.
        Seules les balises META sont prises en compte.
        """
        # on ne prend en compte que les balises META:
        if tag != 'meta': return
        # flag pour noter si on a un http-equiv=content-type
        http_equiv = False
        # charset vide au départ
        charset = ""
        for attr in attrs:
            # conversion du nom et de la valeur de l'attribut en minuscule:
            nom_attr = attr[0].lower()
            val_attr = attr[1].lower()
            if nom_attr == "content":
                # on découpe suivant les points virgules:
                champs = val_attr.split(';')
                for champ in champs:
                    # on découpe ensuite au 1er signe égal
                    variables = champ.split('=', 1)
                    if len(variables) == 2:
                        if variables[0].strip() == "charset":
                            # s'il y avait déjà un charset, problème
                            if charset != "":
                                raise ValueError, _(u"Double charset dans une balise META")
                            charset = variables[1].strip()
                            Journal.debug(u'trouvé attribut content = "charset=%s"' % charset)
            elif nom_attr == "http-equiv" and val_attr == "content-type":
                http_equiv = True
                Journal.debug(u"trouvé attribut http-equiv = content-type")
        # une fois parcouru tous les attributs, on regarde le résultat:
        if http_equiv and charset != "":
            # si un encodage différent de charset était déjà spécifié, incohérence:
            if self.encodage_META != None and charset != self.encodage_META:
                raise ValueError, _(u"Double encodage META incoherent.")
            # idem si l'encodage du BOM et celui de la balise META sont différents:
            elif self.encodage_BOM != None and charset != self.encodage_BOM:
                raise ValueError, _(u"Encodages BOM et META incoherents.")
            else:
                self.encodage_META = charset


#==============================================================================
# classe HTML_Nettoyeur
#=======================
class HTML_Nettoyeur(HTMLParser_base):
    """pour nettoyer un code HTML de tout code exécutable."""

    def __init__(self, fichier_sortie=sys.stdout, encoding=None):
        """constructeur pour HTML_Nettoyeur.

        fichier_sortie: fichier pour écrire la sortie.
        encoding: codec à utiliser pour décoder le fichier, None sinon."""
        HTMLParser_base.__init__(self)
        # fichier de sortie (objet file)
        self._fdest = fichier_sortie
        # flag pour indiquer qu'on est en train de supprimer une balise
        self._suppression = False
        # nom de la balise en cours de suppression: "script", "object", ...
        self._balise_suppr = ""
        # flag pour indiquer qu'un nettoyage a eu lieu, False par défaut
        self.nettoyage = False
        self.encoding = encoding
        # flag pour indiquer qu'une balise META précisant l'encodage a été
        # trouvée, et donc qu'il faut recommencer l'analyse avec le codec
        # indiqué par self.encoding
        self.meta_encoding = False

    def _supprimer_balise_deb(self, tag):
        """pour débuter la suppression d'une balise.
        tag: nom de la balise supprimée."""
        self._suppression = True
        self._balise_suppr = tag
        self._fdest.write(_(u"<!-- balise %s supprimee -->") % tag)
        self.nettoyage = True

    def _supprimer_balise_fin(self, tag):
        """pour terminer la suppression d'une balise.
        tag: nom de la balise supprimée."""
        if self._suppression and self._balise_suppr == tag:
            self._suppression = False


    def handle_starttag(self, tag, attrs):
        """balise ouvrante quelconque"""
        # si c'est une balise à supprimer, on le marque:
        if tag in BALISES_SUPPR:
            self._supprimer_balise_deb(tag)
        # si on n'est pas en mode suppression, on recopie la balise
        elif not self._suppression:
            # on vérifie si un des attributs commence par "on..."
            # ou si une valeur d'attribut est une URL débutant par autre
            # chose que "http:", "ftp:", "mailto:", ...
            # dans ce cas on le supprime
            suppr_attr = False # flag si attributs à supprimer
            attrs_ok = [] # liste des attributs nettoyés
            attrs_bruts = ""
            for attr in attrs:
                nom_attr = attr[0]
                val_attr = attr[1]
                attr_brut = attr[2]
                if nom_attr.lower().startswith("on"):
                    # Attribut à supprimer: on ne l'ajoute pas
                    # à la liste des attributs nettoyés.
                    # On note qu'au moins un attribut est supprimé
                    suppr_attr = True
                    Journal.info2(_(u"attribut interdit: %s=...") % nom_attr)
                elif ":" in val_attr:
                    # la valeur contient ":", ce doit être
                    # une URL de type "protocole:..." ou "*script:..."
                    # on vérifie si c'est un protocole autorisé:
                    url = urlparse.urlsplit(val_attr)
                    proto = url[0].lower()
                    if proto in PROTOCOLES_OK:
                        attrs_ok.append(attr)
                        attrs_bruts += attr_brut
                    else:
                        suppr_attr = True
                        Journal.info2(_(u"attribut interdit: %s=%s:...") %
                            (nom_attr, proto))
                else:
                    # sinon pas de problème, l'attribut est
                    # accepté tel quel
                    attrs_ok.append(attr)
                    attrs_bruts += attr_brut
            # on reconstruit la balise nettoyée avec les attributs autorisés:
#/            balise_nettoyee = u"<%s" % tag
#/            for attr in attrs_ok:
#/                balise_nettoyee += u' %s="%s"' % (attr[0], attr[1])
#/            balise_nettoyee += u">"
            balise_nettoyee = u"<%s%s>" % (tag, attrs_bruts)
            if suppr_attr:
                # si au moins un attribut a été supprimé, on écrit la balise
                # nettoyée:
                self._fdest.write(balise_nettoyee)
                self.nettoyage = True
            else:
                self._fdest.write(balise_nettoyee)
#/                # sinon on écrit la balise et ses attributs sous leur forme
#/                # d'origine, pour conserver au maximum la mise en page:
#/                # Mais auparavant, on vérifie la cohérence du résultat, en
#/                # comptant le nombre de signes "=", qui doit être le même:
#/                # (permet de détecter certains camouflages)
#/                debug(u"balise_nettoyee = %s" % balise_nettoyee)
#/                debug(u"self.get_starttag_text() = %s" % self.get_starttag_text())
#/                starttag_text = self.get_starttag_text()
#/                # parfois get_starttag_text() retourne None, et cela peut lever
#/                # des exceptions... Pour l'éviter:
#/                if not starttag_text: starttag_text = ""
#/                if balise_nettoyee.count("=") != starttag_text.count("="):
#/                    Journal.debug(u"Incohérence détectée lors de la reconstruction balise:")
#/                    Journal.debug(u"Nb signes égal dans balise nettoyée : %d / balise d'origine: %d"
#/                        % ( balise_nettoyee.count("="), starttag_text.count("=")))
#/                    #raise sgmllib.SGMLParseError, "erreur de reconstruction balise"
#/                    # on écrit alors la balise nettoyée:
#/                    self._fdest.write(balise_nettoyee)
#/                    self.nettoyage = True
#/                else:
#/                    self._fdest.write(starttag_text)

    def handle_data(self, data):
        """données hors balises"""
        # si on n'est pas en mode suppression, on recopie les données
        if not self._suppression:
            self._fdest.write(data)

    def handle_endtag(self, tag):
        """balise fermante quelconque"""
        # si c'est une balise à supprimer, on la traite:
        if tag in BALISES_SUPPR:
            self._supprimer_balise_fin(tag)
        # si on n'est pas en mode suppression, on recopie la balise
        elif not self._suppression:
            self._fdest.write("</%s>" % tag)

    def handle_charref(self, name):
        """CharRef décodée dans des données entre balises.

        name est la chaîne du code entre '&#' et ';'.
        """
        # si on n'est pas en mode suppression, on recopie les données
        if not self._suppression:
            self._fdest.write('&#'+name+';')

    def handle_entityref(self, name):
        """EntityRef décodée dans des données entre balises.

        name est la chaîne du code entre '&' et ';'.
        """
        # si on n'est pas en mode suppression, on recopie les données
        if not self._suppression:
            self._fdest.write('&'+name+';')

    def handle_comment(self, data):
        """Commentaire entre '<!--' et '-->'.
        """
        # si on n'est pas en mode suppression, on recopie les données
        if not self._suppression:
            self._fdest.write('<!--'+data+'-->')

    def handle_decl(self, decl):
        """Décalaration SGML entre '<!' et '>'.
        """
        # si on n'est pas en mode suppression, on recopie les données
        if not self._suppression:
            self._fdest.write('<!'+decl+'>')

    def handle_pi(self, data):
        """Processing instruction SGML entre '<?' et '>'.
        """
        # si on n'est pas en mode suppression, on recopie les données
        if not self._suppression:
            self._fdest.write('<?'+data+'>')


#------------------------------------------------------------------------------
# lire_BOM
#---------------------

def lire_BOM (debut_fichier):
    """Pour déterminer si le fichier est codé en Unicode ou UTF-8 en
    regardant s'il commence par un marqueur BOM (Byte Order Marker).
    (sinon employer codec 'latin_1' par défaut si BOM absent)

    @param debut_fichier: chaine correspondant au début du fichier.
    @return: retourne une chaine correspondant au codec à employer.
    """
    for codec in BOM:
        if debut_fichier.startswith(BOM[codec]):
            return codec
    else:
        return None



#------------------------------------------------------------------------------
# classe FILTRE_HTML
#---------------------

class Filtre_HTML (Filtre.Filtre):
    """
    classe pour un filtre de fichiers HTML.

    un objet Filtre sert à reconnaître le format d'un fichier et à
    nettoyer le code éventuel qu'il contient. La classe Filtre_HTML
    correspond aux documents HTML.

    @cvar nom: Le nom detaillé du filtre
    @cvar nom_code: nom de code du filtre
    @cvar extensions: liste des extensions de fichiers possibles
    @cvar format_conteneur: indique si c'est un format conteneur
    @cvar extractible: indique si il s'agit d'une archive
    @cvar nettoyable: indique si il est possible de nettoyer avec ce filtre
    @cvar date: date de la derniere modification du filtre
    @cvar version: version du filtre
    """

    nom = _(u"Document HTML")
    extensions = [".html", ".htm"] # et .php, .asp, .cgi, ... ?
    format_conteneur = False
    extractible = False
    nettoyable = True

    # date et version définies à partir de celles du module
    date = __date__
    version = __version__

    def reconnait_format(self, fichier):
        """analyse le format du fichier, et retourne True s'il correspond
        au format recherché, False sinon."""
        # En théorie un fichier HTML bien formé devrait toujours commencer
        # par une balise "<HTML>" et se terminer par "</HTML>".
        # En pratique les navigateurs n'imposent aucune balise particulière,
        # même un simple fichier texte est affiché comme du HTML.
        # Dans un premier temps on peut vérifier quand même la présence de
        # <HTML> au début: ... ou pas.
        #debut = fichier.lire_debut()
        #if debut.startswith("<HTML>"):
        return True

    def nettoyer (self, fichier):
        """Analyse et modifie le fichier pour supprimer tout code
        exécutable qu'il peut contenir, si cela est possible.
        Retourne un code résultat suivant l'action effectuée.
        """
        # 1) l'encodage par défaut pour un fichier HTML est Latin-1
        encodage = "latin_1"

        # 2) on vérifie si le fichier est codé en Unicode ou UTF-8 en
        # regardant s'il commence par un marqueur BOM (Byte Order Marker):
        debut = fichier.lire_debut()
        encodage_BOM = lire_BOM(debut)
        if encodage_BOM:
            encodage = encodage_BOM
            Journal.info2 (_(u"encodage d'après le BOM: %s") % encodage_BOM)

        # 3) 1ère passe d'analyse pour déterminer si une balise META indique un
        # autre encodage:
        h = HTML_META(encodage_BOM)
        # copie temporaire du fichier
        copie_temp = fichier.copie_temp()
        # on l'ouvre avec le codec déduit du BOM, ou Latin-1 par défaut
        fich_src = codecs.open(copie_temp, 'rb', encodage)
        try:
            texte_source = fich_src.read(TAILLE_BUFFER)
            while texte_source:
                # tant qu'il y a des données à lire
                # on analyse le code HTML à la recherche de balises META
                h.feed(texte_source)
                # on lit le bloc de données suivant
                texte_source = fich_src.read(TAILLE_BUFFER)
            h.close()
        except HTMLParser.HTMLParseError:
            # erreur de syntaxe lors de l'analyse HTML:
            Journal.info2(_(u"Erreur lors de l'analyse des balises META"), exc_info=True)
            erreur = str(sys.exc_info()[1])
            return self.resultat_analyse_impossible(fichier,
                raison=_(u"Syntaxe HTML incorrecte"), erreur=erreur)
        except ValueError, UnicodeError:
            # si on obtient une de ces 2 erreurs, il s'agit de caractères
            # incorrects vis-à-vis de l'encodage, ou bien d'un double encodage
            # incohérent:
            Journal.info2(_(u"Erreur lors de l'analyse des balises META"), exc_info=True)
            erreur = str(sys.exc_info()[1])
            return self.resultat_analyse_impossible(fichier,
                raison=_(u"Encodage du fichier incorrect"), erreur=erreur)
        except:
            # sinon on remonte l'exception:
            raise
        fich_src.close()
        # on récupère l'encodage fourni par une balise META, si c'est le cas:
        if h.encodage_META:
            encodage = h.encodage_META
            Journal.info2 (_(u"encodage d'après la balise META: %s") % encodage)

        # 4) 2ème passe pour nettoyer le code HTML vers un fichier temporaire
        # Création d'un fichier HTML temporaire:
        #f_temp, chem_temp = tempfile.mkstemp(suffix=".html", dir=Conteneur.RACINE_TEMP)
##        f_temp, chem_temp = tempfile.mkstemp(suffix=".html",
##            dir=commun.politique.parametres['rep_temp'].valeur)
        f_temp, chem_temp = newTempFile(suffix=".html")
        Journal.info2 (_(u"Fichier HTML temporaire: %s") % chem_temp)
        # f_temp est un handle de fichier (cf. os.open), il faut le
        # convertir en objet file:
        #fich_dest = os.fdopen(f_temp, 'wb')
        # si le fichier source contenait un BOM, on doit le réécrire dans le
        # fichier destination avant le code HTML nettoyé:
        # --> a priori pas nécessaire, ou bien seulement dans certains cas ?
        #if encodage_BOM:
        #    os.write(f_temp, BOM[encodage_BOM])
        # Bidouille à améliorer: on ferme le fichier pour le réouvrir
        # avec l'encodage correspondant à l'original:
        f_temp.close()
##        os.close(f_temp)
        # ouverture en mode append pour écrire après le BOM éventuel:
        fich_dest = codecs.open(chem_temp, 'ab', encodage)
        hn = HTML_Nettoyeur(fich_dest)
        # on ouvre le fichier source avec le codec déduit du BOM, d'une balise
        # META, ou Latin-1 par défaut:
        fich_src = codecs.open(copie_temp, 'rb', encodage)
        try:
            texte_source = fich_src.read(TAILLE_BUFFER)
            while texte_source:
                # tant qu'il y a des données à lire
                # on analyse le code HTML pour le nettoyer
                hn.feed(texte_source)
                # et on lit le bloc de données suivant
                texte_source = fich_src.read(TAILLE_BUFFER)
            hn.close()
        except HTMLParser.HTMLParseError:
            # erreur de syntaxe lors de l'analyse HTML:
            Journal.info2(_(u"Erreur lors du nettoyage HTML"), exc_info=True)
            erreur = str(sys.exc_info()[1])
            return self.resultat_nettoyage_impossible(fichier,
                raison=_(u"Syntaxe HTML incorrecte"), erreur=erreur)
        except ValueError, UnicodeError:
            # si on obtient une de ces 2 erreurs, il s'agit de caractères
            # incorrects vis-à-vis de l'encodage, ou bien d'un double encodage
            # incohérent:
            Journal.info2(_(u"Erreur lors du nettoyage HTML"), exc_info=True)
            erreur = str(sys.exc_info()[1])
            return self.resultat_nettoyage_impossible(fichier,
                raison=_(u"Encodage du fichier incorrect"), erreur=erreur)
        # IL FAUDRAIT AUSSI SUPPRIMER LE FICHIER TEMP SI ERREUR !!
        fich_src.close()
        fich_dest.close()
        if hn.nettoyage:
            resultat = self.resultat_nettoye(fichier)
        else:
            resultat = self.resultat_accepte(fichier)
        # on modifie la date du nouveau fichier pour correspondre à
        # celle d'origine:
        date_fich = os.path.getmtime(copie_temp)
        os.utime(chem_temp, (date_fich, date_fich))
        # on remplace la copie temporaire du fichier d'origine par
        # la version nettoyée:
        # NOTE: sous Windows on est obligé d'effacer d'abord le fichier
        #       d'origine, alors que sous Unix il serait simplement écrasé
        fichier._copie_temp.remove()
        path_temp = path(chem_temp)
        path_temp.rename(copie_temp)
        return resultat


#------------------------------------------------------------------------------
# TESTS
#---------------------
# tests de certaines fonctions si le module est lancé directement et non importé:
if __name__ == '__main__':
    print "----------------------------------------------------------------------------"
    print "Filtre HTML v%s du %s - %s" % (__version__, __date__, __author__)
    print "----------------------------------------------------------------------------"
    print ""
    if len(sys.argv) == 3:
        fich_src  = file(sys.argv[1], 'rb')
        fich_dest = file(sys.argv[2], 'wb')
        hn = HTML_Nettoyeur(fich_dest)
        hn.feed(fich_src.read())
        hn.close()
        fich_src.close()
        fich_dest.close()
        if hn.nettoyage:
            print "Le fichier HTML a ete nettoye."
        else:
            print "Le fichier HTML ne contenait pas d'elements actifs."
    else:
        print "usage: python Filtre_HTML.py <source.html> <dest.html>"
        print ""

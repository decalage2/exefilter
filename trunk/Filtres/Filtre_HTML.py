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
@author: U{Arnaud Kerr�neur<mailto:arnaud.kerreneur(a)dga.defense.gouv.fr>}
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
# 29/10/2004 v0.01 PL: - 1�re version
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

# liste des protocoles autoris�s dans une URL:
PROTOCOLES_OK = ["file", "http", "https", "ftp", "mailto"]

# liste des balises HTML � supprimer:
BALISES_SUPPR = ['script', 'object', 'embed', 'applet', 'xml', 'iframe']

# Byte-Order Markers utilis�s comme ent�tes pour les encodages Unicode ou UTF-8:
BOM = {
    'utf_16_be': codecs.BOM_UTF16_BE,
    'utf_16_le': codecs.BOM_UTF16_LE,
    'utf_8'    : codecs.BOM_UTF8
    }

# nombre d'octets lus � chaque lecture du fichier
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
    """Pour analyser un code HTML et d�terminer si une balise META indique un
    encodage diff�rent de celui du BOM.

    Apr�s analyse compl�te du code HTML, le r�sultat peut �tre lu dans
    l'attribut encodage_META (None ou nom du codec trouv�).
    Si une incoh�rence est d�tect�e (encodages META et BOM diff�rents, ou bien
    deux balises META diff�rentes), une exception ValueError est lev�e.

    @ivar encodage_META: encodage sp�cifi� par une balise META.
    """

    def __init__(self, encodage_BOM=None):
        """constructeur pour un objet HTML_META.

        @param encodage_BOM: nom du codec d�duit du BOM, None sinon.
        @type  encodage_BOM: str, None
        """
        # on initialise d'abord avec le constructeur de la classe de base:
        HTMLParser_base.__init__(self)
        # encodage d�duit du BOM
        self.encodage_BOM  = encodage_BOM
        # encodage sp�cifi� par balise META
        self.encodage_META = None

    def handle_starttag(self, tag, attrs):
        """Pour traiter une balise HTML ouvrante.
        Seules les balises META sont prises en compte.
        """
        # on ne prend en compte que les balises META:
        if tag != 'meta': return
        # flag pour noter si on a un http-equiv=content-type
        http_equiv = False
        # charset vide au d�part
        charset = ""
        for attr in attrs:
            # conversion du nom et de la valeur de l'attribut en minuscule:
            nom_attr = attr[0].lower()
            val_attr = attr[1].lower()
            if nom_attr == "content":
                # on d�coupe suivant les points virgules:
                champs = val_attr.split(';')
                for champ in champs:
                    # on d�coupe ensuite au 1er signe �gal
                    variables = champ.split('=', 1)
                    if len(variables) == 2:
                        if variables[0].strip() == "charset":
                            # s'il y avait d�j� un charset, probl�me
                            if charset != "":
                                raise ValueError, _(u"Double charset dans une balise META")
                            charset = variables[1].strip()
                            Journal.debug(u'trouv� attribut content = "charset=%s"' % charset)
            elif nom_attr == "http-equiv" and val_attr == "content-type":
                http_equiv = True
                Journal.debug(u"trouv� attribut http-equiv = content-type")
        # une fois parcouru tous les attributs, on regarde le r�sultat:
        if http_equiv and charset != "":
            # si un encodage diff�rent de charset �tait d�j� sp�cifi�, incoh�rence:
            if self.encodage_META != None and charset != self.encodage_META:
                raise ValueError, _(u"Double encodage META incoherent.")
            # idem si l'encodage du BOM et celui de la balise META sont diff�rents:
            elif self.encodage_BOM != None and charset != self.encodage_BOM:
                raise ValueError, _(u"Encodages BOM et META incoherents.")
            else:
                self.encodage_META = charset


#==============================================================================
# classe HTML_Nettoyeur
#=======================
class HTML_Nettoyeur(HTMLParser_base):
    """pour nettoyer un code HTML de tout code ex�cutable."""

    def __init__(self, fichier_sortie=sys.stdout, encoding=None):
        """constructeur pour HTML_Nettoyeur.

        fichier_sortie: fichier pour �crire la sortie.
        encoding: codec � utiliser pour d�coder le fichier, None sinon."""
        HTMLParser_base.__init__(self)
        # fichier de sortie (objet file)
        self._fdest = fichier_sortie
        # flag pour indiquer qu'on est en train de supprimer une balise
        self._suppression = False
        # nom de la balise en cours de suppression: "script", "object", ...
        self._balise_suppr = ""
        # flag pour indiquer qu'un nettoyage a eu lieu, False par d�faut
        self.nettoyage = False
        self.encoding = encoding
        # flag pour indiquer qu'une balise META pr�cisant l'encodage a �t�
        # trouv�e, et donc qu'il faut recommencer l'analyse avec le codec
        # indiqu� par self.encoding
        self.meta_encoding = False

    def _supprimer_balise_deb(self, tag):
        """pour d�buter la suppression d'une balise.
        tag: nom de la balise supprim�e."""
        self._suppression = True
        self._balise_suppr = tag
        self._fdest.write(_(u"<!-- balise %s supprimee -->") % tag)
        self.nettoyage = True

    def _supprimer_balise_fin(self, tag):
        """pour terminer la suppression d'une balise.
        tag: nom de la balise supprim�e."""
        if self._suppression and self._balise_suppr == tag:
            self._suppression = False


    def handle_starttag(self, tag, attrs):
        """balise ouvrante quelconque"""
        # si c'est une balise � supprimer, on le marque:
        if tag in BALISES_SUPPR:
            self._supprimer_balise_deb(tag)
        # si on n'est pas en mode suppression, on recopie la balise
        elif not self._suppression:
            # on v�rifie si un des attributs commence par "on..."
            # ou si une valeur d'attribut est une URL d�butant par autre
            # chose que "http:", "ftp:", "mailto:", ...
            # dans ce cas on le supprime
            suppr_attr = False # flag si attributs � supprimer
            attrs_ok = [] # liste des attributs nettoy�s
            attrs_bruts = ""
            for attr in attrs:
                nom_attr = attr[0]
                val_attr = attr[1]
                attr_brut = attr[2]
                if nom_attr.lower().startswith("on"):
                    # Attribut � supprimer: on ne l'ajoute pas
                    # � la liste des attributs nettoy�s.
                    # On note qu'au moins un attribut est supprim�
                    suppr_attr = True
                    Journal.info2(_(u"attribut interdit: %s=...") % nom_attr)
                elif ":" in val_attr:
                    # la valeur contient ":", ce doit �tre
                    # une URL de type "protocole:..." ou "*script:..."
                    # on v�rifie si c'est un protocole autoris�:
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
                    # sinon pas de probl�me, l'attribut est
                    # accept� tel quel
                    attrs_ok.append(attr)
                    attrs_bruts += attr_brut
            # on reconstruit la balise nettoy�e avec les attributs autoris�s:
#/            balise_nettoyee = u"<%s" % tag
#/            for attr in attrs_ok:
#/                balise_nettoyee += u' %s="%s"' % (attr[0], attr[1])
#/            balise_nettoyee += u">"
            balise_nettoyee = u"<%s%s>" % (tag, attrs_bruts)
            if suppr_attr:
                # si au moins un attribut a �t� supprim�, on �crit la balise
                # nettoy�e:
                self._fdest.write(balise_nettoyee)
                self.nettoyage = True
            else:
                self._fdest.write(balise_nettoyee)
#/                # sinon on �crit la balise et ses attributs sous leur forme
#/                # d'origine, pour conserver au maximum la mise en page:
#/                # Mais auparavant, on v�rifie la coh�rence du r�sultat, en
#/                # comptant le nombre de signes "=", qui doit �tre le m�me:
#/                # (permet de d�tecter certains camouflages)
#/                debug(u"balise_nettoyee = %s" % balise_nettoyee)
#/                debug(u"self.get_starttag_text() = %s" % self.get_starttag_text())
#/                starttag_text = self.get_starttag_text()
#/                # parfois get_starttag_text() retourne None, et cela peut lever
#/                # des exceptions... Pour l'�viter:
#/                if not starttag_text: starttag_text = ""
#/                if balise_nettoyee.count("=") != starttag_text.count("="):
#/                    Journal.debug(u"Incoh�rence d�tect�e lors de la reconstruction balise:")
#/                    Journal.debug(u"Nb signes �gal dans balise nettoy�e : %d / balise d'origine: %d"
#/                        % ( balise_nettoyee.count("="), starttag_text.count("=")))
#/                    #raise sgmllib.SGMLParseError, "erreur de reconstruction balise"
#/                    # on �crit alors la balise nettoy�e:
#/                    self._fdest.write(balise_nettoyee)
#/                    self.nettoyage = True
#/                else:
#/                    self._fdest.write(starttag_text)

    def handle_data(self, data):
        """donn�es hors balises"""
        # si on n'est pas en mode suppression, on recopie les donn�es
        if not self._suppression:
            self._fdest.write(data)

    def handle_endtag(self, tag):
        """balise fermante quelconque"""
        # si c'est une balise � supprimer, on la traite:
        if tag in BALISES_SUPPR:
            self._supprimer_balise_fin(tag)
        # si on n'est pas en mode suppression, on recopie la balise
        elif not self._suppression:
            self._fdest.write("</%s>" % tag)

    def handle_charref(self, name):
        """CharRef d�cod�e dans des donn�es entre balises.

        name est la cha�ne du code entre '&#' et ';'.
        """
        # si on n'est pas en mode suppression, on recopie les donn�es
        if not self._suppression:
            self._fdest.write('&#'+name+';')

    def handle_entityref(self, name):
        """EntityRef d�cod�e dans des donn�es entre balises.

        name est la cha�ne du code entre '&' et ';'.
        """
        # si on n'est pas en mode suppression, on recopie les donn�es
        if not self._suppression:
            self._fdest.write('&'+name+';')

    def handle_comment(self, data):
        """Commentaire entre '<!--' et '-->'.
        """
        # si on n'est pas en mode suppression, on recopie les donn�es
        if not self._suppression:
            self._fdest.write('<!--'+data+'-->')

    def handle_decl(self, decl):
        """D�calaration SGML entre '<!' et '>'.
        """
        # si on n'est pas en mode suppression, on recopie les donn�es
        if not self._suppression:
            self._fdest.write('<!'+decl+'>')

    def handle_pi(self, data):
        """Processing instruction SGML entre '<?' et '>'.
        """
        # si on n'est pas en mode suppression, on recopie les donn�es
        if not self._suppression:
            self._fdest.write('<?'+data+'>')


#------------------------------------------------------------------------------
# lire_BOM
#---------------------

def lire_BOM (debut_fichier):
    """Pour d�terminer si le fichier est cod� en Unicode ou UTF-8 en
    regardant s'il commence par un marqueur BOM (Byte Order Marker).
    (sinon employer codec 'latin_1' par d�faut si BOM absent)

    @param debut_fichier: chaine correspondant au d�but du fichier.
    @return: retourne une chaine correspondant au codec � employer.
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

    un objet Filtre sert � reconna�tre le format d'un fichier et �
    nettoyer le code �ventuel qu'il contient. La classe Filtre_HTML
    correspond aux documents HTML.

    @cvar nom: Le nom detaill� du filtre
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

    # date et version d�finies � partir de celles du module
    date = __date__
    version = __version__

    def reconnait_format(self, fichier):
        """analyse le format du fichier, et retourne True s'il correspond
        au format recherch�, False sinon."""
        # En th�orie un fichier HTML bien form� devrait toujours commencer
        # par une balise "<HTML>" et se terminer par "</HTML>".
        # En pratique les navigateurs n'imposent aucune balise particuli�re,
        # m�me un simple fichier texte est affich� comme du HTML.
        # Dans un premier temps on peut v�rifier quand m�me la pr�sence de
        # <HTML> au d�but: ... ou pas.
        #debut = fichier.lire_debut()
        #if debut.startswith("<HTML>"):
        return True

    def nettoyer (self, fichier):
        """Analyse et modifie le fichier pour supprimer tout code
        ex�cutable qu'il peut contenir, si cela est possible.
        Retourne un code r�sultat suivant l'action effectu�e.
        """
        # 1) l'encodage par d�faut pour un fichier HTML est Latin-1
        encodage = "latin_1"

        # 2) on v�rifie si le fichier est cod� en Unicode ou UTF-8 en
        # regardant s'il commence par un marqueur BOM (Byte Order Marker):
        debut = fichier.lire_debut()
        encodage_BOM = lire_BOM(debut)
        if encodage_BOM:
            encodage = encodage_BOM
            Journal.info2 (_(u"encodage d'apr�s le BOM: %s") % encodage_BOM)

        # 3) 1�re passe d'analyse pour d�terminer si une balise META indique un
        # autre encodage:
        h = HTML_META(encodage_BOM)
        # copie temporaire du fichier
        copie_temp = fichier.copie_temp()
        # on l'ouvre avec le codec d�duit du BOM, ou Latin-1 par d�faut
        fich_src = codecs.open(copie_temp, 'rb', encodage)
        try:
            texte_source = fich_src.read(TAILLE_BUFFER)
            while texte_source:
                # tant qu'il y a des donn�es � lire
                # on analyse le code HTML � la recherche de balises META
                h.feed(texte_source)
                # on lit le bloc de donn�es suivant
                texte_source = fich_src.read(TAILLE_BUFFER)
            h.close()
        except HTMLParser.HTMLParseError:
            # erreur de syntaxe lors de l'analyse HTML:
            Journal.info2(_(u"Erreur lors de l'analyse des balises META"), exc_info=True)
            erreur = str(sys.exc_info()[1])
            return self.resultat_analyse_impossible(fichier,
                raison=_(u"Syntaxe HTML incorrecte"), erreur=erreur)
        except ValueError, UnicodeError:
            # si on obtient une de ces 2 erreurs, il s'agit de caract�res
            # incorrects vis-�-vis de l'encodage, ou bien d'un double encodage
            # incoh�rent:
            Journal.info2(_(u"Erreur lors de l'analyse des balises META"), exc_info=True)
            erreur = str(sys.exc_info()[1])
            return self.resultat_analyse_impossible(fichier,
                raison=_(u"Encodage du fichier incorrect"), erreur=erreur)
        except:
            # sinon on remonte l'exception:
            raise
        fich_src.close()
        # on r�cup�re l'encodage fourni par une balise META, si c'est le cas:
        if h.encodage_META:
            encodage = h.encodage_META
            Journal.info2 (_(u"encodage d'apr�s la balise META: %s") % encodage)

        # 4) 2�me passe pour nettoyer le code HTML vers un fichier temporaire
        # Cr�ation d'un fichier HTML temporaire:
        #f_temp, chem_temp = tempfile.mkstemp(suffix=".html", dir=Conteneur.RACINE_TEMP)
##        f_temp, chem_temp = tempfile.mkstemp(suffix=".html",
##            dir=commun.politique.parametres['rep_temp'].valeur)
        f_temp, chem_temp = newTempFile(suffix=".html")
        Journal.info2 (_(u"Fichier HTML temporaire: %s") % chem_temp)
        # f_temp est un handle de fichier (cf. os.open), il faut le
        # convertir en objet file:
        #fich_dest = os.fdopen(f_temp, 'wb')
        # si le fichier source contenait un BOM, on doit le r��crire dans le
        # fichier destination avant le code HTML nettoy�:
        # --> a priori pas n�cessaire, ou bien seulement dans certains cas ?
        #if encodage_BOM:
        #    os.write(f_temp, BOM[encodage_BOM])
        # Bidouille � am�liorer: on ferme le fichier pour le r�ouvrir
        # avec l'encodage correspondant � l'original:
        f_temp.close()
##        os.close(f_temp)
        # ouverture en mode append pour �crire apr�s le BOM �ventuel:
        fich_dest = codecs.open(chem_temp, 'ab', encodage)
        hn = HTML_Nettoyeur(fich_dest)
        # on ouvre le fichier source avec le codec d�duit du BOM, d'une balise
        # META, ou Latin-1 par d�faut:
        fich_src = codecs.open(copie_temp, 'rb', encodage)
        try:
            texte_source = fich_src.read(TAILLE_BUFFER)
            while texte_source:
                # tant qu'il y a des donn�es � lire
                # on analyse le code HTML pour le nettoyer
                hn.feed(texte_source)
                # et on lit le bloc de donn�es suivant
                texte_source = fich_src.read(TAILLE_BUFFER)
            hn.close()
        except HTMLParser.HTMLParseError:
            # erreur de syntaxe lors de l'analyse HTML:
            Journal.info2(_(u"Erreur lors du nettoyage HTML"), exc_info=True)
            erreur = str(sys.exc_info()[1])
            return self.resultat_nettoyage_impossible(fichier,
                raison=_(u"Syntaxe HTML incorrecte"), erreur=erreur)
        except ValueError, UnicodeError:
            # si on obtient une de ces 2 erreurs, il s'agit de caract�res
            # incorrects vis-�-vis de l'encodage, ou bien d'un double encodage
            # incoh�rent:
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
        # on modifie la date du nouveau fichier pour correspondre �
        # celle d'origine:
        date_fich = os.path.getmtime(copie_temp)
        os.utime(chem_temp, (date_fich, date_fich))
        # on remplace la copie temporaire du fichier d'origine par
        # la version nettoy�e:
        # NOTE: sous Windows on est oblig� d'effacer d'abord le fichier
        #       d'origine, alors que sous Unix il serait simplement �cras�
        fichier._copie_temp.remove()
        path_temp = path(chem_temp)
        path_temp.rename(copie_temp)
        return resultat


#------------------------------------------------------------------------------
# TESTS
#---------------------
# tests de certaines fonctions si le module est lanc� directement et non import�:
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

#!/usr/bin/python
# -*- coding: latin-1 -*-
"""
HTMLParser_PL

Ce module contient la classe L{HTMLParser_PL.HTMLParser_PL} permettant
d'analyser un code HTML. Il s'agit d'une version amelioree du module
HTMLParser de la bibliotheque standard de Python 2.4 et 2.5, afin d'obtenir
un comportement plus proche d'Internet Explorer, notamment pour eviter certaines
techniques de camouflage de contenu malveillant.

Projet: U{http://www.decalage.info/python/HTMLParser}

@author: U{Philippe Lagadec<mailto:philippe.lagadec(a)laposte.net>}

@contact: U{Philippe Lagadec<mailto:philippe.lagadec(a)laposte.net>}

@license: PSF (Python Software Foundation) v2
          cf. code source ou http://www.python.org

@version: 1.01
@status: beta
"""

__docformat__ = 'epytext en'

#__author__    = "Philippe Lagadec"
__date__      = "2008-02-25"
__version__   = "1.01"


#------------------------------------------------------------------------------
# LICENCE:

# HTMLParser_PL is based on the HTMLParser source code from Python v2.5

# PYTHON SOFTWARE FOUNDATION LICENSE VERSION 2
#
# 1. This LICENSE AGREEMENT is between the Python Software Foundation
# ("PSF"), and the Individual or Organization ("Licensee") accessing and
# otherwise using this software ("Python") in source or binary form and
# its associated documentation.
#
# 2. Subject to the terms and conditions of this License Agreement, PSF
# hereby grants Licensee a nonexclusive, royalty-free, world-wide
# license to reproduce, analyze, test, perform and/or display publicly,
# prepare derivative works, distribute, and otherwise use Python
# alone or in any derivative version, provided, however, that PSF's
# License Agreement and PSF's notice of copyright, i.e., "Copyright (c)
# 2001, 2002, 2003, 2004, 2005, 2006 Python Software Foundation; All Rights
# Reserved" are retained in Python alone or in any derivative version
# prepared by Licensee.
#
# 3. In the event Licensee prepares a derivative work that is based on
# or incorporates Python or any part thereof, and wants to make
# the derivative work available to others as provided herein, then
# Licensee hereby agrees to include in any such work a brief summary of
# the changes made to Python.
#
# 4. PSF is making Python available to Licensee on an "AS IS"
# basis.  PSF MAKES NO REPRESENTATIONS OR WARRANTIES, EXPRESS OR
# IMPLIED.  BY WAY OF EXAMPLE, BUT NOT LIMITATION, PSF MAKES NO AND
# DISCLAIMS ANY REPRESENTATION OR WARRANTY OF MERCHANTABILITY OR FITNESS
# FOR ANY PARTICULAR PURPOSE OR THAT THE USE OF PYTHON WILL NOT
# INFRINGE ANY THIRD PARTY RIGHTS.
#
# 5. PSF SHALL NOT BE LIABLE TO LICENSEE OR ANY OTHER USERS OF PYTHON
# FOR ANY INCIDENTAL, SPECIAL, OR CONSEQUENTIAL DAMAGES OR LOSS AS
# A RESULT OF MODIFYING, DISTRIBUTING, OR OTHERWISE USING PYTHON,
# OR ANY DERIVATIVE THEREOF, EVEN IF ADVISED OF THE POSSIBILITY THEREOF.
#
# 6. This License Agreement will automatically terminate upon a material
# breach of its terms and conditions.
#
# 7. Nothing in this License Agreement shall be deemed to create any
# relationship of agency, partnership, or joint venture between PSF and
# Licensee.  This License Agreement does not grant permission to use PSF
# trademarks or trade name in a trademark sense to endorse or promote
# products or services of Licensee, or any third party.
#
# 8. By copying, installing or otherwise using Python, Licensee
# agrees to be bound by the terms and conditions of this License
# Agreement.


#------------------------------------------------------------------------------
# HISTORIQUE:
# 01/11/2005 v0.01 PL: - 1ère version
# 04/11/2005 v0.02 PL: - ajout méthode feed()
# 12/01/2007 v1.00 PL: - version 1.00 officielle
# 2008-02-25 v1.01 PL: - ajout licence PSF
#                      - amelioration des regex pour etre plus robuste + tests

#------------------------------------------------------------------------------
# A FAIRE:
# ? passer en mode CDATA dans balises SCRIPT et STYLE ? (cf. specs HTML4)
# ? passer en mode CDATA dans attributs scripts/style ?
# - ajouter des options pour choisir le comportement du parseur
# - traduire en anglais
# - convertir les test en unittest
#------------------------------------------------------------------------------

#=== IMPORTS ==================================================================

# modules standards Python:
import re, htmlentitydefs, sys, codecs
from HTMLParser import HTMLParser, tagfind, attrfind


#=== CONSTANTES ===============================================================

# regex pour trouver des EntityRefs:
# (en théorie un nom d'entité pourrait contenir des tirets ou soulignés, mais
# il n'y en a pas dans la liste de Python)
# Par securite, on limite le nombre de caracteres a 32 dans le nom.
#entityref = re.compile('&([a-zA-Z][a-zA-Z0-9]*);?')
entityref = re.compile('&([a-zA-Z][a-zA-Z0-9]{0,31});?')

# CharRef décimal: &# + 1 à 7 chiffres décimaux + point-virgule optionnel,
# suivi d'un caractère non-chiffre si pas de point-virgule et moins de 7 chiffres
#charref_dec = re.compile('&#([0-9]{1,7});?')
# En fait IE semble lire tous les chiffres fournis, mais génère une erreur
# quand ça dépasse 7 chiffres, donc on limite a 8 et on le verifie dans le code:
#charref_dec = re.compile('&#([0-9]+);?')
charref_dec = re.compile('&#([0-9]{1,8});?')
MAX_CHARREF_DEC = 7

# CharRef hexa: &#x ou &#X + 1 à 6 chiffres hexadécimaux + point-virgule optionnel
# (pas besoin de point-virgule si le caractère suivant n'est pas un chiffre hexa)
#charref_hex = re.compile('&#[xX]([0-9a-fA-F]{1,6});?')
# En fait IE semble lire tous les chiffres fournis, mais génère une erreur
# quand ça dépasse 6 chiffres hexa, donc on limite a 7 et on le verifie dans le
# code:
#charref_hex = re.compile('&#[xX]([0-9a-fA-F]+);?')
charref_hex = re.compile('&#[xX]([0-9a-fA-F]{1,7});?')
MAX_CHARREF_HEX = 6

#=== CLASSES ==================================================================

#------------------------------------------------------------------------------
# classe HTMLParser_PL
#-----------------------

class HTMLParser_PL (HTMLParser):
    """Version corrigée de la classe HTMLParser standard de Python v2.4.x."""

    def feed(self, data):
        """
        Pour transmettre des données à analyser par le parseur HTML.
        Par rapport à la version standard de feed(), celle-ci filtre tous
        les caractères nuls avant de parser les données, comme le fait
        Internet Explorer.
        """
        # on doit a priori distinguer les chaînes str et unicode:
        if isinstance(data, str):
            data = data.replace(chr(0), "")
        elif isinstance(data, unicode):
            data = data.replace(unichr(0), "")
        else:
            raise ValueError
        # ensuite on appelle la méthode feed standard
        HTMLParser.feed(self, data)

    def unescape(self, s):
        """Pour décoder les CharRefs (&#NNN, &#xNNN) et EntityRefs (&amp;, ...)
        dans les attributs d'une balise HTML.
        Remplace et corrige la méthode unescape() de HTMLParser.
        """
        i = 0
        # on convertit la chaîne en unicode si ce n'est pas le cas
        if not isinstance (s, unicode):
            s = unicode(s, 'latin-1')
        resultat = u""
        reste =     s[i:]
        #print "unescape('%s')" % s
        while '&' in reste:
            # on cherche le 1er "&":
            j = reste.find('&')
            resultat += reste[:j]
            reste = reste[j:]
            # on regarde d'abord si c'est un CharRef Hexa:
            m = charref_hex.match(reste)
            if m:
                texte = m.group(1)
                #print 'CharRef hexa: %s' % texte
                # on vérifie qu'il y a au plus 6 chiffres hexa (limite d'IE)
                if len(texte)>MAX_CHARREF_HEX:
                    # sinon on déclenche une exception:
                    self.error("CharRef with more than 6 hex digits")
                # conversion hexa en entier
                code = int(texte, 16)
                # et on convertit en caractère unicode correspondant
                resultat += unichr(code)
                reste = reste[m.end():]
                continue
            # puis si c'est un CharRef Décimal:
            m = charref_dec.match(reste)
            if m:
                texte = m.group(1)
                #print 'CharRef decimal: %s' % texte
                # on vérifie qu'il y a au plus 7 chiffres décimaux (limite d'IE)
                if len(texte)>MAX_CHARREF_DEC:
                    # sinon on déclenche une exception:
                    self.error("CharRef with more than 7 decimal digits")
                # conversion décimal en entier
                code = int(texte)
                # et on convertit en caractère unicode correspondant
                resultat += unichr(code)
                reste = reste[m.end():]
                continue
            # enfin si c'est un EntityRef:
            m = entityref.match(reste)
            if m and (m.group(1) in htmlentitydefs.name2codepoint):
                #print 'EntityRef: %s' % m.group(1)
                code = htmlentitydefs.name2codepoint[m.group(1)]
                resultat += unichr(code)
                reste = reste[m.end():]
                continue
            # sinon on avance simplement d'un caractère:
            else:
                resultat += '&'
                reste = reste[1:]
        return resultat + reste

    def parse_starttag(self, i):
        """Remplace et corrige la méthode parse_starttag() de HTMLParser.
        Ajoute à chaque attribut transmis à la méthode handle_starttag un
        troisième item contenant la valeur d'origine de l'attribut, avant
        conversion des CharRefs/EntityRefs.
        """
        # les lignes modifiées par rapport à l'original sont marquées
        # entre <MODIF_PL> et </MODIF_PL>
        self.__starttag_text = None
        endpos = self.check_for_whole_start_tag(i)
        if endpos < 0:
            return endpos
        rawdata = self.rawdata
        self.__starttag_text = rawdata[i:endpos]

        # Now parse the data between i+1 and j into a tag and attrs
        attrs = []
        match = tagfind.match(rawdata, i+1)
        assert match, 'unexpected call to parse_starttag()'
        k = match.end()
        self.lasttag = tag = rawdata[i+1:k].lower()

        while k < endpos:
            m = attrfind.match(rawdata, k)
            if not m:
                break
            attrname, rest, attrvalue = m.group(1, 2, 3)
            if not rest:
                attrvalue = None
            elif attrvalue[:1] == '\'' == attrvalue[-1:] or \
                 attrvalue[:1] == '"' == attrvalue[-1:]:
                attrvalue = attrvalue[1:-1]
                attrvalue = self.unescape(attrvalue)
            # <MODIF_PL>
            # on doit convertir les CharRefs / EntityRefs même si la valeur de
            # l'attribut n'est pas entre guillemets (comme IE):
            else:
                attrvalue = self.unescape(attrvalue)
            # on ajoute à chaque attribut sa valeur non modifiée, pour une
            # reconstruction la plus fidèle possible:
            attr_raw = m.group()
            attrs.append((attrname.lower(), attrvalue, attr_raw))
            #attrs.append((attrname.lower(), attrvalue))
            # </MODIF_PL>
            k = m.end()

        end = rawdata[k:endpos].strip()
        if end not in (">", "/>"):
            lineno, offset = self.getpos()
            if "\n" in self.__starttag_text:
                lineno = lineno + self.__starttag_text.count("\n")
                offset = len(self.__starttag_text) \
                         - self.__starttag_text.rfind("\n")
            else:
                offset = offset + len(self.__starttag_text)
            self.error("junk characters in start tag: %r"
                       % (rawdata[k:endpos][:20],))
        if end.endswith('/>'):
            # XHTML-style empty tag: <span attr="value" />
            self.handle_startendtag(tag, attrs)
        else:
            self.handle_starttag(tag, attrs)
            if tag in self.CDATA_CONTENT_ELEMENTS:
                self.set_cdata_mode()
        return endpos


#==============================================================================
# AUTO-TEST du module
#======================

if __name__ == "__main__":
    print "Auto-test du module %s:\n" % sys.argv[0]

    if sys.platform in ['darwin', 'linux2']:
        sys.stdout = codecs.EncodedFile(sys.stdout, "latin-1", "utf-8")
    elif sys.platform == 'win32':
        sys.stdout = codecs.EncodedFile(sys.stdout, "latin-1", "cp850")

    class htest (HTMLParser_PL):
        def handle_starttag(self, tag, attrs):
            print "Balise: <%s" % tag.upper()
            for attr in attrs:
                print "     %s = '%s'" % (attr[0], attr[1])

    def test(chaine):
        print "-"*79
        print chaine
        h = htest()
        h.feed(chaine)
        h.close()

    test("<body onload=\"alert('boum!')&#34\">")
    test("<test attr=&#65>")
    test("<test attr=&#65;>")
    test("<test attr='&#65'>")
    test("<test attr='&#65;'>")
    test("<test attr='&amp#65;'>")

    class htest2 (HTMLParser_PL):
        def handle_starttag(self, tag, attrs):
            # on retient juste la valeur du 1er attribut
            if attrs:
                if attrs[0][0] == "attr":
                    self.attr = attrs[0][1]

    def test_charref(texte, code):
        h = htest2()
        h.feed(texte)
        h.close()
        if h.attr != unichr(code):
            print "erreur pour %s : attr = unichr(%d)" % (texte, ord(h.attr[0]))

    def test_charref2(ref, code):
        test_charref("<test attr=%s>" % ref, code)
        test_charref("<test attr='%s'>" % ref, code)
        test_charref('<test attr="%s">' % ref, code)
        test_charref("<test attr=%s;>" % ref, code)
        test_charref("<test attr='%s;'>" % ref, code)
        test_charref('<test attr="%s;">' % ref, code)

    print "Test des CharRefs pour les codes 0 à 1024..."
    for val in xrange(0, 1024):
        test_charref2("&#%d" % val, val)
        for x1 in ['x', 'X']:
            for x2 in ['x', 'X']:
                ref = "&#%s%%%s" % (x1, x2)
                ref = ref % val
                test_charref2(ref, val)

    print "Test des EntityRefs..."
    n2c = htmlentitydefs.name2codepoint
    for val in n2c:
        #print "&%s = %d" % (val, n2c[val])
        test_charref2("&%s" % val, n2c[val])

    class htest_script (HTMLParser_PL):
        """Pour détecter "javascript:" dans un attribut"""

        def handle_starttag(self, tag, attrs):
            for attr in attrs:
                if attr[1].lower().startswith("javascript:"):
                    self.script_detecte = True

    def test_script(texte):
        h = htest_script()
        h.feed(texte)
        h.close()
        if not h.script_detecte:
            print "erreur pour %s" % texte

    def test_script_exc(texte):
        try:
            test_script(texte)
            print "erreur pour %s !" % texte
        except:
            pass

    # ces tests sont OK s'ils detectent le script sans generer d'exception:
    print "Test de détection de script..."
    test_script("<img src=javascript:alert(1)>")
    test_script("<img src=javascript&#58alert(1)>")
    test_script("<img src=javascript&#58;alert(1)>")
    test_script("<img src=javascript&#x3A;alert(1)>")
    test_script("<img src=javascript&#X3a;alert(1)>")
    test_script("<img src=javascript&#0000058alert(1)>")
    test_script("<img src=javascript&#0000058;alert(1)>")
    test_script("<img src=javascript&#x00003A;alert(1)>")
    test_script("<img src=javascript&#X00003a;alert(1)>")

    # ces tests sont OK s'ils generent une exception:
    test_script_exc("<img src=javascript&#00000058alert(1)>")
    test_script_exc("<img src=javascript&#00000058;alert(1)>")
    test_script_exc("<img src=javascript&#x000003A;alert(1)>")
    test_script_exc("<img src=javascript&#X000003a;alert(1)>")

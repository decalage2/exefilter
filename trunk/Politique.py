#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
"""
Politique - ExeFilter

Le module Politique permet de charger, stocker et gérer des politiques de filtrage,
à l'aide de la classe L{Politique.Politique}.

Ce fichier fait partie du projet ExeFilter.
URL du projet: http://admisource.gouv.fr/projects/exefilter

@organization: DGA/CELAR
@author: U{Philippe Lagadec<mailto:philippe.lagadec(a)laposte.net>}
@author: U{Tanguy Vinceleux<mailto:tanguy.vinceleux(a)dga.defense.gouv.fr>}

@contact: U{Philippe Lagadec<mailto:philippe.lagadec(a)laposte.net>}

@copyright: DGA/CELAR 2004-2007
@license: CeCILL (open-source compatible GPL) - cf. code source ou fichier LICENCE.txt joint

@version: 1.01

@status: beta
"""
__docformat__ = 'epytext en'

#__author__    = "Philippe Lagadec, Tanguy Vinceleux (DGA/CELAR)"
__date__      = "2007-09-18"
__version__   = "1.01"

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
# 09/03/2005 v0.01 PL: - 1ère version, reprise du code charger_filtres de Sas.py
# 2005-2007     PL,TV: - nombreuses evolutions
# 12/01/2007 v1.00 PL: - version 1.00 officielle
# 2007-09-18 v1.01 PL: - ajout licence CeCILL
# 2007-10-08       PL: - tri des sections et parametres dans ecrire_html

#------------------------------------------------------------------------------
# A FAIRE:
# - sauver la politique dans le fichier indiqué, s'il n'existe pas ?
#------------------------------------------------------------------------------

#=== IMPORTS ==================================================================
import sys, codecs
import ConfigParser
import os

# modules d'ExeFilter:
from commun import *
import Filtres, Parametres, ExeFilter

# third party modules:
import thirdparty.HTML as HTML

#=== VARIABLES GLOBALES =======================================================


#=== CONSTANTES ===============================================================

# section des paramètres globaux du logiciel dans les fichiers de config
SECTION_EXEFILTER = "ExeFilter"


#=== CLASSES ==================================================================

#------------------------------------------------------------------------------
# classe Politique
#-------------------

class Politique:
    """
    Classe permettant de manipuler une politique de filtrage, en y activant
    les filtres voulus avec leurs paramètres, ainsi que certains paramètres
    globaux du moteur de filtrage.

    @ivar filtres: liste d'objets L{Filtre<Filtres.Filtre.Filtre>} de la politique,
        chacun possédant ses L{Parametres}.
    @ivar parametres: dictionnaire des L{Parametres} globaux de la politique.
    @ivar dico_filtres: dictionnaire des filtres, indexé suivant les extensions
        de fichiers acceptées par chaque filtre.
    """

    def __init__(self, config=None, nom="sans nom"):
        """
        Constructeur d'objet Politique.

        config peut être:
            - un objet ConfigParser
            - un nom de fichier conforme à la syntaxe ConfigParser (.INI)
            - un objet file ouvert en lecture
            - ou bien une liste d'objets d'un de ces 3 types
        """
        self.nom = nom
        # on commence par charger la liste des classes de filtres disponibles,
        # en appelant la fonction du package Filtres qui va bien:
        classes_filtres = Filtres.classes_filtres()
        # on instancie chaque classe dans un objet filtre
        self.filtres = []
        for filtre in classes_filtres:
            self.filtres.append( filtre(self) )
        # les paramètres globaux d'ExeFilter sont vides par défaut:
        self.parametres = {}
        # on y importe les paramètres du module ExeFilter:
        Parametres.importer(self.parametres, ExeFilter.parametres)
        # ensuite on applique la config indiquée:
        if config is not None:
            self.lire_config(config)
        else:
            self.creer_dico_filtres()


    def lire_config (self, config):
        """Pour mettre à jour la configuration d'une politique.

        config peut être:
            - un objet ConfigParser
            - un nom de fichier conforme à la syntaxe ConfigParser (.INI)
            - un objet file ouvert en lecture
            - ou bien une liste d'objets d'un de ces 3 types
        """
        if isinstance(config, list):
            # si config est une liste, on la parcourt de façon récursive:
            for item in config:
                self.lire_config(item)
        else:
            # on parcourt les filtres, et on lit la section correspondant à
            # chacun (section = nom du filtre), pour mettre à jour ses
            # paramètres:
            for filtre in self.filtres:
                Parametres.lire_config(filtre.parametres, config,
                    filtre.nom_classe)
            # puis on lit les paramètres globaux d'ExeFilter:
            Parametres.lire_config(self.parametres, config, SECTION_EXEFILTER)
        self.creer_dico_filtres()


    def journaliser(self):
        """Pour ajouter la liste des filtres employés au journal de débogage,
        avec leur version."""
        Journal.info2("Politique: %s" % self.nom)
        for filtre in self.filtres:
            Journal.info2("- %s v%s du %s" % (filtre.nom_classe, filtre.version,
                                             filtre.date))

    def creer_dico_filtres(self):
        """Pour créer un dictionnaire de filtres indexé suivant les extensions
        de fichiers acceptées par chaque filtre. Ce dictionnaire doit être recréé
        à chaque modification de la politique. Il est ensuite accessible en
        tant qu'attribut dico_filtres.

        @return: dictionnaire de filtres
        @rtype : dictionnaire
        """
        self.dico_filtres = {}    # dictionnaire des filtres de formats par extension
        for filtre in self.filtres:
            # on parcourt la liste des extensions de chaque filtre:
            for ext in filtre.extensions:
                # conversion en minuscules de l'extension, pour que la
                # comparaison soit toujours correcte (cf. Fichier.py)
                ext = ext.lower()
                # on cherche s'il y a déjà des filtres avec cette extension
                # dans le dictionnaire:
                if ext in self.dico_filtres:
                    # si oui on ajoute le filtre à la liste correspondante
                    self.dico_filtres[ext].append(filtre)
                else:
                    # si non on crée cette liste avec ce filtre et on
                    # l'ajoute au dictionnaire
                    self.dico_filtres[ext] = [filtre]
        # on retourne le dictionnaire
        return self.dico_filtres

    def ecrire_fichier (self, fichier, params_globaux=True, params_filtres=True,
                        selection_filtres=False, selection_parametres=False):
        """Pour écrire la politique dans un fichier de configuration.

        @param fichier: fichier à écrire
        @type  fichier: nom de fichier ou objet file

        @param params_globaux: indique si les paramètres globaux doivent être
        inclus (oui par défaut)
        @type  params_globaux: bool
        @param params_filtres: indique si les paramètres des filtres doivent être
        inclus (oui par défaut)
        @type  params_filtres: bool
        @param selection_filtres: si ce paramètre contient une chaîne, seuls les
        filtres avec ce paramètre ayant une valeur True seront inclus.
        Si c'est un tuple, on vérifie la valeur indiquée, exemple: ("format_autorise", False).
        (False par défaut)
        @type  selection_filtres: bool, str, tuple
        @param selection_parametres: si ce paramètre contient une liste de
        chaînes, seuls les paramètres des  filtres dont le nom est listé seront
        inclus, par exemple ["format_autorise"]. (False par défaut)
        @type  selection_parametres: bool, list
        """
        # on crée d'abord un objet ConfigParser
        cfg = ConfigParser.SafeConfigParser()
        if params_globaux:
            # on y stocke les paramètres globaux
            Parametres.ecrire_config(self.parametres, cfg, SECTION_EXEFILTER)
        if params_filtres:
            # puis ceux de chaque filtre
            for filtre in self.filtres:
                inclure_filtre = True # par défaut on inclut tous les filtres
                if selection_filtres:
                    inclure_filtre = False # ...sauf si sélection
                    # si on veut sélectionner les filtres suivant un paramètre,
                    # on doit d'abord vérifier que le filtre possède ce paramètre
                    if isinstance(selection_filtres, tuple):
                        # si c'est un tuple on vérifie le paramètre et sa valeur
                        nom_filtre = selection_filtres[0]
                        valeur = selection_filtres[1]
                    else:
                        # si c'est une chaîne on vérifie que le paramètre est vrai
                        nom_filtre = selection_filtres
                        valeur = True
                    if nom_filtre in filtre.parametres:
                        if filtre.parametres[nom_filtre].valeur == valeur:
                            inclure_filtre = True
                if inclure_filtre:
                    if selection_parametres == False:
                        # on prend tous les paramètres du filtre
                        dico_params = filtre.parametres
                    else:
                        # sinon on sélectionne les paramètres indiqués
                        dico_params = {}
                        for param in selection_parametres:
                            if param in filtre.parametres:
                                dico_params[param] = filtre.parametres[param]
                    # puis on écrit le filtre dans la config, à la bonne section:
                    if len(dico_params)>0:
                        Parametres.ecrire_config(dico_params, cfg, filtre.nom_classe)
        # pour finir on écrit le tout dans le fichier indiqué
        Parametres.ecrire_fichier(cfg, fichier)

    def ecrire_html (self, nom_fichier_html):
        """Pour écrire un fichier HTML décrivant en détails chaque paramètre de
        la politique."""
        # table with 5 columns and header row
        t = HTML.Table(header_row = (_('Code Paramètre'), _('Nom'), _('Description'),
            _('Valeur'), _('Valeur par défaut')))
        # row for global section head:
        t.rows.append(HTML.TableRow(('<b>section [%s]</b>' % SECTION_EXEFILTER,
            '', '', '', ''), bgcolor='cyan'))
        # fonction pour comparer 2 noms de parametres afin de trier la liste:
        cmp_params = lambda p1,p2: cmp(p1.code.lower(), p2.code.lower())
        for p in sorted(self.parametres.itervalues(), cmp=cmp_params):
            t.rows.append(('<b>%s</b>' % p.code, p.nom, p.description, str(p), str(p.valeur_defaut)))
        # fonction pour comparer 2 noms de filtres afin de trier la liste:
        cmp_filtres = lambda f1,f2: cmp(f1.nom_classe.lower(), f2.nom_classe.lower())
        for filtre in sorted(self.filtres, cmp=cmp_filtres):
            # row for section head:
            t.rows.append(HTML.TableRow(('<b>section [%s]</b>' % filtre.nom_classe,
                '', '', '', ''), bgcolor='cyan'))
            for p in sorted(filtre.parametres.itervalues(), cmp=cmp_params):
                t.rows.append(('<b>%s</b>' % p.code, p.nom, p.description, str(p), str(p.valeur_defaut)))
        f = open(nom_fichier_html, "w")
        f.write('<FONT FACE="Arial, sans-serif">\n')
        f.write(str(t))
        f.write('</FONT>\n')
        f.close()

##        f = codecs.open(nom_fichier_html, "w", "latin_1")
##        f.write("<HTML>")
##        f.write('<table border=1 WIDTH="100%" BGCOLOR="#FFFFFF">')
##        f.write('<tr BGCOLOR="#FFCC99">')
##        f.write(u'<td><center><b>Code Paramètre</b></center></td>')
##        f.write('<td><center><b>Nom</b></center></td>')
##        f.write('<td><center><b>Description</b><center></td>')
##        f.write('<td><center><b>Valeur</b><center></td>')
##        f.write(u'<td><center><b>Valeur par défaut</b><center></td>')
##        f.write('</tr>')
##        f.write('<tr BGCOLOR="#FFFF00">')
##        f.write('<td><center><b>section [%s]</b></center></td>' % SECTION_EXEFILTER)
##        f.write('</tr>')
##        # fonction pour comparer 2 noms de parametres afin de trier la liste:
##        cmp_params = lambda p1,p2: cmp(p1.code.lower(), p2.code.lower())
##        for p in sorted(self.parametres.itervalues(), cmp=cmp_params):
##            f.write('<tr BGCOLOR="#FFFFFF">')
##            f.write(u'<td><b>%s</b></td>' % p.code)
##            f.write(u'<td>%s</td>' % unistr(p.nom))
##            f.write(u'<td>%s</td>' % unistr(p.description))
##            f.write(u'<td>%s</td>' % unistr(str(p)))
##            f.write(u'<td>%s</td>' % unistr(str(p.valeur_defaut)))
##            f.write('</tr>')
##        # fonction pour comparer 2 noms de filtres afin de trier la liste:
##        cmp_filtres = lambda f1,f2: cmp(f1.nom_classe.lower(), f2.nom_classe.lower())
##        for filtre in sorted(self.filtres, cmp=cmp_filtres):
##            f.write('<tr BGCOLOR="#FFFF00">')
##            f.write('<td><center><b>section [%s]</b></center></td>' % filtre.nom_classe)
##            f.write('</tr>')
##            for p in sorted(filtre.parametres.itervalues(), cmp=cmp_params):
##                f.write('<tr BGCOLOR="#FFFFFF">')
##                f.write(u'<td><b>%s</b></td>' % p.code)
##                f.write(u'<td>%s</td>' % unistr(p.nom))
##                f.write(u'<td>%s</td>' % unistr(p.description))
##                f.write(u'<td>%s</td>' % unistr(str(p)))
##                f.write(u'<td>%s</td>' % unistr(str(p.valeur_defaut)))
##                f.write('</tr>')
##        f.write('</table>')
##        f.write("</HTML>")
##        f.close()


#=== PROGRAMME PRINCIPAL (test) ===============================================

if __name__ == "__main__":
    print "-----------------------------"
    print "TEST DU MODULE Politique.py:"
    print "-----------------------------"
    print ""

    print "creation d'une config de test avec rep_temp=TEST."
    c = ConfigParser.SafeConfigParser()
    c.add_section(SECTION_EXEFILTER)
    c.set(SECTION_EXEFILTER, "rep_temp", "TEST")

    print "creation d'une politique p avec cette config."
    p = Politique()
    p.ecrire_html("Politique.html")
    p.lire_config(c)

    print "ecriture de cette politique p dans un fichier:"
    p.ecrire_fichier("test_Politique.cfg")
    print "-------------------------------------------------"
    import sys
    p.ecrire_fichier(sys.stdout)
    print "-------------------------------------------------"

    print "creation d'une politique p2 en lisant le fichier de config."
    p2 = Politique("test_Politique.cfg")
    if p2.parametres['rep_temp'].valeur == 'TEST':
        print "OK, le parametre modifie a ete pris en compte."
    else:
        print "NOK, le parametre modifie n'a pas ete pris en compte !"

    print "creation d'une politique p3 sans lire le fichier de config."
    p3 = Politique()
    p3.ecrire_fichier(sys.stdout)
    if p3.parametres['rep_temp'].valeur == 'TEST':
        print "NOK, le parametre modifie dans p2 a ete conserve !"
    else:
        print "OK, on a bien tous les parametres par defaut."

    print "modif de la politique p3 pour ajouter parametre specifique_utilisateur"
    print "a certains filtres."
    for filtre in p3.filtres:
        # on sélectionne les filtres Microsoft:
        if "MS" in filtre.nom:
            p = Parametres.Parametre("specifique_utilisateur", bool, valeur_defaut=True)
            p.ajouter(filtre.parametres)
    print "Parametres globaux uniquement:"
    print "-------------------------------------------------"
    p3.ecrire_fichier(sys.stdout, params_filtres=False)
    print "-------------------------------------------------"
    print "Parametres filtres uniquement:"
    print "-------------------------------------------------"
    p3.ecrire_fichier(sys.stdout, params_globaux=False)
    print "-------------------------------------------------"
    print "Parametres filtres specifique_utilisateur uniquement:"
    print "-------------------------------------------------"
    p3.ecrire_fichier(sys.stdout, params_globaux=False,
        selection_filtres="specifique_utilisateur")
    print "-------------------------------------------------"
    print "Parametres tous filtres format_autorise uniquement:"
    print "-------------------------------------------------"
    p3.ecrire_fichier(sys.stdout, params_globaux=False,
        selection_parametres=["format_autorise"])
    print "---------------------------------------------------------"
    print "Parametres filtres format_autorise=False uniquement:"
    print "---------------------------------------------------------"
    # on interdit les filtres PDF et JPEG
    for filtre in p3.filtres:
        if filtre.nom in ["Document PDF", "Fichier Image JPEG"]:
            filtre.parametres["format_autorise"].set(False)
    # ensuite on ne veut que ces filtres interdits dans la config:
    p3.ecrire_fichier(sys.stdout, params_globaux=False,
        selection_filtres=("format_autorise", False),
        selection_parametres=["format_autorise"])
    print "-------------------------------------------------"

    import os
    os.remove("test_Politique.cfg")



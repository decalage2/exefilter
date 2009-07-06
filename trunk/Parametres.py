#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
"""
Parametres - ExeFilter

Le module Parametres permet de g�rer les param�tres des diff�rents modules
et filtres, gr�ce � la classe L{Parametres.Parametre}.

Les param�tres d'un filtre doivent �tre regroup�s dans un dictionnaire index�
suivant les codes des param�tres, et manipul�s gr�ce aux fonctions de ce module.

Ce fichier fait partie du projet ExeFilter.
URL du projet: http://admisource.gouv.fr/projects/exefilter

@organization: DGA/CELAR
@author: U{Philippe Lagadec<mailto:philippe.lagadec(a)laposte.net>}

@contact: U{Philippe Lagadec<mailto:philippe.lagadec(a)laposte.net>}

@copyright: DGA/CELAR 2004-2008
@copyright: NATO/NC3A 2008 (modifications PL apres v1.1.0)

@license: CeCILL (open-source compatible GPL)
          cf. code source ou fichier LICENCE.txt joint

@version: 1.02

@status: beta
"""
#==============================================================================
__docformat__ = 'epytext en'

__date__    = "2008-03-24"
__version__ = "1.02"

#------------------------------------------------------------------------------
# LICENCE pour le projet ExeFilter:

# Copyright DGA/CELAR 2004-2008
# Copyright NATO/NC3A 2008 (PL changes after v1.1.0)
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
# 30/09/2005 v0.01 PL: - 1�re version
# 12/10/2005 v0.02 PL: - ajout et correction de quelques commentaires
#                      - modif compl�te des fonctions, pour permettre
#                        l'utilisation d'objets ConfigParser ou de fichiers
#                      - fonction ajouter_parametre transform�e en m�thode
# 12/01/2007 v1.00 PL: - version 1.00 officielle
# 2007-09-18 v1.01 PL: - ajout licence CeCILL
# 2008-03-27 v1.02 PL: - bug corrige dans Parametre.set

#------------------------------------------------------------------------------
# A FAIRE:
# + ajouter gestion de type=list, pour les listes d'extensions, avec conversion
#   de cha�nes en splittant suivant les virgules + strip espaces
# + ajouter attribut valeurs_possibles=None/liste, avec v�rif dans set()
# + v�rifier si p1=p2 fait bien une recopie de l'objet et non pas juste de la
#   r�f�rence, sinon il faudra utiliser le module copy
# ? ajouter attribut valeurs_restrictives = "croissantes"/"decroissantes" ou
#   True/False + m�thodes pour pouvoir comparer + moyen pour fusionner en ne
#   gardant que les params les + restrictifs ?
# - fonction reinit pour appliquer reinit sur chaque param d'un dico
# - mettre � jour docstring en utilisant mieux les fonctions d'epydoc, et
#   d�clarer les constantes.
#------------------------------------------------------------------------------

#=== IMPORTS ==================================================================
import sys
import ConfigParser
import os, copy

#=== VARIABLES GLOBALES =======================================================


#=== CONSTANTES ===============================================================

__doc__ += """
@var VALEURS_VRAIES: valeurs pouvant �tre utilis�es pour un param�tre bool True
@var VALEURS_FAUSSES: valeurs pouvant �tre utilis�es pour un param�tre bool False
"""
# valeurs pour convertir une cha�ne en bool�en (toujours en minuscules)
VALEURS_VRAIES  = ["1", "oui", "o", "yes", "y", "vrai", "vraie", "v", "t", "true", "on"]
VALEURS_FAUSSES = ["0", "non", "n", "no", "faux", "fausse", "f", "false", "off"]

#=== CLASSES ==================================================================

#------------------------------------------------------------------------------
# classe Parametre
#-------------------

class Parametre:
    """
    classe permettant de g�rer un param�tre avec une valeur.

    @ivar code: nom court utilis� pour indexer un dictionnaire de param�tres,
          et pour utiliser ce param�tre dans un fichier de configuration.
          Doit �tre en minuscules, sans espaces et sans accents.
          Exemple: "supprimer_macros"
    @type code: str, unicode

    @ivar nom: Nom simple d�crivant le param�tre, utilisable par exemple
          dans une IHM, et comme commentaire dans un fichier de config.
          Exemple: "Supprimer les macros"
    @type nom: str, unicode

    @ivar description: (optionnel) Description plus longue et d�taill�e
          du param�tre, utilisable comme aide contextuelle dans l'IHM et
          comme commentaire dans un fichier de config.
          Exemple: "Les macros peuvent contenir du code malveillant."
    @type description: str, unicode

    @ivar type: classe Python de la valeur, par exemple bool, str, int, list, ...
    @type type: classe Python

    @ivar valeur: valeur du param�tre, doit correspondre au type.

    @ivar valeur_defaut: valeur par d�faut du param�tre
    """

    def __init__ (self, code, type, nom="", description="", valeur=None,
                  valeur_defaut=None):
        """Constructeur d'objet Parametre.
        (cf. classe Parametre pour la description des attributs)

        code et type sont obligatoires.
        """
        self.code = code
        self.nom = nom
        self.description = description
        self.type = type
        # conversion de la valeur suivant le type, au cas o�:
        self.valeur_defaut = type(valeur_defaut)
        # on doit initialiser la valeur � None, pour set():
        self.valeur = None
        self.set(valeur)

##    def __set__(self, instance, value):
##        """Pour fixer la valeur d'un param�tre, avec la syntaxe simple
##        Parametre = valeur
##        Cette m�thode convertit automatiquement la valeur suivant le
##        type d�clar� du param�tre.
##        """
##        self.valeur = self.type(value)

    def set(self, valeur):
        """Pour fixer la valeur d'un param�tre.
        Cette m�thode convertit automatiquement la valeur suivant le
        type d�clar� du param�tre.

            - Si le type est bool et que la valeur est une cha�ne les valeurs
            sp�ciales suivantes sont prises en compte:
                - True  = 1, oui, O, yes, Y, T, True, on, ...
                - False = 0, non, N, no, F, False, off, ...
                - (cf. constantes L{Parametres.VALEURS_VRAIES} et
                    L{Parametres.VALEURS_FAUSSES})

            - Si c'est un autre type (int, str, ...) la conversion automatique du
            type est employ�e.

            - Si la valeur est None, la valeur par d�faut est employ�e
                si la valeur d'origine est aussi None (1�re initialisation)
                (sinon pas de modification)
        """
        # si aucune valeur fournie et qu'il n'y en avait pas d�j�,
        # on prend la valeur par d�faut:
        if valeur == None:
            if self.valeur == None:
                self.valeur = self.valeur_defaut
        else:
            # si la valeur est une cha�ne (str ou unicode) et que le
            # param�tre est un bool�en, conversion:
            if self.type == bool:
                if isinstance(valeur, str) or isinstance(valeur, unicode):
                    if valeur.strip().lower() in VALEURS_VRAIES:
                        self.valeur = True
                    elif valeur.strip().lower() in VALEURS_FAUSSES:
                        self.valeur = False
                else:
                    self.valeur = bool(valeur)
            else:
                # sinon on utilise la conversion automatique du type
                # d'objet correspondant au param�tre:
                self.valeur = self.type(valeur)


    def ajouter (self, dico_parametres):
        """Pour ajouter l'objet Parametre au dictionnaire dico_parametres.

        Exemple::
            Parametre("supprimer_macros", bool, nom="Supprimer les macros",
                valeur_defaut=True).ajouter(Filtre_Word.parametres)
        """
        # ATTENTION: ici on ne fait que recopier une r�f�rence � l'objet
        # Parametre dans le dictionnaire. Si on l'ajoute � plusieurs dicos,
        # l'objet sera partag� entre tous les dicos.
        dico_parametres[self.code] = self


    def reinit(self):
        """Pour r�initialiser le param�tre � sa valeur par d�faut.
        """
        self.valeur = self.valeur_defaut


    def __str__(self):
        """Convertit la valeur du param�tre en cha�ne, en 1 ou 0 si c'est
        un bool.

        exemple d'utilisation: print str(parametre["activer_filtre"])
        """
        if self.type == bool:
            if self.valeur: return "1"
            else: return "0"
        else:
            return str(self.valeur)

    def debug(self):
        """Retourne une cha�ne d�crivant compl�tement le param�tre
        et ses attributs, utile surtout pour le d�bogage."""
        return "%s = %s\n" % (self.code, repr(self.valeur)) + \
               "- nom: %s\n" % self.nom + \
               "- description: %s\n" % self.description + \
               "- type: %s\n" % str(self.type) + \
               "- valeur par defaut: %s" % repr(self.valeur_defaut)


#=== FONCTIONS ================================================================

#------------------------------------------------------------------------------
# importer
#---------------------

def importer (dico_parametres, nouveaux_parametres):
    """Pour importer les valeurs du dictionnaire nouveaux_parametres
    dans le dictionnaire dico_parametres.
    nouveaux_parametres doit contenir des valeurs index�es par
    les codes de param�tres, ou bien des objets Parametre.
    """
    for code in nouveaux_parametres:
        valeur = nouveaux_parametres[code]
        if isinstance (valeur, Parametre):
            # on utilise le module copy pour dupliquer le param�tre, car sinon
            # on ne recopie qu'une r�f�rence au m�me param�tre:
            dico_parametres[code] = copy.deepcopy(valeur)
        else:
            dico_parametres[code].set(valeur)
    #Ancienne version, avec nouveaux_parametres un dico de Parametre
    #dico_parametres.update(nouveaux_parametres)

#------------------------------------------------------------------------------
# lire_config
#---------------------

def lire_config (dico_parametres, config, section):
    """Pour mettre � jour les valeurs du dictionnaire dico_parametres,
    en lisant soit:
        - un fichier de configuration au format INI, dans la section indiqu�e,
          fourni sous forme d'objet file ou le nom du fichier
        - un objet (Raw)ConfigParser

    Si un param�tre du fichier n'existe pas dans dico_parametres, il est
    simplement ignor�.

    config    : nom de fichier � lire, objet file, ou ConfigParser
    section : cha�ne
    """
    if isinstance(config, ConfigParser.RawConfigParser):
        # config est un objet (Raw)ConfigParser
        cfg = config
    else:
        # on cr�e un ConfigParser vide:
        cfg = ConfigParser.SafeConfigParser()
        if isinstance(config, str) or isinstance(config, unicode):
            # config est un nom de fichier
            f = file(config, 'r')
            cfg.readfp(f)
            f.close()
        elif isinstance(config, file):
            # config est un fichier d�j� ouvert
            cfg.readfp(config)
        else:
            # sinon c'est une erreur
            raise TypeError
    # ensuite on peut exploiter la config lue, si la section demand�e est
    # pr�sente:
    if cfg.has_section(section):
        for code, valeur in cfg.items(section):
            if code in dico_parametres:
                dico_parametres[code].set(valeur)


#------------------------------------------------------------------------------
# ecrire_config
#---------------------

def ecrire_config (dico_parametres, config, section):
    """Pour �crire les valeurs du dictionnaire dico_parametres dans
    un objet ConfigParser, dans la section indiqu�e.
    Si la section existait d�j�, elle est simplement mise � jour.

    @param config: objet ConfigParser � �crire
    @param section: cha�ne
    """
    if not config.has_section(section):
        config.add_section(section)
    for code in dico_parametres:
        config.set(section, code, str(dico_parametres[code]))

def lire_fichier(config, fichier):
    """Pour lire un fichier dans un objet ConfigParser.

    @param config: objet ConfigParser � �crire
    @param fichier: fichier � lire
    @type  fichier: nom de fichier ou objet file
    """
    if isinstance(fichier, file):
        # directement si c'est un objet file
        config.readfp(fichier)
    else:
        # sinon on ouvre le fichier
        f = file(fichier)
        config.readfp(f)
        f.close()

def ecrire_fichier(config, fichier):
    """Pour �crire un objet ConfigParser dans un fichier.

    @param config : objet ConfigParser � lire
    @param fichier: fichier � �crire
    @type  fichier: nom de fichier ou objet file
    """
    if isinstance(fichier, file):
        # directement si c'est un objet file (par exemple sys.stdout)
        config.write(fichier)
    else:
        # sinon on cr�e le fichier
        f = file(fichier, "w")
        config.write(f)
        f.close()


#=== PROGRAMME PRINCIPAL (test) ===============================================

if __name__ == "__main__":
    print "-----------------------------"
    print "TEST DU MODULE Parametres.py:"
    print "-----------------------------"
    print ""

    # fonction utiles uniquement pour les tests:

    def print_fichier(fichier):
        """Pour afficher un fichier � l'�cran."""
        f = file(fichier)
        print f.read()
        f.close()

    # BOOLEEN :
    p1 = Parametre("p_bool", bool, nom="valeur booleenne",
                   description="Ceci est un parametre booleen.",
                   valeur_defaut=False)
    print p1.debug()
    p1.set(True)
    print p1.debug()
    p1.set("0")
    print p1.debug()
    print "test des valeurs bool:"
    for valeur in VALEURS_VRAIES:
        p1.set(valeur)
        if p1.valeur == True:
            print "%s: OK" % valeur
        else:
            print "%s: NOK !" % valeur
            print p1.debug()
    for valeur in VALEURS_FAUSSES:
        p1.set(valeur)
        if p1.valeur == False:
            print "%s: OK" % valeur
        else:
            print "%s: NOK !" % valeur
            print p1.debug()
    print "-----------------------------"

    # ENTIER :
    p = Parametre("p_entier", int, nom="valeur entiere",
                   description="Ceci est un parametre entier.",
                   valeur_defaut=0)
    print p.debug()
    p.set(17)
    print p.debug()
    p.set("254")
    print p.debug()
    p.set(True)
    print p.debug()
    print "-----------------------------"

    # CHAINE :
    p = Parametre("p_chaine", str, nom="valeur chaine",
                   description="Ceci est un parametre chaine.",
                   valeur_defaut="(vide)")
    print p.debug()
    p.set("ceci est une chaine")
    print p.debug()
    p.set(1789)
    print p.debug()
    p.set(True)
    print p.debug()

    print "-----------------------------"
    print "test de dictionnaires de parametres:"
    params = {}
    Parametre("p_bool", bool, valeur_defaut=False).ajouter(params)
    Parametre("p_int", int, valeur_defaut=0).ajouter(params)
    Parametre("p_str", str, valeur_defaut="").ajouter(params)
    print "parametres avant:"
    for param in params:
        print params[param].debug()
    print ""
    params2 = {}
    Parametre("p_bool", bool, valeur_defaut=True).ajouter(params2)
    Parametre("p_int", int, valeur_defaut=1).ajouter(params2)
    Parametre("p_str2", str, valeur_defaut="toto").ajouter(params2)
    importer(params, params2)
    print "parametres apres:"
    for param in params:
        print params[param].debug()
    print ""
    print ""
    params2 = {"p_bool":False, "p_int":17, "p_str":"titi"}
    importer(params, params2)
    print "parametres apres 2:"
    for param in params:
        print params[param].debug()
    print ""

    print "-----------------------------"
    print "test de fichier de config:"
    cfg = ConfigParser.SafeConfigParser()
    ecrire_config(params, cfg, "section1")
    ecrire_fichier(cfg, "test.cfg")
    Parametre("nouveau", str, valeur_defaut="nouveau parametre").ajouter(params)
    print_fichier("test.cfg")
    #params = {}
    lire_config(params, "test.cfg", "section1")
    for param in params:
        print params[param].debug()
    print ""
    ecrire_config(params, cfg, "section1")
    ecrire_fichier(cfg, "test.cfg")
    print_fichier("test.cfg")





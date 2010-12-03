#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
"""
Journal - ExeFilter

Module qui prend en charge la journalisation et l'affichage des �v�nements.

Les fonctions du module permettent de journaliser les �v�nements � l'�cran sur
la console, dans un fichier texte et/ou un serveur syslog via UDP.

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
          see LICENCE.txt

@version: 1.04

@status: beta
"""

#==============================================================================
__docformat__ = 'epytext en'

#__author__  = "Philippe Lagadec, Tanguy Vinceleux, Arnaud Kerr�neur (DGA/CELAR)"
__date__    = "2010-12-03"
__version__ = "1.05"

#------------------------------------------------------------------------------
# LICENCE pour le projet ExeFilter:

# Copyright DGA/CELAR 2004-2008
# Copyright NATO/NC3A 2008-2010 (modifications PL apres ExeFilter v1.1.0)
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
# 19/01/2005 v0.01 AK: - 1�re version
# 2005-2007     PL,AK: - nombreuses �volutions + contributions de Y. Bidan
#                        et C. Catherin
# 12/01/2007 v1.00 PL: - version 1.00 officielle
# 2007-09-20 v1.01 PL: - licence CeCILL
# 2010-02-07 v1.02 PL: - removed path module import
# 2010-02-23 v1.03 PL: - updated plx import
# 2010-11-26 v1.04 PL: - code cleanup, use ExtendedLogger class
# 2010-12-03 v1.05 PL: - append to log files instead of overwriting
#                      - separate function init_console_logging

#------------------------------------------------------------------------------
# TODO:
# + split init_journal into several functions:
#   - init_console to setup console logging at the root level only once
#   - set_logfile(s) to setup logfile(s) for each session, at the logger level
#   - set_syslog to setup syslog the same way
# + when used as a library, xf should only have a NullHandler
# + fix encoding issue on Windows console
# + option to use a rotating file handler to limit log file size
# ? each new call to init_journal should use a different name for the logger
#   (to support multithreading)
# + do not use a global logger variable, but a per-session logger object
# + init_jounal: return an ExtendedLogger object
# + remove obsolete module-level functions, once other modules are fixed
# - corriger bug syslog: messages dupliqu�s au 2�me transfert d'affil�e depuis
#   l'IHM (puis retour � la normale au 3�me transfert)
# - corriger les docstrings pour �viter les warnings epydoc
# - issue when ExeFilter is embedded into another application that uses logging:
#   it should be possible to create a logger object without handlers.
#   (handlers should only be defined by the main app to avoid duplication)
# ? rename "INFO2" level to "DETAIL" or "TECH" to be clearer?

# EVOLUTIONS ENVISAGEES:
# - avec Python 2.4.2, Formatter_Latin1 n'est plus n�cessaire, utiliser le
#   nouveau param�tre encoding de FileHandler
#------------------------------------------------------------------------------


#=== IMPORTS ==================================================================

import logging, logging.handlers, os.path, sys

# modules du projet:
from commun import *
import commun
from thirdparty.plx.plx import *


#=== CONSTANTES ===============================================================

# OBSOLETE:
SYSLOG  = 0
FICHIER = 1
SYS_FIC = 2

# niveaux de jouralisation ajout�s aux niveaux du module standard logging:
# (cf. notes de d�veloppements pour plus de d�tails)
##CRITICAL = 50    # Erreur fatale, le processus ne peut continuer
##ERROR    = 40    # Erreur grave mais non fatale
IMPORTANT  = 35    # Information importante � toujours journaliser, mais qui
                   # n'est pas un warning.
##WARNING  = 30    # Avertissement, probl�me potentiel
##INFO     = 20    # Information normale
INFO2      = 15    # Information technique
##DEBUG    = 10    # Information de d�boguage pour d�veloppeur
##NOTSET   = 0

#=== VARIABLES GLOBALES =======================================================

# flag pour �viter de faire 2 init_journal()
init_effectue = False

# global logger object
logger = None

#=== CLASSES ==================================================================

#------------------------------------------------------------------------------
# classe Formatter_console
#--------------------------

class Formatter_console (logging.Formatter):
    """classe qui h�rite de logging.Formatter et ajoute une conversion
    gr�ce au codec adapt� � l'OS pour un affichage correct sur la
    console. (CMD sous Windows)
    """

    def format(self, record):
        # on appelle d'abord le format() d'origine pour obtenir la cha�ne:
        chaine = logging.Formatter.format(self, record)
        # ensuite on convertit le r�sultat si besoin:
        return str_console(chaine, errors='replace')

#------------------------------------------------------------------------------
# classe Formatter_Latin1
#-------------------------

class Formatter_Latin1 (logging.Formatter):
    """classe qui h�rite de logging.Formatter et ajoute une conversion
    gr�ce au codec latin_1 pour les messages Unicode.
    (Sinon par d�faut Python emploie UTF-8)
    """

    def format(self, record):
        # on appelle d'abord le format() d'origine pour obtenir la cha�ne:
        chaine = logging.Formatter.format(self, record)
        # ensuite on convertit le r�sultat en str si c'est de l'Unicode:
        return str_lat1(chaine, errors='replace')


class ExtendedLogger (logging.Logger):
    """
    extended Logger class for ExeFilter, based on logging.Logger:
    - with additional methods to support more logging levels
    - with conversion from strings to Unicode if needed
    """

    def debug(self, msg, *args, **kwargs):
        """Pour journaliser un �v�nement de niveau DEBUG, pour le journal de
        d�bogage technique en mode DEBUG pour le d�veloppement uniquement.

        @param msg: le message de l'�v�nement � journaliser
        @type  msg: str, unicode, objet quelconque

        @param exc_info: quand ce param�tre vaut True ou 1, l'exception en cours est
                         journalis�e avec le message.
        @type  exc_info: bool, int, str, ...
        """
        # ci-dessous la virgule est indispensable sinon (unistr(chaine)) est une
        # cha�ne et non un tuple...
        args = (unistr(msg),) + args
        # syntaxe bizarre: "extended call syntax" --> cf. "apply" dans aide Python
        logging.Logger.debug(self, *args, **kwargs)


    def info2(self, msg, *args, **kwargs):
        """Pour journaliser un �v�nement de niveau INFO2, pour le journal de
        d�bogage technique.

        @param msg: le message de l'�v�nement � journaliser
        @type  msg: str, unicode, objet quelconque

        @param exc_info: quand ce param�tre vaut True ou 1, l'exception en cours est
                         journalis�e avec le message.
        @type  exc_info: bool, int, str, ...
        """
        # syntaxe bizarre: "extended call syntax" --> cf. "apply" dans aide Python
        args = (INFO2, unistr(msg)) + args
        logging.Logger.log(self, *args, **kwargs)


    def info(self, msg, *args, **kwargs):
        """Pour journaliser un �v�nement de niveau INFO, qui sera affich� sur la
        console et enregistr� dans diff�rents journaux.
        Exemple: un fichier nettoy� ou accept�.

        @param msg: le message de l'�v�nement � journaliser
        @type  msg: str, unicode, objet quelconque

        @param exc_info: quand ce param�tre vaut True ou 1, l'exception en cours est
                         journalis�e avec le message.
        @type  exc_info: bool, int, str, ...
        """
        # syntaxe bizarre: "extended call syntax" --> cf. "apply" dans aide Python
        args = (unistr(msg),) + args
        logging.Logger.info(self, *args, **kwargs)


    def warning(self, msg, *args, **kwargs):
        """Pour journaliser un �v�nement de niveau WARNING, qui sera affich� sur la
        console et enregistr� dans diff�rents journaux.
        Exemple: un fichier refus�.

        @param msg: le message de l'�v�nement � journaliser
        @type  msg: str, unicode, objet quelconque

        @param exc_info: quand ce param�tre vaut True ou 1, l'exception en cours est
                         journalis�e avec le message.
        @type  exc_info: bool, int, str, ...
        """
        # syntaxe bizarre: "extended call syntax" --> cf. "apply" dans aide Python
        args = (unistr(msg),) + args
        logging.Logger.warning(self, *args, **kwargs)


    def important(self, msg, *args, **kwargs):
        """Pour journaliser un �v�nement de niveau IMPORTANT (entre WARNING ET ERROR).
        Exemple: le d�but et la fin d'un transfert.

        @param msg: le message de l'�v�nement � journaliser
        @type  msg: str, unicode, objet quelconque

        @param exc_info: quand ce param�tre vaut True ou 1, l'exception en cours est
                         journalis�e avec le message.
        @type  exc_info: bool, int, str, ...
        """
        # syntaxe bizarre: "extended call syntax" --> cf. "apply" dans aide Python
        args = (IMPORTANT, unistr(msg)) + args
        logging.Logger.log(self, *args, **kwargs)


    def error(self, msg, *args, **kwargs):
        """Pour journaliser un �v�nement de niveau ERROR, qui sera affich� sur la
        console et enregistr� dans diff�rents journaux.
        Exemple: une erreur anormale, qui ne n�cessite pas l'arr�t du processus.

        @param msg: le message de l'�v�nement � journaliser
        @type  msg: str, unicode, objet quelconque

        @param exc_info: quand ce param�tre vaut True ou 1, l'exception en cours est
                         journalis�e avec le message.
        @type  exc_info: bool, int, str, ...
        """
        # syntaxe bizarre: "extended call syntax" --> cf. "apply" dans aide Python
        args = (unistr(msg),) + args
        logging.Logger.error(self, *args, **kwargs)


    def exception(self, msg, *args, **kwargs):
        """Pour journaliser un �v�nement de niveau ERROR avec le texte complet de
        l'exception en cours, qui sera affich� sur la console et enregistr� dans
        diff�rents journaux. Cette fonction doit normalement �tre appel�e dans un
        bloc "except".
        Exemple: une erreur anormale, qui ne n�cessite pas l'arr�t du processus.

        @param msg: le message de l'�v�nement � journaliser
        @type  msg: str, unicode, objet quelconque
        """
        args = (unistr(msg),) + args
        logging.Logger.exception(self, *args, **kwargs)


    def critical(self, msg, *args, **kwargs):
        """Pour journaliser un �v�nement de niveau CRITICAL, qui sera affich� sur la
        console et enregistr� dans diff�rents journaux.
        Exemple: une erreur critique, qui n�cessite l'arr�t du processus.

        @param msg: le message de l'�v�nement � journaliser
        @type  msg: str, unicode, objet quelconque

        @param exc_info: quand ce param�tre vaut True ou 1, l'exception en cours est
                         journalis�e avec le message.
        @type  exc_info: bool, int, str, ...
        """
        args = (unistr(msg),) + args
        logging.Logger.critical(self, *args, **kwargs)


#=== INITIALISATION ===========================================================

# set ExtendedLogger class as default instead of logging.Logger:
logging.setLoggerClass(ExtendedLogger)
# set global logger
logger = logging.getLogger('ExeFilter')

# two additional logging levels:
logging.addLevelName (INFO2,     "INFO2")
logging.addLevelName (IMPORTANT, "IMPORTANT")



#=== FONCTIONS ================================================================

def init_console_logging():
    """
    initialize a console handler for the root logger, so that messages are
    displayed on the console.
    Should only be called if the main application does not already setup logging
    handlers.
    Should be called early, before any call to logging.
    """
    # get the root logger
    rootLogger = logging.getLogger('')
    # make sure the root logger accepts up to debug messages:
    rootLogger.setLevel(logging.DEBUG)

    # 1) on ajoute un affichage console de niveau INFO,
    #    qui n'affiche que les messages sans date/niveau:
    log_console = logging.StreamHandler(sys.stdout)
    log_console.setLevel(logging.INFO)
    # si on est en mode debug, niveau=DEBUG:
    if commun.mode_debug():
        log_console.setLevel(logging.DEBUG)
    log_console.setFormatter(Formatter_console('%(message)s'))
    rootLogger.addHandler(log_console)


#------------------------------------------------------------------------------
# init_journal
#-------------------

def init_journal (politique, journal_secu=None, journal_debug=None):
    """
    Initialise the logging system for a session. Handlers to use log files and
    syslog are enabled for the logger object according to the policy.

    - politique: policy object
    - journal_secu: filename/path of the security log file (INFO level)
    - journal_debug: filename/path of the debug log file (INFO2 level)

    Note: the policy controls if log files are enabled or not
    """
##    # on r�cup�re le Logger racine du module logging:
##    rootLogger = logging.getLogger('')
    # make sure the logger object accepts up to debug messages:
    logger.setLevel(logging.DEBUG)

    # on supprime tout handler qui serait d�j� configur�, pour �viter les
    # probl�mes �ventuels (�a arrive):
    for h in logger.handlers:
        try:
            h.flush()
        except:
            pass
        h.close()
        logger.removeHandler(h)

    # 2) on ajoute une sortie vers un fichier de niveau INFO2,
    #    qui affiche les messages avec date/niveau:
    if politique.parametres['journal_debug'].valeur:
        # append to existing log file instead of replacing it ('w' mode):
        log_fichier = logging.FileHandler(journal_debug) #, 'w')
        log_fichier.setLevel(INFO2)
        # si on est en mode debug, niveau=DEBUG:
        if commun.mode_debug():
            log_fichier.setLevel(logging.DEBUG)
        log_fichier.setFormatter(Formatter_Latin1(
            #fmt = '%(asctime)s %(name)-12s %(levelname)-9s %(message)s',
            fmt = '%(asctime)s %(levelname)-9s %(message)s',
            datefmt = '%d/%m/%y %H:%M'))
        logger.addHandler(log_fichier)

    # 3) on ajoute une sortie vers un fichier (journal de s�curit�) de niveau INFO,
    #    qui affiche les messages avec date/niveau:
    if politique.parametres['journal_securite'].valeur:
        # append to existing log file instead of replacing it ('w' mode):
        log_fichier2 = logging.FileHandler(journal_secu) #, 'w')
        log_fichier2.setLevel(logging.INFO)
        log_fichier2.setFormatter(Formatter_Latin1(
            #fmt = '%(asctime)s %(name)-12s %(levelname)-9s %(message)s',
            fmt = '%(asctime)s %(levelname)-9s %(message)s',
            datefmt = '%d/%m/%y %H:%M'))
        logger.addHandler(log_fichier2)

    # 4) on ajoute une sortie vers un serveur syslog de niveau WARNING,
    #    qui affiche les messages avec date/niveau:
    # On doit d'abord corriger le tableau de conversion des priorit�s logging/syslog
    # (sinon lev�e d'exceptions pour les niveaux que nous avons ajout�s...)
    # notre niveau INFO correspond au niveau NOTICE de syslog:
    if politique.parametres['journal_syslog'].valeur:
        logging.handlers.SysLogHandler.priority_names['info'] = logging.handlers.SysLogHandler.LOG_NOTICE
        # notre niveau INFO2 correspond au niveau INFO de syslog:
        logging.handlers.SysLogHandler.priority_names['info2'] = logging.handlers.SysLogHandler.LOG_INFO
        # notre niveau IMPORTANT correspond au niveau WARNING de syslog:
        logging.handlers.SysLogHandler.priority_names['important'] = logging.handlers.SysLogHandler.LOG_WARNING
        # ensuite on peut cr�er notre instance de SysLogHandler:
        adresse_ip = politique.parametres['serveur_syslog'].valeur
        port_udp = politique.parametres['port_syslog'].valeur
        log_syslog = logging.handlers.SysLogHandler((adresse_ip, port_udp))
        log_syslog.setLevel(logging.WARNING)
        #log_syslog.setFormatter(Formatter_Latin1(
        #    fmt = '%(asctime)s %(name)-12s %(levelname)-9s %(message)s',
        #    datefmt = '%d/%m/%y %H:%M'))
        # syslog n'a pas besoin des infos date/heure et niveau, juste le message:
        log_syslog.setFormatter(Formatter_Latin1('%(message)s'))
        logger.addHandler(log_syslog)

    # return the logger object (in the future there will be one per session):
    return logger


#------------------------------------------------------------------------------
# fermer_journal
#-------------------

def fermer_journal() :
    """
    Ferme proprement l'objet journal
    """
    try :
        # on r�cup�re le Logger racine du module logging:
##        rootLogger = logging.getLogger('')
        # on ferme proprement chaque handler:
        for h in logger.handlers:
            h.flush()
            h.close()
            logger.removeHandler(h)
##        log_console.flush()
##        log_console.close()
##        log_fichier.flush()
##        log_fichier.close()
##        log_fichier2.flush()
##        log_fichier2.close()
##        log_syslog.flush()
##        log_syslog.close()
##        # puis on les supprime:
##        logger.removeHandler(log_console)
##        logger.removeHandler(log_fichier)
##        logger.removeHandler(log_fichier2)
##        logger.removeHandler(log_syslog)
    except:
        raise


#------------------------------------------------------------------------------
# JOURNALISATION
#-------------------
# cf. aide du module logging

def debug(msg, *args, **kwargs):
    """Pour journaliser un �v�nement de niveau DEBUG, pour le journal de
    d�bogage technique en mode DEBUG pour le d�veloppement uniquement.

    @param msg: le message de l'�v�nement � journaliser
    @type  msg: str, unicode, objet quelconque

    @param exc_info: quand ce param�tre vaut True ou 1, l'exception en cours est
                     journalis�e avec le message.
    @type  exc_info: bool, int, str, ...
    """
    # ci-dessous la virgule est indispensable sinon (unistr(chaine)) est une
    # cha�ne et non un tuple...
    args = (unistr(msg),) + args
    # syntaxe bizarre: "extended call syntax" --> cf. "apply" dans aide Python
    logger.debug(*args, **kwargs)

def info2(msg, *args, **kwargs):
    """Pour journaliser un �v�nement de niveau INFO2, pour le journal de
    d�bogage technique.

    @param msg: le message de l'�v�nement � journaliser
    @type  msg: str, unicode, objet quelconque

    @param exc_info: quand ce param�tre vaut True ou 1, l'exception en cours est
                     journalis�e avec le message.
    @type  exc_info: bool, int, str, ...
    """
    # syntaxe bizarre: "extended call syntax" --> cf. "apply" dans aide Python
    args = (INFO2, unistr(msg)) + args
    logger.log(*args, **kwargs)

def info(msg, *args, **kwargs):
    """Pour journaliser un �v�nement de niveau INFO, qui sera affich� sur la
    console et enregistr� dans diff�rents journaux.
    Exemple: un fichier nettoy� ou accept�.

    @param msg: le message de l'�v�nement � journaliser
    @type  msg: str, unicode, objet quelconque

    @param exc_info: quand ce param�tre vaut True ou 1, l'exception en cours est
                     journalis�e avec le message.
    @type  exc_info: bool, int, str, ...
    """
    # syntaxe bizarre: "extended call syntax" --> cf. "apply" dans aide Python
    args = (unistr(msg),) + args
    logger.info(*args, **kwargs)

def warning(msg, *args, **kwargs):
    """Pour journaliser un �v�nement de niveau WARNING, qui sera affich� sur la
    console et enregistr� dans diff�rents journaux.
    Exemple: un fichier refus�.

    @param msg: le message de l'�v�nement � journaliser
    @type  msg: str, unicode, objet quelconque

    @param exc_info: quand ce param�tre vaut True ou 1, l'exception en cours est
                     journalis�e avec le message.
    @type  exc_info: bool, int, str, ...
    """
    # syntaxe bizarre: "extended call syntax" --> cf. "apply" dans aide Python
    args = (unistr(msg),) + args
    logger.warning(*args, **kwargs)

def important(msg, *args, **kwargs):
    """Pour journaliser un �v�nement de niveau IMPORTANT (entre WARNING ET ERROR).
    Exemple: le d�but et la fin d'un transfert.

    @param msg: le message de l'�v�nement � journaliser
    @type  msg: str, unicode, objet quelconque

    @param exc_info: quand ce param�tre vaut True ou 1, l'exception en cours est
                     journalis�e avec le message.
    @type  exc_info: bool, int, str, ...
    """
    # syntaxe bizarre: "extended call syntax" --> cf. "apply" dans aide Python
    args = (IMPORTANT, unistr(msg)) + args
    logger.log(*args, **kwargs)

def error(msg, *args, **kwargs):
    """Pour journaliser un �v�nement de niveau ERROR, qui sera affich� sur la
    console et enregistr� dans diff�rents journaux.
    Exemple: une erreur anormale, qui ne n�cessite pas l'arr�t du processus.

    @param msg: le message de l'�v�nement � journaliser
    @type  msg: str, unicode, objet quelconque

    @param exc_info: quand ce param�tre vaut True ou 1, l'exception en cours est
                     journalis�e avec le message.
    @type  exc_info: bool, int, str, ...
    """
    # syntaxe bizarre: "extended call syntax" --> cf. "apply" dans aide Python
    args = (unistr(msg),) + args
    logger.error(*args, **kwargs)

def exception(msg, *args, **kwargs):
    """Pour journaliser un �v�nement de niveau ERROR avec le texte complet de
    l'exception en cours, qui sera affich� sur la console et enregistr� dans
    diff�rents journaux. Cette fonction doit normalement �tre appel�e dans un
    bloc "except".
    Exemple: une erreur anormale, qui ne n�cessite pas l'arr�t du processus.

    @param msg: le message de l'�v�nement � journaliser
    @type  msg: str, unicode, objet quelconque
    """
    args = (unistr(msg),) + args
    logger.exception(*args, **kwargs)

def critical(msg, *args, **kwargs):
    """Pour journaliser un �v�nement de niveau CRITICAL, qui sera affich� sur la
    console et enregistr� dans diff�rents journaux.
    Exemple: une erreur critique, qui n�cessite l'arr�t du processus.

    @param msg: le message de l'�v�nement � journaliser
    @type  msg: str, unicode, objet quelconque

    @param exc_info: quand ce param�tre vaut True ou 1, l'exception en cours est
                     journalis�e avec le message.
    @type  exc_info: bool, int, str, ...
    """
    args = (unistr(msg),) + args
    logger.critical(*args, **kwargs)


#=== PROGRAMME PRINCIPAL (test) ===============================================

if __name__ == "__main__":
    print "-----------------------------"
    print "TEST DU MODULE Journal.py:"
    print "-----------------------------"
    print ""
    #mode_debug(True)
##    init_journal()
##    for niv in [
##        logging.DEBUG,
##        INFO2,
##        logging.INFO,
##        logging.WARNING,
##        IMPORTANT,
##        logging.ERROR,
##        logging.CRITICAL,
##        ]:
##        nom = logging.getLevelName(niv)
##        niv2 = logging.getLevelName(nom)
##        print "niveau %s = %d" % (nom,niv2)
##    debug("�v�nement de niveau DEBUG")
##    info2("�v�nement de niveau INFO2")
##    info("�v�nement de niveau INFO")
##    warning("�v�nement de niveau WARNING")
##    important("�v�nement de niveau IMPORTANT")
##    error("�v�nement de niveau ERROR")
##    critical("�v�nement de niveau CRITICAL")
##    print "Je vais maintenant declencher une exception..."
##    try:
##        a=1/0
##    except:
##        exception("exception, �v�nement de niveau ERROR")

    print 'tests using the new ExtendedLogger class:'
    # required to import Politique, because of gettext...
    import ExeFilter
    # setup a default policy:
    import Politique
    policy = Politique.Politique()
    # enable file logging:
    policy.parametres['journal_securite'].valeur = True
    policy.parametres['journal_debug'].valeur = True
    init_journal(policy, journal_secu='test_secu.log', journal_debug='test_debug.log')
    #logging.setLoggerClass(ExtendedLogger)
    #logging.basicConfig(level=logging.DEBUG)
    log = logger #logging.getLogger('test')
    log.debug(u"�v�nement de niveau DEBUG")
    log.info2(u"�v�nement de niveau INFO2")
    log.info(u"�v�nement de niveau INFO")
    log.warning(u"�v�nement de niveau WARNING")
    log.important(u"�v�nement de niveau IMPORTANT")
    log.error(u"�v�nement de niveau ERROR")
    log.critical(u"�v�nement de niveau CRITICAL")
    print "Je vais maintenant declencher une exception..."
    try:
        a=1/0
    except:
        log.exception(u"exception, �v�nement de niveau ERROR")


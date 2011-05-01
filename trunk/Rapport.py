#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
"""
Rapport - ExeFilter

Module pour g�n�rer des rapports aux formats HTML et XML apr�s un transfert.

Ce fichier fait partie du projet ExeFilter.
URL du projet: http://www.decalage.info/exefilter

@organization: DGA/CELAR
@author: U{Philippe Lagadec<mailto:philippe.lagadec(a)laposte.net>}
@author: U{Arnaud Kerr�neur<mailto:arnaud.kerreneur(a)dga.defense.gouv.fr>}

@contact: U{Philippe Lagadec<mailto:philippe.lagadec(a)laposte.net>}

@copyright: DGA/CELAR 2004-2008
@copyright: NATO/NC3A 2008-2010 (modifications PL apres ExeFilter v1.1.0)

@license: CeCILL (open-source compatible GPL)
          cf. code source ou fichier LICENCE.txt joint

@version: 1.05

@status: beta
"""
__docformat__ = 'epytext en'

__date__    = "2011-05-01"
__version__ = "1.05"

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
# 14/01/2005 v0.01 AK: - 1�re version
# 2005-2007     PL,AK: - nombreuses evolutions
# 12/01/2007 v1.00 PL: - version 1.00 officielle
# 2007-09-18 v1.01 PL: - ajout licence CeCILL
#                      - ajout get_username pour am�liorer la portabilit�
#                      - renommage de parametres generer_rapport
#                      - retrait date de la version ExeFilter des rapports
# 2008-03-23 v1.02 PL: - ajout _() a chaque constante chaine pour traduction
# 2010-02-07 v1.03 PL: - removed path module import
# 2010-02-09 v1.04 PL: - workaround when username cannot be determined
# 2011-05-01 v1.05 PL: - fix when destination dir is None
#                      - added initial support for scan mode

#------------------------------------------------------------------------------
# A FAIRE:

# EVOLUTIONS ENVISAGEES:
# + generer_rapport(): utiliser politique plut�t que nom_rapport ?
# + pour l'affichage du r�pertoire source, afficher le path complet (avec lettre de volume)
# ? g�n�rer un rapport au format Excel (l'IHM laisserait le choix entre html et xls) ?
# - param�tres pour choisir quels types de rapport g�n�rer (d'apr�s politique)
# ? l'ouverture automatique du rapport HTML devrait �tre un param�tre d'ExeFilter
# - s�parer les rapports HTML et XML dans 2 fonctions
# - utiliser cElementTree pour simplifier la g�n�ration de code XML (voire XHTML?)
#------------------------------------------------------------------------------

#=== IMPORTS ==================================================================

import sys, os, socket, codecs, xml.sax.saxutils, os.path, time, locale

# modules du projet:
import commun
from commun import *
import Resultat

#=== CONSTANTES ===============================================================

#=== VARIABLES GLOBALES =======================================================

# liste des objets Resultats qui vont servir � g�n�rer le rapport final:
# (vide au d�part)
#TODO: deplacer cette liste dans l'objet ExeFilter
liste_resultats = []

#------------------------------------------------------------------------------
# AJOUTER_RESULTAT
#-------------------

def ajouter_resultat (resultat):
    """Pour ajouter un r�sultat � la liste des r�sultats, qui sert ensuite �
    produire un rapport global."""
    # liste_resultats est une variable globale, il faut le pr�ciser:
    global liste_resultats
    liste_resultats.append(resultat)

#------------------------------------------------------------------------------
# ECHAP
#-------------------

def echap (chaine):
    """
    Pour remplacer tous les caract�res ayant une signification en HTML
    comme '<', '>' ou '&' par un encodage correct: '&lt;', '&gt;', '&amp;', ...
    """
    if chaine:
        return xml.sax.saxutils.escape(chaine)
    else:
        return ''

#------------------------------------------------------------------------------
# GENERER_RAPPORT
#-------------------

def generer_rapport(nom_rapport, repertoire_src, repertoire_dest, version,
                    date_version, continuer_transfert):
    """
    G�n�re un rapport au format HTML et XML.

    Retourne le r�sum� de l'analyse dans une liste.

    @param repertoire_src     : chemin du r�pertoire analys�
    @param nom_rapport        : nom des fichiers rapports HTML/XML (sans extension)
    @param version            : num�ro de version du logiciel
    @param date_version       : date de version du logiciel
    @param continuer_transfert: bool�en pour savoir s'il y a eu interruption de l'analyse
    """
    # initialisation des variables compteurs (nb fichiers analys�s,
    #     nb fichiers accept�s, etc.)
    nb_fichier = 0
    nb_accepte = 0
    nb_nettoye = 0
    nb_refuse = 0
    nb_erreur = 0

    # cr�ation du r�pertoire des rapports s'ils n'existe pas:
    #p = path(politique.parametres['rep_rapports'].valeur)
    p = os.path.dirname(nom_rapport)
    if not os.path.exists(p):
        #p.makedirs()
        os.makedirs(p)

    # on incr�mente les variables compteurs
    for resultat in liste_resultats:
        nb_fichier = nb_fichier+1
        if   resultat.code_resultat == Resultat.ACCEPTE:
            nb_accepte = nb_accepte+1
        elif resultat.code_resultat == Resultat.NETTOYE:
            nb_nettoye = nb_nettoye+1
        elif resultat.code_resultat == Resultat.REFUSE \
        or   resultat.code_resultat == Resultat.EXT_NON_AUTORISEE \
        or   resultat.code_resultat == Resultat.FORMAT_INCORRECT \
        or   resultat.code_resultat == Resultat.VIRUS :
            nb_refuse = nb_refuse+1
        elif resultat.code_resultat == Resultat.ERREUR_LECTURE \
        or   resultat.code_resultat == Resultat.ERREUR_ANALYSE:
            nb_erreur = nb_erreur+1

    # on r�cup�re le nom de l'utilisateur qui lance ExeFilter, avec nom de
    # domaine (ou de machine) sous Windows:
    try:
        username_withdomain = get_username(with_domain=True)
    except:
        # workaround if user name cannot be determined
        username_withdomain = 'unknown'
    hostname = socket.gethostname()

    # cr�ation du rapport HTML "nom_rapport", ouverture en �criture
    f=codecs.open(nom_rapport + ".html", 'w', 'latin_1')
    # le rapport est un fichier encod� en Latin-1, pour �viter les erreurs unicode:
    #f = codecs.EncodedFile (f1, 'latin_1', 'latin_1')
    f.write(u'<html>\n')
    f.write(u'<head>\n')
    f.write(u'<title>\n')
    f.write(_(u'Rapport ExeFilter\n'))
    f.write(u'</title>\n')
    f.write(u'</head>\n\n')
    f.write(u'<body>\n')

    # �criture du bandeau titre
    f.write(u'<table BORDER WIDTH="100%%" BGCOLOR="#FFFFCC"><tr><td><center><b>\n')
    f.write(_(u'Rapport ExeFilter v%(version)s') % {'version': version} + '\n<br>')
    date = unicode(time.strftime("%c", time.localtime()), 'latin_1')
    f.write(_(u"g�n�r� le %(date)s sur la machine %(hostname)s par l'utilisateur %(user)s")\
        % {'date':date, 'hostname':hostname, 'user':username_withdomain})
    f.write("\n<br>")
    if repertoire_dest:
        f.write(_(u'R�pertoire de destination : ') + echap(repertoire_dest))
        f.write('\n<br>')
    f.write(_(u'R�pertoire(s) et/ou fichier(s) analys�(s) : ') + echap(repertoire_src))
    f.write(u'\n</b></center></td></tr></table><p>\n\n')

    # affichage d'un message particulier s'il y a eu une interruption pendant l'analyse
    if continuer_transfert == False:
        f.write(u'<table BORDER WIDTH="100%%" BGCOLOR="#FF0000"><tr><td><b><center>')
        f.write(_(u"ATTENTION ! L'analyse a �t� interrompue pendant son ex�cution : "))
        f.write(_(u"tous les fichiers n'ont pas �t� analys�s."))
        f.write(u'</b></center></td></tr></table>')

    # �criture du r�sum� (nb fichiers analys�s, nb fichiers accept�s, etc.)
    f.write('<br><b>'+_(u'RESUME :')+'</b><br>\n')
    f.write(_(u'Nombre de fichiers analys�s : ') + str(nb_fichier) + '<br>\n')
    if commun.clean_mode:
        f.write(_(u'Nombre de fichiers accept�s : ') + str(nb_accepte) + '<br>\n')
        f.write(_(u'Nombre de fichiers nettoy�s : ') + str(nb_nettoye) + '<br>\n')
        f.write(_(u'Nombre de fichiers refus�s  : ') + str(nb_refuse) + '<br>\n')
    else:
        f.write(u'Number of clean files        : ' + str(nb_accepte) + '<br>\n')
        f.write(u'Number of files to be cleaned: ' + str(nb_nettoye) + '<br>\n')
        f.write(u'Number of not allowed files  : ' + str(nb_refuse) + '<br>\n')
    f.write(_(u"Nombre d'erreurs            : ") + str(nb_erreur) + '<br>\n\n')

    # �criture du tableau contenant les fichiers analys�s
    f.write(u'<br><table border=1 WIDTH="100%" BGCOLOR="#FFFFFF">\n')
    f.write(u'<tr BGCOLOR="#FFCC99">\n')
    f.write(u'<td><center><b>'+_(u'Fichier analys�')+'</b></center></td>\n')
    f.write(u'<td><center><b>'+_(u'R�sultat')+'</b></center></td>\n')
    f.write(u'<td><center><b>'+_(u'Commentaire')+'</b><center></td></tr>\n\n')

    if commun.clean_mode:
        MSG_ACCEPTED = _(u'Accept�')
        MSG_CLEANED  = _(u'Nettoy�')
        MSG_BLOCKED  = _(u'Refus�')
        MSG_ERROR    = _(u'Erreur')
    else:
        MSG_ACCEPTED = u'Clean'
        MSG_CLEANED  = u'To be cleaned'
        MSG_BLOCKED  = u'Not allowed'
        MSG_ERROR    = _(u'Erreur')

    # on modifie la couleur de fond de la colonne r�sultat suivant le code_resultat
    for resultat in liste_resultats:
        # on met le nom du fichier en gras, apr�s son chemin
        repertoire = resultat.chemin_fichier.dirname()
        if repertoire != "": repertoire += os.sep
        chemin_fichier = echap(repertoire) + '<b>' + echap(resultat.chemin_fichier.name) + '</b>'
        f.write(u'<tr valign=top><td>' + chemin_fichier + '</td>\n')
        if   resultat.code_resultat == Resultat.ACCEPTE:
            # couleur verte
            f.write(u'<td BGCOLOR="#66FF00"><center>'+MSG_ACCEPTED+'</center></td>\n')
        elif resultat.code_resultat == Resultat.NETTOYE:
            # couleur jaune
            f.write(u'<td BGCOLOR="#FFFF00"><center>'+MSG_CLEANED+'</center></td>\n')
        elif resultat.code_resultat == Resultat.REFUSE \
        or   resultat.code_resultat == Resultat.EXT_NON_AUTORISEE \
        or   resultat.code_resultat == Resultat.FORMAT_INCORRECT \
        or   resultat.code_resultat == Resultat.VIRUS :
            # couleur rouge
            f.write(u'<td BGCOLOR="#FF0000"><center>'+MSG_BLOCKED+'</center></td>\n')
        elif resultat.code_resultat == Resultat.ERREUR_LECTURE \
        or   resultat.code_resultat == Resultat.ERREUR_ANALYSE:
            # couleur orange
            f.write(u'<td BGCOLOR="#FF9900"><center>'+MSG_ERROR+'</center></td>\n')
        f.write('<td>')
        if resultat.code_resultat == Resultat.EXT_NON_AUTORISEE:
            f.write(echap(resultat.details()) + '<br>')
        for raison in resultat.raison:
            f.write(echap(raison) + '<br>')
        f.write('</td>\n\n')

    f.write('</table>\n')
    f.write('</body>')
    f.close()


    # cr�ation du rapport XML "nom_rapport", ouverture en �criture
    f=codecs.open(nom_rapport + ".xml", 'w', 'latin_1')
    f.write(u'<?xml version="1.0" encoding="iso-8859-1"?>\n')
    f.write(u'<rapport>\n')

    # �criture du bandeau titre
    f.write(u'    <titre>\n')
    f.write(u'        <ver-dat>Rapport ExeFilter v' + version + '</ver-dat>\n')
    f.write(u'        <hostname>' + echap(hostname) + '</hostname>\n')
    f.write(u'        <user>' + echap(username_withdomain) + '</user>\n')
    f.write(u'        <heure>' + time.strftime("%d/%m/%Y : %H:%M", time.localtime()) + '</heure>\n')
    # nom r�pertoire avec accent dcm2205
    f.write(u'        <rep_src>' + echap(repertoire_src) + '</rep_src>\n')
    if repertoire_dest:
        f.write(u'        <rep_dest>' + echap(repertoire_dest) + '</rep_dest>\n')
    f.write(u'    </titre>\n')

    # affichage d'un message particulier s'il y a eu une interruption pendant l'analyse
    if continuer_transfert == False:
        f.write(u'    <alerte>ATTENTION ! \nL\'analyse a �t� interrompue pendant son ex�cution : tous les fichiers n\'ont pas �t� analys�s.</alerte>\n')

    # �criture du r�sum� (nb fichiers analys�s, nb fichiers accept�s, etc.)
    f.write(u'    <resume>\n')
    f.write(u'        <ana>' + str(nb_fichier) + '</ana>\n')
    f.write(u'        <acc>' + str(nb_accepte) + '</acc>\n')
    f.write(u'        <nett>' + str(nb_nettoye) + '</nett>\n')
    f.write(u'        <ref>' + str(nb_refuse) + '</ref>\n')
    f.write(u"        <err>" + str(nb_erreur) + '</err>\n')
    f.write(u'    </resume>\n')

    # �criture du tableau contenant les fichiers analys�s
    f.write(u'    <analyse>\n')

    for resultat in liste_resultats:

        f.write(u'        <fichier>\n')
        f.write(u'            <nom>' + echap(resultat.chemin_fichier) + '</nom>\n')
        if   resultat.code_resultat == Resultat.ACCEPTE:
            f.write(u'            <resultat>Accept�</resultat>\n')
        elif resultat.code_resultat == Resultat.NETTOYE:
            f.write(u'            <resultat>Nettoy�</resultat>\n')
        elif resultat.code_resultat == Resultat.REFUSE \
        or   resultat.code_resultat == Resultat.EXT_NON_AUTORISEE \
        or   resultat.code_resultat == Resultat.FORMAT_INCORRECT \
        or   resultat.code_resultat == Resultat.VIRUS :
            f.write(u'            <resultat>Refus�</resultat>\n')
        elif resultat.code_resultat == Resultat.ERREUR_LECTURE \
        or   resultat.code_resultat == Resultat.ERREUR_ANALYSE:
            f.write(u'            <resultat>Erreur</resultat>\n')
        if resultat.code_resultat == Resultat.EXT_NON_AUTORISEE:
            f.write(u'            <comment>' +echap(resultat.details()) + '</comment>\n')
        for raison in resultat.raison:
            f.write(u'            <comment>' +echap(raison) + '</comment>\n')
        f.write(u'        </fichier>\n')

    f.write(u'    </analyse>\n')
    f.write(u'</rapport>')
    f.close()

##    # ouverture auto du rapport si on est en mode debug (ne marche que sous Windows)
##    if mode_debug() and sys.platform == 'win32' :
##        os.startfile(nom_rapport + ".html")

    # on retourne le r�sum� de l'analyse dans une liste
    resume = (nb_fichier, nb_accepte, nb_nettoye, nb_refuse, nb_erreur)
    return resume



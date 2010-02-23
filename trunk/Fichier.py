#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
"""
Fichier - ExeFilter

Module qui contient la classe L{Fichier.Fichier}, pour representer un fichier a
analyser.

Ce fichier fait partie du projet ExeFilter.
URL du projet: U{http://admisource.gouv.fr/projects/exefilter}

@organization: DGA/CELAR
@author: U{Philippe Lagadec<mailto:philippe.lagadec(a)laposte.net>}
@author: U{Arnaud Kerr�neur<mailto:arnaud.kerreneur(a)dga.defense.gouv.fr>}

@contact: U{Philippe Lagadec<mailto:philippe.lagadec(a)laposte.net>}

@copyright: DGA/CELAR 2004-2008
@copyright: NATO/NC3A 2008-2010 (PL changes after ExeFilter v1.1.0)
@license: CeCILL (open-source compatible GPL) - cf. code source ou fichier LICENCE.txt joint

@version: 1.04

@status: beta
"""

#==============================================================================
__docformat__ = 'epytext en'

__date__    = "2010-02-23"
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
# 24/10/2004 v0.01 PL: - 1�re version
# 22/12/2004       PL: - s�paration dans un module ind�pendant
# 2004-2007     PL,AK: - nombreuses �volutions
#                      - contributions de Y. Bidan
# 12/01/2007 v1.00 PL: - version 1.00 officielle
# 2007-09-20 v1.01 PL: - licence CeCILL
# 2007-10-10       PL: - ajout support antivirus ClamAV (clamd)
# 2007-10-22       PL: - ajout support antivirus F-Prot 6 (fpscan)
# 2007-10-28       PL: - ajout Fichier.remplacer_copie_temp()
# 2008-03-24 v1.02 PL: - ajout de _() pour traduction gettext des chaines
# 2010-02-07 v1.03 PL: - removed path module import
# 2010-02-23 v1.04 PL: - updated pyclamd import

#------------------------------------------------------------------------------
# A FAIRE:
# + antivirus_*: ne pas renvoyer None
# + antivirus_clamd: verif rapport en cas de detection virus
# + antivirus_fpcmd: ajouter codes sup�rieurs � 8 ? (cf. doc sur site F-Prot)
# + corriger journalisation et debug
# + v�rifier que tous les cas d'exceptions sont bien g�r�s

# EVOLUTIONS ENVISAGEES:
# - portabilit� � am�liorer: g�rer F-Prot sous Linux/BSD
#   => classe g�n�rique antivirus ? Voire possibilit� de combiner plusieurs
#   antivirus ?
# ? s�parer nettoyer() en sous-fonctions pour am�liorer la lisibilit� ?
# ? optimiser lire_debut() pour ne lire qu'une fois le buffer ? (cf. notes)
# ? antivirus: param�tres pour choisir si on scanne syst�matiquement tous
#   les fichiers pour avoir des stats pr�cises du nombre de virus, dans ce cas
#   il faudrait le faire avant les filtres de nettoyage (mauvais pour les
#   performances), et si on veut scanner tous les types de fichier (option
#   "-collect" pour F-Prot) ou bien laisser d�cider l'antivirus s'il veut
#   scanner (option "-type", meilleures perfos mais risque de rater des
#   fichiers COM infect�s renomm�s comme eicar.txt => risque acceptable ?)
# ? antivirus: prendre en compte un antivirus local "on-access" qui peut
#   empecher l'acces a un fichier (en lecture et/ou en ecriture), au lieu de
#   lancer un antivirus en ligne de commande. => Situation typique sous Windows.
#------------------------------------------------------------------------------

#=== IMPORTS ==================================================================

# modules standards Python
import traceback, sys, zipfile, socket, os, os.path
import subprocess

# modules du projet:
from commun import *
import Resultat, Journal, Rapport, Politique

# module pyclamd pour utiliser l'antivirus ClamAV (daemon clamd)
try:
    import thirdparty.pyclamd.pyclamd as pyclamd
except:
    raise ImportError, "missing pyclamd module: "\
        "see http://www.decalage.info/en/python/pyclamd"


#=== CONSTANTES ===============================================================

TAILLE_BUFFER_DEBUT = 4096    # taille du buffer pour l'analyse du d�but de fichier

# codes retourn�s par F-Prot 6 / fpscan (champ de bits):
# (http://www.f-prot.com/support/windows/fpwin_faq/fpscan.html)
# 0:   All clean.
# 1:   At least one virus-infected object was found and remains.
# 2:   At least one suspicious object was found and remains.
# 4:   Scanning was aborted by user before it finished; nothing
#      found so far.
# 8:   Some imposed restrictions were reached causing the scanner
#      to skip files (maximum depth of directories, maximum depth
#      of archives, exclusion list, etc).
# 16:  Some platform error occurred e.g. I/O errors, insufficient
#      privileges, out of memory, etc.
# 32:  Internal engine error occurred (whatever the engine fails
#      at).
# 64:  At least one object was not scanned (encrypted file,
#      unsupported/unknown compression method, corrupted or invalid
#      file).
# 128: At least one object was disinfected.
# NOTE: on considere le resultat "desinfection" comme un virus detecte:
FPSCAN_INFECTION = 1 + 2 + 128
FPSCAN_ERROR     = 4 + 8 + 16 + 32 + 64


#=== CLASSES ==================================================================

#------------------------------------------------------------------------------
# classe FICHIER
#-------------------
class Fichier:
    """
    classe stockant les informations sur un fichier a analyser.

    Un objet Fichier correspond � un fichier � nettoyer.

    Attributs d'un objet Fichier:
        - chemin: objet L{path} correspondant au chemin relatif du fichier dans son conteneur.
        - chemin_complet: chemin complet du fichier (incluant le(s) conteneur(s)), objet L{path}.
        - nom: cha�ne (unicode) correspondant au nom du fichier, sans son chemin.
        - extension: cha�ne (unicode) correspondant � l'extension du fichier, convertie en minuscules.
        - conteneur: conteneur qui contient le fichier.
        - resultat_fichier: objet L{Resultat} qui liste les r�sultats des filtres appliqu�s sur le fichier.
    """

    def __init__(self, nom_fichier, conteneur):
        """Constructeur de la classe Fichier.

        @param nom_fichier : nom du fichier, chemin relatif par rapport � la racine du conteneur.
        @type  nom_fichier : str, unicode

        @param conteneur   : objet Conteneur qui contient le fichier
        @type  conteneur   : L{Conteneur.Conteneur}
        """
        # on v�rifie si le nom de fichier fourni est bien un chemin relatif par
        # rapport au conteneur:
        if chemin_relatif_incorrect(nom_fichier):
            debug(_(u"chemin relatif incorrect: %s") % nom_fichier)
            raise ValueError, _(u"Nom de fichier non relatif ou incorrect")
        self.chemin = path(nom_fichier)
        # on construit le chemin absolu � partir de celui du conteneur:
        if conteneur.chemin_complet == "":
            # le fichier est dans le conteneur racine: chemin direct
            self.chemin_complet = self.chemin
        else:
            self.chemin_complet = conteneur.chemin_complet / self.chemin
        self.nom = self.chemin.name
        # on extrait l'extension du fichier, convertie en minuscules
        # pour permettre une comparaison correcte:
        self.extension = self.chemin.ext.lower()
        self.buffer_debut = ""
        self.fich_ouvert = None
        self._copie_temp = None        # chemin vers une copie temporaire du fichier
        self.conteneur = conteneur    # conteneur du fichier
        self.resultat_fichier = Resultat.Resultat(fichier=self)

    def copie_temp (self):
        """copie le fichier vers un r�pertoire temporaire si cela n'a
        pas d�j� �t� fait, gr�ce au conteneur, et retourne le chemin
        de la copie."""
        if self._copie_temp != None:
            # deja fait
            return self._copie_temp
        else:
            self._copie_temp = self.conteneur.copie_temp(self)
            return self._copie_temp

    def rejeter (self):
        """lorsqu'un fichier doit �tre rejet�, supprime la copie
        temporaire du fichier si elle existe."""
        try:
            if self._copie_temp != None and self._copie_temp.exists():
                self._copie_temp.remove()
        except:
            #TODO: mieux gerer exception ?
            Journal.exception(_(u'Impossible de supprimer un fichier temporaire: %s') % self._copie_temp)

    def remplacer_copie_temp (self, nouveau_fichier):
        """
        Pour remplacer la copie temporaire du fichier par une nouvelle
        version nettoyee. Les deux fichiers doivent etre sur le meme disque
        pour permettre un simple renommage.
        Doit etre utilise par tout filtre qui modifie un fichier.
        """
        # on modifie la date du nouveau fichier pour correspondre �
        # celle d'origine:
        date_fich = os.path.getmtime(self._copie_temp)
        os.utime(nouveau_fichier, (date_fich, date_fich))
        # on remplace la copie temporaire du fichier d'origine par
        # la version nettoy�e:
        # NOTE: sous Windows on est oblig� d'effacer d'abord le fichier
        #       d'origine, alors que sous Unix il serait simplement �cras�
        self._copie_temp.remove()
        os.rename(nouveau_fichier, self._copie_temp)

    def lire_debut (self):
        """lit le d�but du fichier et retourne le r�sultat dans une cha�ne.
        Le nombre d'octets lus est fix� par la constante TAILLE_BUFFER_DEBUT."""
        # on cr�e d'abord une copie temporaire du fichier, car celui-ci
        # peut �tre dans un conteneur
        self.copie_temp()
        # puis on lit le d�but du fichier dans le buffer.
        # NOTE: le mode 'rb' est n�cessaire pour lire en mode binaire,
        #       sinon on lit en mode texte et les fins de lignes peuvent
        #       �tre converties, ce qui modifie le fichier.
        # NOTE: on relit � chaque appel le d�but du fichier, car un autre
        #       filtre peut l'avoir modifi� depuis la 1�re lecture.
        #    On pourrait am�liorer un peu les perfos en utilisant un
        #    flag qui indique si le fichier a �t� effectivement modifi�.
        f = file(self._copie_temp, 'rb')
        self.buffer_debut = f.read(TAILLE_BUFFER_DEBUT)
        f.close()
        return self.buffer_debut

    def nettoyer (self, politique):
        """Nettoie un fichier, en appelant le(s) filtre(s) correspondant au
        format du fichier, puis en effectuant une analyse antivirus.

        @param politique: politique de filtrage � appliquer, objet L{Politique.Politique}
            ou None. Si None, la politique par d�faut sera appliqu�e.
        @type  politique: objet L{Politique.Politique}

        @return: le r�sultat global des filtres appliqu�s.
        @rtype : objet L{Resultat<Resultat.Resultat>}
        """
        # si une politique est fournie on r�cup�re son dictionnaire de filtres,
        # sinon on r�cup�re celle du module Politique:
        # (la diff�rence est subtile ;-)
        if politique:
            dico_filtres = politique.dico_filtres
        else:
            dico_filtres = Politique.dico_filtres
        # on dresse une liste des formats reconnus, pour la journalisation:
        formats_reconnus = []
        # si le fichier est chiffr� dans son conteneur, on ne peut pas l'analyser:
        if self.conteneur.est_chiffre(self):
            self.resultat_fichier.ajouter(Resultat.Resultat(
                Resultat.REFUSE,[
                    _(u"%s : Le fichier est chiffr�, il ne peut �tre analys�.")
                    % self.conteneur.type], self))
        # sinon on teste si l'extension est reconnue par un des filtres:
        elif self.extension in dico_filtres:
            # il existe au moins un filtre pour cette extension
            # on r�cup�re la liste des filtres concern�s
            # dans dico_filtres[fichier.extension]:
            for filtre in dico_filtres[self.extension]:
                format_reconnu = False
                # si le format est autoris�, on appelle le filtre:
                if filtre.parametres['format_autorise'].valeur == True:
                    # on appelle d'abord le filtre pour analyser le
                    # contenu du fichier:
                    try:
                        format_reconnu = filtre.reconnait_format(self)
                    except:
                        format_reconnu = False
                        erreur = str(sys.exc_info()[1])
                        msg = _(u"%s : Erreur lors de l'analyse du format (%s)") % \
                            (filtre.nom, erreur)
                        resultat_filtre = Resultat.Resultat(
                            Resultat.ERREUR_ANALYSE, msg, self)
                        self.resultat_fichier.ajouter(resultat_filtre)
                        # on ajoute l'exception au journal technique:
                        Journal.info2(msg, exc_info=True)
                        # et on fait une pause pour la lire si mode debug:
                        debug_pause()
                if format_reconnu:
                    # contenu reconnu
                    Journal.info2(filtre.nom + _(u" : Reconnu"))
                    # on ajoute ce format � la liste:
                    formats_reconnus.append(filtre.nom)
                    # on appelle le filtre pour nettoyer,
                    # et on r�cup�re le r�sultat de ce filtre:
                    try:
                        resultat_filtre = filtre.nettoyer(self)
                    except zipfile.BadZipfile:
                        # si on obtient cette exception, c'est que le module zipfile ne
                        # supporte pas le format de ce fichier zip.
                        erreur = str(sys.exc_info()[1])
                        #msg = _(u"Le format de l'archive zip est incorrect ou non support�, ") \
                        #    + _(u"le fichier ne peut �tre analys�. (%s)") % erreur
                        #resultat_filtre = Resultat.Resultat(
                        #    Resultat.ERREUR_ANALYSE, msg, self)
                        #Journal.info2(msg, exc_info=True)
                        resultat_filtre = filtre.resultat_format_incorrect(self, erreur)
                    except:
                        erreur = str(sys.exc_info()[1])
                        msg = _(u"%s : Erreur lors du nettoyage (%s)") % \
                            (filtre.nom, erreur)
                        resultat_filtre = Resultat.Resultat(
                            Resultat.ERREUR_ANALYSE,msg, self)
                        # on ajoute l'exception au journal technique:
                        Journal.info2(msg, exc_info=True)
                        # et on fait une pause pour la lire si mode debug:
                        debug_pause()
                    # on ajoute ce r�sultat � la liste des
                    # autres filtres pour ce fichier:
                    self.resultat_fichier.ajouter(resultat_filtre)
                    for r in resultat_filtre.raison:
                        Journal.info2(r)
                    # Conteneur: c'est le filtre qui doit g�rer:
#                    if filtre.format_conteneur:
#                        # on cr�e un objet conteneur
#                        conteneur = filtre.conteneur(self.chemin, "", self.dico_filtres, self)
#                        # on nettoie ce conteneur, et on r�cup�re
#                        # les r�sultats de chaque fichier (liste)
#                        liste_resultats = conteneur.nettoyer()
#                        # on ajoute cette liste au r�sultat
#                        self.resultat_fichier.resultats_conteneur = liste_resultats
#                        liste_resultat.append(liste_resultat2) # � compl�ter
                else:
                    # sinon le format n'est pas reconnu, on
                    # met � jour le r�sultat:
                    resultat_filtre = Resultat.Resultat(
                        Resultat.FORMAT_INCORRECT,[filtre.nom \
                        + _(u" : Format de fichier non reconnu ou non autoris�")], self)
                    self.resultat_fichier.ajouter(resultat_filtre)
        else:
            # le fichier a une extension non autoris�e:
            # Faut-il ajouter une raison ?
            pass
        # On appelle l'antivirus apr�s tous les filtres, si le fichier
        # n'est pas d�j� refus�, pour �conomiser son analyse qui prend du temps:
        # (cela peut poser probl�me si on veut obtenir des stats pr�cises
        # de virus, et d'un autre c�t� quand un fichier est nettoy� il ne
        # devrait plus contenir de code, donc plus de virus... Mais c'est tout
        # de m�me utile pour d�tecter certains exploits qui se cachent dans des
        # donn�es normalement non ex�cutables)
        if not self.resultat_fichier.est_refuse():
            resultat_antivirus = self.antivirus(politique)
            # on ajoute le r�sultat que si qqch de suspect a �t� d�tect�:
            if resultat_antivirus:
                self.resultat_fichier.ajouter(resultat_antivirus)
        # tous les filtres sont pass�s, on regarde le code du r�sultat final:
        # on affiche les d�tails du r�sultat:
        #print self.resultat_fichier.details()
        # on journalise le r�sultat:
        if len(formats_reconnus):
            formats = u", ".join(formats_reconnus) + u" -> "
        else:
            formats = u""
        evt_journal = u"%s : %s%s" % (self.chemin_complet, formats,
            self.resultat_fichier.details() )
        if self.resultat_fichier.est_refuse():
            # si c'est un refus, log de niveau WARNING:
            Journal.warning(evt_journal)
        else:
            # sinon, log de niveau INFO:
            Journal.info(evt_journal)
        # on ajoute le r�sultat au rapport:
        Rapport.ajouter_resultat(self.resultat_fichier)


    def antivirus (self, politique):
        """
        Analyse le fichier gr�ce � un ou plusieurs antivirus.

        @param politique: politique de filtrage � appliquer, objet L{Politique.Politique}
            ou None. Si None, la politique par d�faut sera appliqu�e.
        @type  politique: objet L{Politique.Politique}

        @return: le r�sultat de l'analyse, ou None si le fichier est sain.
        @rtype : objet L{Resultat<Resultat.Resultat>} ou None
        """
        # on commence avec un resultat vide:
        resultat = Resultat.Resultat(fichier=self)
        if politique.parametres['antivirus_fpcmd'].valeur:
            res = self.antivirus_fpcmd(politique)
            if res: resultat.ajouter(res)
        if politique.parametres['antivirus_fpscan'].valeur:
            res = self.antivirus_fpscan(politique)
            if res: resultat.ajouter(res)
        if politique.parametres['antivirus_clamd'].valeur:
            res = self.antivirus_clamd(politique)
            if res: resultat.ajouter(res)
        return resultat


    def antivirus_clamd (self, politique):
        """
        Analyse le fichier gr�ce � l'antivirus ClamAV en mode daemon (clamd).

        @param politique: politique de filtrage � appliquer, objet L{Politique.Politique}
            ou None. Si None, la politique par d�faut sera appliqu�e.
        @type  politique: objet L{Politique.Politique}

        @return: le r�sultat de l'analyse, ou None si le fichier est sain.
        @rtype : objet L{Resultat<Resultat.Resultat>} ou None
        """
        if not pyclamd.use_socket:
            # La connexion vers le service clamd n'est pas encore initialisee
            serveur = politique.parametres['clamd_serveur'].valeur
            port    = politique.parametres['clamd_port'].valeur
            Journal.info2(_(u'Connexion au serveur clamd %s:%d...') % (serveur, port))
            try:
                pyclamd.init_network_socket(serveur, port, timeout=180)
            except pyclamd.ScanError:
                Journal.exception(_(u"Connexion au service clamd (%s:%d) impossible.")
                     % (serveur, port))
                raise
            Journal.info2(pyclamd.version())
        Journal.info2(_(u"Appel de clamd pour l'analyse antivirus..."))
        # clamd a besoin du chemin absolu du fichier:
        abspath = str_lat1(self.copie_temp().abspath())
        Journal.debug(_(u'analyse de %s') % abspath)
        try:
            res = pyclamd.scan_file(abspath)
        except socket.timeout:
            return Resultat.Resultat(Resultat.ERREUR_ANALYSE,
                "clamd: "+_(u"Temps d�pass� lors de la v�rification antivirus")
                % self.nom, self)
        except:
            msg = "clamd: "+_(u"Erreur lors de la v�rification antivirus")
            Journal.exception(msg)
            return Resultat.Resultat(Resultat.ERREUR_ANALYSE, msg, self)
        if res == None:
            # resultat OK, pas de virus
            Journal.info2("clamd: "+_(u"Pas de virus d�tect�."))
            # on retourne un objet Resultat vide
            return Resultat.Resultat(fichier=self)
        else:
            # un virus a ete detecte
            fichier = res.keys[0]
            msg_virus = res[fichier]
            Journal.debug("clamd: "+_(u'fichier=%s resultat=%s') %(fichier, msg_virus))
            return Resultat.Resultat(Resultat.REFUSE,
                "clamd: "+_(u"Virus d�tect� ou fichier suspect: %s") % msg_virus,
                self)



    def antivirus_fpscan (self, politique):
        """
        Analyse le fichier gr�ce � l'antivirus F-Prot 6 (fpscan).

        @param politique: politique de filtrage � appliquer, objet L{Politique.Politique}
            ou None. Si None, la politique par d�faut sera appliqu�e.
        @type  politique: objet L{Politique.Politique}

        @return: le r�sultat de l'analyse, ou None si le fichier est sain.
        @rtype : objet L{Resultat<Resultat.Resultat>} ou None
        """
        if sys.platform == "win32":
            # on r�cup�re le chemin de F-Prot:
            chemin_fprot = politique.parametres['fpscan_executable'].valeur
            Journal.info2(_(u"Lancement de fpscan pour l'analyse antivirus..."))
            # Options pour fpscan:
            # -t: analyse des alternate data streams sur NTFS (par precaution)
            # -v 0: pas d'affichage sauf si erreur ou infection
            # /maxdepth=0: pour ne pas analyser l'interieur des archives
            # /report: ne tente pas de desinfecter
            # En mode debug on affiche tous les messages:
            if mode_debug(): verbose = '2'
            else:            verbose = '0'
            chemin_fichier = str_lat1(self.copie_temp())
##            # si le chemin du fichier contient un espace il faut l'entourer de
##            # guillemets: => seulement pour os.spawnv, pas pour popen.
##            if ' ' in chemin_fichier and not chemin_fichier.startswith('"'):
##                chemin_fichier = '"%s"' % chemin_fichier
            # Note: avec popen, '-v 0' doit etre separe en 2: '-v', '2' sinon
            # F-prot genere une erreur et renvoie un code 20.
            args_fprot = [chemin_fprot, '-t', '-v', verbose, '/maxdepth=0', '/report',
                chemin_fichier]
            Journal.debug(' '.join(args_fprot))
            # On lance F-Prot avec Popen_timer pour masquer son affichage
            # et limiter le temps d'ex�cution:
            if mode_debug():
                # on cree un fichier rapport:
                args_fprot += ['-o', 'fpscan_debug.txt']
                # en mode debug on ne masque pas l'affichage:
##                resultat_fprot = subprocess.call(args_fprot)
##                resultat_fprot = os.spawnv(os.P_WAIT, chemin_fprot, args_fprot[1:])
                resultat_fprot = Popen_timer(args_fprot, stdout=sys.stdout,
                    stderr=sys.stderr)
            else:
                resultat_fprot = Popen_timer(args_fprot)
            Journal.debug(_(u'resultat F-Prot fpscan: %d') % resultat_fprot)
            if resultat_fprot == 0:
                Journal.info2(u"fpscan: "+_(u"Pas de virus d�tect�."))
                resultat = None
            # on teste en premier s'il y a eu un timeout:
            elif resultat_fprot == EXIT_KILL_PTIMER:
                resultat = Resultat.Resultat(Resultat.ERREUR_ANALYSE,
                    u"fpscan: "+_(u"Temps d�pass� lors de la v�rification antivirus"),
                    self)
            elif resultat_fprot & FPSCAN_INFECTION:
                resultat = Resultat.Resultat(Resultat.REFUSE,
                    u"fpscan: "+_(u"Virus d�tect� ou fichier suspect"),
                    self)
            else:
                resultat = Resultat.Resultat(Resultat.ERREUR_ANALYSE,
                    u"fpscan: "+_(u"Erreur lors de la v�rification antivirus"),
                    self)
        else:
            # pour l'instant seul F-Prot sous Windows est support�:
            raise NotImplementedError, \
            u"fpscan: "+_(u"Antivirus non supporte ou implemente pour ce systeme.")
        return resultat


    def antivirus_fpcmd (self, politique):
        """
        Analyse le fichier gr�ce � l'antivirus F-Prot 3 (fpcmd).

        @param politique: politique de filtrage � appliquer, objet L{Politique.Politique}
            ou None. Si None, la politique par d�faut sera appliqu�e.
        @type  politique: objet L{Politique.Politique}

        @return: le r�sultat de l'analyse, ou None si le fichier est sain.
        @rtype : objet L{Resultat<Resultat.Resultat>} ou None
        """
        if sys.platform == "win32":
            # on r�cup�re le chemin de fpcmd:
            chemin_fprot = politique.parametres['fpcmd_executable'].valeur
            Journal.info2(_(u"Lancement de fpcmd pour l'analyse antivirus..."))
            args_fprot = [chemin_fprot, '-nomem', '-noboot', '-nosub', '-silent',
                '-old', '-collect', str_lat1(self.copie_temp())]
            # A VOIR: l'option -type laisse F-Prot d�cider si un type de fichier doit
            # �tre scann�, alors que -collect force F-Prot � tout scanner
            # (risque de faux-positifs)

            # On lance F-Prot avec Popen_timer pour masquer son affichage
            # et limiter le temps d'ex�cution:
            resultat_fprot = Popen_timer(args_fprot)
            # codes retourn�s par F-Prot 3:
            #    0 - Normal exit - nothing found
            #    1 - Abnormal termination - unrecoverable error.  This can mean any of
            #        the following:
            #            Internal error in the program.
            #            DOS version prior to 3.0 was used.
            #            ENGLISH.TX0, SIGN.DEF or MACRO.DEF corrupted or not present.
            #    2 - Selftest failed - program has been modified.
            #    3 - A Boot/File virus infection found.
            #    4 - Virus found in memory.
            #    5 - Program terminated with ^C or ESC.
            #    6 - A virus was removed.  This code is only meaningful if
            #        the program is used to scan just a single file.
            #    7 - Insufficient memory to run the program.
            #    8 - At least one suspicious file was found, but no infections.
            if resultat_fprot == 0:
                Journal.info2(u"fpcmd: "+_(u"Pas de virus d�tect�."))
                resultat = None
            elif resultat_fprot in [3, 4, 6, 8]:
                resultat = Resultat.Resultat(Resultat.REFUSE,
                    u"fpcmd: "+_(u"Virus d�tect� ou fichier suspect"),
                    self)
            elif resultat_fprot == EXIT_KILL_PTIMER:
                resultat = Resultat.Resultat(Resultat.ERREUR_ANALYSE,
                    u"fpcmd: "+_(u"Temps d�pass� lors de la v�rification antivirus"),
                    self)
            else:
                resultat = Resultat.Resultat(Resultat.ERREUR_ANALYSE,
                    u"fpcmd: "+_(u"Erreur lors de la v�rification antivirus"),
                    self)
        else:
            # pour l'instant seul F-Prot sous Windows est support�:
            raise NotImplementedError, \
            u"fpcmd: "+_(u"Antivirus non supporte ou implemente pour ce systeme.")
        return resultat
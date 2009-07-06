#!/usr/bin/python
# -*- coding: latin-1 -*-
"""
RechercherRemplacer

Ce module permet la recherche et le remplacement d'une liste de motifs dans
des fichiers.

URL du projet: U{http://www.decalage.info/python/RechercherRemplacer}

@author: U{Philippe Lagadec<mailto:philippe.lagadec(a)laposte.net>}

@contact: U{Philippe Lagadec<mailto:philippe.lagadec(a)laposte.net>}

@copyright: Philippe Lagadec
@license: CeCILL (open-source compatible GPL) - , see source code for details.
          http://www.cecill.info

@version: 1.02
@status: beta
"""
__docformat__ = 'epytext en'

#__author__  = "Philippe Lagadec"
__date__    = "2008-02-24"
__version__ = "1.02"

#------------------------------------------------------------------------------
# LICENCE :

# Copyright Philippe Lagadec 2006-2008 - voir http://www.decalage.info/contact
#
# RechercherRemplacer est un module Python pour effectuer la recherche et le
# remplacement d'une liste de motifs dans des fichiers.
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
# 2006-01-24 v0.01 PL: - 1�re version
# 2007-01-12 v1.00 PL: - version 1.00 officielle
# 2007-09-05 v1.01 PL: - version licence CeCILL
#                      - bug corrige dans rechercherRemplacer
# 2008-02-24 v1.02 PL: - ajout parametres taille_buffer et taille_overlap

# A FAIRE:
# + le contr�le si le motif remplac� est bien absent apr�s remplacement devrait
#   plut�t se faire apr�s tous les remplacements...
# - contr�ler si taille motif > TAILLE_OVERLAP
# - contr�les sur motifs de recherche/remplacement:
#   1) le remplacement ne doit pas contenir la cha�ne de recherche
#   2) le remplacement ne doit pas �tre la fin ou le d�but de la ch de rech
#      (sauf si on remplace par ""), sinon vuln�rabilit� possible, mais d�tectable
#      gr�ce aux autres contr�les : est-ce utile ?
#------------------------------------------------------------------------------

#=== IMPORTS ==================================================================

# modules standards Python:
import re


#=== CONSTANTES ===============================================================

# taille du buffer de recherche
TAILLE_BUFFER = 65536
# taille de recouvrement du buffer entre 2 recherches
# (doit �tre sup�rieure � la taille du motif le plus long)
TAILLE_OVERLAP = 1024

#=== FONCTIONS ================================================================

#------------------------------------------------------------------------------
# RechercherRemplacer
#---------------------
def rechercherRemplacer (motifs, fich_src, fich_dest, taille_identique=True,
    controle_apres=True, taille_buffer=TAILLE_BUFFER,
    taille_overlap=TAILLE_OVERLAP):
    """Pour rechercher une liste de motifs dans un fichier, et �ventuellement
    effectuer des remplacements pour obtenir un fichier modifi�.

    @param motifs: liste d'objets Motif � rechercher/remplacer
    @type  motifs: list

    @param fich_src: fichier source (en lecture seule)
    @type  fich_src: file
    @param fich_dest: fichier destination (en �criture)
    @type  fich_dest: file
    @param taille_identique: si True, indique que la taille du fichier modifi�
    ne doit pas changer (une exception RuntimeError est lev�e sinon)
    @type  taille_identique: bool
    @param controle_apres: si True, une seconde passe de recherche sera
    effectu�e pour v�rifier que les motifs remplac�s ne sont plus pr�sents.
    @type  controle_apres: bool
    @param taille_buffer: taille du buffer pour chaque lecture de fichier.
    @type  taille_buffer: int
    @param taille_overlap: recouvrement pour chaque lecture de fichier.
    @type  taille_overlap: int
    """
    # nombre de motifs trouv�s et/ou remplac�s au total
    nb_occurences = 0
    # pour d�marrer on remplit le buffer
    buffer = fich_src.read(taille_buffer + taille_overlap)
    # on agit tant que la lecture du fichier n'est pas termin�e:
    while (len(buffer)):
        # recherche/remplacement de tous les motifs
        for motif in motifs:
            buffer, nb = motif.rechercher_remplacer(buffer,
               taille_identique=taille_identique, controle_apres=controle_apres)
            nb_occurences += nb
        # on �crit le buffer modifi� dans le fichier destination, sans l'overlap
        fich_dest.write(buffer[:taille_buffer])
        # on ne garde que l'overlap dans le buffer, et on lit la suite du fichier
        buffer = buffer[taille_buffer:] + fich_src.read(taille_buffer)
    return nb_occurences


#=== CLASSES ==================================================================

#------------------------------------------------------------------------------
# classe MOTIF
#-------------------
class Motif:
    """
    Un motif est une expression r�guli�re � rechercher dans un fichier.
    (cf. aide du module re pour la syntaxe des expressions r�guli�res)
    Il peut contenir en option une cha�ne de remplacement.
    """

    def __init__(self, regex, case_sensitive=True, remplacement=False):
        """constructeur d'objet Motif.

        @param regex: cha�ne � rechercher
        @type  regex: str

        @param case_sensitive: indique si la recherche tient compte de la casse (oui par d�faut)
        @type  case_sensitive: bool

        @param remplacement: si ce n'est pas False (par d�faut), doit �tre une
        cha�ne pour remplacer le motif
        """
        self.case_sensitive = case_sensitive
        self.remplacement = remplacement
        if case_sensitive:
            flags = 0
        else:
            flags = re.IGNORECASE
        # on compile la regex pour de meilleures perfos
        self.regex = re.compile(regex, flags)

    def rechercher_remplacer(self, chaine, controle_apres=True, taille_identique=True):
        """Recherche et remplace le motif dans la cha�ne fournie, renvoie un
        tuple qui contient la cha�ne �ventuellement modifi�e, et le nombre
        d'occurrences trouv�es ou remplac�es.

        @param taille_identique: si True, indique que la taille de la cha�ne modifi�e
        ne doit pas changer (une exception RuntimeError est lev�e sinon)
        @type  taille_identique: bool
        @param controle_apres: si True, une seconde passe de recherche sera
        effectu�e pour v�rifier que les motifs remplac�s ne sont plus pr�sents.
        (sinon une exception RuntimeError est lev�e)
        @type  controle_apres: bool
        """
        # on doit tester explicitement si remplacement = False, car ce pourrait
        # �tre une cha�ne vide qui est �quivalente � False
        if self.remplacement == False:
            liste = self.regex.findall(chaine)
            return (chaine, len(liste))
        else:
            # sinon c'est un remplacement
            resultat, nb_rempl = self.regex.subn(self.remplacement, chaine)
            # cf. aide re: retourne (new_string, number_of_subs_made).
            if taille_identique:
                if len(chaine) != len(resultat):
                    raise RuntimeError, "taille modifiee apres remplacement"
            if controle_apres:
                if self.regex.search(resultat):
                    raise RuntimeError, "motif toujours present apres remplacement"
            return resultat, nb_rempl


#=== PROGRAMME PRINCIPAL (auto-test) ==========================================

if __name__ == "__main__":
    print "--------------------------------------"
    print "TEST DU MODULE RechercherRemplacer.py:"
    print "--------------------------------------"
    print ""
    print "1) test de la classe Motif"
    print ""
    c = '...Toto...tOTO...Titi...'
    print "chaine: '%s'" % c
    print "- recherche de 'Toto' sans remplacement, case sensitive:"
    m = Motif(r"Toto")
    print m.rechercher_remplacer(c)
    print "- recherche de 'toto' sans remplacement, case INsensitive:"
    mi = Motif(r"toto", case_sensitive=False)
    print mi.rechercher_remplacer(c)
    print "- recherche de 'Toto' AVEC remplacement, case sensitive:"
    mr = Motif(r"Toto", remplacement=r"Tata")
    print mr.rechercher_remplacer(c)
    print "- recherche de 'toto' AVEC remplacement, case INsensitive:"
    mri = Motif(r"toto", remplacement=r"tAtA", case_sensitive=False)
    print mri.rechercher_remplacer(c)

    print ""
    print "Memes tests avec une chaine Unicode:"
    c = u'...Toto...tOTO...Titi...'
    print "chaine: '%s'" % c
    print "- recherche de 'Toto' sans remplacement, case sensitive:"
    m = Motif(r"Toto")
    print m.rechercher_remplacer(c)
    print "- recherche de 'toto' sans remplacement, case INsensitive:"
    mi = Motif(r"toto", case_sensitive=False)
    print mi.rechercher_remplacer(c)
    print "- recherche de 'Toto' AVEC remplacement, case sensitive:"
    mr = Motif(r"Toto", remplacement=r"Tata")
    print mr.rechercher_remplacer(c)
    print "- recherche de 'toto' AVEC remplacement, case INsensitive:"
    mri = Motif(r"toto", remplacement=r"tAtA", case_sensitive=False)
    print mri.rechercher_remplacer(c)

    print ""
    print "test si une exception est bien levee en cas de controle apres remplacement positif:"
    c = "abcdcd"
    motif = "abcd"
    rempl = "ab"
    print "chaine: '%s'" % c
    print "motif: '%s' remplace par '%s'" % (motif, rempl)
    m = Motif(motif, remplacement=rempl)
    try:
        # on met taille_identique=False pour �viter de lever cette exception
        print m.rechercher_remplacer(c, taille_identique=False)
        print "NOK, pas d'exception !"
    except:
        print "OK, exception levee."

    print ""
    print "test si une exception est bien levee en cas de taille differente apres remplacement:"
    try:
        # on met controle_apres=False pour �viter de lever cette exception
        print m.rechercher_remplacer(c, controle_apres=False)
        print "NOK, pas d'exception !"
    except:
        print "OK, exception levee."

    print "----------------------------------------"
    print ""
    print "2) test de la fonction rechercherRemplacer"
    print ""
    print "Creation d'un fichier court"
    f = file("fich1_src.txt", "w")
    f.write('...abc...DEF...ABCdef...')
    f.close()
    fs = file("fich1_src.txt")
    fd = file("fich1_dest.txt", "w")
    m1 = Motif(r'abc', remplacement=r'xyz')
    m2 = Motif(r'def', remplacement=r'<<<', case_sensitive=False)
    n = rechercherRemplacer([m1, m2], fs, fd)
    print "%d remplacements." % n
    fs.close()
    fd.close()

    print "Creation d'un fichier long, avec caracteres nuls"
    f = file("fich2_src.txt", "w")
    ligne = "." * 80 + "\n"
    motif1 = r"test\000"
    motif2 = r"\000test"
    f.write("."*TAILLE_BUFFER + "TEST\x00")
    f.write("."*(TAILLE_BUFFER+TAILLE_OVERLAP-2) + "\x00tESt")
    f.close()
    fs = file("fich2_src.txt")
    fd = file("fich2_dest.txt", "w")
    m1 = Motif(motif1, remplacement=r"TOTO\000", case_sensitive=False)
    m2 = Motif(motif2, remplacement=r"\000toto", case_sensitive=False)
    n = rechercherRemplacer([m1, m2], fs, fd)
    print "%d remplacements." % n
    fs.close()
    fd.close()




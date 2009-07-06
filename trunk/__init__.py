#!/usr/bin/python
# -*- coding: latin-1 -*-
#
"""
ExeFilter - Package principal

ExeFilter permet de filtrer des fichiers, courriels ou pages web, afin de
supprimer tout code ex�cutable et tout contenu potentiellement dangereux en
termes de s�curit� informatique.

ExeFilter peut �tre employ� soit comme script (lanc� directement depuis la
ligne de commande), soit comme module (import� dans un autre script).

Lanc� comme script, ExeFilter d�pollue un ensemble de fichiers situ�s dans un
r�pertoire et place le r�sultat dans un r�pertoire destination.
La source et la destination peuvent �tre fournies en ligne de commande,
ou bien gr�ce � la fonction transfert() si ce module est import�.

Ce fichier fait partie du projet ExeFilter.
URL du projet: U{http://admisource.gouv.fr/projects/exefilter}

@organization: DGA/CELAR
@author: U{Philippe Lagadec<mailto:philippe.lagadec(a)laposte.net>}
@author: U{Arnaud Kerr�neur<mailto:arnaud.kerreneur(a)dga.defense.gouv.fr>}
@author: U{Tanguy Vinceleux<mailto:tanguy.vinceleux(a)dga.defense.gouv.fr>}

@contact: U{Philippe Lagadec<mailto:philippe.lagadec(a)laposte.net>}

@copyright: DGA/CELAR 2004-2007
@version: 1.1.0

@status: beta

@license: CeCILL (open-source compatible GPL) - cf. code source ou fichier LICENCE.txt joint

LICENCE pour le projet ExeFilter:

Copyright DGA/CELAR 2004-2007

Auteurs:
    - Philippe Lagadec (PL) - philippe.lagadec(a)laposte.net
    - Arnaud Kerr�neur (AK) - arnaud.kerreneur(a)dga.defense.gouv.fr
    - Tanguy Vinceleux (TV) - tanguy.vinceleux(a)dga.defense.gouv.fr

Ce logiciel est r�gi par la licence CeCILL soumise au droit fran�ais et
respectant les principes de diffusion des logiciels libres. Vous pouvez
utiliser, modifier et/ou redistribuer ce programme sous les conditions
de la licence CeCILL telle que diffus�e par le CEA, le CNRS et l'INRIA
sur le site "http://www.cecill.info". Une copie de cette licence est jointe
dans les fichiers Licence_CeCILL_V2-fr.html et Licence_CeCILL_V2-en.html.

En contrepartie de l'accessibilit� au code source et des droits de copie,
de modification et de redistribution accord�s par cette licence, il n'est
offert aux utilisateurs qu'une garantie limit�e.  Pour les m�mes raisons,
seule une responsabilit� restreinte p�se sur l'auteur du programme,  le
titulaire des droits patrimoniaux et les conc�dants successifs.

A cet �gard  l'attention de l'utilisateur est attir�e sur les risques
associ�s au chargement,  � l'utilisation,  � la modification et/ou au
d�veloppement et � la reproduction du logiciel par l'utilisateur �tant
donn� sa sp�cificit� de logiciel libre, qui peut le rendre complexe �
manipuler et qui le r�serve donc � des d�veloppeurs et des professionnels
avertis poss�dant  des  connaissances  informatiques approfondies.  Les
utilisateurs sont donc invit�s � charger  et  tester  l'ad�quation  du
logiciel � leurs besoins dans des conditions permettant d'assurer la
s�curit� de leurs syst�mes et ou de leurs donn�es et, plus g�n�ralement,
� l'utiliser et l'exploiter dans les m�mes conditions de s�curit�.

Le fait que vous puissiez acc�der � cet en-t�te signifie que vous avez
pris connaissance de la licence CeCILL, et que vous en avez accept� les
termes.
"""

__docformat__ = 'epytext en'

#__author__    = 'Philippe Lagadec, Tanguy Vinceleux, Arnaud Kerr�neur (DGA/CELAR)'
__date__      = '2008-02-24'
__version__   = '1.1.0' #: le numero de version ExeFilter global suit la logique Linux

# ce fichier __init__.py sert uniquement � faire en sorte que Python consid�re
# ce r�pertoire comme un package de modules, et � constituer la racine de la
# documentation pour epydoc.


#!/usr/bin/python
# -*- coding: latin-1 -*-
#
"""
ExeFilter - Package principal

ExeFilter permet de filtrer des fichiers, courriels ou pages web, afin de
supprimer tout code exécutable et tout contenu potentiellement dangereux en
termes de sécurité informatique.

ExeFilter peut être employé soit comme script (lancé directement depuis la
ligne de commande), soit comme module (importé dans un autre script).

Lancé comme script, ExeFilter dépollue un ensemble de fichiers situés dans un
répertoire et place le résultat dans un répertoire destination.
La source et la destination peuvent être fournies en ligne de commande,
ou bien grâce à la fonction transfert() si ce module est importé.

Ce fichier fait partie du projet ExeFilter.
URL du projet: U{http://admisource.gouv.fr/projects/exefilter}

@organization: DGA/CELAR
@author: U{Philippe Lagadec<mailto:philippe.lagadec(a)laposte.net>}
@author: U{Arnaud Kerréneur<mailto:arnaud.kerreneur(a)dga.defense.gouv.fr>}
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
    - Arnaud Kerréneur (AK) - arnaud.kerreneur(a)dga.defense.gouv.fr
    - Tanguy Vinceleux (TV) - tanguy.vinceleux(a)dga.defense.gouv.fr

Ce logiciel est régi par la licence CeCILL soumise au droit français et
respectant les principes de diffusion des logiciels libres. Vous pouvez
utiliser, modifier et/ou redistribuer ce programme sous les conditions
de la licence CeCILL telle que diffusée par le CEA, le CNRS et l'INRIA
sur le site "http://www.cecill.info". Une copie de cette licence est jointe
dans les fichiers Licence_CeCILL_V2-fr.html et Licence_CeCILL_V2-en.html.

En contrepartie de l'accessibilité au code source et des droits de copie,
de modification et de redistribution accordés par cette licence, il n'est
offert aux utilisateurs qu'une garantie limitée.  Pour les mêmes raisons,
seule une responsabilité restreinte pèse sur l'auteur du programme,  le
titulaire des droits patrimoniaux et les concédants successifs.

A cet égard  l'attention de l'utilisateur est attirée sur les risques
associés au chargement,  à l'utilisation,  à la modification et/ou au
développement et à la reproduction du logiciel par l'utilisateur étant
donné sa spécificité de logiciel libre, qui peut le rendre complexe à
manipuler et qui le réserve donc à des développeurs et des professionnels
avertis possédant  des  connaissances  informatiques approfondies.  Les
utilisateurs sont donc invités à charger  et  tester  l'adéquation  du
logiciel à leurs besoins dans des conditions permettant d'assurer la
sécurité de leurs systèmes et ou de leurs données et, plus généralement,
à l'utiliser et l'exploiter dans les mêmes conditions de sécurité.

Le fait que vous puissiez accéder à cet en-tête signifie que vous avez
pris connaissance de la licence CeCILL, et que vous en avez accepté les
termes.
"""

__docformat__ = 'epytext en'

#__author__    = 'Philippe Lagadec, Tanguy Vinceleux, Arnaud Kerréneur (DGA/CELAR)'
__date__      = '2008-02-24'
__version__   = '1.1.0' #: le numero de version ExeFilter global suit la logique Linux

# ce fichier __init__.py sert uniquement à faire en sorte que Python considère
# ce répertoire comme un package de modules, et à constituer la racine de la
# documentation pour epydoc.


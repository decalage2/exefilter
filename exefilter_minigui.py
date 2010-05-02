#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
"""
exefilter_minigui.py

A minimalistic GUI (graphical user interface) for ExeFilter.

This file is part of the ExeFilter project.
Project website: U{http://www.decalage.info/en/exefilter}

@author: U{Philippe Lagadec<mailto:decalage(a)laposte.net>}

@contact: U{Philippe Lagadec<mailto:decalage(a)laposte.net>}

@license: CeCILL (open-source, GPL compatible)
          see attached file LICENCE.txt

@version: 0.01

@status: alpha
"""
#==============================================================================
__docformat__ = 'epytext en'

__date__    = "2010-05-02"
__version__ = "0.01"

#------------------------------------------------------------------------------
# CHANGELOG:
# 2010-05-02 v0.01 PL: - initial version

#------------------------------------------------------------------------------
# TODO:

#------------------------------------------------------------------------------
# REFERENCES:
# http://easygui.sourceforge.net/


#=== IMPORTS ==================================================================

import os.path
import ExeFilter as xf
import Politique
from thirdparty.plx import plx
from thirdparty.easygui import *


#=== CONSTANTS ================================================================

MAIN_TITLE = 'ExeFilter v%s miniGUI' % xf.XF_VERSION

MODE_FILE = 'file'
MODE_DIR = 'directory'

FILE   = 'A - choose a File to be analyzed'
DIR    = 'D - choose a Directory or Removable Device to be analyzed'
POLICY = 'E - load/edit Policy'
LAUNCH = 'L - Launch ExeFilter'
EXIT   = 'X - Exit'

main_menu_choices = [
    FILE,
    DIR,
    POLICY,
    LAUNCH,
    EXIT,
    ]

POLICY_EDIT = 'E - Edit policy'
POLICY_LOAD = 'L - Load policy from file'
POLICY_SAVE = 'S - Save policy to file'
POLICY_HTML = 'T - Create HTML file describing the policy'
POLICY_EXIT = 'X - return to main menu'

policy_menu_choices = [
    POLICY_EDIT,
    POLICY_LOAD,
    POLICY_SAVE,
    POLICY_HTML,
    POLICY_EXIT,
    ]

#=== GLOBAL VARIABLES =========================================================

mode = MODE_DIR

source_dir = os.path.abspath('demo_files')
dest_dir = os.path.abspath('demo_output')

source_file = os.path.join(source_dir, '*')
dest_file = os.path.join(dest_dir, '*')

config_file = None

# default policy:
policy = Politique.Politique()


#=== FUNCTIONS ================================================================

def edit_param(section, param):
    title = 'Edit %s.%s' % (section, param.code)
    msg = '%s.%s: %s\n\n%s\n\nDefault value: %s' % (section,
        param.code, param.nom, param.description, param.valeur_defaut)
    value = enterbox(msg, title, default=param.valeur)
    if value is not None:
        param.valeur = value


def edit_section (section, params):
    msg = "Select policy parameter to be edited:"
    choices2params = {}
    choices = [POLICY_EXIT]
    for param in params.values():
        choice = '%s: %s' % (param.code, param.nom)
        choices2params[choice] = param
        choices.append(choice)
    while True:
        choice = choicebox(msg=msg, title=section,
            choices=choices)
        if not choice or choice == POLICY_EXIT:
            break
        param = choices2params[choice]
        edit_param(section, param)


def policy_menu():
    global config_file, policy

    while True:
        choice = choicebox(msg='Edit the filtering policy', title=MAIN_TITLE,
            choices=policy_menu_choices)

        if choice == POLICY_LOAD:
            title = "Load policy file"
            msg = "Select policy file to be loaded:"
            f = fileopenbox(msg, title, default='*.ini')
            if f:
                config_file = str(f)
                # start with default policy:
                policy = Politique.Politique()
                # load policy from file
                policy.lire_config(config_file)

        if choice == POLICY_EDIT:
            title = "Edit policy"
            msg = "Select policy section to be edited:"
            choices = [Politique.SECTION_EXEFILTER, POLICY_EXIT]
            filter_params = {}
            for filter in policy.filtres:
                choices.append(filter.nom_classe)
                filter_params[filter.nom_classe] = filter.parametres
            while True:
                choice = choicebox(msg=msg, title=title,
                    choices=choices)
                if not choice or choice == POLICY_EXIT:
                    break
                if choice == Politique.SECTION_EXEFILTER:
                    params = policy.parametres
                else:
                    params = filter_params[choice]
                section = choice
                edit_section(section, params)


        if choice == POLICY_SAVE:
            title = "Save policy file"
            msg = "Select policy file to be saved:"
            if config_file:
                default_name = str(config_file)
            else:
                default_name = 'policy.ini'
            f = filesavebox(msg, title, default=default_name)
            if f:
                config_file = str(f)
                # save policy to file
                policy.ecrire_fichier(config_file)

        if choice == POLICY_HTML:
            title = "Create HTML file describing the policy"
            msg = "Select HTML file to create:"
            if config_file:
                default_name = str(config_file+'.html')
            else:
                default_name = 'policy.html'
            f = filesavebox(msg, title, default=default_name)
            if f:
                # create HTML file
                policy.ecrire_html(f)
                plx.display_html_file(f)

        if not choice or choice == POLICY_EXIT:
            break


#=== MAIN =====================================================================

try:
    while True:
        if mode == MODE_DIR:
            source, dest = source_dir, dest_dir
        else:
            source, dest = source_file, dest_file
        status = """ExeFilter v%s

mode: %s
source dir or file: %s
destination dir or file: %s
config/policy file: %s
""" % (xf.XF_VERSION, mode, source, dest, config_file)

        choice = choicebox(msg=status, title=MAIN_TITLE, choices=main_menu_choices)

        if not choice:
            break

        if choice == FILE:
            title = "Source file"
            msg = "Select source file to be analyzed:"
            f = fileopenbox(msg, title, default=source_file)
            if f:
                mode = MODE_FILE
                # convert to string because easygui does not like unicode...
                source_file = str(f)
                # dest file = source file + _cleaned by default:
                filename, ext = os.path.splitext(f)
                dest_file = str(filename + '_cleaned' + ext)
                title = "Destination file"
                msg = "Select destination file to store the sanitized version:"
                f = filesavebox(msg, title, default=dest_file)
                if f:
                    dest_file = str(f)


        if choice == DIR:
            title = "Source directory"
            msg = "Select source directory (or removable device) to be analyzed:"
            d = diropenbox(msg, title, default=source_dir)
            if d:
                mode = MODE_DIR
                source_dir = d
                title = "Destination directory"
                msg = "Select destination directory where to copy sanitized files:"
                #TODO: create dest dir if not there?
                d = diropenbox(msg, title, default=dest_dir)
                if d:
                    dest_dir = d

        if choice == POLICY:
            policy_menu()

        if choice == LAUNCH:
            if mode == MODE_DIR:
                xf.transfert([source_dir], dest_dir, pol=policy)
            else:
                xf.transfert([source_file], dest_file, pol=policy, dest_is_a_file=True)
            xf.display_html_report()

        if choice == EXIT:
            break
except:
    exceptionbox()
#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" This project aims to cover 2 basic things:
1: Self-taughing myself how to code and improve in Python and Qt.
2: Learning how Git works.

That said, the goal is to make a Guild Wars 2 Raid API manager to check for information
and embbed everything a Raider might ever need in Guild Wars 2 (short: GW2)
"""

import json
import urllib.request
import urllib.parse
import webbrowser
import hashlib
import sys
import psutil
from subprocess import Popen
from os import environ
from pathlib import Path
from PySide2.QtWidgets import (QApplication, QComboBox, QDialog, QFileDialog,
                               QGraphicsColorizeEffect, QGroupBox, QLabel, QMainWindow, QMessageBox,
                               QPlainTextEdit, QPushButton, QStackedWidget, QTabWidget, QTextEdit)
from PySide2.QtGui import QIcon, QColor
from PySide2.QtCore import Qt, QEvent, QPoint, QSize, QSettings
from ui.gw2info_ui import Ui_MainWindow
from ui.add_ui import Ui_Dialog
import rc.resources_rc

__version__ = "1.0.1"
__author__ = "(Made by Elrey.5472) - https://github.com/Aens"
INI_OPTIONS = QSettings("options.ini", QSettings.IniFormat)


########################################################
##################### MAIN WINDOW ######################
########################################################

class MainForm(QMainWindow, Ui_MainWindow):
    """Main window of the program."""

    def __init__(self, parent=None):
        """Set the initial state of the window (size/pos).
        Connect the buttons to their functions.
        Connect the events to their triggers.
        Set proper colors to their items.
        And fire up initial functions."""
        QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.setWindowIcon(QIcon(":/images/Images/Main.ico"))
        self.setWindowTitle("Gw2 API Raid Explorer {0} {0}".format(__version__, __author__))
        # Initial window size/pos last saved. Use default values for first time
        self.setFixedSize(QSize(970, 600))
        self.move(INI_OPTIONS.value("menu_position", QPoint(350, 250)))
        self.lineInstallationFolder.setText((INI_OPTIONS.value("installation_folder", "")))
        # Left side Buttons
        self.buttonThemeLight.clicked.connect(lambda: self.initialize_colors("light"))
        self.buttonThemeDark.clicked.connect(lambda: self.initialize_colors("dark"))
        self.buttonThemeDefault.clicked.connect(lambda: self.initialize_colors("default"))
        self.buttonLanguage_english.clicked.connect(lambda: self.initialize_language("en"))
        self.buttonLanguage_spanish.clicked.connect(lambda: self.initialize_language("es"))
        self.buttonLanguage_french.clicked.connect(lambda: self.initialize_language("fr"))
        self.buttonLanguage_deutsch.clicked.connect(lambda: self.initialize_language("de"))
        self.buttonWebsite_Anet.clicked.connect(self.open_web_anet)
        self.buttonLoad.clicked.connect(self.load_api)
        self.buttonAddAPI.clicked.connect(self.open_window_add)
        self.buttonDeleteAPI.clicked.connect(self.delete_api)
        self.buttonDonate.clicked.connect(self.open_web_donate)
        # Right side buttons
        self.buttonFindfolder.clicked.connect(self.set_installation_folder)
        self.buttonArcDps.clicked.connect(self.update_arcdps)
        self.buttonArcDps_mechanics.clicked.connect(self.update_arcdps_mechanics)
        self.buttonWebsite_arcdps.clicked.connect(self.open_web_arcdps)
        self.buttonWebsite_arcdpsmechanics.clicked.connect(self.open_web_arcdpsmechanics)
        self.buttonLaunchgame.clicked.connect(self.launch_game)
        self.buttonClosegame.clicked.connect(self.close_game)
        self.buttonWebsite_dulfy.clicked.connect(self.open_web_dulfy)
        self.buttonWebsite_builds.clicked.connect(self.open_web_builds)
        self.buttonWebsite_builds_alternative.clicked.connect(self.open_web_builds_alternative)
        self.buttonWebsite_dpsreport.clicked.connect(self.open_web_dpsreport)
        self.buttonWebsite_killproof.clicked.connect(self.open_web_killproof)
        self.buttonWebsite_raidar.clicked.connect(self.open_web_raidar)
        self.buttonWebsite_gw2raidexplorer.clicked.connect(self.open_web_gw2raidexplorer)
        self.buttonDebugger.clicked.connect(self.debugger)
        # Events
        self.comboSelectAPI.installEventFilter(self)
        self.comboSelectAPI.activated.connect(self.load_combo_stuff)
        self.checkBosses.stateChanged.connect(lambda: self.save_checkboxes_status(self.checkBosses))
        self.checkMinis.stateChanged.connect(lambda: self.save_checkboxes_status(self.checkMinis))
        self.checkSkins.stateChanged.connect(lambda: self.save_checkboxes_status(self.checkSkins))
        self.checkAchievements.stateChanged.connect(lambda: self.save_checkboxes_status(self.checkAchievements))
        self.checkCurrency.stateChanged.connect(lambda: self.save_checkboxes_status(self.checkCurrency))
        # Default vars
        self.debug_mode = False
        self.stored_keys = []
        self.api_key = None
        self.api_permissions = None
        self.style_background = ""
        self.style_lineedits = ""
        # Check if we are ready to work
        self.check_if_ready()

    ################################################
    ##################### BASICS ###################
    ################################################

    def closeEvent(self, event):
        """Write window position to config file"""
        INI_OPTIONS.setValue("menu_position", self.pos())
        event.accept()

    def eventFilter(self, target, event):
        """Configure special events"""
        # Comboboxes
        if target == self.comboSelectAPI and event.type() == QEvent.MouseButtonPress:
            self.fill_combo_selectapi()
        return False

    def change_statusbar(self, statusmode, message):
        """Edit the status bar, both with a message and style."""
        if statusmode == "wait":
            self.statusbar.setStyleSheet("background-color: rgb(234, 140, 6);color: rgb(0, 0, 0);")
            self.statusbar.showMessage("WAIT: " + message)
        elif statusmode == "ready":
            self.statusbar.setStyleSheet(self.style_background)
            self.statusbar.showMessage("READY: " + message)
        elif statusmode == "error":
            self.statusbar.setStyleSheet("background-color: rgb(200, 0, 0);color: rgb(255, 255, 255);")
            self.statusbar.showMessage("ERROR: " + message)
        elif statusmode == "special":
            self.statusbar.setStyleSheet("background-color: rgb(190, 1, 190);color: rgb(255, 255, 255);")
            self.statusbar.showMessage("SPECIAL: " + message)

    def api_open(self, section, **keyarguments):
        """Build the right address"""
        address = "https://api.guildwars2.com/v2/"+section
        separator = "?"
        if 'ids' in keyarguments:
            if len(keyarguments['ids']) > 1:
                address = address+"?ids="+",".join(keyarguments['ids'])
                separator = "&"
            else:
                address = address+"/"+keyarguments['ids'][0]
        # Check for special parameters
        if 'token' in keyarguments:
            address = address+separator+"access_token="+keyarguments['token']
        elif 'lang' in keyarguments:
            address = address+separator+"lang="+keyarguments['lang']
        # Now encode, debug and open it
        address = urllib.parse.quote(address, safe='/:=', encoding="utf-8", errors="strict")
        if self.debug_mode:
            self.plainDebugger.appendPlainText(address)
        address = urllib.request.urlopen(address).read().decode('utf8')
        return json.loads(address)

    ###############################################
    ################### ON LOAD ###################
    ###############################################

    def check_if_ready(self):
        """Make sure we are ready to work."""
        self.change_statusbar("wait", "Checking if everything is fine...")
        warning = []
        # Theme and colors
        self.initialize_colors(INI_OPTIONS.value("theme", "default"))
        # Languages
        self.initialize_language(INI_OPTIONS.value("language", "en"))
        # Load checkboxes status
        for checkbox in (self.checkBosses, self.checkCurrency, self.checkAchievements, self.checkMinis,
                         self.checkSkins):
            if self.load_checkboxes_status(checkbox) == "true":
                checkbox.setChecked(True)
        # Check if there is something stored
        self.fill_combo_selectapi()
        if not self.stored_keys:
            warning.append("There is no API keys yet, add one.")
        else:
            self.load_permissions()
        # Check if we are in the last version
        version = self.check_online_version()
        if version is not None:
            warning.append(version)
        # Check if there is warnings
        if len(warning) >= 1:
            self.change_statusbar("error", ",".join(warning))
        else:
            self.change_statusbar("ready", "Everything seems fine. Program ready.")

    @staticmethod
    def load_checkboxes_status(checkbox):
        """Load the status of the checkbox."""
        return INI_OPTIONS.value(checkbox.objectName(), "false")

    @staticmethod
    def save_checkboxes_status(checkbox):
        """Save the status of the checkbox."""
        INI_OPTIONS.setValue(checkbox.objectName(), checkbox.isChecked())

    @staticmethod
    def default_theme():
        """Set the default theme colors."""
        colors = {"backgroundcolor": "background-color: rgb(217, 217, 217);"
                                     "color: rgb(0, 0, 0);",
                  "buttoncolor": "background-color: rgb(200, 210, 210);"
                                 "color: rgb(0, 0, 0);",
                  "dropdowncolor": "background-color: rgb(200, 210, 210);"
                                   "color: rgb(0, 0, 0);",
                  "inputcolor": "background-color: rgb(255, 250, 200);"
                                "color: rgb(0, 0, 0);"
                                "border: 1px solid rgb(145, 145, 145);",
                  "inputcolorreadonly": "background-color: rgb(255, 245, 220);"
                                        "color: rgb(0, 0, 0);"
                                        "border: 1px solid rgb(145, 145, 145);",
                  "labelcolor": "background-color: rgb(0, 0, 0, 0);"
                                 "color: rgb(0, 0, 0);",
                  "groupstyle": "QGroupBox{border: 2px solid rgb(150, 150, 150);border-radius: 5px;"
                                "margin-top: 5px; /* leave space at the top for the title */}"
                                "QGroupBox::title {subcontrol-origin: margin;"
                                "subcontrol-position: top center; /* position at the top center */"
                                "padding: 0 3px;  /* empty space at each side of title */}",
                  "tabstyle": "/* The tab menu buttons */"
                              "QTabBar::tab {border: 2px solid rgb(150, 150, 150);border-bottom: 0px;"
                              "border-top-left-radius: 6px;border-top-right-radius: 6px;"
                              "padding: 2px;}"
                              " /* The tab specific buttons */"
                              "QTabBar::tab:selected {border-color: rgb(150, 150, 150);"
                              "background-color: rgb(200, 210, 210);}"
                              "QTabBar::tab:hover {background-color: rgb(200, 210, 210);}"
                              " /* The tab widget frame */"
                              "QTabWidget::pane {border: 2px solid rgb(150, 150, 150);"
                              "border-top-right-radius: 5px;border-bottom-right-radius: 5px;"
                              "border-bottom-left-radius: 5px;padding: 2px;}"
                  }
        return colors

    @staticmethod
    def dark_theme():
        """Set the dark theme colors."""
        colors = {"backgroundcolor": "background-color: rgb(60, 63, 65);"
                                     "color: rgb(207, 207, 207);",
                  "buttoncolor": "background-color: rgb(90, 95, 100);"
                                 "color: rgb(200, 200, 200);",
                  "dropdowncolor": "background-color: rgb(167, 177, 182);"
                                   "color: rgb(0, 0, 0);",
                  "inputcolor": "background-color: rgb(190, 190, 190);"
                                "color: rgb(0, 0, 0);"
                                "border: 1px solid rgb(0, 0, 0);",
                  "inputcolorreadonly": "background-color: rgb(115, 115, 115);"
                                        "color: rgb(0, 0, 0);"
                                        "border: 1px solid rgb(0, 0, 0);",
                  "labelcolor": "background-color: rgb(0, 0, 0, 0);"
                                 "color: rgb(200, 200, 200);",
                  "groupstyle": "QGroupBox{border: 2px solid rgb(0, 0, 0);border-radius: 5px;"
                                "margin-top: 5px; /* leave space at the top for the title */}"
                                "QGroupBox::title {subcontrol-origin: margin;"
                                "subcontrol-position: top center; /* position at the top center */"
                                "padding: 0 3px;  /* empty space at each side of title */}",
                  "tabstyle": "/* The tab menu buttons */"
                              "QTabBar::tab {border: 2px solid black;border-bottom: 0px;"
                              "border-top-left-radius: 6px;border-top-right-radius: 6px;"
                              "padding: 2px;}"
                              " /* The tab specific buttons */"
                              "QTabBar::tab:selected {border-color: black;background-color: rgb(90, 95, 100);}"
                              "QTabBar::tab:hover {background-color: rgb(90, 95, 100);}"
                              " /* The tab widget frame */"
                              "QTabWidget::pane {border: 2px solid black;"
                              "border-top-right-radius: 5px;border-bottom-right-radius: 5px;"
                              "border-bottom-left-radius: 5px;padding: 2px;}"
                  }
        return colors

    @staticmethod
    def light_theme():
        """Set the light theme colors."""
        colors = {"backgroundcolor": "background-color: rgb(150, 200, 255);"
                                     "color: rgb(24, 113, 131);",
                  "buttoncolor": "background-color: rgb(107, 162, 212);"
                                 "color: rgb(0, 0, 0);",
                  "dropdowncolor": "background-color: rgb(255, 255, 150);"
                                   "color: rgb(0, 0, 0);",
                  "inputcolor": "background-color: rgb(255, 248, 194);"
                                "color: rgb(50, 50, 50);"
                                "border: 1px solid rgb(100, 100, 100);",
                  "inputcolorreadonly": "background-color: rgb(225, 255, 225);"
                                        "color: rgb(50, 50, 50);"
                                        "border: 1px solid rgb(100, 100, 100);",
                  "labelcolor": "background-color: rgb(0, 0, 0, 0);"
                                 "color: rgb(24, 100, 130);",
                  "groupstyle": "QGroupBox{border: 2px solid rgb(10, 105, 170);border-radius: 5px;"
                                "margin-top: 5px; /* leave space at the top for the title */}"
                                "QGroupBox::title {subcontrol-origin: margin;"
                                "subcontrol-position: top center; /* position at the top center */"
                                "padding: 0 3px;  /* empty space at each side of title */}",
                  "tabstyle": "/* The tab menu buttons */"
                              "QTabBar::tab {border: 2px solid rgb(10, 105, 170);border-bottom: 0px;"
                              "border-top-left-radius: 6px;border-top-right-radius: 6px;"
                              "padding: 2px;}"
                              " /* The tab specific buttons */"
                              "QTabBar::tab:selected {border-color: rgb(10, 105, 170);"
                              "background-color: rgb(225, 255, 225);}"
                              "QTabBar::tab:hover {background-color: rgb(225, 255, 225);}"
                              " /* The tab widget frame */"
                              "QTabWidget::pane {border: 2px solid rgb(10, 105, 170);"
                              "border-top-right-radius: 5px;border-bottom-right-radius: 5px;"
                              "border-bottom-left-radius: 5px;padding: 2px;}"
                  }
        return colors

    def initialize_colors(self, theme):
        """Iterate over every widget to paint them."""
        if theme == "dark":
            colors = self.dark_theme()
            INI_OPTIONS.setValue("theme", "dark")
        elif theme == "light":
            colors = self.light_theme()
            INI_OPTIONS.setValue("theme", "light")
        else:
            colors = self.default_theme()
            INI_OPTIONS.setValue("theme", "default")
        # Let's paint them
        for widget in app.topLevelWidgets():
            if widget.isWindow():
                self.set_colors(widget, colors)
        self.style_background = colors['backgroundcolor']  # For the statusbar
        self.style_lineedits = colors['inputcolorreadonly']  # For the reset of YES/NO fields
        self.load_permissions()
        self.change_statusbar("ready", "New theme loaded.")

    def set_colors(self, widget, colors):
        """Paint the initial colors for the controls"""
        for item in widget.children():
            item_type = item.metaObject().className()
            # SPECIALS: Set background to it and then re-iterate on these items
            if item_type == "QWidget" or isinstance(item, QDialog):
                widget.setStyleSheet(colors['backgroundcolor'])
                self.set_colors(item, colors)
            # SPECIALS: Set style to it and then re-iterate on these items
            elif isinstance(item, QGroupBox):
                item.setStyleSheet(colors['groupstyle'])
                self.set_colors(item, colors)
            elif isinstance(item, QTabWidget) or isinstance(item, QStackedWidget):
                item.setStyleSheet(colors['tabstyle'])
                self.set_colors(item, colors)
            # OTHER: Stand-alone widgets
            elif item_type == "QLineEdit":
                if item.isReadOnly():
                    item.setStyleSheet(colors['inputcolorreadonly'])
                else:
                    item.setStyleSheet(colors['inputcolor'])
            elif isinstance(item, QPlainTextEdit):
                item.setStyleSheet(colors['inputcolor'])
            elif isinstance(item, QTextEdit):
                item.setStyleSheet(colors['inputcolor'])
            elif isinstance(item, QLabel):
                item.setStyleSheet(colors['labelcolor'])
            elif isinstance(item, QPushButton):
                item.setStyleSheet(colors['buttoncolor'])
            elif isinstance(item, QComboBox):
                item.setStyleSheet(colors['dropdowncolor'])
            else:
                # print(item_type) # TBD Used to debug
                # print(item.objectName())# TBD Used to debug
                pass

    def initialize_language(self, lang):
        """Iterate over every widget to paint them."""
        self.change_statusbar("special", "Languages are not programmed yet.")
        INI_OPTIONS.setValue("lang", lang)

    def check_online_version(self):
        """Check if we need an update."""
        version_file = "https://raw.githubusercontent.com/Aens/Gw2RaidExplorer/master/version.txt"
        try:
            address = urllib.parse.quote(version_file, safe='/:=', encoding="utf-8", errors="strict")
            address = urllib.request.urlopen(address).read().decode('utf8')
            data = json.loads(address)
            online_version = int(data["version"].replace(".", ""))
            offline_version = int(__version__.replace(".", ""))
        except Exception as e:
            return "I couldn't check if there is a new version availible: {0}".format(str(e))
        else:
            if offline_version < online_version:
                if popup_question(
                        title="New update found.",
                        message="There is a new version availible for this program."
                                "\n\nYou have the outdated version: {0}"
                                "\nDo you want to Download the new one: {1}?"
                                "\n\nIMPORTANT: Before updating, backup your options.ini file, it's located "
                                "in this program folder and that's where your API keys and settings are stored."
                                .format(__version__, data["version"])):
                    webbrowser.open(data["release_url"])
            return None

    #######################################################
    ################## BUTTONS and EVENTS #################
    #######################################################

    def fill_combo_selectapi(self):
        """Fill the combo with all the APIs"""
        self.comboSelectAPI.clear()
        self.stored_keys = self.get_stored_keys()
        for key in self.stored_keys:
            self.comboSelectAPI.addItem(key['name'])

    def load_combo_stuff(self):
        """Load the stuff on selecting anything on the combo"""
        self.reset_everything()
        self.load_permissions()

    def open_window_add(self):
        """Create instance of the Add API window, get the right theme
        Iterate over every widget to paint them, execute instance."""
        addwindow = AddNewApi()
        # Get correct theme
        theme = INI_OPTIONS.value("theme", "default")
        if theme == "dark":
            colors = self.dark_theme()
        elif theme == "light":
            colors = self.light_theme()
        else:
            colors = self.default_theme()
        # Let's paint them
        self.set_colors(addwindow, colors)
        addwindow.setStyleSheet(colors['backgroundcolor'])
        # Execute instance
        addwindow.exec_()

    @staticmethod
    def get_stored_keys():
        """Get stored APIs from database, which is a list of dicts."""
        stored_keys = []
        for key in INI_OPTIONS.value("api_keys", []):
            stored_keys.append(key)
        return stored_keys

    def delete_api(self):
        """Delete the selected API from database"""
        self.change_statusbar("wait", "Deleting key...")
        if not self.comboSelectAPI.currentText() == "":
            if popup_question(title="Security Check", message="Are you sure that you want to delete that key?"):
                # get all keys
                keys = self.get_stored_keys()
                # delete right one
                for item in keys:
                    if item['name'] == self.comboSelectAPI.currentText():
                        keys.remove(item)
                # update new keys
                self.stored_keys = keys
                # Save them into file
                INI_OPTIONS.setValue("api_keys", keys)
                # Clean it up
                self.comboSelectAPI.clear()
                self.change_statusbar("ready", "API key deleted from local database.")
            else:
                self.change_statusbar("ready", "Key not deleted ^^")
        else:
            self.change_statusbar("error", "There is no API key selected.")

    def debugger(self):
        """Enable/Disable the debugger section"""
        if self.debug_mode:
            self.debug_mode = False
            self.setFixedSize(QSize(self.width(), self.height() - self.plainDebugger.height()))
        else:
            self.debug_mode = True
            self.setFixedSize(QSize(self.width(), self.height() + self.plainDebugger.height()))

    def open_web_anet(self):
        """Open the website browser with this website."""
        self.change_statusbar("wait", "Loading website...")
        webbrowser.open("https://account.arena.net/applications")
        self.change_statusbar("ready", "Website for Arenanet API keys launched on your browser.")

    def open_web_builds(self):
        """Open the website browser with this website."""
        self.change_statusbar("wait", "Loading website...")
        webbrowser.open("https://www.snowcrows.com")
        self.change_statusbar("ready", "Website for Raid Builds launched on your browser.")

    def open_web_builds_alternative(self):
        """Open the website browser with this website."""
        self.change_statusbar("wait", "Loading website...")
        webbrowser.open("http://metabattle.com/wiki/Raid")
        self.change_statusbar("ready", "Website for Raid Builds launched on your browser.")

    def open_web_dpsreport(self):
        """Open the website browser with this website."""
        self.change_statusbar("wait", "Loading website...")
        webbrowser.open("https://dps.report/")
        self.change_statusbar("ready", "Website for Raid DPS Reports launched on your browser.")

    def open_web_killproof(self):
        """Open the website browser with this website."""
        self.change_statusbar("wait", "Loading website...")
        webbrowser.open("https://killproof.me")
        self.change_statusbar("ready", "Website to check Killproofs launched on your browser.")

    def open_web_raidar(self):
        """Open the website browser with this website."""
        self.change_statusbar("wait", "Loading website...")
        webbrowser.open("https://www.gw2raidar.com")
        self.change_statusbar("ready", "Website for Raid Reports Raidar launched on your browser.")

    def open_web_arcdps(self):
        """Open the website browser with this website."""
        self.change_statusbar("wait", "Loading website...")
        webbrowser.open("https://www.deltaconnected.com/arcdps/")
        self.change_statusbar("ready", "Website for ArcDps Plugin launched on your browser.")

    def open_web_arcdpsmechanics(self):
        """Open the website browser with this website."""
        self.change_statusbar("wait", "Loading website...")
        webbrowser.open("http://martionlabs.com/arcdps-mechanics-log-plugin/")
        self.change_statusbar("ready", "Website for ArcDps Mechanics Addon launched on your browser.")

    def open_web_dulfy(self):
        """Open the website browser with this website."""
        self.change_statusbar("wait", "Loading website...")
        webbrowser.open("http://dulfy.net/category/gw2/raid-guides/")
        self.change_statusbar("ready", "Website for Dulfy raid guides launched on your browser.")

    def open_web_gw2raidexplorer(self):
        """Open the website browser with this website."""
        self.change_statusbar("wait", "Loading website...")
        webbrowser.open("https://github.com/Aens/Gw2RaidExplorer")
        self.change_statusbar("ready", "Website for this tool launched on your browser.")

    def open_web_donate(self):
        """Open the website browser with this website."""
        self.change_statusbar("wait", "Loading website...")
        webbrowser.open("https://www.paypal.com/cgi-bin/webscr?cmd=_donations"
                        "&business=Aenswindstorm@gmail.com&lc=US&item_name=For+Gw2raidexplorer"
                        "&no_note=0&cn=&curency_code=USD&bn=PP-DonationsBF:btn_donateCC_LG.gif:NonHosted")
        self.change_statusbar("ready", "Website to donate launched on your browser.")

    #######################################################
    ################## ARCDPS AND PLUGINS #################
    #######################################################

    def set_installation_folder(self):
        """Set the installation folder"""
        folderpath = QFileDialog.getExistingDirectory()
        if not folderpath == "":
            self.lineInstallationFolder.setText(folderpath)
            INI_OPTIONS.setValue("installation_folder", folderpath)

    def check_folder_is_right(self):
        """Check that there is no issues with that folder"""
        folder = self.lineInstallationFolder.text()
        if folder == "":
            self.change_statusbar("error", "You need to set your GW2 installation folder above.")
        elif "Guild Wars 2" not in folder:
            self.change_statusbar("error", "You didn't set the folder for Guild Wars 2")
        else:
            self.change_statusbar("ready", "Installation folder verified.")
            return True
        return False

    @staticmethod
    def get_hash_of_file(filepath):
        """Get the hash of a file"""
        hash_md5 = hashlib.md5()
        with open(filepath, "rb") as file_to_check:
            for chunk in iter(lambda: file_to_check.read(4096), b""):
                hash_md5.update(chunk)
            return hash_md5.hexdigest()

    @staticmethod
    def file_exists(filename):
        """Check if a file exists."""
        pathoffile = Path(filename)
        if pathoffile.is_file():
            return True
        else:
            return False

    def update_arcdps(self):
        """Install or update ArcDps plugin."""
        if self.check_folder_is_right():
            self.change_statusbar("wait", "Verifying hash files of ArcDps...")
            # Files
            bin_folder = self.lineInstallationFolder.text() + "/bin64"
            local_file = '{0}/d3d9.dll'.format(bin_folder)
            local_file_bt = '{0}/d3d9_arcdps_buildtemplates.dll'.format(bin_folder)
            online_file = "https://www.deltaconnected.com/arcdps/x64/d3d9.dll"
            online_file_bt = "https://www.deltaconnected.com/arcdps/x64/buildtemplates/d3d9_arcdps_buildtemplates.dll"
            online_file_md5 = "https://www.deltaconnected.com/arcdps/x64/d3d9.dll.md5sum"
            # Check if exists
            try:
                if self.file_exists(local_file):
                    # Get both md5
                    local_file_md5 = self.get_hash_of_file(local_file)
                    address = urllib.parse.quote(online_file_md5, safe='/:=', encoding="utf-8", errors="strict")
                    address = urllib.request.urlopen(address).read().decode('utf8')
                    online_md5 = address.split(" ")[0]
                    # Compare online MD5 with local md5
                    if online_md5 == local_file_md5:
                        self.change_statusbar("ready", "NOPE, ArcDps was already updated.")
                    else:
                        # Download files and replace them
                        self.change_statusbar("wait", "ArcDps is being updated...")
                        urllib.request.urlretrieve(online_file, local_file)
                        urllib.request.urlretrieve(online_file_bt, local_file_bt)
                        self.change_statusbar("ready", "YES, there was a new version. ArcDps has been updated.")
                else:
                    # Download files
                    self.change_statusbar("wait", "ArcDps is not installed, downloading...")
                    urllib.request.urlretrieve(online_file, local_file)
                    urllib.request.urlretrieve(online_file_bt, local_file_bt)
                    self.change_statusbar("ready", "YES, there was a new version. ArcDps has been Installed.")
            except Exception as e:
                self.change_statusbar("error", "Unexpected error: {0}".format(str(e)))

    def update_arcdps_mechanics(self):
        """Install or update ArcDps Mechanics plugin."""
        if self.check_folder_is_right():
            self.change_statusbar("wait", "Verifying hash file of ArcDps Mechanics Addon...")
            # Files
            bin_folder = self.lineInstallationFolder.text() + "/bin64"
            local_file = '{0}/d3d9_arcdps_mechanics.dll'.format(bin_folder)
            online_file = "http://martionlabs.com/wp-content/uploads/d3d9_arcdps_mechanics.dll"
            online_file_md5 = "http://martionlabs.com/wp-content/uploads/d3d9_arcdps_mechanics.dll.md5sum"
            # Check if exists
            try:
                if self.file_exists(local_file):
                    # Get both md5
                    local_file_md5 = self.get_hash_of_file(local_file)
                    address = urllib.parse.quote(online_file_md5, safe='/:=', encoding="utf-8", errors="strict")
                    address = urllib.request.urlopen(address).read().decode('utf8')
                    online_md5 = address[:32]
                    # Compare online md5 with local md5
                    if online_md5 == local_file_md5:
                        self.change_statusbar("ready", "ArcDps Mechanics Addon was already updated.")
                    else:
                        # Download files and replace them
                        self.change_statusbar("wait", "ArcDps Mechanics Addon is being updated...")
                        urllib.request.urlretrieve(online_file, local_file)
                        self.change_statusbar("ready", "ArcDps Mechanics Addon has been updated.")
                else:
                    # Download files
                    self.change_statusbar("wait", "ArcDps Mechanics Addon is not installed, downloading...")
                    urllib.request.urlretrieve(online_file, local_file)
                    self.change_statusbar("ready", "ArcDps Mechanics Addon has been Installed.")
            except Exception as e:
                self.change_statusbar("error", "Unexpected error: {0}".format(str(e)))

    #######################################################
    ################## GUILD WARS 2 #######################
    #######################################################

    @staticmethod
    def game_is_running():
        """Check if game is running."""
        game_names = ["Gw2-64.exe", "Gw2.exe"]
        for process in psutil.process_iter():
            for name in game_names:
                if process.name() == name:
                    return True, process
        return False, None

    def launch_game(self):
        """Launch the game."""
        if self.check_folder_is_right():
            if self.game_is_running()[0]:
                self.change_statusbar("error", "Guild Wars 2 is already running.")
            else:
                self.change_statusbar("wait", "Launching Guild Wars 2...")
                filepath = self.lineInstallationFolder.text()
                game_paths = ["{0}/Gw2-64.exe".format(filepath), "{0}/Gw2.exe".format(filepath),
                              "{0}/gw2-64.exe".format(filepath), "{0}/gw2.exe".format(filepath)]
                for file in game_paths:
                    if self.file_exists(file):
                        Popen([file, "-maploadinfo"])
                        self.change_statusbar("ready", "Guild Wars 2 started.")
                        return
                self.change_statusbar("error", "Executable file could not be found.")

    def close_game(self):
        """Close the game."""
        if self.check_folder_is_right():
            running, game_proccess = self.game_is_running()
            if running:
                game_proccess.kill()
                self.change_statusbar("ready", "Guild Wars 2 has been forced to be closed.")
            else:
                self.change_statusbar("error", "Guild Wars 2 is not running.")

    ###############################################################
    ################### MAIN LOADING API CODE #####################
    ###############################################################

    def reset_everything(self):
        """Reset all fields"""
        self.reset_permissions()
        self.reset_bosses()
        self.reset_currency()
        self.reset_achievements()
        self.reset_minis()
        self.reset_skins()

    def load_api(self):
        """Load all the data of this API"""
        if self.comboSelectAPI.currentText() == "":
            self.change_statusbar("error", "You have not added any API key yet.")
        else:
            self.change_statusbar("wait", "Loading your data...")
            try:
                # Fill Bosses section
                self.change_statusbar("wait", "Loading Bosses section...")
                bosses = self.load_bosses_section()
                self.change_statusbar("ready", "Bosses section loaded.")
                # Fill Raid currencies section
                self.change_statusbar("wait", "Loading Currencies section...")
                currency = self.load_currency_section()
                self.change_statusbar("ready", "Currency section loaded.")
                # Fill Raid Achievements section
                self.change_statusbar("wait", "Loading Achievements section...")
                achievements = self.load_achievements_section()
                self.change_statusbar("ready", "Achievements section loaded.")
                # Fill Minis section
                self.change_statusbar("wait", "Loading Minis section...")
                minis = self.load_minis_section()
                self.change_statusbar("ready", "Minis section loaded.")
                # Fill Skins section
                self.change_statusbar("wait", "Loading Skins section...")
                skins = self.load_skins_section()
                self.change_statusbar("ready", "Skins section loaded.")
                # Final message
                warning = []
                for result in [bosses, currency, achievements, minis, skins]:
                    if result is not None:
                        warning.append(result)
                if len(warning) >= 1:
                    self.change_statusbar("error", "Not enough permission to do that - {0}".format(" - ".join(warning)))
                else:
                    self.change_statusbar("ready", "API data loaded.")
            # Special exceptions
            except Exception as e:
                if "HTTP Error 400" in str(e):
                    self.change_statusbar("error", "Your API key is not valid.")
                elif "HTTP Error 403" in str(e):
                    self.change_statusbar("error", "LAZY BUG 0001 - If you can read this, tell the programmer.")
                else:
                    self.change_statusbar("error", str(e))

    def load_permissions(self):
        """Load the permissions of the selected key"""
        if not self.comboSelectAPI.currentText() == "":
            self.change_statusbar("wait", "Loading API key permissions...")
            # Get key of that name
            self.api_key = None
            for x in self.stored_keys:
                if x['name'] == self.comboSelectAPI.currentText():
                    self.api_key = x['key']
                    break
            if self.api_key is not None:
                # Fill the permissions sections
                try:
                    permissions = self.api_open("tokeninfo", token=self.api_key)['permissions']
                    self.fill_permissions(permissions)
                    self.api_permissions = permissions
                except Exception as e:
                    if "HTTP Error 400" in str(e):
                        self.change_statusbar("error", "Your API key is not valid.")
            else:
                self.change_statusbar("ready", "API key not valid, probably empty or corrupted.")

    def fill_permissions(self, permissions):
        """Set yes or no for each item."""
        # Get new colors to paint based on theme
        yes_style = self.adapt_line_theme("yes")
        no_style = self.adapt_line_theme("no")
        # Load everything
        all_sections = [("account", self.linePermission_Account),
                        ("builds", self.linePermission_Builds),
                        ("characters", self.linePermission_Characters),
                        ("guilds", self.linePermission_Guilds),
                        ("inventories", self.linePermission_Inventories),
                        ("progression", self.linePermission_Progression),
                        ("pvp", self.linePermission_PvP),
                        ("tradingpost", self.linePermission_Tradingpost),
                        ("unlocks", self.linePermission_Unlocks),
                        ("wallet", self.linePermission_Wallet)]
        for section in all_sections:
            if section[0] in permissions:
                section[1].setStyleSheet(yes_style)
            else:
                section[1].setStyleSheet(no_style)
        self.change_statusbar("ready", "Permissions loaded.")

    def reset_permissions(self):
        """Clean all permissions"""
        # Get new color to paint based on theme
        reset_style = self.adapt_line_theme("reset")
        # Clean everything
        permission_fields = (
            self.linePermission_Progression, self.linePermission_Wallet,
            self.linePermission_Unlocks, self.linePermission_PvP,
            self.linePermission_Inventories, self.linePermission_Guilds,
            self.linePermission_Guilds, self.linePermission_Characters,
            self.linePermission_Builds, self.linePermission_Account,
            self.linePermission_Tradingpost)
        for i in permission_fields:
            i.setStyleSheet(reset_style)

    def adapt_line_theme(self, value):
        """Get a sample of a linedit and change the theme to meet new conditions."""
        background_color = ""
        border = ""
        if value == "yes":
            background_color = "background-color: rgb(160, 200, 90)"
            border = "border: 1px solid rgb(180, 200, 90)"
        elif value == "no":
            background_color = "background-color: rgb(200, 0, 0)"
            border = "border: 1px solid rgb(220, 0, 0)"
        elif value == "reset":
            return self.style_lineedits
        # Create the new style
        new_style = self.lineInstallationFolder.styleSheet().split(";")
        for index, value in enumerate(new_style):
            if "background-color:" in value:
                new_style[index] = background_color
            elif "border:" in value:
                new_style[index] = border
        new_style = ";".join(new_style)
        return new_style

    #######################################################
    ################### BOSSES SECTION ####################
    #######################################################

    def load_bosses_section(self):
        """Load bosses section"""
        if self.checkBosses.isChecked():
            if "progression" in self.api_permissions:
                self.fill_bosses(self.api_key)
            else:
                self.reset_bosses()
                return "Raid bosses need: Progression"
        else:
            self.reset_bosses()

    def fill_bosses(self, api_key):
        """Set the correct style for each item."""
        # Get new colors to paint based on theme
        yes_style = self.adapt_line_theme("yes")
        no_style = self.adapt_line_theme("no")
        # Bosses
        bosses = [{"name": "vale_guardian", "flag": 0, "uiitem": self.lineRaidboss_valeguardian},
                  {"name": "spirit_woods", "flag": 0, "uiitem": self.lineRaidboss_spiritwoods},
                  {"name": "gorseval", "flag": 0, "uiitem": self.lineRaidboss_gorseval},
                  {"name": "sabetha", "flag": 0, "uiitem": self.lineRaidboss_sabetha},
                  {"name": "slothasor", "flag": 0, "uiitem": self.lineRaidboss_slothasor},
                  {"name": "bandit_trio", "flag": 0, "uiitem": self.lineRaidboss_trio},
                  {"name": "matthias", "flag": 0, "uiitem": self.lineRaidboss_matthias},
                  {"name": "escort", "flag": 0, "uiitem": self.lineRaidboss_glenna},
                  {"name": "keep_construct", "flag": 0, "uiitem": self.lineRaidboss_keepconstruct},
                  {"name": "twisted_castle", "flag": 0, "uiitem": self.lineRaidboss_twistedcastle},
                  {"name": "xera", "flag": 0, "uiitem": self.lineRaidboss_xera},
                  {"name": "cairn", "flag": 0, "uiitem": self.lineRaidboss_cairn},
                  {"name": "mursaat_overseer", "flag": 0, "uiitem": self.lineRaidboss_mursaat},
                  {"name": "samarog", "flag": 0, "uiitem": self.lineRaidboss_samarog},
                  {"name": "deimos", "flag": 0, "uiitem": self.lineRaidboss_deimos},
                  {"name": "soulless_horror", "flag": 0, "uiitem": self.lineRaidboss_desmina},
                  {"name": "river_of_souls", "flag": 0, "uiitem": self.lineRaidboss_riverofsouls},
                  {"name": "statues_of_grenth", "flag": 0, "uiitem": self.lineRaidboss_statues},
                  {"name": "voice_in_the_void", "flag": 0, "uiitem": self.lineRaidboss_dhuum},
                  {"name": "conjured_amalgamate", "flag": 0, "uiitem": self.lineRaidboss_conjureda},
                  {"name": "twin_largos", "flag": 0, "uiitem": self.lineRaidboss_twinlargos},
                  {"name": "qadim", "flag": 0, "uiitem": self.lineRaidboss_qadim},
                  ]
        bosses_killed = self.api_open("account", ids=["raids"], token=api_key)
        for i in bosses:
            for j in bosses_killed:
                if j == i['name']:
                    i['flag'] = 1
                    break
            if i['flag'] == 1:
                i['uiitem'].setStyleSheet(yes_style)
            else:
                i['uiitem'].setStyleSheet(no_style)

    def reset_bosses(self):
        """Clean all bosses"""
        # Get new color to paint based on theme
        reset_style = self.adapt_line_theme("reset")
        # Clean everything
        raids_fields = (
            self.lineRaidboss_valeguardian, self.lineRaidboss_spiritwoods, self.lineRaidboss_gorseval,
            self.lineRaidboss_sabetha, self.lineRaidboss_slothasor, self.lineRaidboss_trio,
            self.lineRaidboss_matthias, self.lineRaidboss_glenna, self.lineRaidboss_keepconstruct,
            self.lineRaidboss_twistedcastle, self.lineRaidboss_xera, self.lineRaidboss_cairn,
            self.lineRaidboss_mursaat, self.lineRaidboss_samarog, self.lineRaidboss_deimos,
            self.lineRaidboss_desmina, self.lineRaidboss_riverofsouls, self.lineRaidboss_statues,
            self.lineRaidboss_dhuum, self.lineRaidboss_conjureda, self.lineRaidboss_twinlargos,
            self.lineRaidboss_qadim)
        for i in raids_fields:
            i.setStyleSheet(reset_style)

    #######################################################
    ################### CURRENCY SECTION ##################
    #######################################################

    def load_currency_section(self):
        """Load currency section"""
        if self.checkCurrency.isChecked():
            if ("inventories" in self.api_permissions
                    and "wallet" in self.api_permissions
                    and "characters" in self.api_permissions):
                api_characters_names = self.api_open("characters", token=self.api_key)
                api_characters = self.api_open("characters", ids=api_characters_names, token=self.api_key)
                if type(api_characters) is dict:
                    api_characters = [api_characters]
                api_shared_inventory = self.api_open("account/inventory", token=self.api_key)
                api_materials = self.api_open("account/materials", token=self.api_key)
                api_bank = self.api_open("account/bank", token=self.api_key)
                api_wallet = self.api_open("account", ids=["wallet"], token=self.api_key)
                self.fill_currency(api_wallet, api_characters,
                                   api_shared_inventory, api_materials, api_bank)
            else:
                self.reset_currency()
                return "Currency needs: Inventories, Wallet, Characters"
        else:
            self.reset_currency()

    def fill_currency(self, api_wallet, api_characters, api_shared_inventory, api_materials, api_bank):
        """Sum the values and set the correct style for each item."""
        # Get new colors to paint based on theme
        yes_style = self.adapt_line_theme("yes")
        # Wallet
        for i in api_wallet:
            wallet_items = [{"name": "magnetite_shards", "id": 28, "uiitem": self.lineCurrency_Magnetiteshards},
                            {"name": "gaeting_crystals", "id": 39, "uiitem": self.lineCurrency_Gaetingcrystals}]
            for item in wallet_items:
                if i['id'] == item['id']:
                    item['uiitem'].setText(str(i['value']))
                    item['uiitem'].setStyleSheet(yes_style)
        # Find items everywhere
        items_to_find = [{"name": "legendary_insight", "id": 77302, "uiitem": self.lineCurrency_Legend_insights},
                         {"name": "legendary_divination", "id": 88485, "uiitem": self.lineCurrency_Legend_divinations}]
        for item in items_to_find:
            total = 0
            # Each character
            for char in api_characters:
                char_items = 0
                # Equipped items
                if "equipment" in char:
                    for equipped in char['equipment']:
                        if "id" in equipped:
                            if equipped['id'] == item['id']:
                                char_items += 1
                                break
                # Inventories
                for bag in char['bags']:
                    if bag is not None:
                        for slot in bag['inventory']:
                            if slot is not None:
                                if slot['id'] == item['id']:
                                    char_items += slot['count']
                                    break
                total += char_items
            # Shared inventory
            for slot in api_shared_inventory:
                if slot is not None:
                    if slot['id'] == item['id']:
                        total += slot['count']
            # Materials bank
            for mat in api_materials:
                if mat['id'] == item['id']:
                    total += mat['count']
                    break
            # Bank tabs
            for slot in api_bank:
                if slot is not None:
                    if slot['id'] == item['id']:
                        total += slot['count']
            # Set the UI
            item['uiitem'].setText(str(total))
            item['uiitem'].setStyleSheet(yes_style)

    def reset_currency(self):
        """Clean all currency"""
        # Get new color to paint based on theme
        reset_style = self.adapt_line_theme("reset")
        # Clean everything
        currency_fields = (self.lineCurrency_Magnetiteshards, self.lineCurrency_Gaetingcrystals,
                           self.lineCurrency_Legend_insights, self.lineCurrency_Legend_divinations,)
        for i in currency_fields:
            i.clear()
            i.setStyleSheet(reset_style)

    #######################################################
    ################ ACHIEVEMENTS SECTION #################
    #######################################################

    def load_achievements_section(self):
        """Load achievements section"""
        if self.checkAchievements.isChecked():
            if "progression" in self.api_permissions:
                api_achievs = self.api_open("account/achievements", token=self.api_key)
                self.fill_achievements(api_achievs)
            else:
                self.reset_achievements()
                return "Achievements need: Progression"
        else:
            self.reset_achievements()

    def fill_achievements(self, api_achievs):
        """Set the correct style for each item."""
        # Get new colors to paint based on theme
        yes_style = self.adapt_line_theme("yes")
        no_style = self.adapt_line_theme("no")
        # Achievements
        achievements = [{"id": 2657, "flag": 0, "uiitem": self.lineAchiev_w1_closure},
                        {"id": 2651, "flag": 0, "uiitem": self.lineAchiev_w1_lootfinder},
                        {"id": 2663, "flag": 0, "uiitem": self.lineAchiev_w1_piecingit},
                        {"id": 2654, "flag": 0, "uiitem": self.lineAchiev_w1_beyondthevale},
                        {"id": 2658, "flag": 0, "uiitem": self.lineAchiev_w1_fleethestorm},
                        {"id": 2655, "flag": 0, "uiitem": self.lineAchiev_w1_rgb},
                        {"id": 2656, "flag": 0, "uiitem": self.lineAchiev_w1_whitenoise},
                        {"id": 2647, "flag": 0, "uiitem": self.lineAchiev_w1_intothewoods},
                        {"id": 2660, "flag": 0, "uiitem": self.lineAchiev_w1_outranaghost},
                        {"id": 2665, "flag": 0, "uiitem": self.lineAchiev_w1_keepthelights},
                        {"id": 2662, "flag": 0, "uiitem": self.lineAchiev_w1_quickmarch},
                        {"id": 2667, "flag": 0, "uiitem": self.lineAchiev_w1_puttorest},
                        {"id": 2666, "flag": 0, "uiitem": self.lineAchiev_w1_angermanage},
                        {"id": 2649, "flag": 0, "uiitem": self.lineAchiev_w1_denied},
                        {"id": 2648, "flag": 0, "uiitem": self.lineAchiev_w1_spectralanomaly},
                        {"id": 2659, "flag": 0, "uiitem": self.lineAchiev_w1_fireextinguish},
                        {"id": 2664, "flag": 0, "uiitem": self.lineAchiev_w1_backdraftd},
                        {"id": 2652, "flag": 0, "uiitem": self.lineAchiev_w1_lastcannon},
                        {"id": 2661, "flag": 0, "uiitem": self.lineAchiev_w1_liftoff},
                        {"id": 2668, "flag": 0, "uiitem": self.lineAchiev_w1_myhero},
                        {"id": 2653, "flag": 0, "uiitem": self.lineAchiev_w1_undefeated},
                        {"id": 2832, "flag": 0, "uiitem": self.lineAchiev_w2_scatteredm},
                        {"id": 2826, "flag": 0, "uiitem": self.lineAchiev_w2_thebigsleep},
                        {"id": 2824, "flag": 0, "uiitem": self.lineAchiev_w2_spmastery},
                        {"id": 2830, "flag": 0, "uiitem": self.lineAchiev_w2_theshield},
                        {"id": 2821, "flag": 0, "uiitem": self.lineAchiev_w2_seimurwasw},
                        {"id": 2836, "flag": 0, "uiitem": self.lineAchiev_w2_avengerofpact},
                        {"id": 2831, "flag": 0, "uiitem": self.lineAchiev_w2_slipperyslub},
                        {"id": 2835, "flag": 0, "uiitem": self.lineAchiev_w2_environmentally},
                        {"id": 2823, "flag": 0, "uiitem": self.lineAchiev_w2_spsadist},
                        {"id": 3024, "flag": 0, "uiitem": self.lineAchiev_w3_siegethestrong},
                        {"id": 3021, "flag": 0, "uiitem": self.lineAchiev_w3_minecontrol},
                        {"id": 3016, "flag": 0, "uiitem": self.lineAchiev_w3_scourgeofwm},
                        {"id": 3014, "flag": 0, "uiitem": self.lineAchiev_w3_deconstructed},
                        {"id": 3010, "flag": 0, "uiitem": self.lineAchiev_w3_traversethetc},
                        {"id": 3017, "flag": 0, "uiitem": self.lineAchiev_w3_dismantled},
                        {"id": 3019, "flag": 0, "uiitem": self.lineAchiev_w3_downdownd},
                        {"id": 3011, "flag": 0, "uiitem": self.lineAchiev_w3_evasivemane},
                        {"id": 3022, "flag": 0, "uiitem": self.lineAchiev_w3_outrunawarg},
                        {"id": 3025, "flag": 0, "uiitem": self.lineAchiev_w3_loveisbunny},
                        {"id": 3013, "flag": 0, "uiitem": self.lineAchiev_w3_mildlyinsane},
                        {"id": 3287, "flag": 0, "uiitem": self.lineAchiev_w4_attuned},
                        {"id": 3349, "flag": 0, "uiitem": self.lineAchiev_w4_breakingin},
                        {"id": 3364, "flag": 0, "uiitem": self.lineAchiev_w4_freeatlast},
                        {"id": 3299, "flag": 0, "uiitem": self.lineAchiev_w4_greetedaslib},
                        {"id": 3342, "flag": 0, "uiitem": self.lineAchiev_w4_harshsentence},
                        {"id": 3321, "flag": 0, "uiitem": self.lineAchiev_w4_justagame},
                        {"id": 3334, "flag": 0, "uiitem": self.lineAchiev_w4_jaded},
                        {"id": 3292, "flag": 0, "uiitem": self.lineAchiev_w4_solitaryconfi},
                        {"id": 3347, "flag": 0, "uiitem": self.lineAchiev_w4_wardenwillsee},
                        {"id": 3296, "flag": 0, "uiitem": self.lineAchiev_w4_voiceofdecease},
                        {"id": 3392, "flag": 0, "uiitem": self.lineAchiev_w4_realraidertyr},
                        {"id": 4020, "flag": 0, "uiitem": self.lineAchiev_w5_silencer},
                        {"id": 3979, "flag": 0, "uiitem": self.lineAchiev_w5_deatheater},
                        {"id": 3998, "flag": 0, "uiitem": self.lineAchiev_w5_deathsaver},
                        {"id": 3993, "flag": 0, "uiitem": self.lineAchiev_w5_exileexecution},
                        {"id": 4038, "flag": 0, "uiitem": self.lineAchiev_w5_icebreaker},
                        {"id": 4033, "flag": 0, "uiitem": self.lineAchiev_w5_necrodancer},
                        {"id": 4036, "flag": 0, "uiitem": self.lineAchiev_w5_soreeyes},
                        {"id": 4004, "flag": 0, "uiitem": self.lineAchiev_w5_souledout},
                        {"id": 4037, "flag": 0, "uiitem": self.lineAchiev_w5_statuesoflimit},
                        {"id": 4010, "flag": 0, "uiitem": self.lineAchiev_w5_theferrywoman},
                        {"id": 4016, "flag": 0, "uiitem": self.lineAchiev_w5_whatisdeathmay},
                        {"id": 4423, "flag": 0, "uiitem": self.lineAchiev_w6_thunderfall},
                        {"id": 4364, "flag": 0, "uiitem": self.lineAchiev_w6_aquaassasins},
                        {"id": 4397, "flag": 0, "uiitem": self.lineAchiev_w6_dontgowater},
                        {"id": 4415, "flag": 0, "uiitem": self.lineAchiev_w6_hardhats},
                        {"id": 4355, "flag": 0, "uiitem": self.lineAchiev_w6_heroesofforge},
                        {"id": 4429, "flag": 0, "uiitem": self.lineAchiev_w6_letsnotdothat},
                        {"id": 4361, "flag": 0, "uiitem": self.lineAchiev_w6_manipulateman},
                        {"id": 4409, "flag": 0, "uiitem": self.lineAchiev_w6_mythscholar},
                        {"id": 4395, "flag": 0, "uiitem": self.lineAchiev_w6_regularstour},
                        {"id": 4416, "flag": 0, "uiitem": self.lineAchiev_w6_somedisassem},
                        {"id": 4388, "flag": 0, "uiitem": self.lineAchiev_w6_stackingswords},
                        {"id": 4404, "flag": 0, "uiitem": self.lineAchiev_w6_takingturns},
                        {"id": 4396, "flag": 0, "uiitem": self.lineAchiev_w6_firedjinnextin}]
        # Flag the ones done
        for api_achiev in api_achievs:
            for achievement in achievements:
                if api_achiev['id'] == achievement['id']:
                    if api_achiev['done']:
                        achievement['flag'] = 1
                        break
        # Set the UI
        for achievement in achievements:
            if achievement['flag'] == 1:
                achievement['uiitem'].setStyleSheet(yes_style)
            else:
                achievement['uiitem'].setStyleSheet(no_style)

    def reset_achievements(self):
        """Clean all achievements"""
        # Get new color to paint based on theme
        reset_style = self.adapt_line_theme("reset")
        # Clean everything
        achievements_fields = (
            self.lineAchiev_w1_closure, self.lineAchiev_w1_lootfinder, self.lineAchiev_w1_piecingit,
            self.lineAchiev_w1_beyondthevale, self.lineAchiev_w1_fleethestorm, self.lineAchiev_w1_rgb,
            self.lineAchiev_w1_whitenoise, self.lineAchiev_w1_intothewoods, self.lineAchiev_w1_outranaghost,
            self.lineAchiev_w1_keepthelights, self.lineAchiev_w1_quickmarch, self.lineAchiev_w1_puttorest,
            self.lineAchiev_w1_angermanage, self.lineAchiev_w1_denied, self.lineAchiev_w1_spectralanomaly,
            self.lineAchiev_w1_fireextinguish, self.lineAchiev_w1_backdraftd, self.lineAchiev_w1_lastcannon,
            self.lineAchiev_w1_liftoff, self.lineAchiev_w1_myhero, self.lineAchiev_w1_undefeated,
            self.lineAchiev_w2_scatteredm, self.lineAchiev_w2_thebigsleep, self.lineAchiev_w2_spmastery,
            self.lineAchiev_w2_theshield, self.lineAchiev_w2_seimurwasw, self.lineAchiev_w2_avengerofpact,
            self.lineAchiev_w2_slipperyslub, self.lineAchiev_w2_environmentally, self.lineAchiev_w2_spsadist,
            self.lineAchiev_w3_siegethestrong, self.lineAchiev_w3_minecontrol, self.lineAchiev_w3_scourgeofwm,
            self.lineAchiev_w3_deconstructed, self.lineAchiev_w3_traversethetc, self.lineAchiev_w3_dismantled,
            self.lineAchiev_w3_downdownd, self.lineAchiev_w3_evasivemane, self.lineAchiev_w3_outrunawarg,
            self.lineAchiev_w3_loveisbunny, self.lineAchiev_w3_mildlyinsane, self.lineAchiev_w4_attuned,
            self.lineAchiev_w4_breakingin, self.lineAchiev_w4_freeatlast, self.lineAchiev_w4_greetedaslib,
            self.lineAchiev_w4_harshsentence, self.lineAchiev_w4_justagame, self.lineAchiev_w4_jaded,
            self.lineAchiev_w4_solitaryconfi, self.lineAchiev_w4_wardenwillsee, self.lineAchiev_w4_voiceofdecease,
            self.lineAchiev_w4_realraidertyr, self.lineAchiev_w5_silencer, self.lineAchiev_w5_deatheater,
            self.lineAchiev_w5_deathsaver, self.lineAchiev_w5_exileexecution, self.lineAchiev_w5_icebreaker,
            self.lineAchiev_w5_necrodancer, self.lineAchiev_w5_soreeyes, self.lineAchiev_w5_souledout,
            self.lineAchiev_w5_statuesoflimit, self.lineAchiev_w5_theferrywoman, self.lineAchiev_w5_whatisdeathmay,
            self.lineAchiev_w6_thunderfall, self.lineAchiev_w6_aquaassasins, self.lineAchiev_w6_dontgowater,
            self.lineAchiev_w6_hardhats, self.lineAchiev_w6_heroesofforge, self.lineAchiev_w6_letsnotdothat,
            self.lineAchiev_w6_manipulateman, self.lineAchiev_w6_mythscholar, self.lineAchiev_w6_regularstour,
            self.lineAchiev_w6_somedisassem, self.lineAchiev_w6_stackingswords, self.lineAchiev_w6_takingturns,
            self.lineAchiev_w6_firedjinnextin)
        for i in achievements_fields:
            i.setStyleSheet(reset_style)

    ####################################################
    ################### MINIS SECTION ##################
    ####################################################

    def load_minis_section(self):
        """Load minis section"""
        if self.checkMinis.isChecked():
            if "unlocks" in self.api_permissions:
                api_minis = self.api_open("account/minis", token=self.api_key)
                self.fill_minis(api_minis)
            else:
                self.reset_minis()
                return "Minis need: Unlocks"
        else:
            self.reset_minis()

    def fill_minis(self, api_minis):
        """Set the correct style for each item."""
        # Minis IDs
        raid_minis = [{"id": 371, "flag": 0, "uiitem": self.label_Mini_redguardian},
                      {"id": 376, "flag": 0, "uiitem": self.label_Mini_greenguardian},
                      {"id": 373, "flag": 0, "uiitem": self.label_Mini_blueguardian},
                      {"id": 368, "flag": 0, "uiitem": self.label_Mini_valeguardian},
                      {"id": 372, "flag": 0, "uiitem": self.label_Mini_gorseval},
                      {"id": 377, "flag": 0, "uiitem": self.label_Mini_knuckles},
                      {"id": 375, "flag": 0, "uiitem": self.label_Mini_kernan},
                      {"id": 370, "flag": 0, "uiitem": self.label_Mini_karde},
                      {"id": 390, "flag": 0, "uiitem": self.label_Mini_slubling},
                      {"id": 389, "flag": 0, "uiitem": self.label_Mini_slothasor},
                      {"id": 393, "flag": 0, "uiitem": self.label_Mini_berg},
                      {"id": 394, "flag": 0, "uiitem": self.label_Mini_zane},
                      {"id": 392, "flag": 0, "uiitem": self.label_Mini_narella},
                      {"id": 391, "flag": 0, "uiitem": self.label_Mini_matthias},
                      {"id": 402, "flag": 0, "uiitem": self.label_Mini_mcleod},
                      {"id": 403, "flag": 0, "uiitem": self.label_Mini_keepconstruct},
                      {"id": 401, "flag": 0, "uiitem": self.label_Mini_xera},
                      {"id": 441, "flag": 0, "uiitem": self.label_Mini_cairn},
                      {"id": 438, "flag": 0, "uiitem": self.label_Mini_mursaat},
                      {"id": 447, "flag": 0, "uiitem": self.label_Mini_eyeofjanthir},
                      {"id": 442, "flag": 0, "uiitem": self.label_Mini_samarog},
                      {"id": 440, "flag": 0, "uiitem": self.label_Mini_whitemantle},
                      {"id": 436, "flag": 0, "uiitem": self.label_Mini_ragged_whitemantle},
                      {"id": 622, "flag": 0, "uiitem": self.label_Mini_desmina},
                      {"id": 621, "flag": 0, "uiitem": self.label_Mini_brokenking},
                      {"id": 623, "flag": 0, "uiitem": self.label_Mini_dhuum},
                      {"id": 722, "flag": 0, "uiitem": self.label_Mini_zommoros},
                      {"id": 721, "flag": 0, "uiitem": self.label_Mini_kenut},
                      {"id": 725, "flag": 0, "uiitem": self.label_Mini_nikare},
                      {"id": 723, "flag": 0, "uiitem": self.label_Mini_qadim}]
        # Flag the ones done
        for your_mini in api_minis:
            for mini in raid_minis:
                if mini['id'] == your_mini:
                    mini['flag'] = 1
                    break
        # Set the UI
        for mini in raid_minis:
            if mini['flag'] == 1:
                yes_style = QGraphicsColorizeEffect(self)
                yes_style.setColor(QColor(0, 150, 0))
                mini['uiitem'].setGraphicsEffect(yes_style)
            else:
                no_style = QGraphicsColorizeEffect(self)
                no_style.setColor(QColor(150, 0, 0))
                mini['uiitem'].setGraphicsEffect(no_style)

    def reset_minis(self):
        """Clean all minis"""
        # Clean everything
        minis_fields = (self.label_Mini_redguardian, self.label_Mini_greenguardian, self.label_Mini_blueguardian,
                        self.label_Mini_valeguardian, self.label_Mini_gorseval, self.label_Mini_knuckles,
                        self.label_Mini_kernan, self.label_Mini_karde, self.label_Mini_slubling,
                        self.label_Mini_slothasor, self.label_Mini_berg, self.label_Mini_zane,
                        self.label_Mini_narella, self.label_Mini_matthias, self.label_Mini_mcleod,
                        self.label_Mini_keepconstruct, self.label_Mini_xera, self.label_Mini_cairn,
                        self.label_Mini_mursaat, self.label_Mini_eyeofjanthir, self.label_Mini_samarog,
                        self.label_Mini_whitemantle, self.label_Mini_ragged_whitemantle, self.label_Mini_desmina,
                        self.label_Mini_brokenking, self.label_Mini_dhuum, self.label_Mini_zommoros,
                        self.label_Mini_kenut, self.label_Mini_nikare, self.label_Mini_qadim)
        for i in minis_fields:
            i.setGraphicsEffect(None)

    ####################################################
    ################### SKINS SECTION ##################
    ####################################################

    def load_skins_section(self):
        """Load skins section"""
        if self.checkSkins.isChecked():
            if "unlocks" in self.api_permissions:
                api_skins = self.api_open("account/skins", token=self.api_key)
                self.fill_skins(api_skins)
            else:
                self.reset_skins()
                return "Skins need: Unlocks"
        else:
            self.reset_skins()

    def fill_skins(self, api_skins):
        """Set the correct style for each item."""
        # Skins IDs
        raid_skins = [{"id": 6528, "flag": 0, "uiitem": self.label_Skin_vg_dagger},
                      {"id": 6532, "flag": 0, "uiitem": self.label_Skin_vg_greatsword},
                      {"id": 6536, "flag": 0, "uiitem": self.label_Skin_gorse_shield},
                      {"id": 6531, "flag": 0, "uiitem": self.label_Skin_gorse_staff},
                      {"id": 6141, "flag": 0, "uiitem": self.label_Skin_sab_rifle},
                      {"id": 6135, "flag": 0, "uiitem": self.label_Skin_sab_back},
                      {"id": 6642, "flag": 0, "uiitem": self.label_Skin_sloth_hammer},
                      {"id": 6639, "flag": 0, "uiitem": self.label_Skin_sloth_focus},
                      {"id": 6645, "flag": 0, "uiitem": self.label_Skin_matthias_staff},
                      {"id": 6630, "flag": 0, "uiitem": self.label_Skin_matthias_greatsword},
                      {"id": 6652, "flag": 0, "uiitem": self.label_Skin_matthias_longbow},
                      {"id": 6638, "flag": 0, "uiitem": self.label_Skin_matthias_shortbow},
                      {"id": 6649, "flag": 0, "uiitem": self.label_Skin_matthias_mace},
                      {"id": 6651, "flag": 0, "uiitem": self.label_Skin_matthias_shield},
                      {"id": 6626, "flag": 0, "uiitem": self.label_Skin_matthias_warhorn},
                      {"id": 6635, "flag": 0, "uiitem": self.label_Skin_matthias_pistol},
                      {"id": 6633, "flag": 0, "uiitem": self.label_Skin_matthias_torch},
                      {"id": 6805, "flag": 0, "uiitem": self.label_Skin_kc_hammer},
                      {"id": 6836, "flag": 0, "uiitem": self.label_Skin_kc_torch},
                      {"id": 6821, "flag": 0, "uiitem": self.label_Skin_kc_focus},
                      {"id": 6804, "flag": 0, "uiitem": self.label_Skin_kc_scepter},
                      {"id": 6813, "flag": 0, "uiitem": self.label_Skin_xera_scepter},
                      {"id": 6825, "flag": 0, "uiitem": self.label_Skin_xera_staff},
                      {"id": 6835, "flag": 0, "uiitem": self.label_Skin_xera_rifle},
                      {"id": 6788, "flag": 0, "uiitem": self.label_Skin_xera_sword},
                      {"id": 6810, "flag": 0, "uiitem": self.label_Skin_xera_axe},
                      {"id": 6815, "flag": 0, "uiitem": self.label_Skin_xera_dagger},
                      {"id": 6809, "flag": 0, "uiitem": self.label_Skin_xera_back},
                      {"id": 7101, "flag": 0, "uiitem": self.label_Skin_cairn_pistol},
                      {"id": 7125, "flag": 0, "uiitem": self.label_Skin_cairn_sword},
                      {"id": 7097, "flag": 0, "uiitem": self.label_Skin_mursaat_longbow},
                      {"id": 7091, "flag": 0, "uiitem": self.label_Skin_samarog_axe},
                      {"id": 7155, "flag": 0, "uiitem": self.label_Skin_samarog_shortbow},
                      {"id": 7113, "flag": 0, "uiitem": self.label_Skin_samarog_staff},
                      {"id": 7147, "flag": 0, "uiitem": self.label_Skin_samarog_warhorn},
                      {"id": 7076, "flag": 0, "uiitem": self.label_Skin_deimos_mace},
                      {"id": 7151, "flag": 0, "uiitem": self.label_Skin_deimos_hammer},
                      {"id": 7104, "flag": 0, "uiitem": self.label_Skin_deimos_staff},
                      {"id": 7114, "flag": 0, "uiitem": self.label_Skin_deimos_back},
                      {"id": 7115, "flag": 0, "uiitem": self.label_Skin_deimos_gloves},
                      {"id": 7909, "flag": 0, "uiitem": self.label_Skin_desmina_axe},
                      {"id": 7894, "flag": 0, "uiitem": self.label_Skin_desmina_hammer},
                      {"id": 7845, "flag": 0, "uiitem": self.label_Skin_river_shield},
                      {"id": 7863, "flag": 0, "uiitem": self.label_Skin_river_sword},
                      {"id": 7867, "flag": 0, "uiitem": self.label_Skin_statues_dagger},
                      {"id": 7910, "flag": 0, "uiitem": self.label_Skin_statues_greatsword},
                      {"id": 7881, "flag": 0, "uiitem": self.label_Skin_dhuum_staff},
                      {"id": 7872, "flag": 0, "uiitem": self.label_Skin_dhuum_helm},
                      {"id": 7871, "flag": 0, "uiitem": self.label_Skin_dhuum_shoulders},
                      {"id": 7848, "flag": 0, "uiitem": self.label_Skin_dhuum_gloves},
                      {"id": 7887, "flag": 0, "uiitem": self.label_Skin_dhuum_boots},
                      {"id": 8412, "flag": 0, "uiitem": self.label_Skin_conjured_shield},
                      {"id": 8398, "flag": 0, "uiitem": self.label_Skin_conjured_greatsword},
                      {"id": 8337, "flag": 0, "uiitem": self.label_Skin_largos_sword},
                      {"id": 8363, "flag": 0, "uiitem": self.label_Skin_largos_longbow},
                      {"id": 8344, "flag": 0, "uiitem": self.label_Skin_qadim_mace},
                      {"id": 8409, "flag": 0, "uiitem": self.label_Skin_qadim_pistol}]
        # Flag the ones done
        for your_skin in api_skins:
            for skin in raid_skins:
                if skin['id'] == your_skin:
                    skin['flag'] = 1
                    break
        # Set the UI
        for skin in raid_skins:
            if skin['flag'] == 1:
                yes_style = QGraphicsColorizeEffect(self)
                yes_style.setColor(QColor(0, 150, 0))
                skin['uiitem'].setGraphicsEffect(yes_style)
            else:
                no_style = QGraphicsColorizeEffect(self)
                no_style.setColor(QColor(150, 0, 0))
                skin['uiitem'].setGraphicsEffect(no_style)

    def reset_skins(self):
        """Clean all skins"""
        # Clean everything
        skins_fields = (self.label_Skin_vg_dagger, self.label_Skin_vg_greatsword, self.label_Skin_gorse_shield,
                        self.label_Skin_gorse_staff, self.label_Skin_sab_rifle, self.label_Skin_sab_back,
                        self.label_Skin_sloth_hammer, self.label_Skin_sloth_focus, self.label_Skin_matthias_staff,
                        self.label_Skin_matthias_greatsword, self.label_Skin_matthias_longbow,
                        self.label_Skin_matthias_shortbow, self.label_Skin_matthias_mace,
                        self.label_Skin_matthias_shield, self.label_Skin_matthias_warhorn,
                        self.label_Skin_matthias_pistol, self.label_Skin_matthias_torch,  self.label_Skin_kc_hammer,
                        self.label_Skin_kc_torch, self.label_Skin_kc_focus, self.label_Skin_kc_scepter,
                        self.label_Skin_xera_scepter, self.label_Skin_xera_staff, self.label_Skin_xera_rifle,
                        self.label_Skin_xera_sword, self.label_Skin_xera_axe, self.label_Skin_xera_dagger,
                        self.label_Skin_xera_back, self.label_Skin_cairn_pistol, self.label_Skin_cairn_sword,
                        self.label_Skin_mursaat_longbow, self.label_Skin_samarog_axe,
                        self.label_Skin_samarog_shortbow, self.label_Skin_samarog_staff,
                        self.label_Skin_samarog_warhorn, self.label_Skin_deimos_mace, self.label_Skin_deimos_hammer,
                        self.label_Skin_deimos_staff, self.label_Skin_deimos_back, self.label_Skin_deimos_gloves,
                        self.label_Skin_desmina_axe, self.label_Skin_desmina_hammer, self.label_Skin_river_shield,
                        self.label_Skin_river_sword, self.label_Skin_statues_dagger,
                        self.label_Skin_statues_greatsword, self.label_Skin_dhuum_staff, self.label_Skin_dhuum_helm,
                        self.label_Skin_dhuum_shoulders, self.label_Skin_dhuum_gloves, self.label_Skin_dhuum_boots,
                        self.label_Skin_conjured_shield, self.label_Skin_conjured_greatsword,
                        self.label_Skin_largos_sword, self.label_Skin_largos_longbow, self.label_Skin_qadim_mace,
                        self.label_Skin_qadim_pistol)
        for i in skins_fields:
            i.setGraphicsEffect(None)

#########################################################
################### WINDOW ADD API ######################
#########################################################


class AddNewApi(QDialog, Ui_Dialog):
    """Class for the Add New Api window"""

    def __init__(self, parent=None):
        """Set initial status"""
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setWindowIcon(QIcon(":/images/Images/Main.ico"))
        self.setFixedSize(QSize(595, 100))
        self.move(INI_OPTIONS.value("add_position", QPoint(360, 325)))
        self.buttonSave.clicked.connect(self.save_new_api)

    def save_new_api(self):
        """Validate the data. Get old keys. Add the new one. Store them."""
        # Validate the data
        if not len(self.lineKey.text()) == 72:
            self.labelInfo.setStyleSheet("color: rgb(250, 0, 0);")
            self.labelInfo.setText("Error: The provided Key doesn't fits 72 characters.")
        elif self.lineName.text() == "":
            self.labelInfo.setStyleSheet("color: rgb(250, 0, 0);")
            self.labelInfo.setText("Error: You must provide a name for that key.")
        else:
            self.labelInfo.clear()
            # Get old keys
            keys = MainForm.get_stored_keys()
            # Add the new key
            keys.append({'name': self.lineName.text(), 'key': self.lineKey.text()})
            # Save them into file
            INI_OPTIONS.setValue("api_keys", keys)
            self.labelInfo.setStyleSheet("color: rgb(0, 190, 0);")
            self.labelInfo.setText("Success: Key stored.")

    def closeEvent(self, event):
        """Write window position to config file"""
        INI_OPTIONS.setValue("add_position", self.pos())
        event.accept()

###########################################
################ QMESSAGEBOX ##############
###########################################


def popup_question(title, message):
    """Generate a popup that requests if you are really sure that you want to delete a record."""
    msgbox = QMessageBox()
    msgbox.setWindowTitle(title)
    msgbox.setIcon(QMessageBox.Warning)
    msgbox.setText(message)
    buttonyes = QPushButton("Yes")
    msgbox.addButton(buttonyes, QMessageBox.YesRole)
    buttonno = QPushButton("No")
    msgbox.addButton(buttonno, QMessageBox.NoRole)
    msgbox.exec_()
    if msgbox.clickedButton() == buttonno:
        return False
    else:
        return True

######################################################
##################### INITIALIZE #####################
######################################################


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Make sure you scale for high DPI
    environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    app.setAttribute(Qt.AA_EnableHighDpiScaling)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)
    # Launch the window
    window = MainForm()
    window.show()
    sys.exit(app.exec_())

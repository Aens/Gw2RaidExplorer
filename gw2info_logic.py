import json
import urllib.request
import urllib.parse
import webbrowser
import hashlib
import sys
import psutil
import subprocess
from pathlib import Path
from PySide2 import QtWidgets
from PySide2.QtGui import QIcon, QColor
from PySide2.QtCore import Qt, QEvent, QPoint, QSize, QSettings
from gw2info_ui import Ui_MainWindow
from add_ui import Ui_Dialog

PROGRAM_VERSION = "090"
PROGRAM_AUTHOR = "(Made by Elrey.5472) https://github.com/Aens"
INI_OPTIONS = QSettings("options.ini", QSettings.IniFormat)


########################################################
##################### MAIN WINDOW ######################
########################################################

class MainForm(QtWidgets.QMainWindow, Ui_MainWindow):
    """Main window of the program."""

    def __init__(self, parent=None):
        """Set the initial state of the window (size/pos).
        Connect the buttons to their functions.
        Connect the events to their triggers.
        Set proper colors to their items.
        And fire up initial functions."""
        QtWidgets.QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.setWindowIcon(QIcon(":/images/Images/Main.ico"))
        self.setWindowTitle("Gw2 API Raid Explorer {0}".format(PROGRAM_AUTHOR))
        # Initial window size/pos last saved. Use default values for first time
        self.setFixedSize(QSize(1030, 840))
        self.move(INI_OPTIONS.value("menu_position", QPoint(350, 250)))
        self.lineInstallationFolder.setText((INI_OPTIONS.value("installation_folder", "")))
        # Left side Buttons
        self.botonThemeLight.clicked.connect(lambda: self.initialize_colors("light"))
        self.botonThemeDark.clicked.connect(lambda: self.initialize_colors("dark"))
        self.botonThemeDefault.clicked.connect(lambda: self.initialize_colors("default"))
        self.botonLanguage_english.clicked.connect(lambda: self.initialize_language("en"))
        self.botonLanguage_spanish.clicked.connect(lambda: self.initialize_language("es"))
        self.botonWebsite_Anet.clicked.connect(self.open_web_anet)
        self.botonLoad.clicked.connect(self.load_api)
        self.botonAddAPI.clicked.connect(self.open_window_add)
        self.botonDeleteAPI.clicked.connect(self.delete_api)
        # Right side buttons
        self.botonFindfolder.clicked.connect(self.set_installation_folder)
        self.botonArcDps.clicked.connect(self.update_arcdps)
        self.botonArcDps_mechanics.clicked.connect(self.update_arcdps_mechanics)
        self.botonWebsite_arcdps.clicked.connect(self.open_web_arcdps)
        self.botonWebsite_arcdpsmechanics.clicked.connect(self.open_web_arcdpsmechanics)
        self.botonLaunchgame.clicked.connect(self.launch_game)
        self.botonClosegame.clicked.connect(self.close_game)
        self.botonWebsite_dulfy.clicked.connect(self.open_web_dulfy)
        self.botonWebsite_builds.clicked.connect(self.open_web_builds)
        self.botonWebsite_builds_alternative.clicked.connect(self.open_web_builds_alternative)
        self.botonWebsite_dpsreport.clicked.connect(self.open_web_dpsreport)
        self.botonWebsite_killproof.clicked.connect(self.open_web_killproof)
        self.botonWebsite_raidar.clicked.connect(self.open_web_raidar)
        # Events
        self.comboSelectAPI.installEventFilter(self)
        self.comboSelectAPI.activated.connect(self.load_combo_stuff)
        self.checkBosses.stateChanged.connect(lambda: self.save_checkboxes_status(self.checkBosses))
        self.checkMinis.stateChanged.connect(lambda: self.save_checkboxes_status(self.checkMinis))
        self.checkChallenges.stateChanged.connect(lambda: self.save_checkboxes_status(self.checkChallenges))
        self.checkCurrency.stateChanged.connect(lambda: self.save_checkboxes_status(self.checkCurrency))
        # Check if we are ready to work
        self.debug_mode = True
        self.stored_keys = []
        self.api_key = None
        self.api_permissions = None
        self.style_background = ""
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
            print(address)
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
        for checkbox in [self.checkBosses, self.checkCurrency, self.checkChallenges, self.checkMinis]:
            if self.load_checkboxes_status(checkbox) == "true":
                checkbox.setChecked(True)
        # Check if there is something stored
        self.fill_combo_selectapi()
        if not self.stored_keys:
            warning.append("There is no API keys yet, add one.")
        else:
            self.load_permissions()
        # Check if there is warnings
        if len(warning) >= 1:
            self.change_statusbar("error", ",".join(warning))
            return False
        else:
            self.change_statusbar("ready", "Everything seems fine. Program ready.")
            # Check if we are in the last version
            online_version = self.check_online_version()
            if int(PROGRAM_VERSION) < int(online_version):
                self.change_statusbar("special", "There is a new version availible, you should download it.")
            return True

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
                               "QTabWidget::pane {border-radius: 5px;border: 2px solid rgb(150, 150, 150);}"
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
                              "QTabWidget::pane {border-radius: 5px;border: 2px solid black;}"
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
                              "QTabWidget::pane {border-radius: 5px;border: 2px solid rgb(10, 105, 170);}"
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
        self.style_background = colors['backgroundcolor']
        self.change_statusbar("ready", "New theme loaded, you may need to reload data to assign correct colors to it.")

    def set_colors(self, widget, colors):
        """Paint the initial colors for the controls"""
        for item in widget.children():
            item_type = item.metaObject().className()
            if item_type == "QLineEdit":
                if item.isReadOnly():
                    item.setStyleSheet(colors['inputcolorreadonly'])
                else:
                    item.setStyleSheet(colors['inputcolor'])
            elif item_type == "QPlainTextEdit":
                item.setStyleSheet(colors['inputcolor'])
            elif item_type == "QTextEdit":
                item.setStyleSheet(colors['inputcolor'])
            elif item_type == "QLabel":
                item.setStyleSheet(colors['labelcolor'])
            elif item_type == "QPushButton":
                item.setStyleSheet(colors['buttoncolor'])
            elif item_type == "QComboBox":
                item.setStyleSheet(colors['dropdowncolor'])
            # SPECIALS: Set background to it and then re-iterate on these items
            elif item_type == "QMainWindowLayout" or item_type == "QWidget":
                widget.setStyleSheet(colors['backgroundcolor'])
                self.set_colors(item, colors)
            # SPECIALS: Set style to it and then re-iterate on these items
            elif item_type == "QGroupBox":
                item.setStyleSheet(colors['groupstyle'])
                self.set_colors(item, colors)
            elif item_type == "QTabWidget":
                item.setStyleSheet(colors['tabstyle'])
                self.set_colors(item, colors)
            else:
                pass

    def initialize_language(self, lang):
        """Iterate over every widget to paint them."""
        if lang == "en":
            self.change_statusbar("special", "Languages are not programmed yet.")
            INI_OPTIONS.setValue("lang", "en")
        elif lang == "es":
            self.change_statusbar("special", "Languages are not programmed yet.")
            INI_OPTIONS.setValue("lang", "es")

    @staticmethod
    def check_online_version():
        """Check if we need an update."""
        version_file = "https://raw.githubusercontent.com/Aens/Gw2RaidExplorer/master/version.txt"
        address = urllib.parse.quote(version_file, safe='/:=', encoding="utf-8", errors="strict")
        address = urllib.request.urlopen(address).read().decode('utf8')
        return address

    #######################################################
    ################## BUTTONS and EVENTS #################
    #######################################################

    def fill_combo_selectapi(self):
        """Fill the combo with all the APIs"""
        self.comboSelectAPI.clear()
        self.stored_keys = get_stored_keys()
        for key in self.stored_keys:
            self.comboSelectAPI.addItem(key['name'])

    def load_combo_stuff(self):
        """Load the stuff on selecting anything on the combo"""
        self.reset_everything()
        self.load_permissions()

    @staticmethod
    def open_window_add():
        """Open the Add API window."""
        addwindow = AddNewApi()
        addwindow.exec_()

    def delete_api(self):
        """Delete the selected API from database"""
        self.change_statusbar("wait", "Deleting key...")
        if not self.comboSelectAPI.currentText() == "":
            if popup_delete():
                # get all keys
                keys = get_stored_keys()
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

    #######################################################
    ################## ARCDPS AND PLUGINS #################
    #######################################################

    def set_installation_folder(self):
        """Set the installation folder"""
        folderpath = QtWidgets.QFileDialog.getExistingDirectory()
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
            if self.file_exists(local_file):
                # Get both md5
                local_file_md5 = self.get_hash_of_file(local_file)
                address = urllib.parse.quote(online_file_md5, safe='/:=', encoding="utf-8", errors="strict")
                address = urllib.request.urlopen(address).read().decode('utf8')
                online_md5 = address.split(" ")[0]
                # Compare online MD5 with local md5
                if online_md5 == local_file_md5:
                    self.change_statusbar("ready", "ArcDps was already updated.")
                else:
                    # Download files and replace them
                    self.change_statusbar("wait", "ArcDps is being updated...")
                    urllib.request.urlretrieve(online_file, local_file)
                    urllib.request.urlretrieve(online_file_bt, local_file_bt)
                    self.change_statusbar("ready", "ArcDps has been updated.")
            else:
                # Download files
                try:
                    self.change_statusbar("wait", "ArcDps is not installed, downloading...")
                    urllib.request.urlretrieve(online_file, local_file)
                    urllib.request.urlretrieve(online_file_bt, local_file_bt)
                    self.change_statusbar("ready", "ArcDps has been Installed.")
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
                try:
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
                        subprocess.call(file + " -maploadinfo")
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
        self.reset_challenges()
        self.reset_minis()

    def load_api(self):
        """Load all the data of this API"""
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
            # Fill Raid challenges section
            self.change_statusbar("wait", "Loading Challenges section...")
            challenges = self.load_challenges_section()
            self.change_statusbar("ready", "Challenges section loaded.")
            # Fill Minis section
            self.change_statusbar("wait", "Loading Minis section...")
            minis = self.load_minis_section()
            self.change_statusbar("ready", "Minis section loaded.")
            # Final message
            warning = []
            for result in [bosses, currency, challenges, minis]:
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
            background_color = "background-color: rgb(150, 150, 150)"
        # Create the new style
        new_style = self.lineRaidboss_valeguardian.styleSheet().split(";")
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
            if i['flag'] == 1:
                i['uiitem'].setText("YES")
                i['uiitem'].setStyleSheet(yes_style)
            else:
                i['uiitem'].setText("NO")
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
            i.clear()
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
                for equipped in char['equipment']:
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
    ################## CHALLENGES SECTION #################
    #######################################################

    def load_challenges_section(self):
        """Load challenges section"""
        if self.checkChallenges.isChecked():
            if "progression" in self.api_permissions:
                api_achievs = self.api_open("account/achievements", token=self.api_key)
                self.fill_challenges(api_achievs)
            else:
                self.reset_challenges()
                return "Challenges need: Progression"
        else:
            self.reset_challenges()

    def fill_challenges(self, api_achievs):
        """Set the correct style for each item."""
        # Get new colors to paint based on theme
        yes_style = self.adapt_line_theme("yes")
        no_style = self.adapt_line_theme("no")
        # Challenge Modes
        challenges = [{"id": 3019, "flag": 0, "uiitem": self.lineRaidboss_keepconstruct_cm},
                      {"id": 3334, "flag": 0, "uiitem": self.lineRaidboss_cairn_cm},
                      {"id": 3287, "flag": 0, "uiitem": self.lineRaidboss_mursaat_cm},
                      {"id": 3342, "flag": 0, "uiitem": self.lineRaidboss_samarog_cm},
                      {"id": 3292, "flag": 0, "uiitem": self.lineRaidboss_deimos_cm},
                      {"id": 3993, "flag": 0, "uiitem": self.lineRaidboss_desmina_cm},
                      {"id": 3979, "flag": 0, "uiitem": self.lineRaidboss_dhuum_cm},
                      {"id": 4416, "flag": 0, "uiitem": self.lineRaidboss_conjureda_cm},
                      {"id": 4429, "flag": 0, "uiitem": self.lineRaidboss_twinlargos_cm},
                      {"id": 4355, "flag": 0, "uiitem": self.lineRaidboss_qadim_cm}]
        # Flag the ones done
        for achiev in api_achievs:
            for challenge in challenges:
                if achiev['id'] == challenge['id']:
                    if achiev['done']:
                        challenge['flag'] = 1
        # Set the UI
        for challenge in challenges:
            if challenge['flag'] == 1:
                challenge['uiitem'].setText("YES")
                challenge['uiitem'].setStyleSheet(yes_style)
            else:
                challenge['uiitem'].setText("NO")
                challenge['uiitem'].setStyleSheet(no_style)

    def reset_challenges(self):
        """Clean all challenges"""
        # Get new color to paint based on theme
        reset_style = self.adapt_line_theme("reset")
        # Clean everything
        achievements_fields = (
            self.lineRaidboss_keepconstruct_cm, self.lineRaidboss_cairn_cm, self.lineRaidboss_mursaat_cm,
            self.lineRaidboss_samarog_cm, self.lineRaidboss_deimos_cm, self.lineRaidboss_desmina_cm,
            self.lineRaidboss_dhuum_cm, self.lineRaidboss_conjureda_cm, self.lineRaidboss_twinlargos_cm,
            self.lineRaidboss_qadim_cm)
        for i in achievements_fields:
            i.clear()
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
        # Set the UI
        for mini in raid_minis:
            if mini['flag'] == 1:
                yes_style = QtWidgets.QGraphicsColorizeEffect(self)
                yes_style.setColor(QColor(0, 150, 0))
                mini['uiitem'].setGraphicsEffect(yes_style)
            else:
                no_style = QtWidgets.QGraphicsColorizeEffect(self)
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

#########################################################
################### WINDOW ADD API ######################
#########################################################


class AddNewApi(QtWidgets.QDialog, Ui_Dialog):
    """Class for the Add New Api window"""

    def __init__(self, parent=None):
        """Set initial status"""
        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)
        # self.setAttribute(Qt.WA_DeleteOnClose)
        self.setFixedSize(QSize(595, 100))
        self.move(INI_OPTIONS.value("add_position", QPoint(360, 325)))
        self.botonSave.clicked.connect(self.save_new_api)

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
            keys = get_stored_keys()
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

#################################################
##################### UTILS #####################
#################################################


def get_stored_keys():
    """Get stored APIs from database, which is a list of dicts."""
    stored_keys = []
    for key in INI_OPTIONS.value("api_keys", []):
        stored_keys.append(key)
    return stored_keys

###########################################
################ QMESSAGEBOX ##############
###########################################


def popup_delete():
    """Generate a popup that requests if you are really sure that you want to delete a record."""
    msgbox = QtWidgets.QMessageBox()
    msgbox.setWindowTitle("Security check.")
    msgbox.setIcon(QtWidgets.QMessageBox.Warning)
    msgbox.setText("Are you sure that you want to delete that key?")
    botonyes = QtWidgets.QPushButton("Yes")
    msgbox.addButton(botonyes, QtWidgets.QMessageBox.YesRole)
    botonno = QtWidgets.QPushButton("No")
    msgbox.addButton(botonno, QtWidgets.QMessageBox.NoRole)
    msgbox.exec_()
    if msgbox.clickedButton() == botonno:
        return False
    else:
        return True

######################################################
##################### INITIALIZE #####################
######################################################


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    # Make sure you scale for high DPI
    app.setAttribute(Qt.AA_EnableHighDpiScaling)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)
    # Launch the window
    window = MainForm()
    window.show()
    sys.exit(app.exec_())

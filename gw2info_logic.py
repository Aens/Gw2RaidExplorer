import json
import urllib.request
import urllib.parse
import webbrowser
import hashlib
from pathlib import Path
from PySide2 import QtWidgets
from PySide2.QtGui import QColor, QIcon
from PySide2.QtCore import QFile, Qt, QEvent, QPoint, QSize, QSettings
from gw2info_ui import Ui_MainWindow
from add_ui import Ui_Dialog

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
        self.setWindowIcon(QIcon("images\\Main.ico"))
        # Initial window size/pos last saved. Use default values for first time
        self.setFixedSize(QSize(1050, 560))
        self.move(ini_options.value("menu_position", QPoint(350, 250)))
        self.lineInstallationFolder.setText((ini_options.value("installation_folder", "")))
        # Buttons
        self.botonLoad.clicked.connect(self.load_api)
        self.botonAddAPI.clicked.connect(self.open_window_add)
        self.botonDeleteAPI.clicked.connect(self.delete_api)
        # Bottom buttons
        self.botonFindfolder.clicked.connect(self.set_installation_folder)
        self.botonArcDps.clicked.connect(self.update_arcdps)
        self.botonArcDps_mechanics.clicked.connect(self.update_arcdps_mechanics)
        self.botonWebsite_arcdps.clicked.connect(self.open_web_arcdps)
        self.botonWebsite_arcdpsmechanics.clicked.connect(self.open_web_arcdpsmechanics)
        self.botonWebsite_dulfy.clicked.connect(self.open_web_dulfy)
        self.botonWebsite_builds.clicked.connect(self.open_web_builds)
        self.botonWebsite_builds_alternative.clicked.connect(self.open_web_builds_alternative)
        self.botonWebsite_dpsreport.clicked.connect(self.open_web_dpsreport)
        self.botonWebsite_killproof.clicked.connect(self.open_web_killproof)
        self.botonWebsite_raidar.clicked.connect(self.open_web_raidar)
        # Events
        self.comboSelectAPI.installEventFilter(self)
        # Special colors
        self.set_colors()
        # Check if we are ready to work
        self.check_if_ready()

    ################################################
    ##################### BASICS ###################
    ################################################

    def closeEvent(self, event):
        """Write window position to config file"""
        ini_options.setValue("menu_position", self.pos())
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
            self.statusbar.setStyleSheet("background-color: rgb(234, 140, 6);\n"
                                    "color: rgb(0, 0, 0);")
            self.statusbar.showMessage("WAIT: " + message)
        elif statusmode == "ready":
            self.statusbar.setStyleSheet("background-color: rgb(217, 217, 217);\n"
                                        "color: rgb(0, 0, 0);")
            self.statusbar.showMessage("READY: " + message)
        elif statusmode == "error":
            self.statusbar.setStyleSheet("background-color: rgb(200, 0, 0);\n"
                                    "color: rgb(255, 255, 255);")
            self.statusbar.showMessage("ERROR: " + message)
        elif statusmode == "special":
            self.statusbar.setStyleSheet("background-color: rgb(190, 1, 190);\n"
                                    "color: rgb(255, 255, 255);")
            self.statusbar.showMessage("SPECIAL: " + message)

    def set_colors(self):
        """Set the initial colors for the controls"""
        #TBD to let the user use custom colors

    ###############################################
    ################### ON LOAD ###################
    ###############################################

    def check_if_ready(self):
        """Make sure we are ready to work."""
        self.change_statusbar("wait", "Checking if everything is fine...")
        warning = []
        # Check if there is something stored
        self.fill_combo_selectapi()
        if self.stored_keys == []:
            warning.append("There is no API keys yet, add one.")
        # Check if there is warnings
        if len(warning) >= 1:
            self.change_statusbar("error", ",".join(warning))
            return False
        else:
            self.change_statusbar("ready", "Everything seems fine. Program ready.")
            return True

    #######################################################
    ################## BUTTONS and EVENTS #################
    #######################################################

    def fill_combo_selectapi(self):
        """Fill the combo with all the APIs"""
        self.comboSelectAPI.clear()
        self.stored_keys = get_stored_keys()
        for key in self.stored_keys:
            self.comboSelectAPI.addItem(key['name'])

    def open_window_add(self):
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
                ini_options.setValue("api_keys", keys)
                # Clean it up
                self.comboSelectAPI.clear()
                self.change_statusbar("ready", "API key deleted from local database.")
            else:
                self.change_statusbar("ready", "Key not deleted ^^")
        else:
            self.change_statusbar("error", "There is no API key selected.")

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
        self.lineInstallationFolder.setText(folderpath)
        ini_options.setValue("installation_folder", folderpath)

    def check_folder_is_right(self):
        """Check that there is no issues with that folder"""
        folder = self.lineInstallationFolder.text()
        if folder == "":
            self.change_statusbar("error", "You need to set your GW2 installation folder above.")
        elif not "Guild Wars 2" in folder and not "bin64" in folder:
            self.change_statusbar("error", "You didn't set the folder bin64 of Guild Wars 2")
        else:
            self.change_statusbar("ready", "Installation folder verified.")
            return True
        return False

    def get_hash_of_file(self, filepath):
        """Get the hash of a file"""
        hash_md5 = hashlib.md5()
        with open(filepath, "rb") as file_to_check:
            for chunk in iter(lambda: file_to_check.read(4096), b""):
                hash_md5.update(chunk)
            return hash_md5.hexdigest()

    def file_exists(self, filename):
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
            local_file = '{0}/d3d9.dll'.format(self.lineInstallationFolder.text())
            local_file_bt = '{0}/d3d9_arcdps_buildtemplates.dll'.format(self.lineInstallationFolder.text())
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
                self.change_statusbar("wait", "ArcDps is not installed, downloading...")
                urllib.request.urlretrieve(online_file, local_file)
                urllib.request.urlretrieve(online_file_bt, local_file_bt)
                self.change_statusbar("ready", "ArcDps has been Installed.")

    def update_arcdps_mechanics(self):
        """Install or update ArcDps Mechanics plugin."""
        if self.check_folder_is_right():
            self.change_statusbar("wait", "Verifying hash file of ArcDps Mechanics Addon...")
            # Files
            local_file = '{0}/d3d9_arcdps_mechanics.dll'.format(self.lineInstallationFolder.text())
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
                self.change_statusbar("wait", "ArcDps Mechanics Addon is not installed, downloading...")
                urllib.request.urlretrieve(online_file, local_file)
                self.change_statusbar("ready", "ArcDps Mechanics Addon has been Installed.")

    ###############################################################
    ################### MAIN LOADING API CODE #####################
    ###############################################################

    def load_api(self):
        """Load all the data of this API"""
        self.change_statusbar("wait", "Loading your data...")
        if self.comboSelectAPI.currentText() == "":
            self.change_statusbar("error", "There is no API key selected.")
        else:
            # Get key of that name
            api_key = None
            for x in self.stored_keys:
                if x['name'] == self.comboSelectAPI.currentText():
                    api_key = x['key']
            if api_key is not None:
                # Fill the permissions sections
                try:
                    permissions = api_open("tokeninfo", token=api_key)['permissions']
                    self.fill_permissions(permissions)
                    # Fill each section now
                    self.change_statusbar("wait", "Loading weekly bosses...")
                    self.fill_raid_bosses(api_key)
                    self.change_statusbar("wait", "Loading currencies...")
                    self.fill_wallet_currencies(api_key)
                    self.change_statusbar("wait", "Loading challenge modes...")
                    self.fill_achievements(api_key)
                    self.change_statusbar("ready", "API data loaded.")
                except Exception as e:
                    if "HTTP Error 400" in str(e) :
                        self.change_statusbar("error", "Your API key is not valid.")
                        self.reset_permissions()
                        self.reset_raidstuff()
                        self.reset_walletstuff()
                        self.reset_achievementsstuff()
                    else:
                        self.change_statusbar("error", str(e))
            else:
                self.change_statusbar("ready", "API key not valid, probably empty or corrupted.")

    def fill_permissions(self, permissions):
        """Set yes or no for each item."""
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
                section[1].setText("YES")
                section[1].setStyleSheet("background-color: rgb(160, 200, 90);")
            else:
                section[1].setText("NO")
                section[1].setStyleSheet("background-color: rgb(200, 0, 0);")

    def fill_raid_bosses(self, api_key):
        """Reset values and set yes or no for each item."""
        self.reset_raidstuff()
        if self.linePermission_Progression.text() == "YES":
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
            bosses_killed = api_open("account", ids=["raids"], token=api_key)
            for i in bosses:
                for j in bosses_killed:
                    if j == i['name']:
                        i['flag'] = 1
                if i['flag'] == 1:
                    i['uiitem'].setText("YES")
                    i['uiitem'].setStyleSheet("background-color: rgb(160, 200, 90);")
                else:
                    i['uiitem'].setText("NO")
                    i['uiitem'].setStyleSheet("background-color: rgb(200, 0, 0);")

    def fill_wallet_currencies(self, api_key):
        """Reset values and set new ones."""
        self.reset_walletstuff()
        if self.linePermission_Wallet.text() == "YES":
            api_wallet = api_open("account", ids=["wallet"], token=api_key)
            for i in api_wallet:
                if i['id'] == 28: # ID for magnetites is 28
                    self.lineWallet_Magnetiteshards.setText(str(i['value']))
                    self.lineWallet_Magnetiteshards.setStyleSheet("background-color: rgb(190, 120, 50);")
                if i['id'] == 39:  # ID for gaeting is 39
                    self.lineWallet_Gaetingcrystals.setText(str(i['value']))
                    self.lineWallet_Gaetingcrystals.setStyleSheet("background-color: rgb(190, 120, 50);")

    def fill_achievements(self, api_key):
        """Reset values and set yes or no for each item."""
        self.reset_achievementsstuff()
        if self.linePermission_Progression.text() == "YES":
            challenges = [{"id": 3019, "flag": 0, "uiitem": self.lineRaidboss_keepconstruct_cm},
                          {"id": 3334, "flag": 0, "uiitem": self.lineRaidboss_cairn_cm},
                          {"id": 3287, "flag": 0, "uiitem": self.lineRaidboss_mursaat_cm},
                          {"id": 3342, "flag": 0, "uiitem": self.lineRaidboss_samarog_cm},
                          {"id": 3292, "flag": 0, "uiitem": self.lineRaidboss_deimos_cm},
                          {"id": 3993, "flag": 0, "uiitem": self.lineRaidboss_desmina_cm},
                          {"id": 3979, "flag": 0, "uiitem": self.lineRaidboss_dhuum_cm},
                          {"id": 4416, "flag": 0, "uiitem": self.lineRaidboss_conjureda_cm},
                          {"id": 4429, "flag": 0, "uiitem": self.lineRaidboss_twinlargos_cm},
                          {"id": 4355, "flag": 0, "uiitem": self.lineRaidboss_qadim_cm},
                      ]
            account_achievs = api_open("account", ids=["achievements"], token=api_key)
            for achiev in account_achievs:
                for challenge in challenges:
                    if achiev['id'] == challenge['id']:
                        if achiev['done']:
                            challenge['flag'] = 1
            for challenge in challenges:
                if challenge['flag'] == 1:
                    challenge['uiitem'].setText("YES")
                    challenge['uiitem'].setStyleSheet("background-color: rgb(160, 200, 90);")
                else:
                    challenge['uiitem'].setText("NO")
                    challenge['uiitem'].setStyleSheet("background-color: rgb(200, 0, 0);")

    def reset_permissions(self):
        """Clean all permissions stuff"""
        permission_fields = (
            self.linePermission_Progression, self.linePermission_Wallet,
            self.linePermission_Unlocks, self.linePermission_PvP,
            self.linePermission_Inventories, self.linePermission_Guilds,
            self.linePermission_Guilds, self.linePermission_Characters,
            self.linePermission_Builds, self.linePermission_Account,
            self.linePermission_Tradingpost)
        for i in permission_fields:
            i.setText("")
            i.setStyleSheet("background-color: rgb(150, 150, 150);")

    def reset_raidstuff(self):
        """Clean all raid stuff"""
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
            i.setText("")
            i.setStyleSheet("background-color: rgb(150, 150, 150);")

    def reset_walletstuff(self):
        """Clean all wallet stuff"""
        wallet_fields = (self.lineWallet_Magnetiteshards, self.lineWallet_Gaetingcrystals)
        for i in wallet_fields:
            i.setText("")
            i.setStyleSheet("background-color: rgb(150, 150, 150);")

    def reset_achievementsstuff(self):
        """Clean all achievements stuff"""
        achievements_fields = (
            self.lineRaidboss_keepconstruct_cm, self.lineRaidboss_cairn_cm, self.lineRaidboss_mursaat_cm,
            self.lineRaidboss_samarog_cm, self.lineRaidboss_deimos_cm, self.lineRaidboss_desmina_cm,
            self.lineRaidboss_dhuum_cm, self.lineRaidboss_conjureda_cm, self.lineRaidboss_twinlargos_cm,
            self.lineRaidboss_qadim_cm)
        for i in achievements_fields:
            i.setText("")
            i.setStyleSheet("background-color: rgb(150, 150, 150);")


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
        self.move(ini_options.value("add_position", QPoint(360, 325)))
        self.botonSave.clicked.connect(self.save_new_api)

    def save_new_api(self):
        """Validate the data. Get old keys. Add the new one. Store them."""
        # Validate the data
        if not len(self.lineKey.text()) == 72:
            self.labelInfo.setText("Error: The provided Key doesn't fits 72 characters.")
        elif self.lineName.text() == "":
            self.labelInfo.setText("Error: You must provide a name for that key.")
        else:
            self.labelInfo.clear()
            # Get old keys
            keys = get_stored_keys()
            # Add the new key
            keys.append({'name': self.lineName.text(), 'key': self.lineKey.text()})
            # Save them into file
            ini_options.setValue("api_keys", keys)
            self.labelInfo.setText("Success: Key stored.") #TBD green color

    def closeEvent(self, event):
        """Write window position to config file"""
        ini_options.setValue("add_position", self.pos())
        event.accept()

#################################################
##################### UTILS #####################
#################################################

def get_stored_keys():
    """Get stored APIs from database, which is a list of dicts."""
    stored_keys = []
    for key in ini_options.value("api_keys", []):
        stored_keys.append(key)
    return stored_keys

def api_open(section, **keyarguments):
    """Build the right address"""
    address = "https://api.guildwars2.com/v2/"+section
    separator = "?"
    if 'ids' in keyarguments:
        if len(keyarguments['ids']) > 1:
            address = address+"?ids="+",".join(keyarguments['ids'])
            separator = "&"
        else:
            address = address+"/"+keyarguments['ids'][0]
    #check for special parameters
    if 'token' in keyarguments:
        address = address+separator+"access_token="+keyarguments['token']
    elif 'lang' in keyarguments:
        address = address+separator+"lang="+keyarguments['lang']
    #now encode, debug and open it
    address = urllib.parse.quote(address, safe='/:=', encoding="utf-8", errors="strict")
    address = urllib.request.urlopen(address).read().decode('utf8')
    return json.loads(address)

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
    import sys
    ini_options = QSettings("options.ini", QSettings.IniFormat)
    app = QtWidgets.QApplication(sys.argv)
    window = MainForm()
    window.show()
    sys.exit(app.exec_())


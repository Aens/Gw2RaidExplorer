# Gw2RaidExplorer
A tool to check raid-based stuff of Guild Wars 2.
You can download executable version
[here](https://github.com/Aens/Gw2RaidExplorer/releases).

* Download the `.rar` file.
* Extract it on any folder with any program (e.g. winrar, 7zip, etc)
* Execute the **Gw2RaidExplorer** file with a red skull icon.

## For developers
If you want to compile it yourself, make sure you are using Python 3.7.

## How to update?
If you need to update this program, make sure to backup your
**options.ini file**, that's where your API keys are stored.
It's safe to delete/replace everything else.

# Changelog

### Version 1.0
-Redesign: I didn't like how the sections were made. It was confusing to know from which raid is a skin/mini. Now that's not an issue anymore.
-Fixed: Asigning colors would iterate over the wrong widgets and reset would always set it gray instead of theme.
-Fixed: Trying to download files for arcdps would crash the program under specific circunstances.
-New: Added a donate button for nice people that wants to support me.
-New: Achievements section (Visually, still can be improved, but at least data load/programming part is done).

#### Things To Be Done (TBD) in 1.0 before we can release it:
-Redesign: The "you can download a new version" message has been replaced by a prompt to directly download new versions so you don't have to enter the website anymore (you still need to install it, though).
-Fixed: Start Guild Wars 2 on a new thread to not stall the main thread.
-Fixed: Blurry on high DPI scales.
-Fixed: Currency earned "this week" might be imposible. https://en-forum.guildwars2.com/discussion/67421/week-magnetite-shards-gaeting-crystals#latest
-New: Languages section.
-New: Titles section.

### Version 0.9
* Fixed: Added right icon to the windows.
* Fixed: Reduced size of resource files because I had way-too-big icon files.
* Fixed: Removed wrong GUI notes.
* Fixed: Now checks permissions better in order to not create forbidden
  API calls.
* Fixed: Loading of LIs and DIs was broken.
* Fixed: Added right theme to the "Add New API" window.
* New: Added a debug mode to see all API calls to ANet servers.
* New: Added Minis section.
* New: Added skins section.
* New: Added a button to go to the program website (github/Aens).
* Redesign: The entire permissions code has been revamped.
  This should make the requests faster.
* Redesign: Most of the colors system has been re-coded.
  This should make it prettier.
* Maybe Fixed: Investigation on DPI Scaling continues.
  A new fix has been added, please test it out.

### Version 0.8
* Changed: Installation path changed for base folder, not bin64.
* Fixed: Fixed a crash if installation folder was wrong.
* Fixed: Don't clear installation path if selection is cancelled.
* Fixed: Enabled auto-scale for high DPI scaling.
* New: Added code to check for new updates
  (although you need to download it manually).
* New: Added buttons to launch and close the game (maploadinfo by default).
* New: Added info for Legendary insights and Legendary divinations (this takes
  ages to load because it must scan all your characters inventories, bank,
  materials, etc).
* New: Added themes to customize the colors of the program (this took 8 hours
  and nobody requested it but I got bored of how the program was looking so
  this one is on me! xD).
* New: Added check boxes to customize which sections to load and which ones not.
* New: Added preparations to support different languages (not ready yet).

### Previous Versions
I kept track of them locally but I never published anything,
that's why we start on 0.8!

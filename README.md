# kind2anki

A simple Anki add-on which imports words from Kindle's Vocabulary Builder. It translates words to chosen language using www.transltr.org.

# Installation

Extract files to ~/Anki/addons and restart Anki or go to  https://ankiweb.net/shared/info/1621749993 and follow instructions in Download section.

# Usage
1. Go to Tools -> kind2anki
 
   ![Menu](/../screenshots/1menu.png?raw=true)

2. In a "kind2anki" window:

   ![kind2anki window](/../screenshots/2kind2anki_window_2.png?raw=true)

 * choose a deck to which you wish add words (you can create new one)
 * specify behaviour in case of duplicates
 * check "Include usage example" if you want to have a sentence with the word included in your flashcard
 * uncheck "Translate words" if you wish to import words without translating them
 * specify target language. You can select from a list or enter appropriate code (you can check language codes here: http://www.transltr.org/api/getlanguagesfortranslate)
 * change the number of days in "Import words not older than..." if you wish. The default numer is the number of days since last run of the add-on.

3. Click Import

4. Select a vocab.db file from your Kindle. In Linux, it should be in /media/username/Kindle/system/vocabulary. In Windows, find a letter assigned to your Kindle and enter system\vocabulary after it manually in the address bar (system folder is not visible), e.g. D:\system\vocabulary

   ![Select DB](/../screenshots/3select_db.png?raw=true)

5. Click Open and wait. Translating words can take several minutes (so be patient and don't restart Anki).
6. When importing is completed, summary will appear. That's all!

   ![Summary](/../screenshots/4import_complete.png?raw=true)

(sorry for outdated screenshots)

# Disclaimer

This add-on uses www.transltr.org as a translating engine. Some translations will be unsatisfactory and you will have to manually correct them.

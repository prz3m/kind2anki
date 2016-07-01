# kind2anki

A simple Anki add-on which imports words from Kindle's Vocabulary Builder. It translates words to chosen language using Google Translate.

# Installation

Extract files to ~/Anki/addons and restart Anki.

# Usage

1. Go to Tools -> kind2anki
![Menu](/../screenshots/1menu.png?raw=true)
2. In a "kind2anki" window:
![kind2anki window](/../screenshots/2kind2anki_window.png?raw=true)
* choose a deck to which you wish add words (you can create new one)
* specify behaviour in case of duplicates
* specify target language. You can select from a list or enter appropriate code (you can check language codes here: https://sites.google.com/site/tomihasa/google-language-codes)
3. Click Import
4. Select a vocab.db file from your Kindle. In Linux, it should be in /media/username/Kindle/system/vocabulary. In Windows, find a letter assigned to your Kindle and enter system\vocabulary after it manually in the address bar (system folder is not visible), e.g. D:\system\vocabulary
![Select DB](/../screenshots/3select_db.png?raw=true)
5. Click Open and wait. Translating words can take a while (in my case, translating ~2000 words took over 5 minutes)
6. When importing is completed, summary will appear. That's all!
![Summary](/../screenshots/4import_complete.png?raw=true)

# Tips

Translating big database takes a long time. If you don't use Vocabulary Builder, you can delete vocab.db from your Kindle. The next time you want to import words to Anki, the database will be smaller and importing will be faster.

# Disclaimer

This add-on uses Google Translate as a translating engine (through TextBlob library). Some translations will be unsatisfactory and you will have to manually correct them.

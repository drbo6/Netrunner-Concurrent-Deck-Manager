# Netrunner Concurrent Deck Manager

This Python script can check Netrunner decks against a card collection so that you can build multiple decks at the same time (given that you have multiple core sets or some proxies for commonly used cards).

## Instructions

1. Windows users can run the executable provided in the "dist" folder. Non-windows users can Install Python (3.10.5) and run the script manually (which requires installing the items at the top of the script).

2. File > "Load Collection" to load a card collection. This should be a UTF-8-SIG-formatted CSV file. If you have MS Excel, saving your spreadsheet as a CSV-file will do this for you. 
   
   - The spreadsheet needs two columns:
     
     - *Name:* The card names. I recommend copy-pasting them over from NetrunnerDB.com.
     
     - *Quantity*: The amount of copies that you own of the card.
   
   - You can have as many other columns as you like. The sample files have a set and notes column for additional information and easier tracking.-
   
   - You do not need count up every version of each cards. The script will do this manually. For example, if you have a 3 Sure Gambles from the core set, 6 Sure Gambles from System Gateway and 6 Sure Gamble proxies that you made yourself, you can put them each different type on separate rows. The script will read them as 15 Sure Gambles.
   
   - I recommend setting up separate files for your Runner and your Corp cards.

3- File > "Select Decks Folder" to load a folder with Octgn decks. 

- You can get an Octgn deck file from NetrunnerDB.com for every deck that you like. Click on Action > Octgn file. 

- I recommend setting up separate folders for Runner decks and for Corp decks. (I went with this format as it is an easy-to-parse XML-file.)

- I like to label the decks I download with the name of the ID and faction for easier browsing. (Unfortunately, none of NetrunnerDB's deck downloads have that kind of meta-information in their file.)

4- After step 2 and 3, you should see your card collection in the upper left box, and your decks in the 4 box to the right of it.

- Click a deck to select it. The script will remove all decks that can no longer be made with the remaining cards from your collection from the other boxes.

- The decklists for selected decks become visible underneath the deck.

- Double-click a deck to open the Octgn file.

- Select a different deck to update your options.

- Use the reset options in the menu bar to reset as needed.

5- Have fun, and always be running!

## About the Sample Files

I only added cards that I have in my own collection to them, but there is no reason why you could not support any Netrunner card ever made. The sample files show a collection that includes:

- Ashes cycle (with Uprising Booster Pack)

- NSG System Gateway x2

- Project APEX System Gateway Proxies x2

- System Update 2021

- Project APEX System Update 2021 Proxies

- Borealis cycle (with Midnight Sun Booster Pack)

- The Automata Initiative

For the Netrunner decks, I download a number of popular decks from NetrunnerDB.com. The most important cards needed to support a lot of options are System Gateway cards and maybe a second System Update 2021.

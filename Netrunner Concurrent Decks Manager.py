import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import csv
import os
import xml.etree.ElementTree as ET
import copy
import webbrowser

class Data:
    def __init__(self, csv_file="Cards/Runner Cards.csv", decks_folder="Decks/Runner"):
        self.cards_file_path = csv_file
        self.decks_folder_path = decks_folder
        self.decks = self.load_decks_data_from_folder()
        self.cards_remaining = self.load_card_data_from_csv()
        self.cards_used = copy.deepcopy(self.cards_remaining) # This is a mutable list with a mutable dict inside. Copy() will only copy the list. Deepcopy will copy the list and the dict.
        self.decks_remaining = self.decks.copy()
        self.deck_names_selected = ["","","",""]

        # Set the quantity of every card in the cards_used to 0 so that all the names are in there.
        for card in self.cards_used:
            card['Quantity'] = 0

    def load_card_data_from_csv(self):
        card_data = []
        if os.path.isfile(self.cards_file_path):
            with open(self.cards_file_path, newline='', encoding='utf-8-sig') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    card_data.append(row)
        return self.merge_duplicate_cards(card_data)

    def merge_duplicate_cards(self, card_data):
        merged_cards = {}
        for card in card_data:
            card_name = card.get("Name", "")
            card_quantity = int(card.get("Quantity", 0))
            if card_name in merged_cards:
                # Card already exists, update quantity
                merged_cards[card_name]["Quantity"] += card_quantity
            else:
                # Add new card
                merged_cards[card_name] = card.copy()
                # Ensure Quantity is stored as an integer
                merged_cards[card_name]["Quantity"] = card_quantity
        return list(merged_cards.values())

    def load_decks_data_from_folder(self):
        decks_data = {}
        if os.path.isdir(self.decks_folder_path):
            deck_files = [f for f in os.listdir(self.decks_folder_path) if f.endswith(".o8d")]
        else:
            deck_files = []
        for deck_filename in deck_files:
            deck_file_path = os.path.join(self.decks_folder_path, deck_filename)
            tree = ET.parse(deck_file_path)
            root = tree.getroot()

            deck_name = os.path.splitext(deck_filename)[0]
            decks_data[deck_name] = {}

            for section in root.findall(".//section"):
                for card in section.findall(".//card"):
                    qty = int(card.get("qty", 1))
                    card_name = card.text.strip()

                    if card_name in decks_data[deck_name]:
                        decks_data[deck_name][card_name] += qty
                    else:
                        decks_data[deck_name][card_name] = qty
        return decks_data

    def get_decks_remaining(self, cards_remaining):
        new_decks_remaining = {}
        for deck_name, deck_cards in self.decks.items():
            cards_found = 0
            card_quantity_test_passed = True
            for card_name, card_quantity in deck_cards.items():
                for card_remaining in cards_remaining:
                    if card_remaining['Name'] == card_name:
                        cards_found += 1
                        if card_quantity > card_remaining['Quantity']:
                            card_quantity_test_passed = False
                            break
                        break
            if cards_found == len(deck_cards) and card_quantity_test_passed:
                new_decks_remaining[deck_name] = deck_cards
        return new_decks_remaining

    def remove_deck_from_cards_list(self, deck_name, cards_list):
        deck_cards = self.get_deck_cards(deck_name)
        for card in cards_list:
            card_name = card.get("Name", "")
            if card_name in deck_cards:
                card["Quantity"] = max(0, card["Quantity"] - deck_cards[card_name]) # Mutable, so this updates cards_remaining

    def add_deck_to_cards_list(self, deck_name, cards_list):
        deck_cards = self.get_deck_cards(deck_name)
        for card in cards_list:
            card_name = card.get("Name", "")
            if card_name in deck_cards:
                card["Quantity"] = card["Quantity"] + deck_cards[card_name]

    def get_deck_cards(self, deck_name):
        deck_cards = self.decks.get(deck_name, {})
        return deck_cards

    def get_deck(self, deck_name):
        deck = {}
        deck[deck_name] = self.get_deck_cards(deck_name)
        return deck

class NetrunnerConcurrentDecksManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Netrunner Proxy Manager")

        # Initialize data
        self.data = Data()

        # Create GUI
        self.createGUI()

    def createGUI(self):
        # Add a menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu with Open option
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Load Collection", command=self.open_collection_csv_file)
        file_menu.add_command(label="Select Decks Folder", command=self.open_decks_xml_folder)

        reset_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Reset", menu=reset_menu)
        reset_menu.add_command(label="Reset Deck 1", command=self.reset1)
        reset_menu.add_command(label="Reset Deck 2", command=self.reset2)
        reset_menu.add_command(label="Reset Deck 3", command=self.reset3)
        reset_menu.add_command(label="Reset Deck 4", command=self.reset4)
        reset_menu.add_command(label="Reset All", command=self.reset)

        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Documentation", command=self.open_documentation)
        help_menu.add_command(label="About", command=self.about)

        # Create a 2x5 grid of listboxes
        self.listboxes = [[None for _ in range(5)] for _ in range(2)]
        for i in range(2):
            for j in range(5):
                self.create_listboxes(i, j)

        # Configure grid weights to allow dynamic resizing
        for i in range(2):
            self.root.grid_rowconfigure(i, weight=1)
        for j in range(5):
            self.root.grid_columnconfigure(j, weight=1)

        # Call update_listboxes after all listboxes are created
        self.update_listboxes()

        for col in range(1, 5):
            # Bind a method that will process what happens when the listbox changes selection
            self.listboxes[0][col].bind("<<ListboxSelect>>", lambda event, col=col: self.on_listbox_select(event, self.listboxes, 0, col))

            # Bind the double-click event to open the selected deck file
            self.listboxes[0][col].bind("<Double-1>", self.open_selected_deck_file)

    def on_listbox_select(self, event, listboxes, listbox_y, listbox_x):
        listbox = listboxes[listbox_y][listbox_x]
        if listbox.curselection():
            selected_item = listbox.get(listbox.curselection())
        else:
            selected_item = ""

        deselected_item = self.data.deck_names_selected[listbox_x - 1]
        self.data.deck_names_selected[listbox_x - 1] = selected_item

        if deselected_item != "":
            self.data.add_deck_to_cards_list(deselected_item, self.data.cards_remaining)
            self.data.remove_deck_from_cards_list(deselected_item, self.data.cards_used)
        self.data.add_deck_to_cards_list(selected_item, self.data.cards_used)
        self.data.remove_deck_from_cards_list(selected_item, self.data.cards_remaining)

        self.update_listboxes()

        # Keep the selection in view
        if listbox.curselection():
            listbox.see(listbox.curselection())

    def create_listboxes(self, row, col):
        # Frame for each listbox with title and scrollbar
        frame = ttk.Frame(self.root, padding=5)
        frame.grid(row=row, column=col, sticky="nsew")

        # Determine the title for each listbox
        if row == 0:
            if col == 0:
                title = "Unused Cards"
            else:
                title = f"Select Deck {col}"
        else:
            if col == 0:
                title = "Used Cards"
            else:
                title = f"Decklist {col}"

        # Title label
        title_label = ttk.Label(frame, text=f"{title}")
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 5))

        # Select mode so that only top right 4 can interact
        select_mode = tk.SINGLE if row == 0 and col > 0 else tk.NONE # We defined tk.NONE ourselves later as this does not exist otherwise

        # Listbox
        listbox = tk.Listbox(frame, selectmode=select_mode, exportselection=False)
        listbox.grid(row=1, column=0, sticky="nsew")

        # Scrollbar
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=listbox.yview)
        scrollbar.grid(row=1, column=1, sticky="ns")

        # Configure listbox to use the scrollbar
        listbox.config(yscrollcommand=scrollbar.set)

        # Configure row and column weights to allow dynamic resizing
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        # Store listbox in the 2D list for future reference
        self.listboxes[row][col] = listbox

        # Disable selection for specific listboxes
        if select_mode == tk.NONE:
            listbox.bind("<Button-1>", lambda e: "break")  # Disable left mouse button click

    def update_listboxes(self):
        for row in range(2):
            for col in range(min(5, len(self.listboxes[row]))):
                listbox = self.listboxes[row][col]
                if col == 0:
                    if row == 0:
                        self.load_all_cards_to_listbox(self.data.cards_remaining, listbox)
                    else:
                        self.load_all_cards_to_listbox(self.data.cards_used, listbox)
                else:
                    if row == 0:
                        self.load_all_decks_remaining_to_listbox(self.listboxes, row, col)
                    else:
                        self.load_deck_list_to_listbox(self.listboxes, row, col)
    def load_all_cards_to_listbox(self, cards_list_name, listbox):
        sorted_cards = sorted(cards_list_name, key=lambda x: (-int(x.get("Quantity", 0)), x.get("Name", "")))
        listbox.delete(0, tk.END)
        for card in sorted_cards:
            card_name = card.get("Name", "N/A")
            card_quantity = card.get("Quantity", "N/A")
            if card_quantity > 0:
                listbox.insert(tk.END, f"{card_name} ({card_quantity})")

    def load_all_decks_remaining_to_listbox(self, listboxes, listbox_y, listbox_x):
        listbox = listboxes[listbox_y][listbox_x]
        current_selected_deck_name = self.data.deck_names_selected[listbox_x - 1]

        # We are inserting the cards of the deck that we selected just for this one listbox.
        # This will show the deck but also all the decks that we can create when this deck is changed to a different one.
        # We need to make a copy because deck_names will be emutable and we don't want to add the deck to the real data set.
        temporary_cards_remaining = copy.deepcopy(self.data.cards_remaining)
        if current_selected_deck_name != "": self.data.add_deck_to_cards_list(current_selected_deck_name, temporary_cards_remaining)
        temporary_decks_remaining = self.data.get_decks_remaining(temporary_cards_remaining)
        deck_names = temporary_decks_remaining.keys()
        listbox.delete(0, tk.END)
        for i, deck_name in enumerate(deck_names):
            listbox.insert(tk.END, deck_name)
            if deck_name == current_selected_deck_name: listbox.selection_set(i)

        # Keep the selection in view
        if listbox.curselection():
            listbox.see(listbox.curselection())

    def load_deck_list_to_listbox(self, listboxes, listbox_y, listbox_x):
        listbox = listboxes[listbox_y][listbox_x]
        current_selected_deck_name = self.data.deck_names_selected[listbox_x - 1]
        listbox.delete(0, tk.END)
        if current_selected_deck_name != "":
            deck_cards = self.data.get_deck_cards(current_selected_deck_name)
            for card in deck_cards:
                listbox.insert(tk.END, f"{card}: {deck_cards[card]}")


    def open_collection_csv_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            print(f"Opening file: {file_path}")
            self.data = Data(csv_file=file_path, decks_folder=self.data.decks_folder_path)
            self.update_listboxes()

    def open_decks_xml_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            print(f"Opening folder: {folder_path}")
            self.data = Data(decks_folder=folder_path, csv_file=self.data.cards_file_path)
            self.update_listboxes()

    def open_selected_deck_file(self, event):
        selected_index = event.widget.curselection()
        if selected_index:
            selected_deck_name = event.widget.get(selected_index[0])
            deck_file_path = os.path.join(self.data.decks_folder_path, f"{selected_deck_name}.o8d")
            try:
                os.startfile(deck_file_path)
            except OSError as e:
                print(f"Error opening file: {e}")

    def reset(self):
        self.data = Data(csv_file=self.data.cards_file_path, decks_folder=self.data.decks_folder_path)
        self.update_listboxes()

    def reset_listbox(self, listbox_x):
        listbox_y = 0
        listbox = self.listboxes[listbox_y][listbox_x]
        if listbox.curselection():
            selected_item = listbox.get(listbox.curselection())
        else:
            selected_item = ""

        if selected_item != "":
            self.data.deck_names_selected[listbox_x - 1] = ""
            self.data.add_deck_to_cards_list(selected_item, self.data.cards_remaining)
            self.data.remove_deck_from_cards_list(selected_item, self.data.cards_used)

            self.update_listboxes()

    def reset1(self):
        self.reset_listbox(1)

    def reset2(self):
        self.reset_listbox(2)

    def reset3(self):
        self.reset_listbox(3)

    def reset4(self):
        self.reset_listbox(4)

    def open_documentation(self):
        url = "https://github.com/drbo6/Netrunner-Concurrent-Deck-Manager"
        webbrowser.open(url)

    def about(self):
        messagebox.showinfo("About", "Netrunner Concurrent Decks Manager v1.0\nBy DrBo6\n\nDeveloped in Python 3.10")

if __name__ == "__main__":
    root = tk.Tk()
    app = NetrunnerConcurrentDecksManager(root)
    root.geometry("1024x768")
    root.mainloop()
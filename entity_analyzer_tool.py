import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import os

########################
# Entity_Analyzer_Tool #
########################

# simple Entities Tool to analyze your csv-file
# import and export csv file
# free entity search 
# area & platform filter
# entities statistic

class EntityAnalyzerApp:
    # --- Globale App-Konfiguration ---
    THEME_COLORS = {
        'light': {
            'bg': '#ececec', 'fg': 'black', 'tree_odd': 'white', 'tree_even': '#f0f0f0',
            'tree_heading_bg': '#d8d8d8', 'tree_heading_fg': 'black', 'status_bg': '#d8d8d8',
            'status_fg': '#333333', 'entry_fg': 'black', 'button_fg': 'black',
            'menu_bg': '#ececec', 'menu_fg': 'black', 'tree_field_bg': '#f0f0f0' 
        },
        'dark': {
            'bg': '#2e2e2e', 'fg': 'white', 'tree_odd': '#3c3c3c', 'tree_even': '#2e2e2e',
            'tree_heading_bg': '#d8d8d8', 'tree_heading_fg': 'black', 'status_bg': '#1a1a1a',
            'status_fg': '#cccccc', 'entry_fg': 'black', 'button_fg': 'black',
            'menu_bg': '#2e2e2e', 'menu_fg': 'white', 'tree_field_bg': '#2e2e2e' 
        }
    }
    VERSION = "v1.1 by jayjojayson"
    
    def __init__(self, root):
        self.root = root
        self.root.title("Home Assistant Entity Analyzer Tool")
        self.root.geometry("1200x700")

        # >>> NEU: Icon-Integration <<<
        try:
            # Setzt das Icon für das Hauptfenster (Taskleiste und Fenster-Header)
            self.root.iconbitmap('E_A_T-logo.ico')
        except tk.TclError as e:
            print(f"Warnung: Konnte Icon 'E_A_T-logo.ico' nicht laden. Stellen Sie sicher, dass es sich im selben Ordner befindet. Fehler: {e}")
            pass 
        # >>> ENDE Icon-Integration <<<

        # --- Variablen ---
        self.df_data = None
        self.df_original = None
        self.is_dark_mode = False
        self.is_always_on_top = False

        # --- Stil-Konfiguration ---
        self.style = ttk.Style()
        self.style.configure("Treeview", rowheight=25)

        # --- GUI-Elemente erstellen ---
        self._create_menu()
        self._create_widgets()
        
        # Initialisierung des Themes (Standard: Light Mode)
        self.apply_theme('light')

    # --- GUI-Erstellung ---

    def _create_menu(self):
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)

        # 1. Datei-Menü
        self.datei_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Datei", menu=self.datei_menu)
        self.datei_menu.add_command(label="📂 CSV öffnen", command=self.load_csv_data)
        self.datei_menu.add_command(label="💾 CSV Export", command=self.export_current_view_to_csv)
        self.datei_menu.add_separator()
        self.datei_menu.add_command(label="Exit", command=self.root.destroy)

        # 2. Filter-Menü
        self.filter_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Filter", menu=self.filter_menu)
        self.filter_menu.add_command(label="📍 Filtern nach Area", command=lambda: self.filter_data('area'))
        self.filter_menu.add_command(label="🔌 Filtern nach Plattform", command=lambda: self.filter_data('platform'))
        self.filter_menu.add_separator()
        self.filter_menu.add_command(label="📊 Typ-Statistik anzeigen", command=self.show_domain_stats_gui)
        self.filter_menu.add_separator()
        self.filter_menu.add_command(label="🔄 Filter & Suche zurücksetzen", command=self.reset_filter)

        # 3. Optionen-Menü
        self.optionen_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Optionen", menu=self.optionen_menu)
        self.optionen_menu.add_command(label="⬜ Hell/Dunkel Modus", command=self.toggle_dark_mode)
        self.optionen_menu.add_separator()
        self.optionen_menu.add_command(label="⬜ App im Vordergrund halten", command=self.toggle_always_on_top)

    def _create_widgets(self):
        # 1. Top Bar (Steuerungselemente)
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(fill=tk.X)

        ttk.Label(control_frame, text="Freie Suche:").pack(side=tk.LEFT, padx=(5, 5))
        self.search_entry = ttk.Entry(control_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        # Bindet die vektorisierte Suchfunktion
        self.search_entry.bind('<KeyRelease>', self.apply_filter_search)

        ttk.Button(control_frame, text="🔄 Filter zurücksetzen", command=self.reset_filter).pack(side=tk.RIGHT, padx=5)

        # 2. Treeview (Datenansicht)
        table_frame = ttk.Frame(self.root, padding="10")
        table_frame.pack(fill=tk.BOTH, expand=True)

        self.vsb = ttk.Scrollbar(table_frame, orient="vertical")
        self.hsb = ttk.Scrollbar(table_frame, orient="horizontal")

        self.tree = ttk.Treeview(table_frame, columns=[], show='headings',
                                 yscrollcommand=self.vsb.set, xscrollcommand=self.hsb.set)
        self.vsb.config(command=self.tree.yview)
        self.hsb.config(command=self.tree.xview)

        self.vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # 3. Status Bar
        footer_frame = ttk.Frame(self.root, padding="1")
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.status_label = ttk.Label(footer_frame, text="Bereit, lade eine Home Assistant Entitäten CSV-Datei.", anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.version_label = ttk.Label(footer_frame, text=self.VERSION, anchor=tk.E)
        self.version_label.pack(side=tk.RIGHT)

    # --- Theme und GUI-Optionen ---

    def apply_theme(self, mode):
        """Wendet das ausgewählte Theme an und reduziert redundante Konfigurationen."""
        self.is_dark_mode = (mode == 'dark')
        colors = self.THEME_COLORS[mode]
        
        # 1. Root und allgemeine Styles
        self.root.config(bg=colors['bg'])
        self.style.configure('.', background=colors['bg'], foreground=colors['fg'])
        self.style.configure('TFrame', background=colors['bg'])
        self.style.configure('TLabel', background=colors['bg'], foreground=colors['fg'])
        self.style.configure('TButton', background=colors['bg'], foreground=colors['button_fg'])
        self.style.configure('TEntry', fieldbackground='white', foreground=colors['entry_fg'])

        # 2. Menüs (Standardoptionen + manuelle Konfiguration)
        self.root.option_add('*Menu.background', colors['menu_bg'])
        self.root.option_add('*Menu.foreground', colors['menu_fg'])
        self.root.option_add('*Menu.activeBackground', colors['tree_odd'])
        self.root.option_add('*Menu.activeForeground', colors['fg'])
        # Manuelle Konfiguration für sofortige Aktualisierung (weniger Redundanz)
        for menu in [self.menu_bar, self.datei_menu, self.filter_menu, self.optionen_menu]:
            if menu:
                menu.config(bg=colors['menu_bg'], fg=colors['menu_fg'], activebackground=colors['tree_odd'], activeforeground=colors['fg'])
        
        # 3. Status Bar und Version Label
        status_style = {'background': colors['status_bg'], 'foreground': colors['status_fg'], 'relief': tk.SUNKEN}
        self.status_label.config(**status_style)
        self.version_label.config(**status_style)

        # 4. Treeview Styles
        self.style.configure("Treeview.Heading", background=colors['tree_heading_bg'], foreground=colors['tree_heading_fg'], relief="raised")
        self.tree.tag_configure('oddrow', background=colors['tree_odd'], foreground=colors['fg'])
        self.tree.tag_configure('evenrow', background=colors['tree_even'], foreground=colors['fg'])
        # Standardfarbe des Treeview-Hintergrunds, wenn keine Daten geladen sind
        self.style.configure("Treeview", fieldbackground=colors['tree_field_bg'], background=colors['tree_field_bg'], foreground=colors['fg'])

        # 5. Scrollbars (Styling nur im Dark Mode)
        if mode == 'dark':
            self.style.configure("Vertical.TScrollbar", background="#555555", troughcolor="#3e3e3e", bordercolor="#3e3e3e", arrowcolor="white")
            self.style.configure("Horizontal.TScrollbar", background="#555555", troughcolor="#3e3e3e", bordercolor="#3e3e3e", arrowcolor="white")
            self.vsb.config(style="Vertical.TScrollbar")
            self.hsb.config(style="Horizontal.TScrollbar")
        else:
            self.style.configure("Vertical.TScrollbar")
            self.style.configure("Horizontal.TScrollbar")
            self.vsb.config(style="TScrollbar")
            self.hsb.config(style="TScrollbar")

        # 6. Menü-Checkmarks aktualisieren
        self.optionen_menu.entryconfig(0, label=f"{'✅' if self.is_dark_mode else '⬜'} Hell/Dunkel Modus")
        self.optionen_menu.entryconfig(2, label=f"{'✅' if self.is_always_on_top else '⬜'} App im Vordergrund halten")

        # Re-display the data to apply new colors if data is loaded
        if self.df_data is not None:
            self.setup_treeview(self.df_data)

    def toggle_dark_mode(self):
        """Schaltet zwischen Dark und Light Mode um."""
        self.apply_theme('light' if self.is_dark_mode else 'dark')

    def toggle_always_on_top(self):
        """Schaltet die 'always on top'-Eigenschaft um."""
        self.is_always_on_top = not self.is_always_on_top
        self.root.wm_attributes('-topmost', self.is_always_on_top)
        self.optionen_menu.entryconfig(2, label=f"{'✅' if self.is_always_on_top else '⬜'} App im Vordergrund halten")

    # --- Datenlade- und Anzeige-Funktionen ---

    def load_csv_data(self):
        """Läd, bereinigt und formatiert die CSV-Datei."""
        filepath = filedialog.askopenfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not filepath: return

        try:
            # Pandas-Optimierung: Nur die benötigten Spalten explizit laden, falls bekannt. Hier: alle.
            new_df = pd.read_csv(filepath, sep=';', dtype=str) # Lade alle als String für Konsistenz
            
            # 1. Bereinigung
            new_df.columns = new_df.columns.str.lower().str.strip()
            cols_to_drop = [col for col in new_df.columns if col.startswith('unnamed:')]
            new_df.drop(columns=cols_to_drop, inplace=True, errors='ignore')

            # 2. String-Konvertierung (bereits durch dtype=str im read_csv enthalten, nur NaN füllen)
            self.df_original = new_df.fillna('')
            self.df_data = self.df_original.copy()
            
            self.status_label.config(text=f"✅ Datei geladen: {os.path.basename(filepath)} ({len(self.df_data)} Entitäten)", foreground="green")
            self.setup_treeview(self.df_data)

        except Exception as e:
            self.status_label.config(text=f"❌ Fehler beim Laden der Datei: {e}", foreground="red")
            messagebox.showerror("Ladefehler", f"Fehler beim Laden oder Verarbeiten der CSV-Datei:\n{e}")

    def export_current_view_to_csv(self):
        """Exportiert die aktuell angezeigten Daten als CSV."""
        if self.df_data is None or self.df_data.empty:
            self.status_label.config(text="❌ Keine Daten zum Exportieren verfügbar.", foreground="red")
            return

        filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not filepath: return

        try:
            self.df_data.to_csv(filepath, sep=';', index=False, encoding='utf-8')
            filename = os.path.basename(filepath)
            self.status_label.config(text=f"✅ Daten erfolgreich nach '{filename}' exportiert. ({len(self.df_data)} Zeilen)", foreground="green")
            messagebox.showinfo("Export erfolgreich", f"Die gefilterten Daten wurden erfolgreich nach:\n{filepath}")

        except Exception as e:
            self.status_label.config(text=f"❌ Fehler beim Exportieren: {e}", foreground="red")
            messagebox.showerror("Exportfehler", f"Fehler beim Speichern der Datei:\n{e}")

    def setup_treeview(self, df_to_display):
        """Konfiguriert und füllt das Treeview-Widget."""
        
        # 1. Entfernt vorhandene Childs und Spalten (Optimierung: Treeview-Delete vor Spalten-Config)
        self.tree.delete(*self.tree.get_children())
        
        new_columns = df_to_display.columns.tolist()
        self.tree['columns'] = new_columns

        # 2. Definiert Spaltenüberschriften und passt die Spaltenbreite an
        self.tree.heading("#0", text="", anchor=tk.W)
        self.tree.column("#0", width=0, stretch=tk.NO)

        for col in new_columns:
            # Bessere Breitenberechnung, um die Performance nicht bei jeder Spalte zu beeinträchtigen
            # Breitenberechnung nur, wenn der DF nicht leer ist
            max_len = df_to_display[col].astype(str).str.len().max() if not df_to_display.empty else 10
            width = max(100, min(300, max_len * 7 + 10))
            
            self.tree.heading(col, text=col.upper(), command=lambda c=col: self.sort_column(c, False))
            self.tree.column(col, width=width, anchor=tk.W)

        # 3. Füllt die Tabelle mit den Zeilen und wendet Tags für die Farbe an
        data_to_insert = df_to_display.values.tolist()
        for i, row in enumerate(data_to_insert):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.tree.insert('', tk.END, values=row, tags=(tag,))

    def sort_column(self, col, reverse):
        """Sortiert die Treeview-Spalte und aktualisiert die Anzeige."""
        if self.df_data is None:
            self.status_label.config(text="❌ Bitte zuerst eine CSV-Datei laden!", foreground="red")
            return

        try:
            # Case-Insensitive Sortierung mittels .str.lower() als Key
            sorted_df = self.df_data.sort_values(by=col, ascending=not reverse, key=lambda x: x.str.lower())
            self.df_data = sorted_df
            self.setup_treeview(self.df_data)

            # Setzt den Befehl für die nächste Sortierung (umgekehrt)
            self.tree.heading(col, command=lambda c=col: self.sort_column(c, not reverse))
            self.status_label.config(text=f"Daten sortiert nach '{col.upper()}' {'(Absteigend)' if reverse else '(Aufsteigend)'}", foreground="blue")

        except Exception as e:
            self.status_label.config(text=f"❌ Sortierfehler: {e}", foreground="red")

    def apply_filter_search(self, event=None):
        """Sucht und filtert die Daten basierend auf der Eingabe (Case-Insensitive, alle Spalten) 
        unter Verwendung einer Vektorisierten Pandas-Operation.
        """
        if self.df_original is None:
            self.status_label.config(text="❌ Bitte zuerst eine CSV-Datei laden!", foreground="red")
            return

        search_term = self.search_entry.get().strip()
        
        if not search_term:
            self.df_data = self.df_original.copy()
            self.status_label.config(text="Filter entfernt. Zeige alle Daten.", foreground="black")
            self.setup_treeview(self.df_data)
            return

        # Vektorisierte Suche: Vermeidet apply(lambda...) für bessere Performance
        # Initialisierung der Maske mit False (keine Zeile ausgewählt)
        mask = False
        
        try:
            # Iteriere über alle Spalten und verknüpfe die booleschen Masken mit OR (|)
            for col in self.df_original.columns:
                # Wichtig: Konvertiere zu String und ignoriere NaN/Fehler
                mask |= self.df_original[col].astype(str).str.contains(search_term, case=False, na=False)
            
            self.df_data = self.df_original[mask].copy()
            
        except Exception as e:
            self.status_label.config(text=f"❌ Fehler bei der vektorisierten Suche: {e}", foreground="red")
            return

        if not self.df_data.empty:
            self.status_label.config(text=f"🔎 {len(self.df_data)} Entitäten gefunden, die '{search_term}' enthalten.", foreground="green")
            self.setup_treeview(self.df_data)
        else:
            self.status_label.config(text=f"Keine Entität mit '{search_term}' gefunden.", foreground="orange")
            self.setup_treeview(pd.DataFrame(columns=self.df_original.columns)) # Leeren DF mit Spalten

    def reset_filter(self):
        """Setzt Filter und Suche zurück."""
        if self.df_original is None: return

        self.df_data = self.df_original.copy()
        self.search_entry.delete(0, tk.END)
        self.apply_filter_search()
        self.status_label.config(text="Filter und Suche zurückgesetzt. Zeige alle Entitäten.", foreground="black")

    # --- Funktionen für Filtern und Gruppierung (Ausschnitt) ---

    def filter_data(self, column_key):
        """Zeigt ein Auswahlfenster zum Filtern nach Area oder Plattform an."""
        if self.df_original is None:
            self.status_label.config(text="❌ Bitte zuerst eine CSV-Datei laden!", foreground="red")
            return

        col_map = {'area': 'area', 'platform': 'platform (integration)'}
        filter_col = col_map.get(column_key)

        if filter_col not in self.df_original.columns:
            self.status_label.config(text=f"❌ Spalte '{filter_col}' nicht in CSV gefunden.", foreground="red")
            return

        unique_values = self.df_original[filter_col].unique().tolist()
        unique_values.sort(key=str.lower)

        # Neues Toplevel-Fenster (Code zur Erstellung des Fensters ist kompakt genug)
        filter_window = tk.Toplevel(self.root)
        filter_window.title(f"Filtern nach {column_key.upper()}")
        
        current_theme = 'dark' if self.is_dark_mode else 'light'
        colors = self.THEME_COLORS[current_theme]
        filter_window.config(bg=colors['bg'])
        
        listbox_frame = ttk.Frame(filter_window)
        listbox_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Vereinfachte Listbox Style Config
        listbox_style = {
            'bg': colors['tree_even'], 'fg': colors['fg'], 
            'selectbackground': colors['tree_odd'], 'selectforeground': colors['fg']
        }
        listbox = tk.Listbox(listbox_frame, selectmode=tk.SINGLE, width=40, **listbox_style)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Füllt die Listbox
        if '' in self.df_original[filter_col].unique():
            listbox.insert(tk.END, "— KEIN WERT ZUGEWIESEN —")
        for val in unique_values:
            if val != '':
                listbox.insert(tk.END, val)
        
        def apply_single_filter():
            try:
                selected_value = listbox.get(listbox.curselection()[0])
                filter_value = '' if selected_value == "— KEIN WERT ZUGEWIESEN —" else selected_value
                
                self.df_data = self.df_original[self.df_original[filter_col] == filter_value].copy()
                
                self.status_label.config(text=f"✅ Gefiltert nach {column_key.upper()}: '{selected_value}' ({len(self.df_data)} Entitäten)", foreground="green")
                self.setup_treeview(self.df_data)
                filter_window.destroy()
            except IndexError:
                messagebox.showwarning("Auswahl fehlt", "Bitte einen Wert zum Filtern auswählen.")
            except Exception as e:
                messagebox.showerror("Filterfehler", f"Fehler beim Filtern: {e}")

        ttk.Button(filter_window, text="Filter anwenden", command=apply_single_filter).pack(pady=10)

    def show_domain_stats_gui(self):
        """Gruppiert Entitäten nach Typ (Domain) und zeigt die Zählungen an."""
        if self.df_original is None:
            self.status_label.config(text="❌ Keine Daten geladen!", foreground="red")
            return

        entity_id_col = 'entity id'
        if entity_id_col not in self.df_original.columns:
            self.status_label.config(text="❌ Spalte 'entity id' fehlt für die Statistik!", foreground="red")
            return

        # Extrahieren des Entitätstyps (Domain) und Zählen (Pandas-Optimierung)
        # .str.split().str[0] ist oft schneller als expand=True
        domain_counts = self.df_original[entity_id_col].str.split('.', n=1).str[0].value_counts()
        
        # DataFrame für die Darstellung erstellen
        stats_df = domain_counts.reset_index()
        stats_df.columns = ['Entitätstyp (Domain)', 'Anzahl']

        # Neues Fenster für die Statistik erstellen (Code zur Erstellung des Fensters ist kompakt genug)
        stats_window = tk.Toplevel(self.root)
        stats_window.title("📊 Entitäts-Statistik nach Typ")
        stats_window.geometry("400x550")
        
        current_theme = 'dark' if self.is_dark_mode else 'light'
        colors = self.THEME_COLORS[current_theme]
        stats_window.config(bg=colors['bg'])
        
        stats_tree = ttk.Treeview(stats_window, columns=stats_df.columns.tolist(), show='headings')
        stats_tree.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        for col in stats_df.columns:
            stats_tree.heading(col, text=col)
            stats_tree.column(col, width=150, anchor=tk.W)

        # Füllen der Tabelle mit den Statistiken
        for i, row in stats_df.iterrows():
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            stats_tree.insert('', tk.END, values=row.tolist(), tags=(tag,))
        
        ttk.Label(stats_window, text=f"Gesamtanzahl eindeutiger Typen: {len(domain_counts)}", padding=5).pack()

if __name__ == "__main__":
    root = tk.Tk()
    app = EntityAnalyzerApp(root)
    root.mainloop()
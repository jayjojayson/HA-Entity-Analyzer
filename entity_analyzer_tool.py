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

class Tooltip:
    """Erstellt ein Tooltip für ein gegebenes Widget."""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25

        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")

        label = tk.Label(self.tooltip_window, text=self.text, justify='left',
                         background="#ffffe0", relief='solid', borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hide_tooltip(self, event):
        if self.tooltip_window:
            self.tooltip_window.destroy()
        self.tooltip_window = None

class EntityAnalyzerApp:
    # --- Konstanten ---
    COL_ENTITY_ID = 'entity id'
    COL_AREA = 'area'
    COL_PLATFORM = 'platform'
    
    # --- Globale App-Konfiguration --- 
    THEME_COLORS = {
        'light': {
            'bg': '#ececec', 'fg': 'black', 'tree_odd': 'white', 'tree_even': '#f0f0f0',
            'tree_heading_bg': '#d8d8d8', 'tree_heading_fg': 'black', 'status_bg': '#d8d8d8',
            'status_fg': '#333333', 'entry_bg': 'white', 'entry_fg': 'black',
            'button_bg': '#ececec', 'button_fg': 'black', 'menu_bg': '#ececec',
            'menu_fg': 'black', 'tree_field_bg': '#f0f0f0'
        },
        'dark': {
            'bg': '#2e2e2e', 'fg': 'white', 'tree_odd': '#3c3c3c', 'tree_even': '#2e2e2e',
            'tree_heading_bg': '#d8d8d8', 'tree_heading_fg': 'black', 'status_bg': '#1a1a1a',
            'status_fg': '#cccccc', 'entry_bg': '#555555', 'entry_fg': 'white',
            'button_bg': '#d8d8d8', 'button_fg': 'black', 'menu_bg': '#2e2e2e',
            'menu_fg': 'white', 'tree_field_bg': '#2e2e2e'
        }
    }
    VERSION = "v1.2 by jayjojayson"
     
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
        self.style.theme_use('clam')  # Sorgt für konsistentes Styling
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
        self.optionen_menu.add_separator()
        self.optionen_menu.add_command(label="ℹ️ Über", command=self.show_about_window)
 
    def _create_widgets(self): 
        # 1. Top Bar (Steuerungselemente) 
        control_frame = ttk.Frame(self.root, padding="10") 
        control_frame.pack(fill=tk.X) 
 
        ttk.Label(control_frame, text="Freie Suche:").pack(side=tk.LEFT, padx=(5, 5)) 
        self.search_entry = ttk.Entry(control_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind('<KeyRelease>', self.apply_filter_search)
        Tooltip(self.search_entry, "Geben Sie einen Suchbegriff ein, um die Entitäten zu filtern.\nDie Suche ist Case-Insensitive.")

        reset_button = ttk.Button(control_frame, text="🔄 Filter zurücksetzen", command=self.reset_filter)
        reset_button.pack(side=tk.RIGHT, padx=5)
        Tooltip(reset_button, "Setzt alle Filter und die Suche zurück.")
 
        # 2. Treeview (Datenansicht) 
        table_frame = ttk.Frame(self.root, padding="10") 
        table_frame.pack(fill=tk.BOTH, expand=True) 
 
        self.vsb = ttk.Scrollbar(table_frame, orient="vertical") 
        self.hsb = ttk.Scrollbar(table_frame, orient="horizontal") 
 
        self.tree = ttk.Treeview(table_frame, columns=[], show='headings', 
                                 yscrollcommand=self.vsb.set, xscrollcommand=self.hsb.set) 
        self.tree.bind('<Double-1>', self.show_entity_details)
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
        """Wendet das ausgewählte Theme an und konfiguriert die ttk-Styles."""
        self.is_dark_mode = (mode == 'dark')
        colors = self.THEME_COLORS[mode]

        # 1. Root-Fenster
        self.root.config(bg=colors['bg'])

        # 2. Allgemeine ttk-Styles
        self.style.configure('.', background=colors['bg'], foreground=colors['fg'])
        self.style.configure('TFrame', background=colors['bg'])
        self.style.configure('TLabel', background=colors['bg'], foreground=colors['fg'])
        
        # Style für TButton mit Padding und Relief
        self.style.configure('TButton', background=colors['button_bg'], foreground=colors['button_fg'],
                             padding=5, relief=tk.RAISED, borderwidth=1)
        self.style.map('TButton', background=[('active', colors['tree_odd'])])

        self.style.configure('TEntry', fieldbackground=colors['entry_bg'], foreground=colors['entry_fg'],
                             insertcolor=colors['fg'])

        # 3. Menü-Konfiguration
        menu_config = {
            'bg': colors['menu_bg'], 'fg': colors['menu_fg'],
            'activebackground': colors['tree_odd'], 'activeforeground': colors['fg']
        }
        self.menu_bar.config(**menu_config)
        for menu in [self.datei_menu, self.filter_menu, self.optionen_menu]:
            if menu:
                menu.config(**menu_config)

        # 4. Status Bar (manuelle Konfiguration, da kein ttk-Widget)
        status_style = {'background': colors['status_bg'], 'foreground': colors['status_fg']}
        self.status_label.config(**status_style)
        self.version_label.config(**status_style)

        # 5. Treeview-Styles
        self.style.configure("Treeview.Heading", background=colors['tree_heading_bg'],
                             foreground=colors['tree_heading_fg'], relief="raised")
        self.style.map("Treeview.Heading", background=[('active', colors['tree_odd'])])
        
        self.tree.tag_configure('oddrow', background=colors['tree_odd'], foreground=colors['fg'])
        self.tree.tag_configure('evenrow', background=colors['tree_even'], foreground=colors['fg'])
        self.style.configure("Treeview", fieldbackground=colors['tree_field_bg'],
                             background=colors['tree_field_bg'], foreground=colors['fg'])

        # 6. Scrollbar-Styles
        if mode == 'dark':
            self.style.configure("Vertical.TScrollbar", background="#555555", troughcolor="#3e3e3e",
                                 bordercolor="#3e3e3e", arrowcolor="white")
            self.style.configure("Horizontal.TScrollbar", background="#555555", troughcolor="#3e3e3e",
                                 bordercolor="#3e3e3e", arrowcolor="white")
        else:
            # Stellt sicher, dass beim Zurückschalten zum Light-Mode der Standard-Style verwendet wird
            self.style.configure("Vertical.TScrollbar")
            self.style.configure("Horizontal.TScrollbar")

        # 7. Menü-Checkmarks aktualisieren
        self.optionen_menu.entryconfig(0, label=f"{'✅' if self.is_dark_mode else '⬜'} Hell/Dunkel Modus")
        self.optionen_menu.entryconfig(2, label=f"{'✅' if self.is_always_on_top else '⬜'} App im Vordergrund halten")

        # 8. Daten neu anzeigen, um Theme-Änderungen zu übernehmen
        if self.df_data is not None:
            self.setup_treeview(self.df_data)

    def show_entity_details(self, event):
        """Zeigt ein Pop-up-Fenster mit den Details der ausgewählten Entität an."""
        selected_item = self.tree.focus()
        if not selected_item:
            return

        item_values = self.tree.item(selected_item, 'values')
        column_names = self.tree['columns']

        details_window = tk.Toplevel(self.root)
        details_window.title("Entitätsdetails")
        
        colors = self.THEME_COLORS['dark' if self.is_dark_mode else 'light']
        details_window.config(bg=colors['bg'])

        details_frame = ttk.Frame(details_window, padding="15")
        details_frame.pack(expand=True, fill="both")

        for i, col_name in enumerate(column_names):
            # Label für den Spaltennamen (fett)
            ttk.Label(details_frame, text=f"{col_name.title()}:", font=("Helvetica", 10, "bold")).grid(row=i, column=0, sticky="w", pady=2, padx=5)
            
            # Label für den Wert
            value = item_values[i] if i < len(item_values) else ""
            ttk.Label(details_frame, text=value, wraplength=400, justify="left").grid(row=i, column=1, sticky="w", pady=2, padx=5)

        ttk.Button(details_frame, text="Schließen", command=details_window.destroy).grid(row=len(column_names), column=0, columnspan=2, pady=15)

    def show_about_window(self):
        """Zeigt das 'Über'-Fenster mit Informationen zur Anwendung an."""
        about_window = tk.Toplevel(self.root)
        about_window.title("Über den Entity Analyzer")
        about_window.geometry("350x200")
        about_window.resizable(False, False)

        colors = self.THEME_COLORS['dark' if self.is_dark_mode else 'light']
        about_window.config(bg=colors['bg'])

        about_frame = ttk.Frame(about_window, padding="20")
        about_frame.pack(expand=True, fill=tk.BOTH)

        ttk.Label(about_frame, text="HA Entity Analyzer Tool", font=("Helvetica", 14, "bold")).pack(pady=(0, 8))
        ttk.Label(about_frame, text=f"Version: {self.VERSION}", font=("Helvetica", 10)).pack()
        ttk.Label(about_frame, text="", font=("Helvetica", 8)).pack()
        ttk.Label(about_frame, text="Thanks to", font=("Helvetica", 8)).pack()
        ttk.Label(about_frame, text="Drecksfresse, Nicknol and MarzyHA", font=("Helvetica", 8)).pack()
        
        ttk.Button(about_frame, text="Schließen", command=about_window.destroy).pack(pady=10)
 
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
            new_df = pd.read_csv(filepath, sep=';', dtype=str, skipinitialspace=True)
             
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
        """Zeigt ein Auswahlfenster zum Filtern nach eindeutigen Werten in einer Spalte."""
        if self.df_original is None:
            messagebox.showwarning("Keine Daten", "Bitte zuerst eine CSV-Datei laden.")
            return

        col_map = {'area': self.COL_AREA, 'platform': self.COL_PLATFORM}
        filter_col = col_map.get(column_key)

        if filter_col not in self.df_original.columns:
            messagebox.showerror("Fehler", f"Die Spalte '{filter_col}' wurde in der CSV-Datei nicht gefunden.")
            return

        # Verwende FilterUtility, um das Auswahlfenster zu erstellen und den Filter anzuwenden
        FilterUtility.show_filter_window(self, filter_col)

    def show_domain_stats_gui(self):
        """Erstellt und zeigt eine Statistik der Entitätstypen (Domains)."""
        if self.df_original is None:
            messagebox.showwarning("Keine Daten", "Bitte zuerst eine CSV-Datei laden.")
            return

        if self.COL_ENTITY_ID not in self.df_original.columns:
            messagebox.showerror("Fehler", f"Die Spalte '{self.COL_ENTITY_ID}' fehlt für die Statistik.")
            return

        # Verwende FilterUtility, um die Statistik zu erstellen und anzuzeigen
        FilterUtility.show_stats_window(self)
class FilterUtility:
    """Eine Hilfsklasse zur Kapselung der Filter- und Statistik-Fensterlogik."""
    
    @staticmethod
    def show_filter_window(app, filter_col):
        """Erstellt und zeigt ein Fenster zum Filtern von Daten basierend auf einer Spalte."""
        unique_values = sorted(app.df_original[filter_col].unique().tolist(), key=str.lower)

        filter_window = tk.Toplevel(app.root)
        filter_window.title(f"Filtern nach {filter_col.replace('_', ' ').title()}")
        filter_window.geometry("350x450")
        
        colors = app.THEME_COLORS['dark' if app.is_dark_mode else 'light']
        filter_window.config(bg=colors['bg'])
        
        listbox = tk.Listbox(filter_window, selectmode=tk.SINGLE, width=40,
                              bg=colors['tree_even'], fg=colors['fg'],
                              selectbackground=colors['tree_odd'], selectforeground=colors['fg'])
        listbox.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Fügt einen speziellen Wert für leere Einträge hinzu
        if '' in app.df_original[filter_col].unique():
            listbox.insert(tk.END, "— KEIN WERT ZUGEWIESEN —")
        
        for val in unique_values:
            if val:  # Fügt nur nicht-leere Werte hinzu
                listbox.insert(tk.END, val)
        
        def apply_filter():
            try:
                selected_value = listbox.get(listbox.curselection()[0])
                filter_value = '' if selected_value == "— KEIN WERT ZUGEWIESEN —" else selected_value
                
                app.df_data = app.df_original[app.df_original[filter_col] == filter_value].copy()
                app.status_label.config(text=f"Gefiltert nach '{selected_value}' ({len(app.df_data)} Entitäten)", foreground="green")
                app.setup_treeview(app.df_data)
                filter_window.destroy()
            except IndexError:
                messagebox.showwarning("Auswahl fehlt", "Bitte einen Wert zum Filtern auswählen.")

        ttk.Button(filter_window, text="Filter anwenden", command=apply_filter).pack(pady=10)

    @staticmethod
    def show_stats_window(app):
        """Erstellt und zeigt ein Fenster für die Entitäts-Statistik."""
        domain_counts = app.df_original[app.COL_ENTITY_ID].str.split('.', n=1).str[0].value_counts()
        stats_df = domain_counts.reset_index()
        stats_df.columns = ['Entitätstyp (Domain)', 'Anzahl']

        stats_window = tk.Toplevel(app.root)
        stats_window.title("📊 Entitäts-Statistik nach Typ")
        stats_window.geometry("400x550")
        
        colors = app.THEME_COLORS['dark' if app.is_dark_mode else 'light']
        stats_window.config(bg=colors['bg'])
        
        stats_tree = ttk.Treeview(stats_window, columns=list(stats_df.columns), show='headings')
        stats_tree.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        for col in stats_df.columns:
            stats_tree.heading(col, text=col)
            stats_tree.column(col, width=150, anchor=tk.W)

        for i, row in stats_df.iterrows():
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            stats_tree.insert('', tk.END, values=row.tolist(), tags=(tag,))
        
        ttk.Label(stats_window, text=f"Gesamtanzahl eindeutiger Typen: {len(domain_counts)}").pack(pady=5)

if __name__ == "__main__": 
    root = tk.Tk() 
    app = EntityAnalyzerApp(root) 
    root.mainloop()
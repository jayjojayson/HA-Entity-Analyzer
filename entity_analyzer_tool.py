import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import pandas as pd
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from tkinter.font import Font
import numpy as np
import random

###########################
# HA_Entity_Analyzer_Tool #
###########################

# simple Entities Tool to analyze your exported csv-file
# simply display exported energy CSV files (line & bar-chart)
# import and export csv file
# free entity search
# area, platform & manufacturer filter
# entities statistic

class CustomNavigationToolbar(NavigationToolbar2Tk):
    def __init__(self, canvas, window):
        super().__init__(canvas, window)
        self.label_font = Font(family="Helvetica", size=12, weight="bold")
        for child in self.winfo_children():
            if isinstance(child, tk.Label):
                child.config(font=self.label_font, foreground='dark red')

    def set_message(self, msg):
        if msg:
            super().set_message(msg)
            for child in self.winfo_children():
                if isinstance(child, tk.Label):
                    child.config(font=self.label_font, foreground='dark red')

class CheckboxList(tk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0, bg=kwargs.get('bg'))
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.configure(style='TFrame')

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.checkboxes = {}
        self.style = ttk.Style()

        # Bind mouse wheel event for scrolling
        self.scrollable_frame.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        """Handles mouse wheel scrolling."""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def populate(self, items, colors):
        """Füllt die Liste mit Checkboxen."""
        for i, item in enumerate(items):
            var = tk.BooleanVar()
            
            bg_color = colors['tree_even'] if i % 2 == 0 else colors['tree_odd']
            font_size = 11
            style_name = f"CheckboxList{i}.TCheckbutton"
            self.style.configure(style_name, background=bg_color, foreground=colors['fg'], font=('Helvetica', font_size))

            cb = ttk.Checkbutton(self.scrollable_frame, text=item, variable=var, style=style_name)
            cb.pack(fill="x", expand=True)
            cb.bind("<MouseWheel>", self._on_mousewheel)
            self.checkboxes[item] = var

    def get_selected(self):
        """Gibt eine Liste der ausgewählten Elemente zurück."""
        return [item for item, var in self.checkboxes.items() if var.get()]

    def select_all(self):
        """Wählt alle Checkboxen aus."""
        for var in self.checkboxes.values():
            var.set(True)

    def deselect_all(self):
        """Hebt die Auswahl aller Checkboxen auf."""
        for var in self.checkboxes.values():
            var.set(False)

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
    COL_MANUFACTURER = 'manufacturer'
    
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
    VERSION = "v_1.3 by jayjojayson"
     
    def __init__(self, root):
        self.root = root
        self.root.title("Home Assistant Entity Analyzer Tool")
        self.root.geometry("1200x700")
 
        try:
            self.root.iconbitmap('E_A_T-logo.ico')
        except tk.TclError as e:
            print(f"Warnung: Konnte Icon 'E_A_T-logo.ico' nicht laden. Fehler: {e}")
            pass
 
        self.df_data = None
        self.df_original = None
        self.is_dark_mode = False
        self.is_always_on_top = False
        self.current_csv_type = None
        self.chart_type = 'line'  # Standard-Chart-Typ
        self.search_job = None

        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("Treeview", rowheight=25)
 
        self._create_menu()
        self._create_widgets()
         
        self.apply_theme('light')
 
    def _create_menu(self):
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)
 
        self.datei_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Datei", menu=self.datei_menu)
        self.datei_menu.add_command(label="📂 CSV Import", command=self.load_csv_data)
        self.datei_menu.add_command(label="💾 CSV Export", command=self.export_current_view_to_csv)
        self.datei_menu.add_separator()
        self.datei_menu.add_command(label="Exit", command=self.root.destroy)
 
        self.filter_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Filter", menu=self.filter_menu)
        self.filter_menu.add_command(label="📍 Filter Area", command=lambda: self.filter_data('area'))
        self.filter_menu.add_command(label="🔌 Filter Plattform", command=lambda: self.filter_data('platform'))
        self.filter_menu.add_command(label="🏭 Filter Manufacturer", command=lambda: self.filter_data('manufacturer'))
        self.filter_menu.add_separator()
        self.filter_menu.add_command(label="📊 Typ-Statistik anzeigen", command=self.show_domain_stats_gui)
        self.filter_menu.add_separator()
        self.filter_menu.add_command(label="🔄 Filter & Suche reset", command=self.reset_filter)
 
        self.optionen_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Optionen", menu=self.optionen_menu)
        self.optionen_menu.add_command(label="⬜ Hell/Dunkel Modus", command=self.toggle_dark_mode)
        self.optionen_menu.add_separator()
        self.optionen_menu.add_command(label="⬜ App im Vordergrund halten", command=self.toggle_always_on_top)
        self.optionen_menu.add_separator()
        self.optionen_menu.add_command(label="ℹ️ Info", command=self.show_about_window)

    def _create_widgets(self):
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Footer (persistent across views)
        footer_frame = ttk.Frame(self.root, padding="1")
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.status_label = ttk.Label(footer_frame, text="Bereit, lade eine CSV-Datei.", anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        progress_container = ttk.Frame(footer_frame)
        progress_container.pack(side=tk.LEFT, fill=tk.X, expand=False, padx=10)

        self.progress_bar = ttk.Progressbar(progress_container, orient='horizontal', mode='determinate', length=200)
        self.progress_bar.pack()

        self.progress_label = ttk.Label(progress_container, text="0%", anchor=tk.CENTER)
        self.progress_label.place(relx=0.5, rely=0.5, anchor='center')
        progress_container.pack_forget()

        self.version_label = ttk.Label(footer_frame, text=self.VERSION, anchor=tk.E)
        self.version_label.pack(side=tk.RIGHT)

        # Initial: Kontroll- und Tabellenansicht
        self._show_table_view()

    def _show_table_view(self):
        """Erstellt und zeigt die Standard-Tabellenansicht für Entitätsdaten."""
        # Löscht vorherige Ansichten, falls vorhanden
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        control_frame = ttk.Frame(self.main_frame, padding="10")
        control_frame.pack(fill=tk.X)

        ttk.Label(control_frame, text="Freie Suche:").pack(side=tk.LEFT, padx=(5, 5))
        self.search_entry = ttk.Entry(control_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind('<KeyRelease>', self.apply_filter_search)
        Tooltip(self.search_entry, "Geben Sie einen Suchbegriff ein, um die Entitäten zu filtern.")

        reset_button = ttk.Button(control_frame, text="🔄 Filter zurücksetzen", command=self.reset_filter)
        reset_button.pack(side=tk.RIGHT, padx=5)
        Tooltip(reset_button, "Setzt alle Filter und die Suche zurück.")

        table_frame = ttk.Frame(self.main_frame, padding="10")
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

        # Theme erneut anwenden, um sicherzustellen, dass alle neuen Widgets korrekt gestylt sind
        self.apply_theme('dark' if self.is_dark_mode else 'light')


    def apply_theme(self, mode):
        self.is_dark_mode = (mode == 'dark')
        colors = self.THEME_COLORS[mode]

        self.root.config(bg=colors['bg'])
        self.style.configure('.', background=colors['bg'], foreground=colors['fg'])
        self.style.configure('TFrame', background=colors['bg'])
        self.style.configure('TLabel', background=colors['bg'], foreground=colors['fg'])
        self.style.configure('TButton', background=colors['button_bg'], foreground=colors['button_fg'], padding=5, relief=tk.RAISED, borderwidth=1)
        self.style.map('TButton', background=[('active', colors['tree_odd'])])
        self.style.configure('TEntry', fieldbackground=colors['entry_bg'], foreground=colors['entry_fg'], insertcolor=colors['fg'])
        
        menu_config = {'bg': colors['menu_bg'], 'fg': colors['menu_fg'], 'activebackground': colors['tree_odd'], 'activeforeground': colors['fg']}
        self.menu_bar.config(**menu_config)
        for menu in [self.datei_menu, self.filter_menu, self.optionen_menu]:
            if menu:
                menu.config(**menu_config)

        if hasattr(self, 'status_label'):
            status_style = {'background': colors['status_bg'], 'foreground': colors['status_fg']}
            self.status_label.config(**status_style)
            self.version_label.config(**status_style)

        self.style.configure("Treeview.Heading", background=colors['tree_heading_bg'], foreground=colors['tree_heading_fg'], relief="raised")
        self.style.map("Treeview.Heading", background=[('active', colors['tree_odd'])])
        
        if hasattr(self, 'tree') and self.tree.winfo_exists():
            self.tree.tag_configure('oddrow', background=colors['tree_odd'], foreground=colors['fg'])
            self.tree.tag_configure('evenrow', background=colors['tree_even'], foreground=colors['fg'])
            self.style.configure("Treeview", fieldbackground=colors['tree_field_bg'], background=colors['tree_field_bg'], foreground=colors['fg'])

        if mode == 'dark':
            self.style.configure("Vertical.TScrollbar", background="#555555", troughcolor="#3e3e3e", bordercolor="#3e3e3e", arrowcolor="white")
            self.style.configure("Horizontal.TScrollbar", background="#555555", troughcolor="#3e3e3e", bordercolor="#3e3e3e", arrowcolor="white")
            self.style.configure('dark.Horizontal.TProgressbar', background='#4caf50', troughcolor=colors['status_bg'])
            self.progress_bar.configure(style='dark.Horizontal.TProgressbar')
        else:
            self.style.configure("Vertical.TScrollbar")
            self.style.configure("Horizontal.TScrollbar")
            self.style.configure('light.Horizontal.TProgressbar', background='#4caf50', troughcolor=colors['status_bg'])
            self.progress_bar.configure(style='light.Horizontal.TProgressbar')

        self.optionen_menu.entryconfig(0, label=f"{'✅' if self.is_dark_mode else '⬜'} Hell/Dunkel Modus")
        self.optionen_menu.entryconfig(2, label=f"{'✅' if self.is_always_on_top else '⬜'} App im Vordergrund halten")

        if self.df_data is not None and self.current_csv_type == 'entity':
             self.setup_treeview(self.df_data)

    def show_entity_details(self, event):
        selected_item = self.tree.focus()
        if not selected_item: return

        item_values = self.tree.item(selected_item, 'values')
        column_names = self.tree['columns']

        details_window = tk.Toplevel(self.root)
        details_window.title("Entitätsdetails")
        try:
            details_window.iconbitmap('E_A_T-logo.ico')
        except tk.TclError:
            pass
        colors = self.THEME_COLORS['dark' if self.is_dark_mode else 'light']
        details_window.config(bg=colors['bg'])
        details_frame = ttk.Frame(details_window, padding="15")
        details_frame.pack(expand=True, fill="both")

        for i, col_name in enumerate(column_names):
            ttk.Label(details_frame, text=f"{col_name.title()}:", font=("Helvetica", 10, "bold")).grid(row=i, column=0, sticky="w", pady=2, padx=5)
            value = item_values[i] if i < len(item_values) else ""
            ttk.Label(details_frame, text=value, wraplength=400, justify="left").grid(row=i, column=1, sticky="w", pady=2, padx=5)

        ttk.Button(details_frame, text="Schließen", command=details_window.destroy).grid(row=len(column_names), column=0, columnspan=2, pady=15)

    def show_about_window(self):
        about_window = tk.Toplevel(self.root)
        about_window.title("Über den Entity Analyzer")
        try:
            about_window.iconbitmap('E_A_T-logo.ico')
        except tk.TclError:
            pass
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
        ttk.Button(about_window, text="Schließen", command=about_window.destroy).pack(pady=10)
 
    def toggle_dark_mode(self):
        self.apply_theme('light' if self.is_dark_mode else 'dark')
 
    def toggle_always_on_top(self):
        self.is_always_on_top = not self.is_always_on_top
        self.root.wm_attributes('-topmost', self.is_always_on_top)
        self.optionen_menu.entryconfig(2, label=f"{'✅' if self.is_always_on_top else '⬜'} App im Vordergrund halten")
 
    def detect_csv_type(self, filepath):
        """Analysiert die Kopfzeile, um den CSV-Typ und das Trennzeichen zu bestimmen."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                header = f.readline().strip()
                # Heuristik für Energy-CSV: Zeitstempel-Format im Header
                if ',' in header and any(c.isdigit() for c in header):
                    if header.count(',') > header.count(';'):
                        return 'energy', ','
                # Standard-Annahme: Entity-CSV mit Semikolon
                return 'entity', ';'
        except Exception:
            # Fallback
            return 'entity', ';'

    def load_csv_data(self):
        filepath = filedialog.askopenfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not filepath: return

        self.current_csv_type, separator = self.detect_csv_type(filepath)
        
        try:
            new_df = pd.read_csv(filepath, sep=separator, dtype=str, skipinitialspace=True)
            new_df.columns = new_df.columns.str.lower().str.strip()
            cols_to_drop = [col for col in new_df.columns if col.startswith('unnamed:')]
            new_df.drop(columns=cols_to_drop, inplace=True, errors='ignore')

            self.df_original = new_df.fillna('')
            self.df_data = self.df_original.copy()
            
            filename = os.path.basename(filepath)
            
            if self.current_csv_type == 'energy':
                self.status_label.config(text=f"✅ Energie-CSV geladen: {filename}", foreground="green")
                # Direkter Aufruf des Chart-Fensters
                self.show_energy_chart_view()
            else: # entity
                self.status_label.config(text=f"✅ Entitäten-CSV geladen: {filename} ({len(self.df_data)} Entitäten)", foreground="green")
                # Stellt sicher, dass die Tabellenansicht angezeigt wird
                self._show_table_view()
                self.setup_treeview(self.df_data)

        except Exception as e:
            self.status_label.config(text=f"❌ Fehler: {e}", foreground="red")
            messagebox.showerror("Ladefehler", f"Fehler beim Laden der CSV-Datei:\n{e}")

    def export_current_view_to_csv(self):
        if self.df_data is None or self.df_data.empty:
            self.status_label.config(text="❌ Keine Daten zum Exportieren.", foreground="red")
            return

        filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not filepath: return

        try:
            sep = ',' if self.current_csv_type == 'energy' else ';'
            self.df_data.to_csv(filepath, sep=sep, index=False, encoding='utf-8')
            filename = os.path.basename(filepath)
            self.status_label.config(text=f"✅ Daten nach '{filename}' exportiert.", foreground="green")
            messagebox.showinfo("Export erfolgreich", f"Daten wurden nach:\n{filepath} exportiert.")
        except Exception as e:
            self.status_label.config(text=f"❌ Exportfehler: {e}", foreground="red")
            messagebox.showerror("Exportfehler", f"Fehler beim Speichern:\n{e}")
 
    def setup_treeview(self, df_to_display):
        if not hasattr(self, 'tree'): return

        self.tree.delete(*self.tree.get_children())
        new_columns = df_to_display.columns.tolist()
        self.tree['columns'] = new_columns

        self.tree.heading("#0", text="", anchor=tk.W)
        self.tree.column("#0", width=0, stretch=tk.NO)

        for col in new_columns:
            max_len = df_to_display[col].astype(str).str.len().max() if not df_to_display.empty else 10
            width = max(100, min(300, int(max_len * 7.5))) # Angepasste Berechnung
            self.tree.heading(col, text=col.upper(), command=lambda c=col: self.sort_column(c, False))
            self.tree.column(col, width=width, anchor=tk.W)

        data_to_insert = df_to_display.values.tolist()
        for i, row in enumerate(data_to_insert):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.tree.insert('', tk.END, values=row, tags=(tag,))
 
    def sort_column(self, col, reverse):
        if self.df_data is None: return

        try:
            # Versuch, numerisch zu sortieren, wenn möglich
            df_sorted = self.df_data.copy()
            df_sorted[col] = pd.to_numeric(df_sorted[col], errors='ignore')
            df_sorted.sort_values(by=col, ascending=not reverse, inplace=True, key=lambda x: x.astype(str).str.lower() if pd.api.types.is_string_dtype(x) else x)
            self.df_data = df_sorted
            self.setup_treeview(self.df_data)
            self.tree.heading(col, command=lambda c=col: self.sort_column(c, not reverse))
            self.status_label.config(text=f"Sortiert nach '{col.upper()}'", foreground="blue")
        except Exception as e:
            self.status_label.config(text=f"❌ Sortierfehler: {e}", foreground="red")
 
    def apply_filter_search(self, event=None):
        if self.search_job:
            self.root.after_cancel(self.search_job)
        self.search_job = self.root.after(300, self._perform_search)

    def _perform_search(self):
        if self.df_original is None: return

        search_term = self.search_entry.get().strip().lower()
        if not search_term:
            self.reset_filter()
            return

        mask = self.df_original.apply(lambda row: row.astype(str).str.lower().str.contains(search_term).any(), axis=1)
        self.df_data = self.df_original[mask]
        
        self.setup_treeview(self.df_data)
        self.status_label.config(text=f"{len(self.df_data)} Einträge für '{search_term}' gefunden.", foreground="green")
 
    def reset_filter(self):
        if self.df_original is None: return
        self.df_data = self.df_original.copy()
        if hasattr(self, 'search_entry'):
            self.search_entry.delete(0, tk.END)
        self.setup_treeview(self.df_data)
        self.status_label.config(text="Filter zurückgesetzt.", foreground="black")

    def filter_data(self, column_key):
        if self.df_original is None:
            messagebox.showwarning("Keine Daten", "Bitte eine CSV-Datei laden.")
            return
        if self.current_csv_type != 'entity':
             messagebox.showinfo("Info", "Filter sind nur für Entitäten-CSVs verfügbar.")
             return

        col_map = {'area': self.COL_AREA, 'platform': self.COL_PLATFORM, 'manufacturer': self.COL_MANUFACTURER}
        filter_col = col_map.get(column_key)

        if filter_col not in self.df_original.columns:
            messagebox.showerror("Fehler", f"Spalte '{filter_col}' nicht gefunden.")
            return
        FilterUtility.show_filter_window(self, filter_col)

    def show_domain_stats_gui(self):
        if self.df_original is None:
            messagebox.showwarning("Keine Daten", "Bitte eine CSV-Datei laden.")
            return
        if self.current_csv_type != 'entity':
             messagebox.showinfo("Info", "Statistiken sind nur für Entitäten-CSVs verfügbar.")
             return
             
        if self.COL_ENTITY_ID not in self.df_original.columns:
            messagebox.showerror("Fehler", f"Spalte '{self.COL_ENTITY_ID}' fehlt.")
            return
        FilterUtility.show_stats_window(self)

    # --- Energie-Chart-spezifische Methoden ---
    def show_energy_chart_view(self):
        """Bereitet die Daten vor und zeigt die Sensorauswahl an."""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        # HINWEIS: Die zeitaufwändige 'melt'-Operation wird hier entfernt
        # und erst nach der Sensorauswahl auf die gefilterten Daten angewendet.
        self.show_sensor_selection()

    def show_sensor_selection(self):
        """Zeigt eine Liste der verfügbaren Sensoren zur Auswahl an."""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        selection_frame = ttk.Frame(self.main_frame, padding="10")
        selection_frame.pack(fill=tk.BOTH, expand=True)
        
        colors = self.THEME_COLORS['dark' if self.is_dark_mode else 'light']
        selection_frame.configure(style="TFrame") # Ensure theme is applied

        # Top bar for title and select/deselect all button
        top_bar = ttk.Frame(selection_frame)
        top_bar.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(top_bar, text="Wähle Sensoren für die Analyse:", font=("Helvetica", 12, "bold")).pack(side=tk.LEFT)
        
        self.select_all_var = tk.BooleanVar()
        select_all_button = ttk.Checkbutton(top_bar, text="Alle auswählen/abwählen", variable=self.select_all_var, command=self.toggle_select_all_sensors)
        select_all_button.pack(side=tk.RIGHT)

        # CheckboxList
        self.sensor_checklist = CheckboxList(selection_frame, bg=colors['bg'])
        self.sensor_checklist.pack(fill="both", expand=True)
        
        sensors = self.df_data['entity_id'].unique()
        self.sensor_name_mapping = {s.replace('sensor.', ''): s for s in sensors}
        display_sensors = sorted(list(self.sensor_name_mapping.keys()))
        self.sensor_checklist.populate(display_sensors, colors)

        # Buttons
        button_frame = ttk.Frame(selection_frame)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Auswahl anzeigen (einzelne Diagramme)", command=self.plot_selected_individual).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="vergleiche Auswahl (kombiniertes Diagramm)", command=self.plot_selected_combined).pack(side=tk.LEFT, padx=5)
        self.apply_theme('dark' if self.is_dark_mode else 'light')


    def toggle_select_all_sensors(self):
        if self.select_all_var.get():
            self.sensor_checklist.select_all()
        else:
            self.sensor_checklist.deselect_all()

    def _perform_melt_on_selection(self, selected_sensors):
        """Führt die Transformation nur für die ausgewählten Sensoren durch."""
        df_filtered = self.df_data[self.df_data['entity_id'].isin(selected_sensors)]
        
        df_melted = df_filtered.melt(id_vars=['entity_id', 'type', 'unit'], var_name='timestamp', value_name='value')
        df_melted['timestamp'] = pd.to_datetime(df_melted['timestamp'], errors='coerce')
        df_melted.dropna(subset=['timestamp'], inplace=True)
        df_melted['value'] = pd.to_numeric(df_melted['value'], errors='coerce').fillna(0)
        
        return df_melted

    def plot_selected_individual(self):
        selected_short_names = self.sensor_checklist.get_selected()
        if not selected_short_names:
            messagebox.showwarning("Auswahl fehlt", "Bitte mindestens einen Sensor auswählen.")
            return
        
        selected_sensors = [self.sensor_name_mapping[s] for s in selected_short_names]
        self.selected_df = self._perform_melt_on_selection(selected_sensors)
        self.show_chart_plots()

    def plot_selected_combined(self):
        selected_short_names = self.sensor_checklist.get_selected()
        if not selected_short_names:
            messagebox.showwarning("Auswahl fehlt", "Bitte mindestens einen Sensor auswählen.")
            return

        selected_sensors = [self.sensor_name_mapping[s] for s in selected_short_names]
        df_plot = self._perform_melt_on_selection(selected_sensors)
        
        self.show_combined_chart_view(df_plot)

    def show_chart_plots(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        chart_container = ttk.Frame(self.main_frame)
        chart_container.pack(fill=tk.BOTH, expand=True)

        top_bar = ttk.Frame(chart_container)
        top_bar.pack(fill=tk.X, padx=10, pady=5)

        aggregation_frame = ttk.Frame(top_bar)
        aggregation_frame.pack(side=tk.LEFT, padx=0)
        buttons = {"Original": "original", "Tag": "D", "Woche": "W", "Monat": "M", "Jahr": "Y"}
        for text, period in buttons.items():
            btn = ttk.Button(aggregation_frame, text=text, command=lambda p=period: self.redraw_charts(p))
            btn.pack(side=tk.LEFT, padx=2)

        self.chart_type_button = ttk.Button(top_bar, text="Zu Balkendiagramm wechseln", command=self.toggle_chart_type)
        self.chart_type_button.pack(side=tk.RIGHT, padx=13)

        ttk.Button(top_bar, text="Zurück zur Sensorauswahl", command=self.show_sensor_selection).pack(side=tk.RIGHT, padx=10)

        self.chart_canvas = tk.Canvas(chart_container, borderwidth=0)
        self.chart_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        colors = self.THEME_COLORS['dark' if self.is_dark_mode else 'light']
        self.chart_canvas.config(bg=colors['bg'])

        scrollbar = ttk.Scrollbar(chart_container, orient="vertical", command=self.chart_canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.chart_canvas.configure(yscrollcommand=scrollbar.set)

        self.scrollable_frame = ttk.Frame(self.chart_canvas)
        self.scrollable_frame_id = self.chart_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        self.scrollable_frame.bind("<Configure>", self.on_frame_configure)
        self.chart_canvas.bind("<Configure>", self.on_canvas_configure)
        self.chart_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        self.redraw_charts()

    def show_combined_chart_view(self, df_plot):
        """Zeigt ein einzelnes Diagramm mit mehreren Sensoren und allen Steuerelementen an."""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        self.combined_df = df_plot  # Speichern für die Neuzeichnung

        chart_container = ttk.Frame(self.main_frame)
        chart_container.pack(fill=tk.BOTH, expand=True)

        top_bar = ttk.Frame(chart_container)
        top_bar.pack(fill=tk.X, padx=10, pady=5)
        
        # Hinzufügen der Steuerelemente
        aggregation_frame = ttk.Frame(top_bar)
        aggregation_frame.pack(side=tk.LEFT, padx=20)
        buttons = {"Original": "original", "Tag": "D", "Woche": "W", "Monat": "M", "Jahr": "Y"}
        for text, period in buttons.items():
            btn = ttk.Button(aggregation_frame, text=text, command=lambda p=period: self.redraw_combined_chart(p))
            btn.pack(side=tk.LEFT, padx=2)

        self.chart_type_button_combined = ttk.Button(top_bar, text="Zu Balkendiagramm wechseln", command=self.toggle_combined_chart_type)
        self.chart_type_button_combined.pack(side=tk.RIGHT, padx=10)

        ttk.Button(top_bar, text="Zurück zur Sensorauswahl", command=self.show_sensor_selection).pack(side=tk.RIGHT, padx=10)

        # Frame für das Diagramm selbst
        self.combined_chart_frame = ttk.Frame(chart_container)
        self.combined_chart_frame.pack(fill=tk.BOTH, expand=True)

        self.redraw_combined_chart()
        
    def redraw_combined_chart(self, period='original'):
        """Zeichnet das kombinierte Diagramm neu, basierend auf Aggregation und Typ."""
        for widget in self.combined_chart_frame.winfo_children():
            widget.destroy()
        
        self.current_period_combined = period
        df_to_plot = self.combined_df.copy()
        
        total_sum = df_to_plot['value'].sum()
        unit = df_to_plot['unit'].iloc[0] if not df_to_plot.empty and 'unit' in df_to_plot.columns else ''

        fig, ax = plt.subplots(figsize=(12, 6))
        colors = self.THEME_COLORS['dark' if self.is_dark_mode else 'light']

        if period != 'original':
            # Prüfen, ob die Datenmenge für ein Balkendiagramm geeignet ist
            try:
                first_entity = df_to_plot['entity_id'].unique()[0]
                resampled_data = df_to_plot[df_to_plot['entity_id'] == first_entity].set_index('timestamp')['value'].resample(period).sum()
                if len(resampled_data) > 50:
                    self.chart_type_button_combined.config(state=tk.DISABLED)
                    self.chart_type = 'line'
                else:
                    self.chart_type_button_combined.config(state=tk.NORMAL)
            except (IndexError, KeyError):
                 self.chart_type_button_combined.config(state=tk.DISABLED)
        else:
             self.chart_type_button_combined.config(state=tk.DISABLED)
             self.chart_type = 'line'

        # Zeichnen
        if self.chart_type == 'bar' and period != 'original':
            df_resampled = df_to_plot.groupby('entity_id').apply(lambda x: x.set_index('timestamp')['value'].resample(period).sum()).T
            df_resampled.plot(kind='bar', ax=ax, width=0.8)
            
            period_sums = df_resampled.sum(axis=1)
            max_heights = df_resampled.max(axis=1)
            for i, p_sum in enumerate(period_sums):
                if pd.notna(p_sum) and p_sum != 0:
                    y_pos = max_heights.iloc[i] if pd.notna(max_heights.iloc[i]) else 0
                    ax.text(i, y_pos, f'{p_sum:.2f}', ha='center', va='bottom', color=colors['fg'], fontsize=9, weight='bold')
            df_resampled.index = df_resampled.index.strftime('%Y-%m-%d %H:%M')

        else: # Liniendiagramm
            for entity, group in df_to_plot.groupby('entity_id'):
                sensor_sum = group['value'].sum()
                df_plot_resampled = group.set_index('timestamp')
                
                if period != 'original':
                    df_plot_resampled = df_plot_resampled['value'].resample(period).sum()
                else:
                    df_plot_resampled = df_plot_resampled['value']
                
                if not df_plot_resampled.empty:
                    label = f"{entity} ({sensor_sum:.2f} {unit})"
                    df_plot_resampled.plot(ax=ax, label=label, marker='.', linestyle='-')

        # Styling
        fig.patch.set_facecolor(colors['bg'])
        ax.set_facecolor(colors['tree_odd'])
        ax.tick_params(axis='x', colors=colors['fg'], labelrotation=45)
        ax.tick_params(axis='y', colors=colors['fg'])
        for spine in ax.spines.values():
            spine.set_color(colors['fg'])
        ax.title.set_color(colors['fg'])
        ax.xaxis.label.set_color(colors['fg'])
        ax.yaxis.label.set_color(colors['fg'])
        ax.legend(facecolor=colors['bg'], labelcolor=colors['fg'])
        ax.set_title(f"Sensorvergleich\nGesamtsumme aller Sensoren: {total_sum:.2f} {unit}")
        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.combined_chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        toolbar = CustomNavigationToolbar(canvas, self.combined_chart_frame)
        toolbar.update()
        canvas.get_tk_widget().pack(fill=tk.X)
        plt.close(fig)

    def toggle_combined_chart_type(self):
        """Schaltet den Chart-Typ für die kombinierte Ansicht um."""
        if self.chart_type == 'line':
            self.chart_type = 'bar'
            self.chart_type_button_combined.config(text="Zu Liniendiagramm wechseln")
        else:
            self.chart_type = 'line'
            self.chart_type_button_combined.config(text="Zu Balkendiagramm wechseln")
        self.redraw_combined_chart(getattr(self, 'current_period_combined', 'original'))
        
    def toggle_chart_type(self):
        """Wechselt zwischen Linien- und Balkendiagramm für individuelle Charts."""
        if self.chart_type_button.cget('state') == tk.DISABLED:
            messagebox.showinfo("Info", "Balkendiagramm nur für aggregierte Daten verfügbar.")
            return

        if self.chart_type == 'line':
            self.chart_type = 'bar'
            self.chart_type_button.config(text="Zu Liniendiagramm wechseln")
        else:
            self.chart_type = 'line'
            self.chart_type_button.config(text="Zu Balkendiagramm wechseln")
        
        self.redraw_charts(getattr(self, 'current_period', 'original'))

    def _on_mousewheel(self, event):
        if hasattr(self, 'chart_canvas'):
            self.chart_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
    def on_frame_configure(self, event):
        if hasattr(self, 'chart_canvas'):
            self.chart_canvas.configure(scrollregion=self.chart_canvas.bbox("all"))

    def on_canvas_configure(self, event):
        if hasattr(self, 'scrollable_frame_id'):
            self.chart_canvas.itemconfig(self.scrollable_frame_id, width=event.width)

    def redraw_charts(self, period='original'):
        """Zeichnet alle individuellen Charts basierend auf der gewählten Aggregationsperiode neu."""
        if not hasattr(self, 'scrollable_frame') or not hasattr(self, 'selected_df'):
            return
        
        self.current_period = period

        # Prüfung der Datenmenge für Balkendiagramm-Option
        if period != 'original':
            first_entity_data = self.selected_df.groupby('entity_id').get_group(list(self.selected_df['entity_id'].unique())[0])
            resampled_data = first_entity_data.set_index('timestamp')['value'].resample(period).sum()
            if len(resampled_data) > 100:
                self.chart_type_button.config(state=tk.DISABLED)
                if self.chart_type == 'bar': self.chart_type = 'line'
            else:
                self.chart_type_button.config(state=tk.NORMAL)
        else:
            self.chart_type_button.config(state=tk.DISABLED)
            if self.chart_type == 'bar': self.chart_type = 'line'
        
        # Update button text based on current chart type
        if self.chart_type == 'line':
            self.chart_type_button.config(text="Zu Balkendiagramm wechseln")
        else:
            self.chart_type_button.config(text="Zu Balkendiagramm wechseln")

        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        total_charts = len(self.selected_df['entity_id'].unique())
        self.progress_bar.config(maximum=total_charts, value=0)
        self.progress_label.config(text="0%")
        self.progress_bar.master.pack(side=tk.LEFT, fill=tk.X, expand=False, padx=10)
        
        chart_generator = self._chart_drawing_generator(period)
        self.root.after(100, self._process_chart_generator, chart_generator)

    def _chart_drawing_generator(self, period):
        """Generator, der jedes Diagramm einzeln erstellt und 'yield'ed."""
        for entity, group in self.selected_df.groupby('entity_id'):
            df_plot = group.set_index('timestamp')
            
            if period != 'original':
                df_plot = df_plot['value'].resample(period).sum().reset_index()
                df_plot['unit'] = group['unit'].iloc[0] if not group.empty else ''
            else:
                df_plot = df_plot.reset_index()
            
            self.create_chart_for_entity(entity, df_plot)
            yield

    def _process_chart_generator(self, generator):
        """Verarbeitet den Chart-Generator, um die UI nicht zu blockieren."""
        try:
            next(generator)
            self.progress_bar['value'] += 1
            percent = (self.progress_bar['value'] / self.progress_bar['maximum']) * 100
            self.progress_label.config(text=f"{percent:.0f}%")
            self.root.after(10, self._process_chart_generator, generator)
        except StopIteration:
            self.progress_bar.master.pack_forget()

    def create_chart_for_entity(self, entity_id, df_group):
        """Erstellt ein Matplotlib-Chart für eine einzelne Entität und fügt es dem scrollbaren Frame hinzu."""
        fig_frame = ttk.Frame(self.scrollable_frame, padding=10)
        fig_frame.pack(fill=tk.X, expand=True, pady=10)

        df_plot = df_group.copy()
        df_plot['timestamp'] = pd.to_datetime(df_plot['timestamp'])
        df_plot.set_index('timestamp', inplace=True)

        if df_plot.empty or df_plot['value'].isnull().all():
            ttk.Label(fig_frame, text=f"{entity_id}: Keine plotbaren Daten.").pack()
            return

        total_sum = df_plot['value'].sum()
        unit = df_plot['unit'].iloc[0] if not df_plot.empty and 'unit' in df_plot.columns else ''
        
        fig, ax = plt.subplots(figsize=(10, 4))
        colors = self.THEME_COLORS['dark' if self.is_dark_mode else 'light']
        color_choices = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
        random_color = random.choice(color_choices)

        if self.chart_type == 'line':
            df_plot['value'].plot(kind='line', ax=ax, marker='.', linestyle='-', color=random_color)
            if len(df_plot) < 50:  # Nur Werte bei wenigen Datenpunkten anzeigen
                for index, value in df_plot['value'].items():
                    ax.text(index, value, f' {value:.2f}', color=colors['fg'], va='bottom', ha='center', fontsize=8)
        else:
            # Für Balkendiagramme Zeitstempel in Strings umwandeln
            df_plot.index = df_plot.index.strftime('%Y-%m-%d %H:%M')
            bars = df_plot['value'].plot(kind='bar', ax=ax, color=random_color, width=0.8)
            for bar in bars.patches:
                yval = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2.0, yval, f'{yval:.2f}', ha='center', va='bottom', color=colors['fg'], fontsize=8)

        # Styling
        fig.patch.set_facecolor(colors['bg'])
        ax.set_facecolor(colors['tree_odd'])
        ax.tick_params(axis='x', colors=colors['fg'], labelrotation=45)
        ax.tick_params(axis='y', colors=colors['fg'])
        for spine in ax.spines.values():
            spine.set_color(colors['fg'])
        ax.title.set_color(colors['fg'])
        ax.xaxis.label.set_color(colors['fg'])
        ax.yaxis.label.set_color(colors['fg'])

        ax.set_title(f"Verlauf für: {entity_id}\nGesamtsumme: {total_sum:.2f} {unit}")
        ax.set_ylabel(unit)
        ax.set_xlabel("Zeitstempel")
        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=fig_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        toolbar = CustomNavigationToolbar(canvas, fig_frame)
        toolbar.update()
        canvas.get_tk_widget().pack(fill=tk.X)
        
        plt.close(fig)


class FilterUtility:
    @staticmethod
    def show_filter_window(app, filter_col):
        unique_values = sorted(app.df_original[filter_col].unique().tolist(), key=str.lower)
        filter_window = tk.Toplevel(app.root)
        filter_window.title(f"Filtern nach {filter_col.replace('_', ' ').title()}")
        try:
            filter_window.iconbitmap('E_A_T-logo.ico')
        except tk.TclError:
            pass
        filter_window.geometry("350x450")
        colors = app.THEME_COLORS['dark' if app.is_dark_mode else 'light']
        filter_window.config(bg=colors['bg'])
        
        listbox = tk.Listbox(filter_window, selectmode=tk.SINGLE, width=40, bg=colors['tree_even'], fg=colors['fg'], selectbackground=colors['tree_odd'], selectforeground=colors['fg'])
        listbox.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        if '' in app.df_original[filter_col].unique():
            listbox.insert(tk.END, "— KEIN WERT —")
        
        for val in unique_values:
            if val: listbox.insert(tk.END, val)
        
        def apply_filter():
            try:
                selected_value = listbox.get(listbox.curselection()[0])
                filter_value = '' if selected_value == "— KEIN WERT —" else selected_value
                app.df_data = app.df_original[app.df_original[filter_col] == filter_value].copy()
                app.status_label.config(text=f"Gefiltert nach '{selected_value}' ({len(app.df_data)} Entitäten)", foreground="green")
                app.setup_treeview(app.df_data)
                filter_window.destroy()
            except IndexError:
                messagebox.showwarning("Auswahl fehlt", "Bitte einen Wert auswählen.")

        ttk.Button(filter_window, text="Filter anwenden", command=apply_filter).pack(pady=10)

    @staticmethod
    def show_stats_window(app):
        domain_counts = app.df_original[app.COL_ENTITY_ID].str.split('.', n=1).str[0].value_counts()
        stats_df = domain_counts.reset_index()
        stats_df.columns = ['Entitätstyp (Domain)', 'Anzahl']
        stats_window = tk.Toplevel(app.root)
        stats_window.title("📊 Entitäts-Statistik")
        try:
            stats_window.iconbitmap('E_A_T-logo.ico')
        except tk.TclError:
            pass
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
 
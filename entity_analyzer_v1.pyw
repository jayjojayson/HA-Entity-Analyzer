#
# Entity_Analyzer_v1
#
# simple Entities Tool to analyze your csv-file
# python must be installed
# pandas library for python must be installed to use this Tool

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import sys 


# Globaler DataFrame für die aktuell angezeigten/gefilterten Daten
df_data = None
# Globaler DataFrame, der die Originaldaten speichert
df_original = None
tree = None
search_entry = None
status_label = None

# --- Datenlade- und Anzeige-Funktionen ---

def load_csv_data():
    """Öffnet einen Dateidialog, lädt die ausgewählte CSV-Datei und korrigiert das Format."""
    global df_data, df_original, status_label

    filepath = filedialog.askopenfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv")]
    )
    if not filepath:
        return

    try:
        # 1. CSV mit Semikolon (;) als Trennzeichen laden
        new_df = pd.read_csv(filepath, sep=';')
        
        # 2. Spaltennamen bereinigen (Kleinbuchstaben + Leerzeichen entfernen)
        new_df.columns = new_df.columns.str.lower().str.strip()
        
        # 3. NaN mit Leerstring füllen und alle Spalten zu String machen
        df_original = new_df.fillna('').astype(str)
        
        # 4. Nur "Unnamed" Spalten entfernen.
        cols_to_drop = [col for col in df_original.columns if col.startswith('unnamed:')]
        df_original.drop(columns=cols_to_drop, inplace=True, errors='ignore')
        
        df_data = df_original.copy()
        
        status_label.config(text=f"✅ Datei geladen: {filepath.split('/')[-1]} ({len(df_data)} Entitäten)")
        setup_treeview(df_data)

    except Exception as e:
        status_label.config(text=f"❌ Fehler beim Laden der Datei: {e}", foreground="red")
        messagebox.showerror("Ladefehler", f"Fehler beim Laden oder Verarbeiten der CSV-Datei:\n{e}")

def setup_treeview(df_to_display):
    """Konfiguriert und füllt das Treeview-Widget mit DataFrame-Daten und wendet Zebra-Striping an."""
    global tree
    
    # Entfernt vorhandene Childs und Spalten
    for item in tree.get_children():
        tree.delete(item)
    
    # Definiert neue Spalten
    new_columns = df_to_display.columns.tolist()
    
    tree['columns'] = new_columns
    
    # Definiert Spaltenüberschriften und passt die Spaltenbreite an
    tree.heading("#0", text="", anchor=tk.W)
    tree.column("#0", width=0, stretch=tk.NO)

    for col in new_columns:
        # Spaltenbreite automatisch anpassen
        max_len = df_to_display[col].astype(str).str.len().max() if not df_to_display.empty else 10
        width = max(100, min(300, max_len * 7 + 10)) 
        
        # 💡 SYNTAX-KORREKTUR: Sicherstellen, dass die Klammer am Ende geschlossen ist.
        tree.heading(col, text=col.upper(), command=lambda c=col: sort_column(tree, c, False)) 
        
        tree.column(col, width=width, anchor=tk.W)

    # Füllt die Tabelle mit den Zeilen und wendet Tags für die Farbe an
    for i, (_, row) in enumerate(df_to_display.iterrows()):
        tag = 'evenrow' if i % 2 == 0 else 'oddrow'
        tree.insert('', tk.END, values=row.tolist(), tags=(tag,))


def sort_column(tv, col, reverse):
    """Sortiert die Treeview-Spalte und aktualisiert die Anzeige."""
    global df_data, status_label 
    
    if df_data is None: 
        status_label.config(text="❌ Bitte zuerst eine CSV-Datei laden!", foreground="red")
        return

    try:
        # Die Sortierung wird direkt auf dem aktuell angezeigten DataFrame durchgeführt
        sorted_df = df_data.sort_values(by=col, ascending=not reverse, key=lambda x: x.str.lower())
        
        # Aktualisiert den globalen DF und das GUI
        df_data = sorted_df
        setup_treeview(df_data)
        
        # Setzt den Befehl für die nächste Sortierung (umgekehrt)
        tv.heading(col, command=lambda c=col: sort_column(tv, c, not reverse))
        
        status_label.config(text=f"Daten sortiert nach '{col.upper()}' {'(Absteigend)' if reverse else '(Aufsteigend)'}")
        
    except Exception as e:
        status_label.config(text=f"❌ Sortierfehler: {e}", foreground="red")

def apply_filter_search(event=None):
    """Sucht und filtert die Daten basierend auf der Eingabe (Name/ID)."""
    global df_original, search_entry, df_data, status_label

    if df_original is None:
        status_label.config(text="❌ Bitte zuerst eine CSV-Datei laden!", foreground="red")
        return

    search_term = search_entry.get().strip()
    
    if not search_term:
        df_data = df_original.copy()
        status_label.config(text="Filter entfernt. Zeige alle Daten.")
        setup_treeview(df_data)
        return

    # Suchen und Filtern des Pandas DataFrame (Case-Insensitive, Suche in allen Spalten)
    mask = df_original.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)
    df_data = df_original[mask].copy()

    if not df_data.empty:
        status_label.config(text=f"🔎 {len(df_data)} Entitäten gefunden, die '{search_term}' enthalten.")
        setup_treeview(df_data)
    else:
        status_label.config(text=f"Keine Entität mit '{search_term}' gefunden.", foreground="orange")
        setup_treeview(pd.DataFrame())

# --- Funktionen für Filtern und Gruppierung ---

def filter_data(column_key):
    """Zeigt ein Auswahlfenster zum Filtern nach Area oder Plattform an."""
    global df_original, status_label, root
    
    if df_original is None:
        status_label.config(text="❌ Bitte zuerst eine CSV-Datei laden!", foreground="red")
        return
        
    # Spaltennamen-Mapping (bereinigt)
    col_map = {
        'area': 'area', 
        'platform': 'platform (integration)' 
    }
    
    filter_col = col_map.get(column_key)
    
    if filter_col not in df_original.columns:
        status_label.config(text=f"❌ Spalte '{filter_col}' nicht in CSV gefunden. Verfügbare Spalten: {', '.join(df_original.columns)}", foreground="red")
        return

    unique_values = df_original[filter_col].unique().tolist()
    unique_values.sort(key=str.lower)

    # Neues Toplevel-Fenster für die Auswahl
    filter_window = tk.Toplevel(root)
    filter_window.title(f"Filtern nach {column_key.upper()}")
    
    listbox_frame = ttk.Frame(filter_window)
    listbox_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
    
    listbox_scrollbar = ttk.Scrollbar(listbox_frame)
    listbox_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    listbox = tk.Listbox(listbox_frame, selectmode=tk.SINGLE, yscrollcommand=listbox_scrollbar.set, width=40)
    listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    listbox_scrollbar.config(command=listbox.yview)

    # Fügt die eindeutigen Werte zur Listbox hinzu
    if '' in df_original[filter_col].unique():
         listbox.insert(tk.END, "— KEIN WERT ZUGEWIESEN —")
    for val in unique_values:
        if val != '':
            listbox.insert(tk.END, val)

    def apply_single_filter():
        """Führt den Filtervorgang nach Auswahl aus."""
        global df_data
        
        try:
            selected_index = listbox.curselection()[0]
            selected_value = listbox.get(selected_index)
            
            # Setze den Filterwert auf leeren String, falls "KEIN WERT ZUGEWIESEN" ausgewählt wurde
            filter_value = '' if selected_value == "— KEIN WERT ZUGEWIESEN —" else selected_value
                
            # Filtern des Original-DataFrames
            df_data = df_original[df_original[filter_col] == filter_value].copy()
            
            status_label.config(text=f"✅ Gefiltert nach {column_key.upper()}: '{selected_value}' ({len(df_data)} Entitäten)")
            setup_treeview(df_data)
            filter_window.destroy()
            
        except IndexError:
            messagebox.showwarning("Auswahl fehlt", "Bitte einen Wert zum Filtern auswählen.")
        except Exception as e:
            messagebox.showerror("Filterfehler", f"Fehler beim Filtern: {e}")

    # Button zum Anwenden des Filters
    apply_button = ttk.Button(filter_window, text="Filter anwenden", command=apply_single_filter)
    apply_button.pack(pady=10)
    
def reset_filter():
    """Setzt den Filter zurück und zeigt den Original-DataFrame an."""
    global df_original, df_data, search_entry
    if df_original is None: return
    
    df_data = df_original.copy()
    search_entry.delete(0, tk.END) # Suchfeld leeren
    setup_treeview(df_data)
    status_label.config(text="Filter und Suche zurückgesetzt. Zeige alle Entitäten.")


def show_domain_stats_gui():
    """Gruppiert Entitäten nach Typ (Domain) und zeigt die Zählungen in einer GUI-Tabelle an."""
    global df_original, status_label, root
    
    if df_original is None:
        status_label.config(text="❌ Keine Daten geladen!", foreground="red")
        return
        
    # Abfrage des korrekten Spaltennamens in Kleinbuchstaben
    entity_id_col = 'entity id'
    if entity_id_col not in df_original.columns:
        status_label.config(text="❌ Spalte 'entity id' fehlt für die Statistik!", foreground="red")
        return

    # Extrahieren des Entitätstyps (Domain) und Zählen
    domain_counts = df_original[entity_id_col].str.split('.', n=1, expand=True)[0].value_counts()
    
    # DataFrame für die Darstellung erstellen
    stats_df = domain_counts.reset_index()
    stats_df.columns = ['Entitätstyp (Domain)', 'Anzahl']

    # Neues Fenster für die Statistik erstellen
    stats_window = tk.Toplevel(root)
    stats_window.title("📊 Entitäts-Statistik nach Typ")
    stats_window.geometry("400x400")
    
    # Treeview für die Statistik-Tabelle
    stats_tree = ttk.Treeview(stats_window, columns=stats_df.columns.tolist(), show='headings')
    stats_tree.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    # Konfigurieren der Spaltenüberschriften
    for col in stats_df.columns:
        stats_tree.heading(col, text=col)
        stats_tree.column(col, width=150, anchor=tk.W)

    # Füllen der Tabelle mit den Statistiken
    for _, row in stats_df.iterrows():
        stats_tree.insert('', tk.END, values=row.tolist())
    
    # Gesamtanzahl anzeigen
    total_label = ttk.Label(stats_window, text=f"Gesamtanzahl eindeutiger Typen: {len(domain_counts)}", padding=5)
    total_label.pack()

# ----------------- GUI-Einrichtung -----------------

root = tk.Tk()
root.title("Home Assistant Entitäten Analyse Tool (GUI)")
root.geometry("1200x700")

# --- Stil-Konfiguration ---
style = ttk.Style()
style.configure("Treeview", rowheight=25)

# --- 1. Top Bar (Steuerungselemente) ---
control_frame = ttk.Frame(root, padding="10")
control_frame.pack(fill=tk.X)

# Button zum Laden der Datei
load_button = ttk.Button(control_frame, text="📂 CSV-Datei laden", command=load_csv_data)
load_button.pack(side=tk.LEFT, padx=5)

# Eingabefeld für die Suche
search_label = ttk.Label(control_frame, text="Freie Suche:")
search_label.pack(side=tk.LEFT, padx=(20, 5)) 

search_entry = ttk.Entry(control_frame, width=30)
search_entry.pack(side=tk.LEFT, padx=5)
search_entry.bind('<KeyRelease>', apply_filter_search)

# Filtern Buttons
filter_area_button = ttk.Button(control_frame, text="📍 Filtern nach Area", command=lambda: filter_data('area'))
filter_area_button.pack(side=tk.LEFT, padx=5)

filter_platform_button = ttk.Button(control_frame, text="🔌 Filtern nach Plattform", command=lambda: filter_data('platform'))
filter_platform_button.pack(side=tk.LEFT, padx=5)

# Statistik Button
stats_button = ttk.Button(control_frame, text="📊 Typ-Statistik anzeigen", command=show_domain_stats_gui)
stats_button.pack(side=tk.LEFT, padx=20)

# Reset Button
reset_button = ttk.Button(control_frame, text="🔄 Filter zurücksetzen", command=reset_filter)
reset_button.pack(side=tk.LEFT, padx=5)

# --- 2. Treeview (Datenansicht) ---
table_frame = ttk.Frame(root, padding="10")
table_frame.pack(fill=tk.BOTH, expand=True)

# Scrollbars
vsb = ttk.Scrollbar(table_frame, orient="vertical")
hsb = ttk.Scrollbar(table_frame, orient="horizontal")

# Treeview (Tabelle)
tree = ttk.Treeview(table_frame, columns=[], show='headings', yscrollcommand=vsb.set, xscrollcommand=hsb.set)
vsb.config(command=tree.yview)
hsb.config(command=tree.xview)

# Tags für abwechselnde Zeilenfarben (Zebra-Striping)
tree.tag_configure('oddrow', background='#f0f0f0') # Hellgrau
tree.tag_configure('evenrow', background='white')   # Weiß

# Platzierung der Komponenten
vsb.pack(side=tk.RIGHT, fill=tk.Y)
hsb.pack(side=tk.BOTTOM, fill=tk.X)
tree.pack(fill=tk.BOTH, expand=True)

# --- 3. Status Bar ---
# Ein Frame für die unterste Zeile
footer_frame = ttk.Frame(root, padding="1")
footer_frame.pack(side=tk.BOTTOM, fill=tk.X)

# Status-Label auf der linken Seite
status_label = ttk.Label(footer_frame, text="Bereit, lade eine Home Assistant Entitäten CSV-Datei.", relief=tk.SUNKEN, anchor=tk.W, background='SystemWindow', foreground='SystemWindowText')
status_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Version/Copyright-Label auf der rechten Seite
version_label = ttk.Label(footer_frame, text=" v1 by jayjojayson", relief=tk.SUNKEN, anchor=tk.E, background='SystemWindow', foreground='gray')
version_label.pack(side=tk.RIGHT)

# Hauptloop starten
if __name__ == "__main__":
    root.mainloop()
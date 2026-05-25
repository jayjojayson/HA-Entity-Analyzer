import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
import pandas as pd
import os
import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np
from PIL import Image, ImageTk
import sys

try:
    import ttkbootstrap as ttkb
    TTKBOOTSTRAP_AVAILABLE = True
except ImportError:
    TTKBOOTSTRAP_AVAILABLE = False
    print("TTKBootstrap nicht gefunden. Bitte installieren Sie es mit: pip install ttkbootstrap")

# ─── Übersetzungen / Translations ───────────────────────────────────────────
TRANSLATIONS = {
    'de': {
        # Menü
        'menu_file': 'Datei', 'menu_import_csv': '📂 CSV Importieren',
        'menu_export_csv': '💾 CSV Exportieren', 'menu_exit': '❌ Beenden',
        'menu_filter': 'Filter', 'menu_filter_area': '📍 Nach Area filtern',
        'menu_filter_platform': '🔌 Nach Plattform filtern',
        'menu_filter_manufacturer': '🏭 Nach Hersteller filtern',
        'menu_show_stats': '📊 Statistik anzeigen',
        'menu_reset_filter': '🔄 Filter zurücksetzen',
        'menu_view': 'Ansicht', 'menu_dark_mode': '🌙 Dark Mode',
        'menu_always_on_top': '📌 Immer im Vordergrund',
        'menu_about': 'ℹ️ Über', 'menu_language': '🌐 Deutsch → English',
        # Titel & Buttons
        'app_title': ' Home Assistant Entity Analyzer',
        'search_label': '🔍 Suche:',
        'search_tooltip': 'Suchbegriff eingeben um Entitäten zu filtern',
        'btn_reset': '🔄 Reset', 'btn_reset_tooltip': 'Alle Filter zurücksetzen',
        'btn_import': '📂 Importieren', 'btn_export': '💾 Exportieren',
        'status_ready': 'Bereit - Importieren Sie eine CSV-Datei um zu beginnen',
        # Statusmeldungen
        'status_energy_loaded': '✅ Energie-CSV geladen: {filename}',
        'status_entity_loaded': '✅ Entitäten-CSV geladen: {filename} ({count} Entitäten)',
        'status_error': '❌ Fehler: {error}',
        'status_no_export_data': '❌ Keine Daten zum Exportieren.',
        'status_exported': "✅ Daten nach '{filename}' exportiert.",
        'status_export_error': '❌ Exportfehler: {error}',
        'status_sorted': "Sortiert nach '{col}'",
        'status_sort_error': '❌ Sortierfehler: {error}',
        'status_search_results': "{count} Einträge für '{term}' gefunden.",
        'status_filter_reset': 'Filter zurückgesetzt.',
        'status_filtered': "Gefiltert nach '{value}' ({count} Entitäten)",
        'status_aot_on': 'Immer im Vordergrund: aktiviert',
        'status_aot_off': 'Immer im Vordergrund: deaktiviert',
        # Dialoge
        'dlg_load_error': 'Ladefehler',
        'dlg_load_error_msg': 'Fehler beim Laden der CSV-Datei:\n{error}',
        'dlg_no_data': 'Keine Daten',
        'dlg_load_csv_first': 'Bitte laden Sie zuerst eine CSV-Datei.',
        'dlg_load_csv': 'Bitte eine CSV-Datei laden.',
        'dlg_export_success': 'Export erfolgreich',
        'dlg_export_success_msg': 'Daten wurden exportiert nach:\n{filepath}',
        'dlg_export_error': 'Exportfehler',
        'dlg_export_error_msg': 'Fehler beim Speichern:\n{error}',
        'dlg_info': 'Info',
        'dlg_filter_entity_only': 'Filter sind nur für Entitäten-CSVs verfügbar.',
        'dlg_stats_entity_only': 'Statistiken sind nur für Entitäten-CSVs verfügbar.',
        'dlg_error': 'Fehler',
        'dlg_column_not_found': "Spalte '{col}' nicht gefunden.",
        'dlg_column_missing': "Spalte '{col}' fehlt.",
        'dlg_selection_missing': 'Auswahl fehlt',
        'dlg_select_sensor': 'Bitte mindestens einen Sensor auswählen.',
        'dlg_select_value': 'Bitte einen Wert auswählen.',
        # Detail-Fenster
        'details_title': 'Entitätsdetails', 'details_header': '📋 Entitätsdetails',
        'btn_close': 'Schließen',
        # Über-Fenster
        'about_title': 'Über den HA Entity Analyzer',
        'about_description': 'Ein Tool zur Analyse von Home Assistant\nEntity-CSV-Dateien',
        'about_thanks': 'Entwickelt mit ❤️',
        # Energie-Diagramme
        'sensor_select_title': '⚡ Sensoren für Analyse auswählen:',
        'select_all': 'Alle auswählen',
        'btn_individual': '📈 Einzelne Diagramme', 'btn_compare': '📊 Vergleichen',
        'btn_bar_chart': '📊 Balkendiagramm', 'btn_line_chart': '📈 Liniendiagramm',
        'btn_back': '🔙 Zurück',
        'period_original': 'Original', 'period_day': 'Tag', 'period_week': 'Woche',
        'period_month': 'Monat', 'period_year': 'Jahr',
        'chart_comparison': 'Sensorvergleich',
        'chart_total': 'Gesamtsumme: {total:.2f} {unit}',
        'chart_history': 'Verlauf: {entity}\nSumme: {total:.2f} {unit}',
        'chart_timestamp': 'Zeitstempel',
        'chart_no_data': '{entity}: Keine plotbaren Daten.',
        # Filter-Fenster
        'filter_title': 'Filtern nach {col}',
        'filter_no_value': '— KEIN WERT —',
        'btn_apply_filter': '✅ Filter anwenden', 'btn_cancel': 'Abbrechen',
        # Statistik-Fenster
        'stats_title': '📊 Entitäts-Statistik',
        'stats_col_domain': 'Entitätstyp (Domain)', 'stats_col_count': 'Anzahl',
        'stats_total': 'Gesamtanzahl eindeutiger Typen: {count}',
        # Theme-Namen
        'theme_light': 'Hell', 'theme_darkly': 'Darkly', 'theme_cyborg': 'Cyborg',
        'theme_vapor': 'Vapor', 'theme_litera': 'Litera', 'theme_minty': 'Minty',
    },
    'en': {
        # Menu
        'menu_file': 'File', 'menu_import_csv': '📂 Import CSV',
        'menu_export_csv': '💾 Export CSV', 'menu_exit': '❌ Exit',
        'menu_filter': 'Filter', 'menu_filter_area': '📍 Filter by Area',
        'menu_filter_platform': '🔌 Filter by Platform',
        'menu_filter_manufacturer': '🏭 Filter by Manufacturer',
        'menu_show_stats': '📊 Show Statistics',
        'menu_reset_filter': '🔄 Reset Filter',
        'menu_view': 'View', 'menu_dark_mode': '🌙 Dark Mode',
        'menu_always_on_top': '📌 Always on Top',
        'menu_about': 'ℹ️ About', 'menu_language': '🌐 English → Deutsch',
        # Title & Buttons
        'app_title': ' Home Assistant Entity Analyzer',
        'search_label': '🔍 Search:',
        'search_tooltip': 'Enter search term to filter entities',
        'btn_reset': '🔄 Reset', 'btn_reset_tooltip': 'Reset all filters',
        'btn_import': '📂 Import', 'btn_export': '💾 Export',
        'status_ready': 'Ready - Import a CSV file to begin',
        # Status messages
        'status_energy_loaded': '✅ Energy CSV loaded: {filename}',
        'status_entity_loaded': '✅ Entity CSV loaded: {filename} ({count} entities)',
        'status_error': '❌ Error: {error}',
        'status_no_export_data': '❌ No data to export.',
        'status_exported': "✅ Data exported to '{filename}'.",
        'status_export_error': '❌ Export error: {error}',
        'status_sorted': "Sorted by '{col}'",
        'status_sort_error': '❌ Sort error: {error}',
        'status_search_results': "{count} entries found for '{term}'.",
        'status_filter_reset': 'Filter reset.',
        'status_filtered': "Filtered by '{value}' ({count} entities)",
        'status_aot_on': 'Always on top: enabled',
        'status_aot_off': 'Always on top: disabled',
        # Dialogs
        'dlg_load_error': 'Load Error',
        'dlg_load_error_msg': 'Error loading CSV file:\n{error}',
        'dlg_no_data': 'No Data',
        'dlg_load_csv_first': 'Please load a CSV file first.',
        'dlg_load_csv': 'Please load a CSV file.',
        'dlg_export_success': 'Export Successful',
        'dlg_export_success_msg': 'Data exported to:\n{filepath}',
        'dlg_export_error': 'Export Error',
        'dlg_export_error_msg': 'Error saving:\n{error}',
        'dlg_info': 'Info',
        'dlg_filter_entity_only': 'Filters are only available for entity CSVs.',
        'dlg_stats_entity_only': 'Statistics are only available for entity CSVs.',
        'dlg_error': 'Error',
        'dlg_column_not_found': "Column '{col}' not found.",
        'dlg_column_missing': "Column '{col}' is missing.",
        'dlg_selection_missing': 'Selection Missing',
        'dlg_select_sensor': 'Please select at least one sensor.',
        'dlg_select_value': 'Please select a value.',
        # Details window
        'details_title': 'Entity Details', 'details_header': '📋 Entity Details',
        'btn_close': 'Close',
        # About window
        'about_title': 'About HA Entity Analyzer',
        'about_description': 'A tool for analyzing Home Assistant\nentity CSV files',
        'about_thanks': 'Developed with ❤️',
        # Energy charts
        'sensor_select_title': '⚡ Select sensors for analysis:',
        'select_all': 'Select all',
        'btn_individual': '📈 Individual Charts', 'btn_compare': '📊 Compare',
        'btn_bar_chart': '📊 Bar Chart', 'btn_line_chart': '📈 Line Chart',
        'btn_back': '🔙 Back',
        'period_original': 'Original', 'period_day': 'Day', 'period_week': 'Week',
        'period_month': 'Month', 'period_year': 'Year',
        'chart_comparison': 'Sensor Comparison',
        'chart_total': 'Total: {total:.2f} {unit}',
        'chart_history': 'History: {entity}\nTotal: {total:.2f} {unit}',
        'chart_timestamp': 'Timestamp',
        'chart_no_data': '{entity}: No plottable data.',
        # Filter window
        'filter_title': 'Filter by {col}',
        'filter_no_value': '— NO VALUE —',
        'btn_apply_filter': '✅ Apply Filter', 'btn_cancel': 'Cancel',
        # Stats window
        'stats_title': '📊 Entity Statistics',
        'stats_col_domain': 'Entity Type (Domain)', 'stats_col_count': 'Count',
        'stats_total': 'Total unique types: {count}',
        # Theme names
        'theme_light': 'Light', 'theme_darkly': 'Darkly', 'theme_cyborg': 'Cyborg',
        'theme_vapor': 'Vapor', 'theme_litera': 'Litera', 'theme_minty': 'Minty',
    }
}

# ─── Modernes Chart-Design ──────────────────────────────────────────────────
MODERN_THEME = {
    'light': {
        'bg': '#ffffff',
        'panel': '#ffffff',
        'fg': '#0f172a',
        'muted': '#64748b',
        'grid': '#e2e8f0',
        'spine': '#cbd5e1',
        'palette': [
            '#3b82f6', '#10b981', '#f59e0b', '#ef4444',
            '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16',
            '#f97316', '#14b8a6',
        ],
        'fill_alpha': 0.12,
    },
    'dark': {
        'bg': '#0f172a',
        'panel': '#0f172a',
        'fg': '#f1f5f9',
        'muted': '#94a3b8',
        'grid': '#1e293b',
        'spine': '#334155',
        'palette': [
            '#60a5fa', '#34d399', '#fbbf24', '#f87171',
            '#a78bfa', '#f472b6', '#22d3ee', '#a3e635',
            '#fb923c', '#2dd4bf',
        ],
        'fill_alpha': 0.18,
    },
}


def install_bar_hover(fig, ax, bar_groups, theme, unit=''):
    """Hover-Tooltip für Bar-Charts.

    bar_groups: Liste von Tupeln (BarContainer, label, color, values).
    """
    annot = ax.annotate(
        "", xy=(0, 0), xytext=(0, 12),
        textcoords="offset points", ha='center', va='bottom',
        fontsize=9, fontweight='600',
        bbox=dict(boxstyle="round,pad=0.45", fc=theme['fg'],
                  ec='none', alpha=0.95),
        color=theme['bg'], zorder=10,
    )
    annot.set_visible(False)
    state = {'visible': False}

    def hide():
        if state['visible']:
            annot.set_visible(False)
            state['visible'] = False
            try:
                fig.canvas.draw_idle()
            except Exception:
                pass

    def on_motion(event):
        if event.inaxes is not ax:
            hide()
            return
        for bars, label, _color, values in bar_groups:
            for idx, bar in enumerate(bars):
                contains, _ = bar.contains(event)
                if not contains:
                    continue
                val = float(values[idx]) if idx < len(values) else bar.get_height()
                annot.xy = (bar.get_x() + bar.get_width() / 2,
                            bar.get_height())
                clean_label = str(label).replace('sensor.', '')
                suffix = f" {unit}" if unit else ''
                annot.set_text(f"{clean_label}\n{val:.2f}{suffix}")
                annot.set_visible(True)
                state['visible'] = True
                fig.canvas.draw_idle()
                return
        hide()

    fig.canvas.mpl_connect("motion_notify_event", on_motion)
    fig.canvas.mpl_connect("axes_leave_event", lambda e: hide())
    fig.canvas.mpl_connect("figure_leave_event", lambda e: hide())


def fit_figure_to_widget(fig, canvas, root, tight_rect=(0, 0.04, 1, 0.96),
                         min_w_in=4.0, min_h_in=3.0):
    """Erzwingt nach pack(), dass die Figur auf die echte Widget-Größe wächst.

    Ohne diesen Schritt rendert matplotlib mit der initialen figsize und der
    Platz im Container bleibt ungenutzt (links/rechts Weißraum) oder die
    Figur ist größer als das Widget (Legende wird beschnitten).
    """
    try:
        root.update_idletasks()
        widget = canvas.get_tk_widget()
        w_px = widget.winfo_width()
        h_px = widget.winfo_height()
        if w_px <= 1 or h_px <= 1:
            return
        dpi = fig.get_dpi()
        new_w = max(min_w_in, w_px / dpi)
        new_h = max(min_h_in, h_px / dpi)
        fig.set_size_inches(new_w, new_h, forward=False)
        try:
            fig.tight_layout(rect=tight_rect)
        except Exception:
            pass
        canvas.draw_idle()
    except Exception:
        pass


def bind_responsive_figure(fig, canvas, min_height_in=3.0,
                           tight_rect=(0, 0.04, 1, 0.96)):
    """Hält die Figur an die Breite (und ggf. Höhe) des Tk-Widgets gekoppelt.

    Verwendet einen einfachen Debouncer, damit Drag-Resize nicht hundert
    Mal pro Sekunde neu rendert. set_size_inches(forward=False) verhindert
    Rückkopplung in den Tk-Eventloop. tight_rect sollte zum Original-Layout
    der jeweiligen Figur passen, damit nach Resize keine Beschnitte entstehen.
    """
    widget = canvas.get_tk_widget()
    state = {'pending_id': None, 'last_w': 0, 'last_h': 0}

    def apply(w_px, h_px):
        state['pending_id'] = None
        if w_px <= 1:
            return
        try:
            dpi = fig.get_dpi()
            new_w = max(2.0, w_px / dpi)
            new_h = max(min_height_in, h_px / dpi) if h_px > 1 else fig.get_figheight()
            cur_w, cur_h = fig.get_size_inches()
            if abs(cur_w - new_w) < 0.05 and abs(cur_h - new_h) < 0.05:
                return
            fig.set_size_inches(new_w, new_h, forward=False)
            try:
                fig.tight_layout(rect=tight_rect)
            except Exception:
                pass
            canvas.draw_idle()
        except Exception:
            pass

    def on_configure(event):
        if event.width == state['last_w'] and event.height == state['last_h']:
            return
        state['last_w'] = event.width
        state['last_h'] = event.height
        if state['pending_id'] is not None:
            try:
                widget.after_cancel(state['pending_id'])
            except Exception:
                pass
        state['pending_id'] = widget.after(80, lambda w=event.width, h=event.height: apply(w, h))

    widget.bind('<Configure>', on_configure, add='+')


def install_mouse_zoom(fig, ax, canvas, require_modifier=True):
    """Mausrad-Zoom um den Cursor. Doppelklick setzt zurück (Auto-Range).

    Mit require_modifier=True ist nur Strg/Cmd+Mausrad aktiv — vermeidet
    Konflikt mit Page-Scroll der Einzelansicht-Liste.
    """
    home_xlim = [None]
    home_ylim = [None]

    def capture_home(_evt=None):
        home_xlim[0] = ax.get_xlim()
        home_ylim[0] = ax.get_ylim()

    # Initiale Range nach erstem Draw merken
    fig.canvas.mpl_connect('draw_event', lambda e: capture_home() if home_xlim[0] is None else None)

    def on_scroll(event):
        if event.inaxes is not ax:
            return
        if require_modifier:
            key = (event.key or '').lower()
            if 'control' not in key and 'ctrl' not in key and 'cmd' not in key:
                return
        factor = 0.82 if event.button == 'up' else 1.22
        if event.xdata is None or event.ydata is None:
            return
        x, y = event.xdata, event.ydata
        x0, x1 = ax.get_xlim()
        y0, y1 = ax.get_ylim()
        ax.set_xlim(x - (x - x0) * factor, x + (x1 - x) * factor)
        ax.set_ylim(y - (y - y0) * factor, y + (y1 - y) * factor)
        canvas.draw_idle()

    def on_double_click(event):
        if event.inaxes is not ax or not event.dblclick:
            return
        if home_xlim[0] is not None:
            ax.set_xlim(home_xlim[0])
            ax.set_ylim(home_ylim[0])
            canvas.draw_idle()

    fig.canvas.mpl_connect('scroll_event', on_scroll)
    fig.canvas.mpl_connect('button_press_event', on_double_click)


def install_legend_toggle(fig, legend, artist_groups):
    """Klick auf Legenden-Eintrag toggled Sichtbarkeit der zugehörigen Artists.

    artist_groups: Liste von Listen — pro Legenden-Handle eine Liste von
    Artists, die gemeinsam ein-/ausgeblendet werden (z.B. Line + Fill).
    """
    if legend is None:
        return
    handles = getattr(legend, 'legend_handles', None) or getattr(legend, 'legendHandles', [])
    texts = legend.get_texts()
    mapping = {}
    text_map = {}
    for h, artists, txt in zip(handles, artist_groups, texts):
        h.set_picker(True)
        if hasattr(h, 'set_pickradius'):
            h.set_pickradius(8)
        mapping[id(h)] = artists
        text_map[id(h)] = txt
        # Auch der Text klickbar
        txt.set_picker(True)
        mapping[id(txt)] = artists
        text_map[id(txt)] = txt

    handle_for_text = {}
    for h, txt in zip(handles, texts):
        handle_for_text[id(txt)] = h

    def on_pick(event):
        key = id(event.artist)
        if key not in mapping:
            return
        artists = mapping[key]
        if not artists:
            return
        cur_visible = artists[0].get_visible()
        new_visible = not cur_visible
        for a in artists:
            a.set_visible(new_visible)
        txt = text_map.get(key)
        if txt is not None:
            txt.set_alpha(1.0 if new_visible else 0.35)
        # Den Legend-Handle dimmen
        handle = event.artist if event.artist in handles else handle_for_text.get(id(event.artist))
        if handle is not None:
            handle.set_alpha(1.0 if new_visible else 0.35)
        fig.canvas.draw_idle()

    fig.canvas.mpl_connect('pick_event', on_pick)


def apply_modern_axes_style(fig, ax, theme):
    """Wendet ein modernes, minimalistisches Style auf Figure und Axes an."""
    fig.patch.set_facecolor(theme['bg'])
    ax.set_facecolor(theme['panel'])

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(theme['spine'])
    ax.spines['bottom'].set_color(theme['spine'])
    ax.spines['left'].set_linewidth(0.8)
    ax.spines['bottom'].set_linewidth(0.8)

    ax.grid(True, axis='y', color=theme['grid'], linestyle='-',
            linewidth=0.8, alpha=0.9, zorder=0)
    ax.grid(False, axis='x')
    ax.set_axisbelow(True)

    ax.tick_params(axis='x', colors=theme['muted'], labelsize=9,
                   length=0, pad=6)
    ax.tick_params(axis='y', colors=theme['muted'], labelsize=9,
                   length=0, pad=6)

    ax.title.set_color(theme['fg'])
    ax.xaxis.label.set_color(theme['muted'])
    ax.yaxis.label.set_color(theme['muted'])


class CustomNavigationToolbar(NavigationToolbar2Tk):
    def __init__(self, canvas, window, theme):
        super().__init__(canvas, window)
        self.theme = theme
        self.update_toolbar_colors()

    def update_toolbar_colors(self):
        colors = self.theme.get_colors()
        label_font = ("Helvetica", 10, "bold")
        for child in self.winfo_children():
            if isinstance(child, tk.Label):
                try:
                    child.config(font=label_font, foreground=colors['primary'])
                except:
                    pass

    def set_message(self, msg):
        if msg:
            super().set_message(msg)
            self.update_toolbar_colors()

class CheckboxList(ttk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.checkboxes = {}

        self.scrollable_frame.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def populate(self, items, colors):
        for i, item in enumerate(items):
            var = tk.BooleanVar()
            
            cb = ttk.Checkbutton(
                self.scrollable_frame, 
                text=item, 
                variable=var,
                bootstyle="round-toggle"
            )
            cb.pack(fill="x", expand=True, padx=5, pady=2)
            cb.bind("<MouseWheel>", self._on_mousewheel)
            self.checkboxes[item] = var

    def get_selected(self):
        return [item for item, var in self.checkboxes.items() if var.get()]

    def select_all(self):
        for var in self.checkboxes.values():
            var.set(True)

    def deselect_all(self):
        for var in self.checkboxes.values():
            var.set(False)

class Tooltip:
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

        style = ttk.Style()
        style.configure('tooltip.TLabel', background='#ffffe0', relief='solid', borderwidth=1)
        label = ttk.Label(self.tooltip_window, text=self.text, style='tooltip.TLabel', justify='left')
        label.pack(ipadx=1)

    def hide_tooltip(self, event):
        if self.tooltip_window:
            self.tooltip_window.destroy()
        self.tooltip_window = None

class EntityAnalyzerApp:
    COL_ENTITY_ID = 'entity id'
    COL_AREA = 'area'
    COL_PLATFORM = 'platform'
    COL_MANUFACTURER = 'manufacturer'
    
    VERSION = "v_1.4 by jayjojayson"
    SETTINGS_FILE = "ha_analyzer_settings.json"
     
    def __init__(self, root):
        self.root = root
        self.root.title("Home Assistant Entity Analyzer")
        self.root.geometry("1200x700")
        self.root.minsize(900, 600)
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self._set_icon(self.root)
  
        self.df_data = None
        self.df_original = None
        self.current_csv_type = None
        self.chart_type = 'line'
        self.search_job = None
        
        self.current_language = 'de'
        self.current_theme = "cosmo"
        self.settings = self.load_settings()
        
        if "language" in self.settings:
            self.current_language = self.settings["language"]
        if "theme" in self.settings:
            self.current_theme = self.settings["theme"]
        
        try:
            self.style = ttkb.Style(themename=self.current_theme)
        except TypeError:
            self.style = ttkb.Style()
            self.style.theme_use(self.current_theme)
         
        self._create_menu()
        self._create_widgets()
        
        self.apply_theme()

    def _set_icon(self, window):
        """Setzt das App-Icon plattformunabhängig (Windows: .ico, Linux: .png)."""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        try:
            if sys.platform == 'win32':
                ico_path = os.path.join(script_dir, 'E_A_T-logo.ico')
                if os.path.exists(ico_path):
                    window.iconbitmap(ico_path)
            else:
                png_path = os.path.join(script_dir, 'E_A_T-logo.png')
                if os.path.exists(png_path):
                    icon_image = tk.PhotoImage(file=png_path)
                    window.iconphoto(True, icon_image)
                    if window == self.root:
                        self._icon_image = icon_image
        except Exception:
            pass

    def _load_title_logo(self, size=28):
        """Lädt das Logo als skaliertes Bild für den Titel."""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        png_path = os.path.join(script_dir, 'E_A_T-logo.png')
        try:
            if os.path.exists(png_path):
                img = Image.open(png_path)
                img = img.resize((size, size), Image.LANCZOS)
                self._title_logo = ImageTk.PhotoImage(img)
                return self._title_logo
        except Exception:
            pass
        return None

    def tr(self, key):
        """Gibt den übersetzten Text für den aktuellen Sprachschlüssel zurück."""
        return TRANSLATIONS.get(self.current_language, TRANSLATIONS['de']).get(key, key)

    def toggle_language(self):
        """Wechselt die Sprache zwischen Deutsch und Englisch."""
        self.current_language = 'en' if self.current_language == 'de' else 'de'
        self.save_settings()
        self._rebuild_ui()

    def _rebuild_ui(self):
        """Baut Menü und Widgets mit der neuen Sprache neu auf."""
        had_entity_data = self.df_data is not None and self.current_csv_type == 'entity'
        self.root.config(menu='')
        self._create_menu()
        self.main_frame.destroy()
        self._create_widgets()
        self.apply_theme()
        if had_entity_data:
            self.setup_treeview(self.df_data)
            self.status_label.config(
                text=self.tr('status_entity_loaded').format(
                    filename='', count=len(self.df_data))
            )

    def _create_menu(self):
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)
  
        self.datei_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label=self.tr('menu_file'), menu=self.datei_menu)
        self.datei_menu.add_command(label=self.tr('menu_import_csv'), command=self.load_csv_data, accelerator="Ctrl+O")
        self.datei_menu.add_command(label=self.tr('menu_export_csv'), command=self.export_current_view_to_csv, accelerator="Ctrl+S")
        self.datei_menu.add_separator()
        self.datei_menu.add_command(label=self.tr('menu_exit'), command=self.on_closing)
  
        self.filter_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label=self.tr('menu_filter'), menu=self.filter_menu)
        self.filter_menu.add_command(label=self.tr('menu_filter_area'), command=lambda: self.filter_data('area'))
        self.filter_menu.add_command(label=self.tr('menu_filter_platform'), command=lambda: self.filter_data('platform'))
        self.filter_menu.add_command(label=self.tr('menu_filter_manufacturer'), command=lambda: self.filter_data('manufacturer'))
        self.filter_menu.add_separator()
        self.filter_menu.add_command(label=self.tr('menu_show_stats'), command=self.show_domain_stats_gui)
        self.filter_menu.add_separator()
        self.filter_menu.add_command(label=self.tr('menu_reset_filter'), command=self.reset_filter)
  
        self.optionen_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label=self.tr('menu_view'), menu=self.optionen_menu)
        self.optionen_menu.add_command(label=self.tr('menu_dark_mode'), command=self.toggle_theme)
        self.optionen_menu.add_separator()
        self.optionen_menu.add_command(label=self.tr('menu_language'), command=self.toggle_language)
        self.optionen_menu.add_separator()
        self.optionen_menu.add_command(label=self.tr('menu_always_on_top'), command=self.toggle_always_on_top)
        self.optionen_menu.add_separator()
        self.optionen_menu.add_command(label=self.tr('menu_about'), command=self.show_about_window)

        self.root.bind('<Control-o>', lambda e: self.load_csv_data())
        self.root.bind('<Control-s>', lambda e: self.export_current_view_to_csv())

    def _create_widgets(self):
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        top_frame = ttk.Frame(self.main_frame, padding=(15, 10))
        top_frame.pack(fill=tk.X)

        title_logo = self._load_title_logo(size=32)
        title_label = ttk.Label(
            top_frame, 
            text=self.tr('app_title'), 
            font=("Helvetica", 18, "bold"),
            bootstyle="primary",
            image=title_logo if title_logo else '',
            compound=tk.LEFT
        )
        title_label.pack(side=tk.LEFT)

        self.theme_button = ttk.Button(
            top_frame, 
            text=self.tr('menu_dark_mode'), 
            command=self.toggle_theme,
            bootstyle="outline"
        )
        self.theme_button.pack(side=tk.RIGHT, padx=5)

        control_frame = ttk.Frame(self.main_frame, padding=(15, 10))
        control_frame.pack(fill=tk.X)

        search_label = ttk.Label(control_frame, text=self.tr('search_label'), font=("Helvetica", 11))
        search_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.search_entry = ttk.Entry(control_frame, width=35, font=("Helvetica", 10))
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind('<KeyRelease>', self.apply_filter_search)
        Tooltip(self.search_entry, self.tr('search_tooltip'))

        button_frame = ttk.Frame(control_frame)
        button_frame.pack(side=tk.RIGHT)

        reset_button = ttk.Button(
            button_frame, 
            text=self.tr('btn_reset'), 
            command=self.reset_filter,
            bootstyle="secondary"
        )
        reset_button.pack(side=tk.LEFT, padx=5)
        Tooltip(reset_button, self.tr('btn_reset_tooltip'))

        self.import_button = ttk.Button(
            button_frame, 
            text=self.tr('btn_import'), 
            command=self.load_csv_data,
            bootstyle="success"
        )
        self.import_button.pack(side=tk.LEFT, padx=5)

        self.export_button = ttk.Button(
            button_frame, 
            text=self.tr('btn_export'), 
            command=self.export_current_view_to_csv,
            bootstyle="info"
        )
        self.export_button.pack(side=tk.LEFT, padx=5)

        table_frame = ttk.Frame(self.main_frame, padding=(15, 0))
        table_frame.pack(fill=tk.BOTH, expand=True)

        self.vsb = ttk.Scrollbar(table_frame, orient="vertical")
        self.hsb = ttk.Scrollbar(table_frame, orient="horizontal")

        self.tree = ttk.Treeview(
            table_frame, 
            columns=[], 
            show='headings',
            yscrollcommand=self.vsb.set, 
            xscrollcommand=self.hsb.set,
            style="custom.Treeview"
        )
        self.tree.bind('<Double-1>', self.show_entity_details)
        self.vsb.config(command=self.tree.yview)
        self.hsb.config(command=self.tree.xview)

        self.vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(fill=tk.BOTH, expand=True)

        footer_frame = ttk.Frame(self.main_frame, padding=(15, 8))
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.status_label = ttk.Label(
            footer_frame, 
            text=self.tr('status_ready'), 
            anchor=tk.W,
            font=("Helvetica", 9)
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.progress_bar = ttk.Progressbar(
            footer_frame, 
            orient='horizontal', 
            mode='determinate', 
            length=150,
            bootstyle="striped"
        )
        self.progress_bar.pack(side=tk.LEFT, padx=10)
        self.progress_bar.pack_forget()

        self.version_label = ttk.Label(
            footer_frame, 
            text=self.VERSION, 
            anchor=E,
            font=("Helvetica", 8),
            bootstyle="secondary"
        )
        self.version_label.pack(side=tk.RIGHT)

    def apply_theme(self):
        is_dark = self.current_theme in ["darkly", "cyborg", "vapor"]
        
        try:
            self.style.theme_use(self.current_theme)
        except:
            self.style.theme_use("cosmo")
        
        self.root.update()
        self.root.configure(bg=self.style.lookup('TFrame', 'background'))

        self.style.configure(
            "custom.Treeview",
            rowheight=28,
            font=("Helvetica", 10)
        )
        self.style.configure(
            "custom.Treeview.Heading",
            font=("Helvetica", 10, "bold")
        )

        if hasattr(self, 'tree'):
            self.update_tree_colors(is_dark)

    def update_tree_colors(self, is_dark):
        if is_dark:
            self.style.configure(
                "custom.Treeview",
                background="#2b2b2b",
                foreground="white",
                fieldbackground="#2b2b2b"
            )
            self.style.map(
                "custom.Treeview",
                background=[('selected', '#0078d7')],
                foreground=[('selected', 'white')]
            )
        else:
            self.style.configure(
                "custom.Treeview",
                background="white",
                foreground="black",
                fieldbackground="white"
            )
            self.style.map(
                "custom.Treeview",
                background=[('selected', '#0078d7')],
                foreground=[('selected', 'white')]
            )

    def toggle_theme(self):
        themes = {
            "cosmo": "darkly",
            "darkly": "cyborg", 
            "cyborg": "vapor",
            "vapor": "litera",
            "litera": "minty",
            "minty": "cosmo"
        }
        
        self.current_theme = themes.get(self.current_theme, "cosmo")
        
        self.save_settings()
        
        theme_names = {
            "cosmo": self.tr('theme_light'),
            "darkly": self.tr('theme_darkly'),
            "cyborg": self.tr('theme_cyborg'),
            "vapor": self.tr('theme_vapor'),
            "litera": self.tr('theme_litera'),
            "minty": self.tr('theme_minty')
        }
        
        self.apply_theme()
        
        theme_display = theme_names.get(self.current_theme, self.current_theme)
        is_dark = self.current_theme in ["darkly", "cyborg", "vapor"]
        moon_icon = "☀️" if is_dark else "🌙"
        
        self.theme_button.config(text=f"{moon_icon} {theme_display} Mode")
        
        self.optionen_menu.entryconfig(0, label=f"{moon_icon} Theme: {theme_display}")

    def load_settings(self):
        try:
            if os.path.exists(self.SETTINGS_FILE):
                with open(self.SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Fehler beim Laden der Einstellungen: {e}")
        return {}

    def save_settings(self):
        try:
            self.settings["theme"] = self.current_theme
            self.settings["language"] = self.current_language
            with open(self.SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Fehler beim Speichern der Einstellungen: {e}")

    def on_closing(self):
        self.save_settings()
        self.root.destroy()

    def show_entity_details(self, event):
        selected_item = self.tree.focus()
        if not selected_item: return

        item_values = self.tree.item(selected_item, 'values')
        column_names = self.tree['columns']

        details_window = tk.Toplevel(self.root)
        details_window.title(self.tr('details_title'))
        details_window.geometry("500x400")
        self._set_icon(details_window)

        main_frame = ttk.Frame(details_window, padding=20)
        main_frame.pack(expand=True, fill="both")

        header = ttk.Label(
            main_frame, 
            text=self.tr('details_header'), 
            font=("Helvetica", 14, "bold"),
            bootstyle="primary"
        )
        header.pack(pady=(0, 15), anchor=tk.W)

        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)

        for i, col_name in enumerate(column_names):
            row_frame = ttk.Frame(content_frame)
            row_frame.pack(fill=tk.X, pady=3)
            
            ttk.Label(
                row_frame, 
                text=f"{col_name.title()}:", 
                font=("Helvetica", 10, "bold"),
                width=15,
                anchor=tk.W
            ).pack(side=tk.LEFT)
            
            value = item_values[i] if i < len(item_values) else "-"
            ttk.Label(
                row_frame, 
                text=value, 
                font=("Helvetica", 10),
                wraplength=350,
                anchor=tk.W
            ).pack(side=tk.LEFT, fill=tk.X, expand=True)

        close_button = ttk.Button(
            main_frame, 
            text=self.tr('btn_close'), 
            command=details_window.destroy,
            bootstyle="primary"
        )
        close_button.pack(pady=(15, 0))

    def show_about_window(self):
        about_window = tk.Toplevel(self.root)
        about_window.title(self.tr('about_title'))
        self._set_icon(about_window)
        
        about_window.geometry("400x300")
        about_window.resizable(False, False)

        main_frame = ttk.Frame(about_window, padding=30)
        main_frame.pack(expand=True, fill=tk.BOTH)

        title = ttk.Label(
            main_frame, 
            text="🏠 HA Entity Analyzer", 
            font=("Helvetica", 16, "bold"),
            bootstyle="primary"
        )
        title.pack(pady=(0, 10))

        version = ttk.Label(
            main_frame, 
            text=f"Version: {self.VERSION}", 
            font=("Helvetica", 11)
        )
        version.pack()

        description = ttk.Label(
            main_frame, 
            text=self.tr('about_description'), 
            font=("Helvetica", 10),
            justify=tk.CENTER
        )
        description.pack(pady=20)

        thanks = ttk.Label(
            main_frame, 
            text=self.tr('about_thanks'), 
            font=("Helvetica", 9),
            bootstyle="secondary"
        )
        thanks.pack(side=tk.BOTTOM, pady=10)

        ttk.Button(
            main_frame, 
            text=self.tr('btn_close'), 
            command=about_window.destroy,
            bootstyle="primary"
        ).pack(pady=10)

    def toggle_always_on_top(self):
        is_on_top = self.root.attributes('-topmost')
        self.root.attributes('-topmost', not is_on_top)
        status = self.tr('status_aot_off') if is_on_top else self.tr('status_aot_on')
        self.status_label.config(text=status)

    def detect_csv_type(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                header = f.readline().strip()
                if ',' in header and any(c.isdigit() for c in header):
                    if header.count(',') > header.count(';'):
                        return 'energy', ','
                return 'entity', ';'
        except Exception:
            return 'entity', ';'

    def load_csv_data(self):
        filepath = filedialog.askopenfilename(
            defaultextension=".csv", 
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
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
                self.status_label.config(text=self.tr('status_energy_loaded').format(filename=filename))
                self.show_energy_chart_view()
            else:
                self.status_label.config(
                    text=self.tr('status_entity_loaded').format(filename=filename, count=len(self.df_data))
                )
                self.setup_treeview(self.df_data)

        except Exception as e:
            self.status_label.config(text=self.tr('status_error').format(error=e))
            messagebox.showerror(self.tr('dlg_load_error'), self.tr('dlg_load_error_msg').format(error=e))

    def export_current_view_to_csv(self):
        if self.df_data is None or self.df_data.empty:
            self.status_label.config(text=self.tr('status_no_export_data'))
            messagebox.showwarning(self.tr('dlg_no_data'), self.tr('dlg_load_csv_first'))
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not filepath: return

        try:
            sep = ',' if self.current_csv_type == 'energy' else ';'
            self.df_data.to_csv(filepath, sep=sep, index=False, encoding='utf-8')
            filename = os.path.basename(filepath)
            self.status_label.config(text=self.tr('status_exported').format(filename=filename))
            messagebox.showinfo(self.tr('dlg_export_success'), self.tr('dlg_export_success_msg').format(filepath=filepath))
        except Exception as e:
            self.status_label.config(text=self.tr('status_export_error').format(error=e))
            messagebox.showerror(self.tr('dlg_export_error'), self.tr('dlg_export_error_msg').format(error=e))
  
    def setup_treeview(self, df_to_display):
        if not hasattr(self, 'tree'): return

        self.tree.delete(*self.tree.get_children())
        new_columns = df_to_display.columns.tolist()
        self.tree['columns'] = new_columns

        self.tree.heading("#0", text="", anchor=tk.W)
        self.tree.column("#0", width=0, stretch=tk.NO)

        for col in new_columns:
            max_len = df_to_display[col].astype(str).str.len().max() if not df_to_display.empty else 10
            width = max(100, min(350, int(max_len * 8)))
            self.tree.heading(
                col, 
                text=col.upper(), 
                command=lambda c=col: self.sort_column(c, False)
            )
            self.tree.column(col, width=width, anchor=tk.W)

        data_to_insert = df_to_display.values.tolist()
        is_dark = self.current_theme in ["darkly", "cyborg", "vapor"]
        
        for i, row in enumerate(data_to_insert):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.tree.insert('', tk.END, values=row, tags=(tag,))

        if is_dark:
            self.tree.tag_configure('oddrow', background='#2b2b2b', foreground='white')
            self.tree.tag_configure('evenrow', background='#333333', foreground='white')
        else:
            self.tree.tag_configure('oddrow', background='white', foreground='black')
            self.tree.tag_configure('evenrow', background='#f5f5f5', foreground='black')
  
    def sort_column(self, col, reverse):
        if self.df_data is None: return

        try:
            df_sorted = self.df_data.copy()
            df_sorted[col] = pd.to_numeric(df_sorted[col], errors='ignore')
            df_sorted.sort_values(
                by=col, 
                ascending=not reverse, 
                inplace=True, 
                key=lambda x: x.astype(str).str.lower() if pd.api.types.is_string_dtype(x) else x
            )
            self.df_data = df_sorted
            self.setup_treeview(self.df_data)
            self.tree.heading(col, command=lambda c=col: self.sort_column(c, not reverse))
            self.status_label.config(text=self.tr('status_sorted').format(col=col.upper()))
        except Exception as e:
            self.status_label.config(text=self.tr('status_sort_error').format(error=e))
  
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

        mask = self.df_original.apply(
            lambda row: row.astype(str).str.lower().str.contains(search_term).any(), 
            axis=1
        )
        self.df_data = self.df_original[mask]
        
        self.setup_treeview(self.df_data)
        self.status_label.config(text=self.tr('status_search_results').format(count=len(self.df_data), term=search_term))
  
    def reset_filter(self):
        if self.df_original is None: return
        self.df_data = self.df_original.copy()
        if hasattr(self, 'search_entry'):
            self.search_entry.delete(0, tk.END)
        self.setup_treeview(self.df_data)
        self.status_label.config(text=self.tr('status_filter_reset'))

    def filter_data(self, column_key):
        if self.df_original is None:
            messagebox.showwarning(self.tr('dlg_no_data'), self.tr('dlg_load_csv'))
            return
        if self.current_csv_type != 'entity':
             messagebox.showinfo(self.tr('dlg_info'), self.tr('dlg_filter_entity_only'))
             return

        col_map = {'area': self.COL_AREA, 'platform': self.COL_PLATFORM, 'manufacturer': self.COL_MANUFACTURER}
        filter_col = col_map.get(column_key)

        if filter_col not in self.df_original.columns:
            messagebox.showerror(self.tr('dlg_error'), self.tr('dlg_column_not_found').format(col=filter_col))
            return
        FilterUtility.show_filter_window(self, filter_col)

    def show_domain_stats_gui(self):
        if self.df_original is None:
            messagebox.showwarning(self.tr('dlg_no_data'), self.tr('dlg_load_csv'))
            return
        if self.current_csv_type != 'entity':
             messagebox.showinfo(self.tr('dlg_info'), self.tr('dlg_stats_entity_only'))
             return
              
        if self.COL_ENTITY_ID not in self.df_original.columns:
            messagebox.showerror(self.tr('dlg_error'), self.tr('dlg_column_missing').format(col=self.COL_ENTITY_ID))
            return
        FilterUtility.show_stats_window(self)

    def show_energy_chart_view(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        self.show_sensor_selection()

    def show_sensor_selection(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        selection_frame = ttk.Frame(self.main_frame, padding=15)
        selection_frame.pack(fill=tk.BOTH, expand=True)

        top_bar = ttk.Frame(selection_frame)
        top_bar.pack(fill=tk.X, pady=(0, 15))
        
        title = ttk.Label(
            top_bar, 
            text=self.tr('sensor_select_title'), 
            font=("Helvetica", 14, "bold"),
            bootstyle="primary"
        )
        title.pack(side=tk.LEFT)
        
        self.select_all_var = tk.BooleanVar()
        select_all_button = ttk.Checkbutton(
            top_bar, 
            text=self.tr('select_all'), 
            variable=self.select_all_var, 
            command=self.toggle_select_all_sensors,
            bootstyle="round-toggle"
        )
        select_all_button.pack(side=tk.RIGHT)

        self.sensor_checklist = CheckboxList(selection_frame)
        self.sensor_checklist.pack(fill="both", expand=True, pady=10)
        
        sensors = self.df_data['entity_id'].unique()
        self.sensor_name_mapping = {s.replace('sensor.', ''): s for s in sensors}
        display_sensors = sorted(list(self.sensor_name_mapping.keys()))
        
        is_dark = self.current_theme in ["darkly", "cyborg", "vapor"]
        colors = {'bg': '#2b2b2b' if is_dark else 'white', 'fg': 'white' if is_dark else 'black'}
        self.sensor_checklist.populate(display_sensors, colors)

        button_frame = ttk.Frame(selection_frame)
        button_frame.pack(pady=15)

        ttk.Button(
            button_frame, 
            text=self.tr('btn_individual'), 
            command=self.plot_selected_individual,
            bootstyle="primary"
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame, 
            text=self.tr('btn_compare'), 
            command=self.plot_selected_combined,
            bootstyle="success"
        ).pack(side=tk.LEFT, padx=5)

    def toggle_select_all_sensors(self):
        if self.select_all_var.get():
            self.sensor_checklist.select_all()
        else:
            self.sensor_checklist.deselect_all()

    def _perform_melt_on_selection(self, selected_sensors):
        df_filtered = self.df_data[self.df_data['entity_id'].isin(selected_sensors)]

        id_cols = [c for c in ['entity_id', 'type', 'unit'] if c in df_filtered.columns]
        candidate_cols = [c for c in df_filtered.columns if c not in id_cols]
        parsed_headers = pd.to_datetime(pd.Series(candidate_cols), errors='coerce')
        value_cols = [c for c, ts in zip(candidate_cols, parsed_headers) if pd.notna(ts)]

        df_melted = df_filtered.melt(
            id_vars=id_cols,
            value_vars=value_cols,
            var_name='timestamp',
            value_name='value',
        )
        df_melted['timestamp'] = pd.to_datetime(df_melted['timestamp'], errors='coerce')
        df_melted.dropna(subset=['timestamp'], inplace=True)
        df_melted['value'] = pd.to_numeric(df_melted['value'], errors='coerce').fillna(0)

        df_melted.sort_values(['entity_id', 'timestamp'], inplace=True)
        df_melted.reset_index(drop=True, inplace=True)

        return df_melted

    def plot_selected_individual(self):
        selected_short_names = self.sensor_checklist.get_selected()
        if not selected_short_names:
            messagebox.showwarning(self.tr('dlg_selection_missing'), self.tr('dlg_select_sensor'))
            return
        
        selected_sensors = [self.sensor_name_mapping[s] for s in selected_short_names]
        self.selected_df = self._perform_melt_on_selection(selected_sensors)
        self.show_chart_plots()

    def plot_selected_combined(self):
        selected_short_names = self.sensor_checklist.get_selected()
        if not selected_short_names:
            messagebox.showwarning(self.tr('dlg_selection_missing'), self.tr('dlg_select_sensor'))
            return

        selected_sensors = [self.sensor_name_mapping[s] for s in selected_short_names]
        df_plot = self._perform_melt_on_selection(selected_sensors)
        
        self.show_combined_chart_view(df_plot)

    def show_chart_plots(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        chart_container = ttk.Frame(self.main_frame)
        chart_container.pack(fill=tk.BOTH, expand=True)

        top_bar = ttk.Frame(chart_container, padding=10)
        top_bar.pack(fill=tk.X)

        aggregation_frame = ttk.Frame(top_bar)
        aggregation_frame.pack(side=tk.LEFT)
        
        buttons = {self.tr('period_original'): "original", self.tr('period_day'): "D", self.tr('period_week'): "W", self.tr('period_month'): "M", self.tr('period_year'): "Y"}
        for text, period in buttons.items():
            btn = ttk.Button(
                aggregation_frame, 
                text=text, 
                command=lambda p=period: self.redraw_charts(p),
                bootstyle="outline-secondary"
            )
            btn.pack(side=tk.LEFT, padx=2)

        self.chart_type_button = ttk.Button(
            top_bar, 
            text=self.tr('btn_bar_chart'), 
            command=self.toggle_chart_type,
            bootstyle="outline"
        )
        self.chart_type_button.pack(side=tk.RIGHT, padx=5)

        ttk.Button(
            top_bar, 
            text=self.tr('btn_back'), 
            command=self.show_sensor_selection,
            bootstyle="secondary"
        ).pack(side=tk.RIGHT, padx=5)

        self.chart_canvas = tk.Canvas(chart_container, borderwidth=0, highlightthickness=0)
        self.chart_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        is_dark = self.current_theme in ["darkly", "cyborg", "vapor"]
        bg_color = '#2b2b2b' if is_dark else 'white'
        self.chart_canvas.config(bg=bg_color)

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
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        self.combined_df = df_plot

        chart_container = ttk.Frame(self.main_frame)
        chart_container.pack(fill=tk.BOTH, expand=True)

        top_bar = ttk.Frame(chart_container, padding=10)
        top_bar.pack(fill=tk.X)
        
        aggregation_frame = ttk.Frame(top_bar)
        aggregation_frame.pack(side=tk.LEFT)
        
        buttons = {self.tr('period_original'): "original", self.tr('period_day'): "D", self.tr('period_week'): "W", self.tr('period_month'): "M", self.tr('period_year'): "Y"}
        for text, period in buttons.items():
            btn = ttk.Button(
                aggregation_frame, 
                text=text, 
                command=lambda p=period: self.redraw_combined_chart(p),
                bootstyle="outline-secondary"
            )
            btn.pack(side=tk.LEFT, padx=2)

        self.chart_type_button_combined = ttk.Button(
            top_bar, 
            text=self.tr('btn_bar_chart'), 
            command=self.toggle_combined_chart_type,
            bootstyle="outline"
        )
        self.chart_type_button_combined.pack(side=tk.RIGHT, padx=5)

        ttk.Button(
            top_bar, 
            text=self.tr('btn_back'), 
            command=self.show_sensor_selection,
            bootstyle="secondary"
        ).pack(side=tk.RIGHT, padx=5)

        self.combined_chart_frame = ttk.Frame(chart_container)
        self.combined_chart_frame.pack(fill=tk.BOTH, expand=True)

        self.redraw_combined_chart()

    def get_chart_colors(self):
        """Liefert das aktive moderne Chart-Theme (Light/Dark)."""
        is_dark = self.current_theme in ["darkly", "cyborg", "vapor"]
        return MODERN_THEME['dark'] if is_dark else MODERN_THEME['light']

    def _format_date_axis(self, ax, timestamps):
        """Setzt einen passenden Datumsformatter abhängig vom Zeitraum."""
        if len(timestamps) == 0:
            return
        try:
            span = (pd.Timestamp(timestamps.max()) - pd.Timestamp(timestamps.min())).days
        except Exception:
            span = 0

        locator = mdates.AutoDateLocator(minticks=4, maxticks=8)
        if span <= 2:
            fmt = mdates.DateFormatter('%H:%M')
        elif span <= 60:
            fmt = mdates.DateFormatter('%d. %b')
        elif span <= 365 * 2:
            fmt = mdates.DateFormatter('%b %Y')
        else:
            fmt = mdates.DateFormatter('%Y')
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(fmt)

    def redraw_combined_chart(self, period='original'):
        for widget in self.combined_chart_frame.winfo_children():
            widget.destroy()

        self.current_period_combined = period
        df_to_plot = self.combined_df.copy()
        df_to_plot.sort_values(['entity_id', 'timestamp'], inplace=True)

        total_sum = df_to_plot['value'].sum()
        unit = df_to_plot['unit'].iloc[0] if 'unit' in df_to_plot.columns and not df_to_plot.empty else ''

        df_pivot = df_to_plot.pivot_table(
            index='timestamp', columns='entity_id', values='value',
            aggfunc='sum'
        ).fillna(0).sort_index()

        if period != 'original':
            df_pivot = df_pivot.resample(period).sum()

        if len(df_pivot) > 60:
            self.chart_type_button_combined.config(state=tk.DISABLED)
            if self.chart_type == 'bar':
                self.chart_type = 'line'
        else:
            self.chart_type_button_combined.config(state=tk.NORMAL)

        fig, ax = plt.subplots(figsize=(12, 5.6), dpi=110)
        theme = self.get_chart_colors()
        palette = theme['palette']

        entities = df_pivot.columns.tolist()
        timestamps = df_pivot.index

        # Artists für späteren Legend-Toggle sammeln (in Legenden-Reihenfolge)
        toggle_artist_groups = []

        if self.chart_type == 'bar' and len(timestamps) > 0:
            ts_numeric = mdates.date2num(timestamps)
            n_entities = max(len(entities), 1)
            if len(ts_numeric) > 1:
                gaps = np.diff(ts_numeric)
                gaps = gaps[gaps > 0]
                min_gap = float(gaps.min()) if len(gaps) else 1.0
                total_bar_width = min_gap * 0.78
            else:
                total_bar_width = 0.78
            single_bar_width = total_bar_width / n_entities

            bar_groups = []
            for j, entity in enumerate(entities):
                offset = (j - n_entities / 2 + 0.5) * single_bar_width
                color = palette[j % len(palette)]
                values = df_pivot[entity].values
                bars = ax.bar(ts_numeric + offset, values,
                              width=single_bar_width, color=color,
                              edgecolor='none', alpha=0.95,
                              label=entity.replace('sensor.', ''), zorder=3)
                bar_groups.append((bars, entity, color, values))
                toggle_artist_groups.append(list(bars))

            install_bar_hover(fig, ax, bar_groups, theme, unit=unit)
        else:
            n = max(len(entities), 1)
            fill_scale = 1.0 if n == 1 else max(0.35, 1.0 / n)
            for j, entity in enumerate(entities):
                series = df_pivot[entity]
                sensor_sum = series.sum()
                color = palette[j % len(palette)]
                label = f"{entity.replace('sensor.', '')}  ·  {sensor_sum:.2f} {unit}"
                line_artists = ax.plot(timestamps, series.values, color=color,
                                       linewidth=2.2, solid_capstyle='round',
                                       solid_joinstyle='round',
                                       label=label, zorder=3)
                fill_artist = ax.fill_between(
                    timestamps, series.values, color=color,
                    alpha=theme['fill_alpha'] * fill_scale,
                    zorder=2, linewidth=0,
                )
                toggle_artist_groups.append(line_artists + [fill_artist])

        apply_modern_axes_style(fig, ax, theme)
        if len(timestamps) > 0:
            self._format_date_axis(ax, timestamps)

        ax.set_title(self.tr('chart_comparison'),
                     loc='left', fontsize=13, fontweight='bold',
                     color=theme['fg'], pad=18)
        subtitle = self.tr('chart_total').format(total=total_sum, unit=unit)
        ax.text(0.0, 1.02, subtitle, transform=ax.transAxes,
                color=theme['muted'], fontsize=10, ha='left', va='bottom')

        ax.set_ylabel(unit, fontsize=9)
        ax.set_xlabel('')
        ax.margins(x=0.02)

        # Legende: ncol abhängig vom längsten Label, damit lange Sensor-
        # Namen nicht über den Figur-Rand hinausragen und beschnitten werden.
        max_label_chars = max(
            (len(e.replace('sensor.', '')) + 14 for e in entities),
            default=12,
        )
        if max_label_chars >= 40:
            ncol = 1
        elif max_label_chars >= 28:
            ncol = 2
        elif max_label_chars >= 18:
            ncol = min(3, len(entities))
        else:
            ncol = min(4, len(entities))
        legend = ax.legend(
            loc='upper center', bbox_to_anchor=(0.5, -0.14),
            ncol=max(1, ncol),
            frameon=False, fontsize=9,
            labelcolor=theme['fg'], handlelength=1.4, handletextpad=0.6,
            columnspacing=1.6,
        )
        if legend:
            for text in legend.get_texts():
                text.set_color(theme['fg'])

        fig.tight_layout(rect=(0, 0.04, 1, 0.96))

        canvas = FigureCanvasTkAgg(fig, master=self.combined_chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        toolbar = CustomNavigationToolbar(canvas, self.combined_chart_frame, self)
        toolbar.update()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Initial-Größe einmalig auf echte Widget-Maße anpassen
        # (verhindert weißen Rand bzw. abgeschnittene Legende beim ersten Render).
        fit_figure_to_widget(fig, canvas, self.root,
                             tight_rect=(0, 0.04, 1, 0.96),
                             min_w_in=6.0, min_h_in=4.0)

        # Interaktivität: klickbare Legende, Mausrad-Zoom, responsive Größe
        if legend is not None and len(toggle_artist_groups) == len(entities):
            install_legend_toggle(fig, legend, toggle_artist_groups)
        install_mouse_zoom(fig, ax, canvas, require_modifier=False)
        bind_responsive_figure(fig, canvas, min_height_in=4.0,
                               tight_rect=(0, 0.04, 1, 0.96))

    def toggle_combined_chart_type(self):
        if self.chart_type == 'line':
            self.chart_type = 'bar'
            self.chart_type_button_combined.config(text=self.tr('btn_line_chart'))
        else:
            self.chart_type = 'line'
            self.chart_type_button_combined.config(text=self.tr('btn_bar_chart'))
        self.redraw_combined_chart(getattr(self, 'current_period_combined', 'original'))
        
    def toggle_chart_type(self):
        if str(self.chart_type_button.cget('state')) == str(tk.DISABLED):
            return

        if self.chart_type == 'line':
            self.chart_type = 'bar'
            self.chart_type_button.config(text=self.tr('btn_line_chart'))
        else:
            self.chart_type = 'line'
            self.chart_type_button.config(text=self.tr('btn_bar_chart'))
        
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
        if not hasattr(self, 'scrollable_frame') or not hasattr(self, 'selected_df'):
            return
        
        self.current_period = period

        if period != 'original':
            first_entity_data = self.selected_df.groupby('entity_id').get_group(list(self.selected_df['entity_id'].unique())[0])
            resampled_data = first_entity_data.set_index('timestamp')['value'].resample(period).sum()
            if len(resampled_data) > 100:
                self.chart_type_button.config(state=tk.DISABLED)
                if self.chart_type == 'bar': self.chart_type = 'line'
            else:
                self.chart_type_button.config(state=tk.NORMAL)
        else:
            self.chart_type_button.config(state=tk.NORMAL)
        
        if self.chart_type == 'line':
            self.chart_type_button.config(text=self.tr('btn_bar_chart'))
        else:
            self.chart_type_button.config(text=self.tr('btn_line_chart'))

        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Synchroner Loop. Das frühere Generator-/after()-Pattern hat auf macOS
        # nach dem ersten Chart abgebrochen (vermutlich verschluckte Exception
        # im after-Callback). update_idletasks() hält die UI responsiv.
        groups = list(self.selected_df.groupby('entity_id'))
        for entity, group in groups:
            df_plot = group.set_index('timestamp')
            if period != 'original':
                df_plot = df_plot['value'].resample(period).sum().reset_index()
                df_plot['unit'] = group['unit'].iloc[0] if not group.empty else ''
            else:
                df_plot = df_plot.reset_index()
            try:
                self.create_chart_for_entity(entity, df_plot)
            except Exception as e:
                err_frame = ttk.Frame(self.scrollable_frame, padding=10)
                err_frame.pack(fill=tk.X, expand=True, pady=10)
                ttk.Label(err_frame,
                          text=f"{entity}: {e}",
                          bootstyle="danger").pack(anchor='w')
            self.root.update_idletasks()

    def create_chart_for_entity(self, entity_id, df_group):
        fig_frame = ttk.Frame(self.scrollable_frame, padding=10)
        fig_frame.pack(fill=tk.X, expand=True, pady=10)

        df_plot = df_group.copy()
        df_plot['timestamp'] = pd.to_datetime(df_plot['timestamp'])
        df_plot.set_index('timestamp', inplace=True)
        df_plot.sort_index(inplace=True)

        if df_plot.empty or df_plot['value'].isnull().all():
            ttk.Label(fig_frame, text=self.tr('chart_no_data').format(entity=entity_id)).pack()
            return

        total_sum = df_plot['value'].sum()
        unit = df_plot['unit'].iloc[0] if 'unit' in df_plot.columns and not df_plot.empty else ''

        fig, ax = plt.subplots(figsize=(10, 4.2), dpi=110)
        theme = self.get_chart_colors()
        palette = theme['palette']
        # Stabile, vom Entity-Namen abgeleitete Farbe (kein random)
        series_color = palette[hash(entity_id) % len(palette)]

        values = df_plot['value'].values
        timestamps = df_plot.index

        if self.chart_type == 'line':
            ax.plot(timestamps, values, color=series_color, linewidth=2.2,
                    solid_capstyle='round', solid_joinstyle='round', zorder=3)
            ax.fill_between(timestamps, values, color=series_color,
                            alpha=theme['fill_alpha'], zorder=2)
            if len(df_plot) < 40:
                ax.scatter(timestamps, values, color=series_color, s=22,
                           zorder=4, edgecolors=theme['bg'], linewidths=1.5)
                for ts, value in zip(timestamps, values):
                    ax.annotate(f'{value:.2f}', xy=(ts, value),
                                xytext=(0, 8), textcoords='offset points',
                                color=theme['fg'], fontsize=8, ha='center')
        else:
            ts_numeric = mdates.date2num(timestamps)
            if len(ts_numeric) > 1:
                gaps = np.diff(ts_numeric)
                gaps = gaps[gaps > 0]
                min_gap = float(gaps.min()) if len(gaps) else 1.0
                bar_width = min_gap * 0.75
            else:
                bar_width = 0.6
            bars = ax.bar(ts_numeric, values, width=bar_width,
                          color=series_color, edgecolor='none',
                          alpha=0.95, zorder=3)
            install_bar_hover(fig, ax,
                              [(bars, entity_id, series_color, values)],
                              theme, unit=unit)

        apply_modern_axes_style(fig, ax, theme)
        self._format_date_axis(ax, timestamps)

        ax.set_title(f"{entity_id}",
                     loc='left', fontsize=12, fontweight='bold',
                     color=theme['fg'], pad=14)
        subtitle = self.tr('chart_total').format(total=total_sum, unit=unit)
        ax.text(0.0, 1.02, subtitle, transform=ax.transAxes,
                color=theme['muted'], fontsize=9, ha='left', va='bottom')

        ax.set_ylabel(unit, fontsize=9)
        ax.set_xlabel('')
        ax.margins(x=0.02)
        fig.tight_layout(rect=(0, 0, 1, 0.97))

        canvas = FigureCanvasTkAgg(fig, master=fig_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        toolbar = CustomNavigationToolbar(canvas, fig_frame, self)
        toolbar.update()
        canvas.get_tk_widget().pack(fill=tk.X)

        fit_figure_to_widget(fig, canvas, self.root,
                             tight_rect=(0, 0, 1, 0.97),
                             min_w_in=6.0, min_h_in=3.6)
        bind_responsive_figure(fig, canvas, min_height_in=3.6,
                               tight_rect=(0, 0, 1, 0.97))
        install_mouse_zoom(fig, ax, canvas, require_modifier=True)

        # Keine plt.close(fig) hier: hat zur Folge dass spätere Events
        # (Hover, Zoom, Resize) den Figure-State noch brauchen.


class FilterUtility:
    @staticmethod
    def show_filter_window(app, filter_col):
        unique_values = sorted(app.df_original[filter_col].unique().tolist(), key=str.lower)
        filter_window = tk.Toplevel(app.root)
        filter_window.title(app.tr('filter_title').format(col=filter_col.replace('_', ' ').title()))
        app._set_icon(filter_window)
        
        filter_window.geometry("400x500")

        main_frame = ttk.Frame(filter_window, padding=15)
        main_frame.pack(expand=True, fill=tk.BOTH)

        title = ttk.Label(
            main_frame, 
            text=f"📍 {filter_col.replace('_', ' ').title()}", 
            font=("Helvetica", 12, "bold"),
            bootstyle="primary"
        )
        title.pack(pady=(0, 10))

        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        vsb = ttk.Scrollbar(list_frame, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        is_dark = app.current_theme in ["darkly", "cyborg", "vapor"]
        bg_color = '#2b2b2b' if is_dark else 'white'
        fg_color = 'white' if is_dark else 'black'
        
        listbox = tk.Listbox(
            list_frame, 
            selectmode=tk.SINGLE, 
            width=45, 
            bg=bg_color, 
            fg=fg_color,
            font=("Helvetica", 10),
            selectbackground='#0078d7',
            selectforeground='white'
        )
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        listbox.config(yscrollcommand=vsb.set)
        vsb.config(command=listbox.yview)

        if '' in app.df_original[filter_col].unique():
            listbox.insert(tk.END, app.tr('filter_no_value'))
        
        for val in unique_values:
            if val: listbox.insert(tk.END, val)
        
        def apply_filter():
            try:
                selected_value = listbox.get(listbox.curselection()[0])
                filter_value = '' if selected_value == app.tr('filter_no_value') else selected_value
                app.df_data = app.df_original[app.df_original[filter_col] == filter_value].copy()
                app.status_label.config(text=app.tr('status_filtered').format(value=selected_value, count=len(app.df_data)))
                app.setup_treeview(app.df_data)
                filter_window.destroy()
            except IndexError:
                messagebox.showwarning(app.tr('dlg_selection_missing'), app.tr('dlg_select_value'))

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)

        ttk.Button(
            button_frame, 
            text=app.tr('btn_apply_filter'), 
            command=apply_filter,
            bootstyle="success"
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame, 
            text=app.tr('btn_cancel'), 
            command=filter_window.destroy,
            bootstyle="secondary"
        ).pack(side=tk.LEFT, padx=5)

    @staticmethod
    def show_stats_window(app):
        domain_counts = app.df_original[app.COL_ENTITY_ID].str.split('.', n=1).str[0].value_counts()
        stats_df = domain_counts.reset_index()
        stats_df.columns = [app.tr('stats_col_domain'), app.tr('stats_col_count')]
        
        stats_window = tk.Toplevel(app.root)
        stats_window.title(app.tr('stats_title'))
        app._set_icon(stats_window)
        
        stats_window.geometry("450x550")

        main_frame = ttk.Frame(stats_window, padding=15)
        main_frame.pack(expand=True, fill=tk.BOTH)

        title = ttk.Label(
            main_frame, 
            text=app.tr('stats_title'), 
            font=("Helvetica", 14, "bold"),
            bootstyle="primary"
        )
        title.pack(pady=(0, 10))

        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")

        stats_tree = ttk.Treeview(
            tree_frame, 
            columns=list(stats_df.columns), 
            show='headings',
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set
        )
        vsb.config(command=stats_tree.yview)
        hsb.config(command=stats_tree.xview)

        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        stats_tree.pack(fill=tk.BOTH, expand=True)

        for col in stats_df.columns:
            stats_tree.heading(col, text=col, anchor=tk.W)
            stats_tree.column(col, width=180, anchor=tk.W)

        for i, row in stats_df.iterrows():
            stats_tree.insert('', tk.END, values=row.tolist())

        ttk.Label(
            main_frame, 
            text=app.tr('stats_total').format(count=len(domain_counts)),
            bootstyle="secondary"
        ).pack(pady=5)

        ttk.Button(
            main_frame, 
            text=app.tr('btn_close'), 
            command=stats_window.destroy,
            bootstyle="primary"
        ).pack(pady=10)


if __name__ == "__main__":
    if not TTKBOOTSTRAP_AVAILABLE:
        root = tk.Tk()
        root.title("Fehler")
        ttk.Label(
            root, 
            text="TTKBootstrap ist nicht installiert.\n\nBitte führen Sie aus:\npip install ttkbootstrap",
            padding=20
        ).pack()
        ttk.Button(root, text="OK", command=root.destroy).pack(pady=10)
        root.mainloop()
    else:
        root = tk.Tk()
        app = EntityAnalyzerApp(root)
        root.mainloop()

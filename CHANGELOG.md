# Changelog

## [v_1.4] – 2026-05-15

### Hinzugefügt

- **Modernes Chart-Design** mit kuratierter Farbpalette (Tailwind-inspiriert),
  Light- und Dark-Variante. Subtile horizontale Grids, entfernte top/right
  Spines, dezente Spine-Farben, Titel als Subtitle-Pattern (Haupttitel +
  grauer Untertitel mit Gesamtsumme).
- **Hover-Tooltips für Balkendiagramme** mit Sensorname, Wert und Einheit
  (kontrastreiche, abgerundete Sprechblase). Funktioniert für gruppierte
  Bars (Vergleichsansicht) und Einzelbalken.
- **Anklickbare Legende** in der Vergleichsansicht: Klick auf Legenden-Eintrag
  blendet die jeweilige Serie ein/aus. Ausgeblendete Einträge werden
  optisch gedimmt. Funktioniert für Linien und Balken.
- **Mausrad-Zoom** um den Cursor:
  - In der Vergleichsansicht ohne Modifier (kein Konflikt mit Page-Scroll).
  - In der Einzelansicht mit Strg/Cmd+Mausrad (damit der vertikale
    Page-Scroll der Chart-Liste erhalten bleibt).
  - **Doppelklick** im Chart setzt den Zoom zurück.
- **Responsive Diagrammgröße**: Charts passen sich der Breite des
  Programmfensters automatisch an (debounced, ohne Resize-Schleife).
  Initial wird die Figur per `fit_figure_to_widget()` einmalig auf die
  tatsächliche Tk-Widget-Größe gezogen, damit beim ersten Render kein
  weißer Rand entsteht und die Legende nicht beschnitten wird.
- **Adaptive Legenden-Spaltenanzahl**: Bei langen Sensor-Namen werden
  weniger Spalten in der Legende verwendet (bis hin zu einer einzigen
  Spalte), damit nichts mehr seitlich abgeschnitten wird.
- **Stabile, vom Sensor-Namen abgeleitete Farbgebung** (kein zufälliges
  Wechseln der Farben mehr zwischen Aufrufen).
- **Adaptive Datums-Achse**: Format passt sich an den dargestellten
  Zeitraum an (`HH:MM` · `d. Mon` · `Mon JJJJ` · `JJJJ`).
- **Subtile Flächenfüllung** unter Liniendiagrammen, skaliert nach
  Sensoranzahl (kein muddy Overlap bei mehreren Sensoren mehr).
- **CHANGELOG.md** (diese Datei).

### Geändert

- **Build-Workflow** ([`.github/workflows/build.yml`](.github/workflows/build.yml))
  installiert jetzt zusätzlich `ttkbootstrap` und `Pillow` und packt die
  Logo-Dateien per `--add-data` in die Binaries. 
- **Datenaufbereitung des Energie-CSV** (`_perform_melt_on_selection`):
  - Nur Spalten mit echten Datums-Headern werden gemolten (Junk-Spalten
    wie `_min_ts` werden vorab ausgefiltert).
  - Ergebnis wird sauber nach `entity_id` und `timestamp` sortiert.
- **Annotationen über den Balken entfernt** zugunsten der Hover-Tooltips
  (sowohl in Einzel- als auch in Vergleichsansicht).
- **Statischer Theme-Wechsel** bringt jetzt auch das Chart-Design mit.

### Behoben

- **macOS-Regression: Nur erster Sensor sichtbar in der Einzelansicht.**
  Ursache: Das frühere Generator-Pattern in `_process_chart_generator`
  hat eine Exception im `tk.after`-Callback verschluckt und die Iteration
  nach dem ersten Chart abgebrochen. Jetzt synchroner Loop mit
  `update_idletasks()`-Yield, plus per Sensor `try/except`, das im
  Fehlerfall ein rotes Fehler-Label anzeigt statt still abzubrechen.
- **Liniendiagramme „gestaucht“** dargestellt: Timestamps wurden nach
  `melt()` nicht sortiert, wodurch die Linien zwischen Punkten in
  willkürlicher Reihenfolge gezeichnet wurden. Jetzt explizite Sortierung.
- **Balkendiagramme mit falscher Breite**: `np.min(np.diff(ts))` konnte
  bei unsortierten Timestamps negativ werden und damit negative Bar-Breiten
  erzeugen. Jetzt werden nur positive Gaps berücksichtigt.
- **Vergleichs-Balkendiagramm: kaputter Pivot-Bug** —
  `df.groupby('entity_id').apply(...).T` ergab eine Series mit MultiIndex,
  `.T` war ein No-Op. Ersetzt durch `pivot_table().resample()` mit
  garantierter `DataFrame`-Form (Timestamp-Index, Entity-Spalten).
- **Dark-Mode-Titel unsichtbar**: `ax.set_title()` überschrieb die
  vorher gesetzte Title-Farbe. Jetzt wird `color=` direkt an `set_title`
  übergeben.
- Ungenutzten `random`-Import entfernt.

[![GitHub release](https://img.shields.io/github/release/jayjojayson/HA-Entity-Analyzer?include_prereleases=&sort=semver&color=blue)](https://github.com/jayjojayson/HA-Entity-Analyzer/releases/)
[![Downloads](https://img.shields.io/github/downloads/jayjojayson/HA-Entity-Analyzer/total?label=downloads&logo=github&color=blue)](https://github.com/jayjojayson/HA-Entity-Analyzer/releases)
[![GH-code-size](https://img.shields.io/github/languages/code-size/jayjojayson/HA-Entity-Analyzer?color=blue)](https://github.com/jayjojayson/HA-Entity-Analyzer)
[![README English](https://img.shields.io/badge/README-English-orange)](https://github.com/jayjojayson/HA-Entity-Analyzer/blob/main/docs/README-Eng.md)

<img width="140" height="140" alt="E_A_T-logo" src="https://github.com/user-attachments/assets/c5266520-1eea-4d74-994a-4a34df8d7989" />

# Entity-Analyzer-Tool
Entity_Analyzer to anlyze the exported csv file from Home Assistant

Man kann wie im [HA-Forum](https://community.home-assistant.io/t/export-list-of-entities-automations-etc/884341/23) beschrieben wurde, auf dem Dahsboard einen Button anlegen, der nach drücken alle Home Assistant Entitäten, Automationen usw. in eine csv Datei exportiert. Diese Funktion vermisse ich aktuell in HA, da man so eine schöne “offline/backup” Variante hat, die Entitäten zu strukturieren, zu kontrollieren, zu dokumentieren bzw. sich einen Überblick zu verschaffen. Perfekt um “Leichen” auszusortieren, Namenstrukturen zu entwickeln usw.. Anschauen könnt ihr euch die csv-Datei z.B. mit dem beigefügtem Analyzer Tool oder mit Excel.

Schaut gerne in der Community vorbei. Dort haben wir ein entsprechendes [Diskussion-Thema für den Austausch.](https://community-smarthome.com/t/tutorial-alle-ha-entitaeten-per-csv-auslesen-und-mit-analyzer-tool-oder-excel-auswerten) 

Wenn euch das Tool gefällt würde ich mir über einen Stern ⭐ von euch freuen. 🤗

#### App-Features:
- 📄 simple Entities Tool to analyze your csv-file
- ↔️ import and export csv file
- 🔍 free entity search   
- 🔖 area & platform filter
- 📊 entities statistic

#### Gui-Features
- works on win, (macos & linux)
- dark/lite mode
- app on top (keep in foreground)

Exported csv includes: entity_id, entityName, device_id, deviceName, area, plattform, state, manufacturer, model, model_id, sw_version, hw_version 

## 📌 Vorgehensweise

Erstellt als erstes im Dashboard eine neue [custom button card](https://github.com/custom-cards/button-card) und fügt dort folgenden Code ein. Im Anschluss solltet ihr wie im Bild gezeigt diesen Button erhalten. Drückt nach Fertigstellung den Button und ihr bekommt die csv-Datei in den Download-Ordner.

<img width="551" height="86" alt="image (1)" src="https://github.com/user-attachments/assets/9dbb3d10-0c5c-4f98-90ed-8fffbba94ece" />

```yaml
type: custom:button-card
name: Entity Export as CSV
tap_action:
  action: javascript
  javascript: |
    [[[
      function clean(value) {
        if (!value) return "";
        return String(value)
          .replace(/;/g, ",")
          .replace(/\r?\n|\r/g, " ");
      }

      async function generateCSV() {
        const hass = document.querySelector("home-assistant").hass;

        const areas = await hass.callWS({ type: "config/area_registry/list" });
        const devices = await hass.callWS({ type: "config/device_registry/list" });
        const entities = await hass.callWS({ type: "config/entity_registry/list" });

        const areaLookup = {};
        areas.forEach(a => (areaLookup[a.area_id] = a.name));

        let csv =
          "ENTITY ID;ENTITY NAME;DEVICE NAME;DEVICE ID;AREA;PLATFORM;STATE;FORMATTED STATE;" +
          "MANUFACTURER;MODEL;MODEL ID;SW VERSION;HW VERSION\n";

        Object.values(hass.states)
          .sort((a, b) => a.entity_id.localeCompare(b.entity_id))
          .forEach(stateObj => {
            const entReg = entities.find(e => e.entity_id === stateObj.entity_id);
            const device = devices.find(d => d.id === entReg?.device_id);

            const areaName =
              entReg?.area_id
                ? areaLookup[entReg.area_id] || ""
                : device?.area_id
                ? areaLookup[device.area_id] || ""
                : "";

            // Plattform
            const platform =
              entReg?.platform ||
              entReg?.integration ||
              stateObj.entity_id.split(".")[0];

            // Geräteattribute
            const manufacturer = device?.manufacturer || "";
            const model = device?.model || "";
            const model_id = device?.model_id || "";
            const sw_version = device?.sw_version || "";
            const hw_version = device?.hw_version || "";

            const row = [
              clean(stateObj.entity_id),
              clean(hass.formatEntityName(stateObj)),
              clean(device?.name || ""),
              clean(entReg?.device_id || ""),
              clean(areaName),
              clean(platform),
              clean(stateObj.state),
              clean(hass.formatEntityState(stateObj)),
              clean(manufacturer),
              clean(model),
              clean(model_id),
              clean(sw_version),
              clean(hw_version)
            ].join("; ");

            csv += row + "\n";
          });

        const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "hass_entities.csv";
        a.click();
        URL.revokeObjectURL(url);
      }

      generateCSV();
    ]]]
```

---

<details>
   <summary> <b>For HA-Version before 2025.11 use this card below and dowload the ver_1.1</b></summary> 
   
```yaml
type: custom:button-card
name: Entity Export as CSV
tap_action:
  action: javascript
  javascript: |
    [[[
      function generateEntityItems() {
          const hass = document.querySelector("home-assistant").hass;
          const entities = hass.entities;
          
          const sorted = Object.values(entities).sort((a, b) => {
              const idA = a.entity_id?.toLowerCase() || '';
              const idB = b.entity_id?.toLowerCase() || '';
              return idA.localeCompare(idB);
          });
      
          let csvContent = "ENTITY ID;ENTITY NAME;DEVICE NAME;DEVICE ID;AREA;PLATFORM (INTEGRATION);STATE;FORMATED STATE\n";
          
          sorted.forEach((ent) => {
              const eId = ent.entity_id;
              const stateObj = hass.states[eId];
              const entityName = hass.formatEntityName(stateObj, "entity");
              const deviceName = hass.formatEntityName(stateObj, "device");
              const deviceId =  ent.device_id;
              const areaName = hass.formatEntityName(stateObj, "area") || '';
              const platform = ent.platform || '';
              const state = stateObj.state;
              const formatedState = hass.formatEntityState(stateObj);
              
              const info = [eId, entityName, deviceName, deviceId, areaName, platform, state, formatedState].join("; ");
              
              csvContent += `${info}\n`;
          });
      
          const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
          const url = URL.createObjectURL(blob);
          const link = document.createElement("a");
          link.setAttribute("href", url);
          link.setAttribute("download", "hass_entities.csv");
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
      };
      generateEntityItems();
    ]]]
```
</details>

---

## 📌 Installation

Ich habe ein kleines Python Tool entwickelt, dass die CSV einlesen kann. Für Windows gibt es gibt zwei Wege für die Installation, erstens bequem mit fertigem Programm arbeiten oder zweitens Python direkt installieren und das py-Script starten. Für Linux bleibt aktuell nur die Möglichkeit über Python direkt zu arbeiten, folgt dazu den Anweisungen. 

### Für Windows ladet euch einfach die ausführbare Version (.exe) herunter und startet das Programm.

### Betrifft nur die manuelle Installation!
Das Tool nutzt Python, daher muss Python installiert sein oder werden!

#### In **Windows** öffnet ihr dazu die Powershell und gebt folgenden Befehl ein:

```powershell
winget install Python
```

Danach installiert ihr noch das pandas Paket bzw. die Bibliothek:

```powershell
pip install pandas
```

Unter Windows könnt ihr die Python Datei direkt aus dem "src" Ordner mit Doppelklick starten.

---

#### Unter **Linux** gebt folgende Befehle im Terminal ein:

```powershell
sudo apt update && sudo apt install python3
```

Danach installiert ihr noch das pandas Paket bzw. die Bibliothek:

```powershell
pip install pandas
```

Um das Programm zu öffnen, wechselt mit cd /euer Verzeichnis in den Ordner wo euer Entity_Analyzer liegt und startet mit folgendem Befehl das Tool.

```powershell
python3 entity_analyzer_tool.py
```

---
## 📌 Nutzung

Nun könnt ihr den Entity_Analyzer öffnen und eure csv-Datei auswählen. Die Oberfläche bietet ein paar Möglichkeiten eure Entitäten zu sichten. Nach dem öffnen seht ihr unten links die Anzahl der Entitäten! Dort werden auch sonst nützliche Infos angezeigt.

<img width="1202" height="732" alt="image" src="https://github.com/user-attachments/assets/67fe18c6-1c2e-49f9-be7b-12c46bd9d92d" />

### 1. Jetzt könnt ihr beispielsweise nach gewünschten Entitäten **suchen**:

    
Über die Spaltennamen kann beim auswählen eine aufsteigende oder absteigende Sortierung erfolgen. Außerdem könnt ihr die aktuelle Ansicht der Suche als neue csv Datei exportieren.
    
<img width="1202" height="732" alt="image" src="https://github.com/user-attachments/assets/d84a0497-aa8a-4356-b631-17276693ee4d" />

### 2. Die **Entitätsstatistik** abrufen und sehen wie viele Lichter oder Schalter habt ihr usw.:

<img width="402" height="582" alt="image" src="https://github.com/user-attachments/assets/28d4575d-290c-4e22-9146-8011793e68c5" />


### 3. Oder ihr könnt nach **Area** also Bereichen bzw. **Platform** und somit Integrationen filtern.

<img width="281" height="261" alt="image (5)" src="https://github.com/user-attachments/assets/87a48bf9-9e9d-4575-8537-212dde444bd5" />
<img width="294" height="270" alt="image (6)" src="https://github.com/user-attachments/assets/417d8390-7393-48d3-9424-31517dae19fa" />


---

### ⭐ Danke für die Unterstützung aus der Community, besonders an Dreckfresse, Nicknol und MarzyHA. Immer wieder schön, was man gemeinsam erreichen kann.

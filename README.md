
<img width="120" height="120" alt="analysis" src="https://github.com/user-attachments/assets/7e082b82-7ee9-448a-9919-f802debc88d0" /> 

# HA-Entity-Analyzer
Entity_Analyzer to anlyze the exported csv file from Home Assistant

Man kann wie im [HA-Forum](https://community.home-assistant.io/t/export-list-of-entities-automations-etc/884341/23) beschrieben wurde, auf dem Dahsboard einen Button anlegen, der nach drücken alle Home Assistant Entitäten, Automationen usw. in eine csv Datei exportiert. Diese Funktion vermisse ich aktuell in HA, da man so eine schöne “offline/backup” Variante hat, die Entitäten zu strukturieren, zu kontrollieren, zu dokumentieren bzw. sich einen Überblick zu verschaffen. Perfekt um “Leichen” auszusortieren, Namenstrukturen zu entwickeln usw.. Anschauen könnt ihr euch die csv-Datei z.B. mit dem beigefügtem Analyzer Tool oder mit Excel.

Schaut gerne in die Community vorbei. Dort haben wir ein entsprechendes [Diskussion-Thema für den Austausch.](https://community-smarthome.com/t/tutorial-alle-ha-entitaeten-per-csv-auslesen-und-mit-analyzer-tool-oder-excel-auswerten) 

## Vorgehensweise

Erstellt als erstes im Dashboard eine neue [custom button card](https://github.com/custom-cards/button-card) und fügt dort folgenden Code ein. Im Anschluss solltet ihr wie im Bild gezeigt diesen Button erhalten. Drückt nach Fertigstellung den Button und ihr bekommt die csv-Datei in den Download-Ordner.

<img width="551" height="86" alt="image (1)" src="https://github.com/user-attachments/assets/9dbb3d10-0c5c-4f98-90ed-8fffbba94ece" />

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

---

Ich habe ein kleines Python Tool entwickelt, dass die CSV einlesen kann. Für Windows gibt es gibt zwei Wege für die Installation, erstens bequem mit fertigem Programm arbeiten oder zweitens Python direkt installieren und das py-Script starten. Für Linux bleibt aktuell nur die Möglichkeit über Python direkt zu arbeiten, folgt dazu den Anweisungen. Für Windows ladet euch einfach die ausführbare Version (.exe) herunter und startet das Programm.

### Betrifft nur die manuelle Installation:
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
python3 entity_analyzer_v1.py
```

---

Nun könnt ihr den Entity_Analyzer öffnen und eure csv-Datei auswählen. Die Oberfläche bietet ein paar Möglichkeiten eure Entitäten zu sichten. Nach dem öffnen seht ihr unten links die Anzahl der Entitäten!

<img width="1202" height="734" alt="image (2)" src="https://github.com/user-attachments/assets/164531b0-0746-48b5-968e-350737fa258e" />

### 1. Jetzt könnt ihr beispielsweise nach gewünschten Entitäten **suchen**:

    
    Über die Spaltennamen kann beim auswählen eine aufsteigende oder absteigende Sortierung erfolgen.
    

<img width="1201" height="734" alt="image (3)" src="https://github.com/user-attachments/assets/11d213f2-1755-4419-8168-ab0c71ec8c9a" />

### 2. Die **Entitätsstatistik** abrufen und sehen wie viele Lichter oder Schalter habt ihr usw.:

<img width="401" height="432" alt="image (4)" src="https://github.com/user-attachments/assets/148a169a-915c-4e2a-83db-3341efd37d44" />


### 3. Oder ihr könnt nach **Area** also Bereichen bzw. **Platform** und somit Integrationen filtern.

<img width="281" height="261" alt="image (5)" src="https://github.com/user-attachments/assets/87a48bf9-9e9d-4575-8537-212dde444bd5" />
<img width="294" height="270" alt="image (6)" src="https://github.com/user-attachments/assets/417d8390-7393-48d3-9424-31517dae19fa" />

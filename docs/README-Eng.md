[![GitHub release](https://img.shields.io/github/release/jayjojayson/HA-Entity-Analyzer?include_prereleases=&sort=semver&color=blue)](https://github.com/jayjojayson/HA-Entity-Analyzer/releases/)
[![Downloads](https://img.shields.io/github/downloads/jayjojayson/HA-Entity-Analyzer/total?label=downloads&logo=github&color=blue)](https://github.com/jayjojayson/HA-Entity-Analyzer/releases)
[![GH-code-size](https://img.shields.io/github/languages/code-size/jayjojayson/HA-Entity-Analyzer?color=blue)](https://github.com/jayjojayson/HA-Entity-Analyzer)
[![README English](https://img.shields.io/badge/README-English-orange)](https://github.com/jayjojayson/HA-Entity-Analyzer/blob/main/docs/readME-Eng.md)

<img width="140" height="140" alt="E_A_T-logo" src="https://github.com/user-attachments/assets/c5266520-1eea-4d74-994a-4a34df8d7989" />

# Entity-Analyzer-Tool
Entity_Analyzer to analyze the exported csv file from Home Assistant

As described in the [HA Forum](https://community.home-assistant.io/t/export-list-of-entities-automations-etc/884341/23), you can create a button on your dashboard that exports all Home Assistant entities, automations, etc. into a CSV file when pressed. I currently miss this feature in HA because it's a convenient “offline/backup” method to structure, review, document, and get an overview of your entities. Perfect for cleaning up unused items, developing naming conventions, and more.  
You can open the CSV file with the included Analyzer Tool or with Excel.

Feel free to join the community — we have a dedicated [discussion topic for exchange.](https://community-smarthome.com/t/tutorial-alle-ha-entitaeten-per-csv-auslesen-und-mit-analyzer-tool-oder-excel-auswerten)

If you like the tool, I would appreciate a ⭐. 🤗

#### App-Features:
- 📄 simple entity tool to analyze your csv file
- ↔️ import and export csv files
- 🔍 free entity search
- 🔖 area & platform filter
- 📊 entity statistics

#### Gui-Features
- works on Windows (macOS & Linux planned)
- dark/light mode
- keep app on top (stay in foreground)

Exported CSV includes: entity_id, entityName, device_id, deviceName, area, platform, state, manufacturer, model, model_id, sw_version, hw_version

## 📌 Procedure

First, create a new [custom button card](https://github.com/custom-cards/button-card) on your dashboard and insert the following code. Afterwards you should get the button shown in the image. Press the button to receive the csv file in your download folder.

<img width="551" height="86" alt="image (1)" src="https://github.com/user-attachments/assets/9dbb3d10-0c5c-4f98-90ed-8fffbba94ece" />

<details> 
	<summary> <b>For HA-Version before 2025.11 use this card below and download version 1.1</b></summary>

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

</details>

## 📌 Installation

I developed a small Python tool that can read the CSV. On Windows there are two ways to install it:

Use the precompiled executable, or

Install Python and run the script directly.
For Linux, the only option currently is to run it with Python directly — follow the instructions below.

On Windows simply download the executable (.exe) and run the program.
Manual installation only!

The tool requires Python, so Python must be installed.

On Windows, open PowerShell and enter:
```powershell
winget install Python
```

Then install the pandas package/library:
```powershell
pip install pandas
```

On Windows you can start the Python file directly from the "src" folder by double-clicking it.

On Linux, enter the following commands in the terminal:
```powershell
sudo apt update && sudo apt install python3
```

Then install the pandas package/library:

```powershell
pip install pandas
```

To open the program, change directory with cd /your folder to the folder where your Entity_Analyzer is located and start the tool with:

```powershell
python3 entity_analyzer_tool.py
```

## 📌 Usage

Now you can open the Entity_Analyzer and select your csv file. The interface offers several options to review your entities. After opening, you will see the number of entities at the bottom left! Useful info is also shown there.

<img width="1202" height="732" alt="image" src="https://github.com/user-attachments/assets/67fe18c6-1c2e-49f9-be7b-12c46bd9d92d" />
1. Now you can search for desired entities:

By clicking on column names, you can sort ascending or descending. Also, you can export the current search view as a new csv file.

<img width="1202" height="732" alt="image" src="https://github.com/user-attachments/assets/d84a0497-aa8a-4356-b631-17276693ee4d" />
2. Retrieve the entity statistics and see how many lights or switches you have, etc.:
<img width="402" height="582" alt="image" src="https://github.com/user-attachments/assets/28d4575d-290c-4e22-9146-8011793e68c5" />
3. Or you can filter by Area or Platform (i.e., integrations).
<img width="281" height="261" alt="image (5)" src="https://github.com/user-attachments/assets/87a48bf9-9e9d-4575-8537-212dde444bd5" /> <img width="294" height="270" alt="image (6)" src="https://github.com/user-attachments/assets/417d8390-7393-48d3-9424-31517dae19fa" />

⭐ Thanks for the support from the community, especially Dreckfresse, Nicknol and MarzyHA. Always nice to see what can be achieved together.
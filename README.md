# NAPPA Infant Sleep Analyzer

**NAPPA Infant Sleep Analyzer (ISA)** is a tool designed to analyze infant sleep patterns using accelerometer and gyroscope data from the **NAPing PAnts** wearable developed by the BABA Center. The application provides a graphical user interface (GUI) for importing, processing, and analyzing sleep recordings, and generates detailed reports in PDF and CSV formats.

---

## Features

- **Data import**: Load sleep recordings from ZIP files containing accelerometer and gyroscope feature data in CSV format.  
- **Automatic wear detection**: Automatically detect sleep periods and generate detailed with individual analyses for each sleep period.  
- **Manual selection**: Option to manually select sleep periods for customized report generation.  
- **Configurable analysis**: Set time offset, apply filters, and customize plot settings. 
- **Multi-page PDF reports**: Summarize sleep statistics and visualize infant activity, respiration rate, and more.  
- **CSV outputs**: Classifier results, recording data and related analytics can be exported in CSV format.

---

## Screenshots

<p align="center">
  <img 
    src="https://github.com/matiashaggman/NAPPA-ISA/tree/main/src/example_report_1.png?raw=true" 
    alt="Example report screenshot" 
    width="400"
  />
    <img 
    src="https://github.com/matiashaggman/NAPPA-ISA/tree/main/src/example_report_2.png?raw=true" 
    alt="Example report screenshot" 
    width="400"
  />
   <img 
    src="https://github.com/matiashaggman/NAPPA-ISA/tree/main/src/ui_1.png?raw=true" 
    alt="UI screenshot" 
    width="400"
    style="margin-right: 20px;"
  />
    <img 
    src="https://github.com/matiashaggman/NAPPA-ISA/tree/main/src/ui_2.png?raw=true" 
    alt="UI screenshot" 
    width="400"
    style="margin-right: 20px;"
  />
</p>

---

## Installation


### Using the Client version (`NAPPA-ISA Client.exe` on Windows)

1. **Download** the contents of the `bin` directory.
2. **Keep files together**: All downloaded contents must remain in the **same directory** for the application to work properly.
3. **Run** NAPPA-ISA Client.exe
---

## Usage

1. **Use the GUI** to:
   - Select an input ZIP file containing the sleep recording data (drag & drop supported).
     
     ```IMPORTANT: The ZIP file at the moment may contain only one set of wearable sensor generated files, i.e one pair of 'AccFeatures.csv' and 'GyroFeatures.csv' -feature files.```
   - Configure any analysis options (e.g. filtering, time offset (based on your location)).
   - Click **Analyze** to start the analysis.
   - The resulting files are saved to a ZIP archive of your choice.

2. **Outputs**:
   - A **PDF** report containing:
     - A sleep depth trend or a discrete hypnogram over time
     - Baby movement activity, respiration rate, and body position data as functions of time
     - Bar/violin plots for visualizing overall sleep distribution over long times
     - A donut plot for individual sleep periods visualizing the distribution of sleep stages.
     - Text summary containing the number of hours spent in different sleep stages
   - Optional: a **CSV** file with the classifier output, sleep depth trend and the recorded feature data from the wearable sensor
   - optional: **PNG** files of the report figures separately
---

## Project Structure

### Client side

* **`bin/NAPPA-ISA Client.exe`** – Windows GUI application (portable build).
* **`src/Frontend/`** – Visual Studio 2022 project sources.

| Path                                                      | What it contains                                                                                                                                          |
| --------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`src/Frontend/Common/`**                                | Header-only shared code & `inAppPlugin.h` (plug-in extension API).                                                                                        |
| **`src/Frontend/Frontend/`**                              | Main GUI project<br>• `main.cpp`, `NappaMainWindow.*`, `SettingsWindow.*`<br>• *.ui* files from Qt Designer<br>• `Frontend.vcxproj` plus icons/resources. |
| **`src/Frontend/NappaPlugin/`**                           | Example plug-in project (`NappaPlugin.dll`, `plugin.json`) showing how to extend the app at run-time.                                                     |
| **`src/Frontend/`** – `build_pc.bat` / `build_laptop.bat` | One-click scripts that run **windeployqt**, package the binaries, and zip them for distribution.                                                          |                                                                                        |

                                                                                                                             |


### Server side (lightning.ai based)
- **`src/Backend/nappa-isa.py`**: Server side core analysis functions and utilities.  
- **`src/Backend/nappa/preprocess.py`**: Data preprocessing and scaling functions.  
- **`src/Backend/nappa/pipeline.py`**: Routines for reading and processing feature files.  
- **`src/Backend/nappa/objects.py`**: Classes for organizing sensor data.  
- **`src/Backend/nappa/models.py`**: Deep learning classifier for the sleep depth trend & hypnogram.
---

## License

This project is licensed under the **MIT License**.

---

## Acknowledgements

> **Note**: This program is in **early development** and remains largely untested. Please report any bugs or compatibility issues to the author.  
> Developed and maintained by the [BABA Center](https://www.babacenter.fi/).

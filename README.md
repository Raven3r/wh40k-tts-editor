# Warhammer 40k Crusade TTS Unit Editor

A GUI application for more user-friendly editing of Warhammer 40k unit descriptions in Tabletop Simulator JSON files. Mainly for use in Crusade games to account for battle traits and upgrades.

## Features

- Load and save Tabletop Simulator JSON files
- Structured editor for easier editing of stats, weapons, and abilities
- Preview how the formatted text will appear


## Requirements

- Python 3.6 or higher
- Tkinter (usually included with Python)

## Installation

### From Source

1. Clone the repository
2. Install the package:

```bash
pip install -e .
```

## Usage

### Running the Application

You can run the application in several ways:

1. Using the installed script:

```bash
tts-editor
```

2. Directly from the source:

```bash
python -m tts_editor.main
```

3. With a file to open:

```bash
tts-editor "path/to/your/tts_file.json"
```

### Using the Editor

1. **Loading a File**: 
   - The application will attempt to load the file specified on the command line if provided.
   - You can also open a file using File > Open.

2. **Selecting a Unit**:
   - Units are listed in the left panel.
   - Click on a unit to see its profiles.
   - Click on a profile to load its description for editing.

3. **Editing Description**:
   - Use the Text Editor tab for direct text editing.
   - Use the Structured Editor tab for a more user-friendly interface.

4. **Saving Changes**:
   - Click "Save Changes" to update the unit in memory.
   - Use File > Save to save changes to the JSON file.

## Project Structure

- `src/tts_editor/` - Main package
  - `app.py` - Application class
  - `main.py` - Entry point
  - `models/` - Data models
    - `unit.py` - Unit and profile models
  - `ui/` - User interface components
    - `main_window.py` - Main window
    - `text_editor.py` - Text editor component
    - `structured_editor.py` - Structured editor component
  - `utils/` - Utility functions
    - `description_parser.py` - Stat parsing utilities


## Important Notes

- This editor only modifies the "Description" field in the JSON file.
- The LuaScript and other fields are preserved but not edited.
- Only a unit's nickname is used for identifying units. 
   - You can separate out different profiles within a unit by changing a model's nickname to "<unit_name> - <model_name>". For example: "Howling Banshees - Exarch"
   - Name changes must currently be done within TTS or chosen list editor/creator (may be added as a feature in future)

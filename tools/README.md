# Eva Icons Flutter - Tools

This directory contains tools for generating the Eva Icons Flutter library from TTF font files.

## Overview

The tools in this directory enable automatic generation of Flutter IconData constants from the Eva Icons TTF font file. This ensures that if you update the font file, you can regenerate the entire library automatically.

## Files

- `generate_icons.py` - Python script that extracts font metadata and generates Dart code
- `build.sh` - Shell script that orchestrates the complete build process
- `eva_icons_mappings.json` - Generated metadata file with icon mappings (created during build)
- `venv/` - Python virtual environment (created during first build)

## Quick Start

To regenerate the icon library:

```bash
cd tools
./build.sh
```

This will:
1. Set up a Python virtual environment
2. Install required dependencies (fonttools)
3. Extract metadata from the TTF font
4. Generate new Dart code
5. Format the generated code
6. Run Flutter analysis

## Manual Usage

### Python Script

```bash
cd tools
python generate_icons.py --help
```

Options:
- `--font-path PATH` - Path to TTF font file (default: ../lib/fonts/Eva-Icons.ttf)
- `--output-dir DIR` - Output directory for Dart files (default: ../lib/src)

### Examples

Generate with custom font path:
```bash
python generate_icons.py --font-path /path/to/custom-icons.ttf
```

Generate to custom output directory:
```bash
python generate_icons.py --output-dir /path/to/output
```

## Requirements

- Python 3.6+
- fonttools Python package (automatically installed)
- Flutter SDK (optional, for formatting and analysis)

## Process

1. **Font Analysis**: The script uses fonttools to read the TTF file and extract Unicode character mappings
2. **Name Conversion**: Glyph names are converted to Dart-compatible camelCase identifiers
3. **Duplicate Handling**: Icons with duplicate names get numbered suffixes
4. **Code Generation**: Dart constants are generated with proper documentation
5. **Metadata Export**: A JSON file is created for reference and debugging

## Generated Output

### Dart File (`lib/src/eva_icons_flutter.dart`)
Contains the `EvaIcons` class with static IconData constants:

```dart
class EvaIcons {
  /// Activity icon
  ///
  /// https://akveo.github.io/eva-icons/#/?searchKey=activity
  static const IconData activity = EvaIconData(0xea01);
  
  // ... more icons
}
```

### JSON Metadata (`eva_icons_mappings.json`)
Reference file with detailed mappings:

```json
{
  "font_family": "EvaIcons",
  "font_package": "eva_icons_flutter", 
  "total_icons": 490,
  "unicode_range": {
    "start": "0xea01",
    "end": "0xebea"
  },
  "mappings": {
    "activity": {
      "glyph_name": "activity",
      "unicode": "0xea01",
      "decimal": 59905
    }
  }
}
```

## Updating Icons

To update the icon library with a new TTF file:

1. Replace `lib/fonts/Eva-Icons.ttf` with your new font file
2. Run `./tools/build.sh`
3. Review the generated code
4. Test the icons in your Flutter app
5. Commit the changes

## Troubleshooting

### Common Issues

**Python not found:**
```bash
# Install Python 3
brew install python3  # macOS
sudo apt install python3  # Ubuntu
```

**Permission denied:**
```bash
chmod +x tools/build.sh
```

**Font file not found:**
- Ensure the TTF file exists at `lib/fonts/Eva-Icons.ttf`
- Or specify custom path with `--font-path`

**Generation fails:**
- Check that the TTF file is valid
- Ensure it contains Unicode character mappings
- Verify the font has icons in the expected range (0xEA00-0xEBFF)

### Debug Mode

For verbose output, modify the Python script or run with:
```bash
python -v generate_icons.py
```

## Architecture Notes

The generation process follows these principles:

1. **Single Source of Truth**: The TTF font file contains all icon metadata
2. **Automated Processing**: No manual curation of icon lists required
3. **Intelligent Naming**: Automatic conversion from glyph names to Dart identifiers
4. **Documentation**: Each icon includes links to Eva Icons reference
5. **Type Safety**: Generated constants use proper IconData types

## Contributing

When making changes to the generation tools:

1. Test with the existing Eva Icons font
2. Verify generated code compiles and works
3. Check that formatting and analysis pass
4. Update documentation as needed
5. Consider backward compatibility
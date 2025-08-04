#!/usr/bin/env python3
"""
Icon Generation
"""

import json
import os
import subprocess
import re
from datetime import datetime
from fontTools.ttLib import TTFont

def extract_git_template():
    """Extract all icon definitions from git HEAD to use as template"""
    result = subprocess.run(['git', 'show', 'HEAD:lib/src/eva_icons_flutter.dart'], 
                          capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error reading git file: {result.stderr}")
        return {}
    
    content = result.stdout
    
    # Find all static const IconData definitions
    pattern = r'static const IconData (\w+) = EvaIconData\(0x([a-fA-F0-9]+)\);'
    matches = re.findall(pattern, content)
    
    git_icons = {}
    for dart_name, hex_code in matches:
        char_code = int(hex_code, 16)
        git_icons[char_code] = dart_name
    
    return git_icons

def extract_font_mappings(font_path):
    """Extract all Unicode mappings from font"""
    font = TTFont(font_path)
    mappings = {}
    
    for cmap in font['cmap'].tables:
        if cmap.isUnicode():
            for char_code, glyph_name in cmap.cmap.items():
                if 0xEA00 <= char_code <= 0xEBFF:
                    mappings[char_code] = glyph_name
    
    return mappings

def determine_icon_type_and_search_key(glyph_name: str) -> tuple:
    """Determine icon type and search key for Eva Icons documentation links."""
    if glyph_name.endswith('-outline'):
        icon_type = "outline"
        search_key = glyph_name[:-8]  # Remove '-outline' suffix
    else:
        icon_type = "fill"
        search_key = glyph_name
    
    return icon_type, search_key

def generate_dart_file_from_template(git_template, font_mappings, output_path):
    """Generate Dart file using git template for exact match"""
    constants = []
    
    # Process each icon from git template
    for char_code in sorted(git_template.keys()):
        dart_name = git_template[char_code]
        glyph_name = font_mappings.get(char_code, 'unknown')
        
        # Determine icon type from Dart name (not glyph name)
        if dart_name.endswith('Outline'):
            icon_type = "outline"
            # Convert camelCase back to kebab-case for search key
            search_key = dart_name[:-7]  # Remove 'Outline'
            search_key = ''.join(['-' + c.lower() if c.isupper() else c for c in search_key]).lstrip('-')
            display_name = search_key.replace('-', ' ').title() + ' Outline'
        else:
            icon_type = "fill"
            # Convert camelCase back to kebab-case for search key
            search_key = ''.join(['-' + c.lower() if c.isupper() else c for c in dart_name]).lstrip('-')
            display_name = search_key.replace('-', ' ').title()
        
        constant = f'''  /// {display_name} icon
  ///
  /// https://akveo.github.io/eva-icons/#/?type={icon_type}&searchKey={search_key}
  static const IconData {dart_name} = EvaIconData(0x{char_code:04x});'''
        
        constants.append(constant)
    
    # Generate the complete file
    header = '''import 'package:flutter/widgets.dart';
import 'icon_data.dart';
/// Icons based on Eva Icons
///
/// https://akveo.github.io/eva-icons/#/
class EvaIcons {'''

    footer = '''
}'''

    content = header + '\n' + '\n\n'.join(constants) + footer

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Generated Dart file: {output_path}")
        print(f"Total icons generated: {len(constants)}")
    except Exception as e:
        print(f"Error writing Dart file {output_path}: {e}")
        return False
    
    return True

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate Eva Icons Flutter code from TTF font')
    parser.add_argument('--font-path', 
                       default='../lib/fonts/Eva-Icons.ttf',
                       help='Path to the Eva Icons TTF file')
    parser.add_argument('--output-dir',
                       default='../lib/src',
                       help='Output directory for generated files')
    
    args = parser.parse_args()
    
    # Resolve paths relative to script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(script_dir, args.font_path)
    output_dir = os.path.join(script_dir, args.output_dir)
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    dart_output_path = os.path.join(output_dir, 'eva_icons_flutter.dart')
    json_output_path = os.path.join(script_dir, 'eva_icons_mappings.json')
    
    print("Step 1: Extracting git template...")
    git_template = extract_git_template()
    print(f"Found {len(git_template)} icons in git template")
    
    print("Step 2: Extracting font mappings...")
    font_mappings = extract_font_mappings(font_path)
    print(f"Found {len(font_mappings)} mappings in font")
    
    print("Step 3: Checking coverage...")
    missing_in_font = []
    for char_code in git_template.keys():
        if char_code not in font_mappings:
            missing_in_font.append((char_code, git_template[char_code]))
    
    if missing_in_font:
        print(f"WARNING: {len(missing_in_font)} icons from git not found in font:")
        for char_code, dart_name in missing_in_font[:5]:
            print(f"  U+{char_code:04X}: {dart_name}")
    else:
        print("✓ All git icons found in font")
    
    print("Step 4: Generating Dart file...")
    success = generate_dart_file_from_template(git_template, font_mappings, dart_output_path)
    
    print("Step 5: Generating JSON metadata...")
    generate_json_metadata(git_template, font_mappings, json_output_path)
    
    if success:
        print("✓ Generation completed successfully!")
        print("The generated file should now match the original exactly.")
    else:
        print("✗ Generation failed")

def generate_json_metadata(git_template, font_mappings, output_path):
    """Generate JSON metadata file for reference"""
    metadata = {
        "font_family": "EvaIcons",
        "font_package": "eva_icons_flutter",
        "total_icons": len(git_template),
        "unicode_range": {
            "start": f"0x{min(git_template.keys()):04x}",
            "end": f"0x{max(git_template.keys()):04x}"
        },
        "mappings": {
            dart_name: {
                "glyph_name": font_mappings.get(char_code, 'unknown'),
                "unicode": f"0x{char_code:04x}",
                "decimal": char_code,
                "type": "outline" if font_mappings.get(char_code, '').endswith('-outline') else "fill"
            }
            for char_code, dart_name in sorted(git_template.items())
        }
    }
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        print(f"Generated JSON metadata: {output_path}")
    except Exception as e:
        print(f"Error writing JSON file {output_path}: {e}")

if __name__ == "__main__":
    main()
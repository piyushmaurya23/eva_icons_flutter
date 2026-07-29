#!/usr/bin/env python3
"""Generate Eva Icons Flutter sources from the bundled font."""

import argparse
import json
import os
import re
import subprocess

from fontTools.ttLib import TTFont


ICON_PATTERN = re.compile(
    r'static const IconData\s+(\w+)\s*=\s*'
    r'(?:EvaIconData|IconData)\(\s*0x([a-fA-F0-9]+)'
)


def extract_git_template():
    """Extract the public icon names and code points from git HEAD."""
    result = subprocess.run(
        ['git', 'show', 'HEAD:lib/src/eva_icons_flutter.dart'],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(f"Error reading git file: {result.stderr.strip()}")

    matches = ICON_PATTERN.findall(result.stdout)
    if not matches:
        raise RuntimeError(
            'No icon definitions found; refusing to overwrite the Dart library.'
        )

    return {
        int(hex_code, 16): dart_name
        for dart_name, hex_code in matches
    }


def extract_font_mappings(font_path):
    """Extract the Eva Icons Unicode mappings from the font."""
    font = TTFont(font_path)
    mappings = {}

    for cmap in font['cmap'].tables:
        if cmap.isUnicode():
            for char_code, glyph_name in cmap.cmap.items():
                if 0xEA00 <= char_code <= 0xEBFF:
                    mappings[char_code] = glyph_name

    return mappings


def icon_details(dart_name):
    """Return the display name, icon type, and documentation search key."""
    is_outline = dart_name.endswith('Outline')
    base_name = dart_name[:-7] if is_outline else dart_name
    search_key = re.sub(r'(?<!^)(?=[A-Z])', '-', base_name).lower()
    display_name = search_key.replace('-', ' ').title()

    if is_outline:
        display_name += ' Outline'

    return display_name, 'outline' if is_outline else 'fill', search_key


def generate_dart_content(git_template):
    """Generate the Dart source for the public icon constants."""
    constants = []

    for char_code, dart_name in sorted(git_template.items()):
        display_name, icon_type, search_key = icon_details(dart_name)
        constants.append(
            f'''  /// {display_name} icon
  ///
  /// https://akveo.github.io/eva-icons/#/?type={icon_type}&searchKey={search_key}
  static const IconData {dart_name} = IconData(
    0x{char_code:04x},
    fontFamily: 'EvaIcons',
    fontPackage: 'eva_icons_flutter',
  );'''
        )

    header = '''import 'package:flutter/widgets.dart';

/// Icons based on Eva Icons
///
/// https://akveo.github.io/eva-icons/#/
class EvaIcons {'''

    return header + '\n' + '\n\n'.join(constants) + '\n}\n'


def generate_json_metadata(git_template, font_mappings):
    """Generate JSON metadata for the public icon constants."""
    return {
        'font_family': 'EvaIcons',
        'font_package': 'eva_icons_flutter',
        'total_icons': len(git_template),
        'unicode_range': {
            'start': f"0x{min(git_template):04x}",
            'end': f"0x{max(git_template):04x}",
        },
        'mappings': {
            dart_name: {
                'glyph_name': font_mappings.get(char_code, 'unknown'),
                'unicode': f"0x{char_code:04x}",
                'decimal': char_code,
                'type': (
                    'outline'
                    if font_mappings.get(char_code, '').endswith('-outline')
                    else 'fill'
                ),
            }
            for char_code, dart_name in sorted(git_template.items())
        },
    }


def main():
    parser = argparse.ArgumentParser(
        description='Generate Eva Icons Flutter code from a TTF font',
    )
    parser.add_argument(
        '--font-path',
        default='../lib/fonts/Eva-Icons.ttf',
        help='Path to the Eva Icons TTF file',
    )
    parser.add_argument(
        '--output-dir',
        default='../lib/src',
        help='Directory for generated Dart files',
    )
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(script_dir, args.font_path)
    output_dir = os.path.join(script_dir, args.output_dir)
    dart_output_path = os.path.join(output_dir, 'eva_icons_flutter.dart')
    json_output_path = os.path.join(script_dir, 'eva_icons_mappings.json')

    print('Step 1: Extracting git template...')
    git_template = extract_git_template()
    print(f'Found {len(git_template)} icons in git template')

    print('Step 2: Extracting font mappings...')
    font_mappings = extract_font_mappings(font_path)
    print(f'Found {len(font_mappings)} mappings in font')

    missing_in_font = sorted(set(git_template) - set(font_mappings))
    if missing_in_font:
        missing_icons = ', '.join(
            f'U+{code_point:04X} ({git_template[code_point]})'
            for code_point in missing_in_font[:5]
        )
        raise RuntimeError(f'Icons missing from font: {missing_icons}')

    dart_content = generate_dart_content(git_template)
    json_metadata = generate_json_metadata(git_template, font_mappings)

    os.makedirs(output_dir, exist_ok=True)
    with open(dart_output_path, 'w', encoding='utf-8') as dart_file:
        dart_file.write(dart_content)
    with open(json_output_path, 'w', encoding='utf-8') as json_file:
        json.dump(json_metadata, json_file, indent=2, ensure_ascii=False)
        json_file.write('\n')

    print(f'Generated Dart file: {dart_output_path}')
    print(f'Generated JSON file: {json_output_path}')


if __name__ == '__main__':
    main()

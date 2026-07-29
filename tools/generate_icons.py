#!/usr/bin/env python3
"""Generate Eva Icons Flutter sources from the bundled font."""

import argparse
import json
import logging
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

from fontTools.ttLib import TTFont


EVA_ICONS_UNICODE_START = 0xEA00
EVA_ICONS_UNICODE_END = 0xEBFF
FONT_PACKAGE = 'eva_icons_flutter'
FONT_FAMILY = 'EvaIcons'

ICON_PATTERN = re.compile(
    r'static const IconData\s+(\w+)\s*=\s*'
    r'(?:EvaIconData|IconData)\(\s*0x([a-fA-F0-9]+)'
)

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class IconMapping:
    """A public Dart icon and its corresponding font glyph."""

    dart_name: str
    glyph_name: str
    code_point: int
    icon_type: str

    @property
    def search_key(self) -> str:
        """Convert the Dart name to the Eva Icons documentation key."""
        name = (
            self.dart_name[:-7]
            if self.dart_name.endswith('Outline')
            else self.dart_name
        )
        return re.sub(r'(?<!^)(?=[A-Z])', '-', name).lower()

    @property
    def display_name(self) -> str:
        """Return the human-readable icon name."""
        suffix = ' Outline' if self.icon_type == 'outline' else ''
        return self.search_key.replace('-', ' ').title() + suffix


def extract_git_template() -> Dict[int, str]:
    """Extract the public icon names and code points from git HEAD."""
    result = subprocess.run(
        ['git', 'show', 'HEAD:lib/src/eva_icons_flutter.dart'],
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        raise RuntimeError(f'Error reading git file: {result.stderr.strip()}')

    matches = ICON_PATTERN.findall(result.stdout)
    if not matches:
        raise RuntimeError(
            'No icon definitions found; refusing to overwrite the Dart library.'
        )

    return {
        int(hex_code, 16): dart_name
        for dart_name, hex_code in matches
    }


def extract_font_mappings(font_path: Path) -> Dict[int, str]:
    """Extract the Eva Icons Unicode mappings from the font."""
    font = TTFont(font_path)
    mappings = {}

    for cmap in font['cmap'].tables:
        if cmap.isUnicode():
            for code_point, glyph_name in cmap.cmap.items():
                if EVA_ICONS_UNICODE_START <= code_point <= EVA_ICONS_UNICODE_END:
                    mappings[code_point] = glyph_name

    return mappings


def determine_icon_type(dart_name: str, glyph_name: str) -> str:
    """Determine whether an icon is filled or outlined."""
    if dart_name.endswith('Outline') or glyph_name.endswith('-outline'):
        return 'outline'
    return 'fill'


def build_icon_mappings(
    git_template: Dict[int, str],
    font_mappings: Dict[int, str],
) -> List[IconMapping]:
    """Combine public Dart names with font glyph metadata."""
    missing = sorted(set(git_template) - set(font_mappings))
    if missing:
        missing_icons = ', '.join(
            f'U+{code_point:04X} ({git_template[code_point]})'
            for code_point in missing[:5]
        )
        raise RuntimeError(f'Icons missing from font: {missing_icons}')

    return [
        IconMapping(
            dart_name=dart_name,
            glyph_name=font_mappings[code_point],
            code_point=code_point,
            icon_type=determine_icon_type(
                dart_name,
                font_mappings[code_point],
            ),
        )
        for code_point, dart_name in sorted(git_template.items())
    ]


def generate_icon_constant(mapping: IconMapping) -> str:
    """Generate a single Dart IconData constant."""
    return f'''  /// {mapping.display_name} icon
  ///
  /// https://akveo.github.io/eva-icons/#/?type={mapping.icon_type}&searchKey={mapping.search_key}
  static const IconData {mapping.dart_name} = IconData(
    0x{mapping.code_point:04x},
    fontFamily: '{FONT_FAMILY}',
    fontPackage: '{FONT_PACKAGE}',
  );'''


def generate_dart_content(mappings: List[IconMapping]) -> str:
    """Generate the Dart source for the public icon constants."""
    constants = '\n\n'.join(generate_icon_constant(item) for item in mappings)
    header = '''import 'package:flutter/widgets.dart';

/// Icons based on Eva Icons
///
/// https://akveo.github.io/eva-icons/#/
class EvaIcons {'''

    return f'{header}\n{constants}\n}}\n'


def generate_json_metadata(mappings: List[IconMapping]) -> dict:
    """Generate JSON metadata for the public icon constants."""
    return {
        'font_family': FONT_FAMILY,
        'font_package': FONT_PACKAGE,
        'total_icons': len(mappings),
        'unicode_range': {
            'start': f'0x{mappings[0].code_point:04x}',
            'end': f'0x{mappings[-1].code_point:04x}',
        },
        'mappings': {
            mapping.dart_name: {
                'glyph_name': mapping.glyph_name,
                'unicode': f'0x{mapping.code_point:04x}',
                'decimal': mapping.code_point,
                'type': mapping.icon_type,
            }
            for mapping in mappings
        },
    }


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
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
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Enable verbose output',
    )
    return parser.parse_args()


def main() -> int:
    """Generate the Dart library and JSON metadata."""
    args = parse_args()
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    script_dir = Path(__file__).parent.resolve()
    font_path = (script_dir / args.font_path).resolve()
    output_dir = (script_dir / args.output_dir).resolve()

    if not font_path.exists():
        logger.error('Font file not found: %s', font_path)
        return 1

    try:
        git_template = extract_git_template()
        logger.info('Found %d icons in git template', len(git_template))

        font_mappings = extract_font_mappings(font_path)
        logger.info('Found %d mappings in font', len(font_mappings))

        mappings = build_icon_mappings(git_template, font_mappings)
        dart_content = generate_dart_content(mappings)
        json_metadata = generate_json_metadata(mappings)
    except (OSError, RuntimeError) as error:
        logger.error('%s', error)
        return 1

    output_dir.mkdir(parents=True, exist_ok=True)
    dart_output_path = output_dir / 'eva_icons_flutter.dart'
    json_output_path = script_dir / 'eva_icons_mappings.json'

    dart_output_path.write_text(dart_content, encoding='utf-8')
    json_output_path.write_text(
        json.dumps(json_metadata, indent=2, ensure_ascii=False) + '\n',
        encoding='utf-8',
    )

    logger.info('Generated Dart file: %s', dart_output_path)
    logger.info('Generated JSON file: %s', json_output_path)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

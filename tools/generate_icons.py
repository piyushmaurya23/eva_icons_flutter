#!/usr/bin/env python3
"""
Icon generation tool for Eva Icons Flutter.

This script extracts font metadata from TTF files and generates Dart code
with IconData constants for the Eva Icons Flutter package.
"""

import argparse
import json
import logging
import re
import subprocess
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Tuple

from fontTools.ttLib import TTFont


# Constants
EVA_ICONS_UNICODE_START = 0xEA00
EVA_ICONS_UNICODE_END = 0xEBFF
FONT_PACKAGE = "eva_icons_flutter"
FONT_FAMILY = "EvaIcons"


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class IconMapping:
    """Represents a single icon mapping."""
    dart_name: str
    glyph_name: str
    unicode: int
    icon_type: str
    
    @property
    def unicode_hex(self) -> str:
        """Return unicode as hex string."""
        return f"0x{self.unicode:04x}"
    
    @property
    def unicode_decimal(self) -> int:
        """Return unicode as decimal."""
        return self.unicode
    
    @property
    def search_key(self) -> str:
        """Convert camelCase Dart name to kebab-case search key."""
        # Remove 'Outline' suffix for outline icons
        name = self.dart_name[:-7] if self.dart_name.endswith('Outline') else self.dart_name
        # Convert camelCase to kebab-case
        return re.sub(r'([A-Z])', r'-\1', name).lower().lstrip('-')
    
    @property
    def display_name(self) -> str:
        """Generate human-readable display name."""
        return self.search_key.replace('-', ' ').title() + (
            ' Outline' if self.icon_type == 'outline' else ''
        )


def extract_git_template() -> Dict[int, str]:
    """Extract all icon definitions from git HEAD to use as template.
    
    Returns:
        Dictionary mapping unicode code points to Dart variable names.
    """
    result = subprocess.run(
        ['git', 'show', 'HEAD:lib/src/eva_icons_flutter.dart'],
        capture_output=True,
        text=True,
        check=False
    )
    
    if result.returncode != 0:
        logger.error(f"Error reading git file: {result.stderr}")
        return {}
    
    # Find all static const IconData definitions
    pattern = r'static const IconData (\w+) = EvaIconData\(0x([a-fA-F0-9]+)\);'
    matches = re.findall(pattern, result.stdout)
    
    return {
        int(hex_code, 16): dart_name
        for dart_name, hex_code in matches
    }


def extract_font_mappings(font_path: Path) -> Dict[int, str]:
    """Extract all Unicode mappings from font file.
    
    Args:
        font_path: Path to the TTF font file.
        
    Returns:
        Dictionary mapping unicode code points to glyph names.
    """
    font = TTFont(font_path)
    mappings = {}
    
    for cmap in font['cmap'].tables:
        if cmap.isUnicode():
            for char_code, glyph_name in cmap.cmap.items():
                if EVA_ICONS_UNICODE_START <= char_code <= EVA_ICONS_UNICODE_END:
                    mappings[char_code] = glyph_name
    
    return mappings


def determine_icon_type(dart_name: str, glyph_name: str) -> str:
    """Determine icon type based on Dart and glyph names.
    
    Args:
        dart_name: The Dart variable name.
        glyph_name: The glyph name from the font.
        
    Returns:
        'outline' or 'fill' based on the icon type.
    """
    # Priority: Dart name ending with 'Outline' indicates outline type
    if dart_name.endswith('Outline'):
        return 'outline'
    # Fallback: Check glyph name for '-outline' suffix
    if glyph_name.endswith('-outline'):
        return 'outline'
    return 'fill'


def generate_icon_constant(mapping: IconMapping) -> str:
    """Generate a single Dart IconData constant.
    
    Args:
        mapping: The IconMapping to convert.
        
    Returns:
        Dart code string for the constant.
    """
    return (
        f"  /// {mapping.display_name} icon\n"
        f"  ///\n"
        f"  /// https://akveo.github.io/eva-icons/#/?type={mapping.icon_type}&searchKey={mapping.search_key}\n"
        f"  static const IconData {mapping.dart_name} = EvaIconData(0x{mapping.unicode:04x});"
    )


def generate_dart_file(
    git_template: Dict[int, str],
    font_mappings: Dict[int, str],
    output_path: Path
) -> bool:
    """Generate Dart file using git template for exact match.
    
    Args:
        git_template: Dictionary mapping unicode to Dart names from git.
        font_mappings: Dictionary mapping unicode to glyph names from font.
        output_path: Path to write the generated Dart file.
        
    Returns:
        True if generation succeeded, False otherwise.
    """
    # Generate all icon constants using list comprehension
    constants = [
        generate_icon_constant(IconMapping(
            dart_name=dart_name,
            glyph_name=font_mappings.get(unicode_val, 'unknown'),
            unicode=unicode_val,
            icon_type=determine_icon_type(
                dart_name,
                font_mappings.get(unicode_val, '')
            )
        ))
        for unicode_val, dart_name in sorted(git_template.items())
    ]
    
    # Build complete file content
    content = f'''import 'package:flutter/widgets.dart';
import 'icon_data.dart';

/// Icons based on Eva Icons
///
/// https://akveo.github.io/eva-icons/#/
class EvaIcons {{

{constants}
}}'''
    
    try:
        output_path.write_text(content, encoding='utf-8')
        logger.info(f"Generated Dart file: {output_path}")
        logger.info(f"Total icons generated: {len(constants)}")
        return True
    except Exception as e:
        logger.error(f"Error writing Dart file {output_path}: {e}")
        return False


def generate_json_metadata(
    git_template: Dict[int, str],
    font_mappings: Dict[int, str],
    output_path: Path
) -> None:
    """Generate JSON metadata file for reference.
    
    Args:
        git_template: Dictionary mapping unicode to Dart names.
        font_mappings: Dictionary mapping unicode to glyph names.
        output_path: Path to write the JSON file.
    """
    metadata = {
        "font_family": FONT_FAMILY,
        "font_package": FONT_PACKAGE,
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
                "type": determine_icon_type(dart_name, font_mappings.get(char_code, ''))
            }
            for char_code, dart_name in sorted(git_template.items())
        }
    }
    
    try:
        output_path.write_text(
            json.dumps(metadata, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )
        logger.info(f"Generated JSON metadata: {output_path}")
    except Exception as e:
        logger.error(f"Error writing JSON file {output_path}: {e}")


def check_coverage(
    git_template: Dict[int, str],
    font_mappings: Dict[int, str]
) -> bool:
    """Check if all git icons are present in the font.
    
    Args:
        git_template: Dictionary mapping unicode to Dart names from git.
        font_mappings: Dictionary mapping unicode to glyph names from font.
        
    Returns:
        True if all icons are covered, False otherwise.
    """
    missing = [
        (char_code, git_template[char_code])
        for char_code in git_template.keys()
        if char_code not in font_mappings
    ]
    
    if missing:
        logger.warning(f"{len(missing)} icons from git not found in font:")
        for char_code, dart_name in missing[:5]:
            logger.warning(f"  U+{char_code:04X}: {dart_name}")
        return False
    else:
        logger.info("✓ All git icons found in font")
        return True


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Generate Eva Icons Flutter code from TTF font'
    )
    parser.add_argument(
        '--font-path',
        default='../lib/fonts/Eva-Icons.ttf',
        help='Path to the Eva Icons TTF file'
    )
    parser.add_argument(
        '--output-dir',
        default='../lib/src',
        help='Output directory for generated files'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    return parser.parse_args()


def main() -> int:
    """Main entry point.
    
    Returns:
        Exit code (0 for success, 1 for failure).
    """
    args = parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Resolve paths relative to script location
    script_dir = Path(__file__).parent.resolve()
    font_path = script_dir / args.font_path
    output_dir = script_dir / args.output_dir
    
    # Validate inputs
    if not font_path.exists():
        logger.error(f"Font file not found: {font_path}")
        return 1
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    dart_output_path = output_dir / 'eva_icons_flutter.dart'
    json_output_path = script_dir / 'eva_icons_mappings.json'
    
    logger.info("Step 1: Extracting git template...")
    git_template = extract_git_template()
    logger.info(f"Found {len(git_template)} icons in git template")
    
    logger.info("Step 2: Extracting font mappings...")
    font_mappings = extract_font_mappings(font_path)
    logger.info(f"Found {len(font_mappings)} mappings in font")
    
    logger.info("Step 3: Checking coverage...")
    check_coverage(git_template, font_mappings)
    
    logger.info("Step 4: Generating Dart file...")
    success = generate_dart_file(git_template, font_mappings, dart_output_path)
    
    logger.info("Step 5: Generating JSON metadata...")
    generate_json_metadata(git_template, font_mappings, json_output_path)
    
    if success:
        logger.info("✓ Generation completed successfully!")
        logger.info("The generated file should now match the original exactly.")
        return 0
    else:
        logger.error("✗ Generation failed")
        return 1


if __name__ == "__main__":
    exit(main())

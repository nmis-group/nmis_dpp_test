"""
eclass_build_mapping.py

Utility to parse an ECLASS 16.0 XML delivery (ASSET + UnitsML)
and generate a generic mapping file `config/eclass_mapping.yml`
for use by the nmis_dpp schema mappers.

What it does:
- Scans all ECLASS16_0_ASSET_EN_SG_*.xml files under:
    ../nmis_dpp/ontology_data/eclass_16/ECLASS16_0_Dictionary_ASSET_XML_EN
- Parses:
    * ECLASS classes (class code + preferred name)
    * Properties (IRDI, preferred name, unit reference)
    * Class–property relationships (which properties belong to which class)
- Scans the UnitsML file:
    ../nmis_dpp/ontology_data/eclass_16/ECLASS16_0_UnitsML_EN/ECLASS16_0_UnitsML_EN.xml
  to resolve unit names and symbols.
- Produces a fully generic `part_class_mapping`:
    one entry per ECLASS class code, with all its properties and units.

What it does NOT do:
- It does not decide which ECLASS class corresponds to which domain
  part class in part_class.py; that binding is left to your mapping
  logic or a higher-level config.
"""

from __future__ import annotations

from pathlib import Path
import xml.etree.ElementTree as ET
from typing import Dict, Any, Tuple

import yaml

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

# This file sits in nmis_dpp/, so base is that directory.
BASE = Path(__file__).parent.resolve()

# Root of the ECLASS 16.0 ontology data (relative to nmis_dpp/)
ECLASS_ROOT = (BASE / "../nmis_dpp/ontology_data/eclass_16").resolve()

ASSET_DIR = ECLASS_ROOT / "ECLASS16_0_Dictionary_ASSET_XML_EN"
UNITS_DIR = ECLASS_ROOT / "ECLASS16_0_UnitsML_EN"
UNITS_FILE = UNITS_DIR / "ECLASS16_0_UnitsML_EN.xml"

# Output mapping target
OUT = BASE / "config" / "eclass_mapping.yml"


# ---------------------------------------------------------------------------
# XML helper: namespace-agnostic tag matching
# ---------------------------------------------------------------------------

def _findall_any_ns(elem: ET.Element, local_name: str):
    """
    Find all descendants of `elem` whose local tag name equals `local_name`,
    ignoring XML namespaces.

    Example:
        _findall_any_ns(root, "Unit") will match
        {http://www.unitsml.org/UnitsML/1.0}Unit and similar.
    """
    pattern = f".//{{*}}{local_name}"
    return elem.findall(pattern)


def _findtext_any_ns(elem: ET.Element, local_name: str) -> str:
    """
    Find the first descendant of `elem` with local tag name `local_name`
    (ignoring namespaces) and return its text, or empty string if not found.
    """
    found = _findall_any_ns(elem, local_name)
    if not found:
        return ""
    return (found[0].text or "").strip()


# ---------------------------------------------------------------------------
# 1) Load units from UnitsML
# ---------------------------------------------------------------------------

def load_units() -> Dict[str, Dict[str, Any]]:
    """
    Parse the UnitsML XML file and build a dictionary of units.

    Returns:
        Dict[str, Dict[str, Any]]:
            {
                unit_id_or_symbol: {
                    "name": <unit name>,
                    "symbol": <unit symbol>,
                },
                ...
            }

    Notes:
        - The key is usually the @id attribute of the Unit element.
          If missing, we fall back to the unit symbol as key.
        - You may extend this with dimensions, conversion factors, etc.
    """
    units: Dict[str, Dict[str, Any]] = {}

    if not UNITS_FILE.exists():
        raise FileNotFoundError(f"UnitsML file not found at: {UNITS_FILE}")

    tree = ET.parse(UNITS_FILE)
    root = tree.getroot()

    for u in _findall_any_ns(root, "Unit"):
        uid = (u.get("id") or "").strip()
        name = _findtext_any_ns(u, "UnitName")
        symbol = _findtext_any_ns(u, "UnitSymbol")

        # Fallback key if no id
        key = uid or symbol
        if not key:
            # Skip if we cannot identify the unit
            continue

        units[key] = {
            "name": name or None,
            "symbol": symbol or None,
        }

    return units


# ---------------------------------------------------------------------------
# 2) Collect properties and classes from all SG_xx ASSET files
# ---------------------------------------------------------------------------

def load_properties_and_classes() -> Tuple[
    Dict[str, Dict[str, Any]],  # classes
    Dict[str, Dict[str, Any]],  # props
]:
    """
    Parse all ECLASS ASSET SG_*.xml files to collect:

    - Properties:
        {
          IRDI: {
            "name": <preferred name or short text>,
            "unit_ref": <reference to unit key, if provided>,
          }
        }

    - Classes:
        {
          class_code: {
            "name": <class preferred name>,
            "properties": [IRDI1, IRDI2, ...]
          }
        }

    This function is intentionally schema-agnostic and attempts to use
    common ECLASS element names. You may need to refine the tag names
    if your delivery profile differs.
    """
    props: Dict[str, Dict[str, Any]] = {}
    classes: Dict[str, Dict[str, Any]] = {}

    if not ASSET_DIR.exists():
        raise FileNotFoundError(f"ASSET directory not found at: {ASSET_DIR}")

    for xml_path in sorted(ASSET_DIR.glob("ECLASS16_0_ASSET_EN_SG_*.xml")):
        tree = ET.parse(xml_path)
        root = tree.getroot()

        # --- Properties ---
        # Many ECLASS deliveries use something like "PROPERTIES" / "PROPERTY".
        # Here we look generically for any element named "PROPERTY".
        for p in _findall_any_ns(root, "PROPERTY"):
            irdi = _findtext_any_ns(p, "IRDI")
            if not irdi:
                continue

            name = _findtext_any_ns(p, "PreferredName") or _findtext_any_ns(p, "ShortName")
            unit_ref = _findtext_any_ns(p, "Unit")

            entry = props.setdefault(irdi, {})
            if name:
                entry["name"] = name
            if unit_ref:
                entry["unit_ref"] = unit_ref

        # --- Classes ---
        # Many ECLASS deliveries have "CLASS" or "ClassificationClass".
        for c in _findall_any_ns(root, "CLASS"):
            class_code = _findtext_any_ns(c, "ClassificationClassCode")
            if not class_code:
                # Try alternative tag names if necessary
                class_code = _findtext_any_ns(c, "ClassCode")
            if not class_code:
                continue

            cname = _findtext_any_ns(c, "PreferredName") or _findtext_any_ns(c, "ShortName")
            class_entry = classes.setdefault(class_code, {"name": cname, "properties": []})
            if cname:
                class_entry["name"] = cname

            # Look for direct property links under this class, if available.
            # Some profiles have "ClassPropertyLink" or similar.
            for link in _findall_any_ns(c, "ClassPropertyLink"):
                p_irdi = _findtext_any_ns(link, "PropertyIRDI")
                if p_irdi:
                    class_entry["properties"].append(p_irdi)

        # Note: In some ECLASS profiles, class–property links are in
        # separate elements (e.g. "ClassificationClassPropertyAssignment").
        # If you find such a pattern in your SG XMLs, add another pass here
        # to associate class_code and property IRDIs accordingly.

    return classes, props


# ---------------------------------------------------------------------------
# 3) Build generic part_class_mapping: one entry per ECLASS class
# ---------------------------------------------------------------------------

def build_part_class_mapping(
    classes: Dict[str, Dict[str, Any]],
    props: Dict[str, Dict[str, Any]],
    units: Dict[str, Dict[str, Any]],
) -> Dict[str, Dict[str, Any]]:
    """
    Build a generic mapping structure with one entry per ECLASS class.

    Returns:
        {
          <class_code>: {
            "eclass_code": <class_code>,
            "eclass_name": <class_name>,
            "properties": {
              <irdi>: {
                "irdi": <irdi>,
                "name": <property_name>,
                "unit": <unit_symbol_or_name or None>,
                "unit_ref": <raw unit reference from ECLASS, if any>
              },
              ...
            },
          },
          ...
        }

    This structure matches the shape expected by your mappers, and can
    later be "bound" to domain part classes (Actuator, Sensor, etc.)
    either via config or at runtime.
    """
    mapping: Dict[str, Dict[str, Any]] = {}

    for class_code, cinfo in classes.items():
        class_name = cinfo.get("name", "")
        prop_entries: Dict[str, Dict[str, Any]] = {}

        for irdi in cinfo.get("properties", []):
            p = props.get(irdi, {})
            if not p:
                continue

            unit_ref = p.get("unit_ref")
            unit_info = units.get(unit_ref, {}) if unit_ref else {}

            prop_entries[irdi] = {
                "irdi": irdi,
                "name": p.get("name"),
                "unit": unit_info.get("symbol") or unit_info.get("name"),
                "unit_ref": unit_ref,
            }

        mapping[class_code] = {
            "eclass_code": class_code,
            "eclass_name": class_name,
            "properties": prop_entries,
        }

    return mapping


# ---------------------------------------------------------------------------
# 4) Layer mapping (generic stubs)
# ---------------------------------------------------------------------------

def build_layer_mapping() -> Dict[str, Dict[str, Any]]:
    """
    Build a generic layer_mapping structure.

    This can be refined later, but we provide reasonable defaults
    that are meaningful for JSON-LD and ECLASS-based DPP export.
    """
    return {
        "identity": {
            # How to represent global identifiers (IRDI, serials, etc.)
            "global_ids": "schema:identifier",
            "make_model": "schema:Product",
        },
        "structure": {
            # Hierarchical product/asset structure.
            "hierarchy": "eclass:ProductStructure",
            "parts": "eclass:Component",
        },
        "lifecycle": {
            # You can refine these keys as you define lifecycle semantics.
        },
        "risk": {},
        "sustainability": {},
        "provenance": {},
    }


# ---------------------------------------------------------------------------
# 5) JSON-LD context
# ---------------------------------------------------------------------------

def build_jsonld_context() -> Dict[str, Any]:
    """
    Build a minimal JSON-LD @context for ECLASS-based data.

    You can extend this with QUDT, OM, or other ontologies as needed.
    """
    return {
        "@context": {
            "eclass": "http://www.eclass.eu/",
            "schema": "http://schema.org/",
            "identifier": "schema:identifier",
            "component": "eclass:Component",
            "productStructure": "eclass:ProductStructure",
        }
    }


# ---------------------------------------------------------------------------
# 6) Main entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """
    Main script entry point.

    - Loads UnitsML definitions for units.
    - Loads all ECLASS classes and properties from SG_*.xml ASSET files.
    - Builds a generic part_class_mapping with one entry per ECLASS class.
    - Builds generic layer_mapping and JSON-LD context.
    - Writes everything to config/eclass_mapping.yml.

    Run via:
        python -m nmis_dpp.eclass_build_mapping
    """
    if not ASSET_DIR.exists():
        raise FileNotFoundError(f"ASSET_DIR not found: {ASSET_DIR}")
    if not UNITS_FILE.exists():
        raise FileNotFoundError(f"UNITS_FILE not found: {UNITS_FILE}")

    print(f"Loading units from: {UNITS_FILE}")
    units = load_units()
    print(f"Loaded {len(units)} units")

    print(f"Loading classes and properties from: {ASSET_DIR}")
    classes, props = load_properties_and_classes()
    print(f"Loaded {len(classes)} classes and {len(props)} properties")

    print("Building generic part_class_mapping...")
    part_map = build_part_class_mapping(classes, props, units)
    print(f"Built mapping for {len(part_map)} ECLASS classes")

    layer_map = build_layer_mapping()
    ctx = build_jsonld_context()

    data = {
        "schema_info": {
            "version": "16.0",
            "description": "Auto-generated ECLASS 16.0 mapping for DPP (generic, class-based)",
        },
        "part_class_mapping": part_map,
        "layer_mapping": layer_map,
        "jsonld_context": ctx,
    }

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
    print(f"Wrote mapping to {OUT}")


if __name__ == "__main__":
    main()

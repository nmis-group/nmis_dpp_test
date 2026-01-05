"""
eclass_build_mapping.py

Parses ECLASS XML files from ./eclass_16/ and generates a YAML mapping that connects
your domain PartClass types to ECLASS classes and their allowable item types.

Output format:

part_class_mapping:
PowerConversion:
eclass_class_ids: ["0173-101-AGW606007", ...] # ECLASS categorization classes
eclass_case_item_ids: ["0173-1---ASSET1101-XYZ", ...] # ITEMCLASSCASEOFType ids
properties: {...} # ECLASS properties → PartClass field mappings
Sensor:
eclass_class_ids: [...]
...

Author: Anmol Kumar, NMIS
"""

import os
import glob
import yaml
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import asdict
from part_class import PartClass, OntologyBinding

# eclass_build_mapping.py lives in nmis_dpp/, so go into ontology_data/eclass_16/dictionary_assets_en
ECLASS_DIR = Path(__file__).resolve().parent / "ontology_data" / "eclass_16" / "dictionary_assets_en"
OUTPUT_YAML = "eclass_part_class_mapping.yaml"

# Domain class to ECLASS mapping (extend as needed)
DOMAIN_TO_ECLASS = {
    "PowerConversion": ["0173-101-AGW606007"],  # Power supply units, converters
    "EnergyStorage": ["0173-101-AGW608007"],     # Batteries, capacitors
    "Actuator": ["0173-101-ABX123"],             # Motors, valves, servos
    "Sensor": ["0173-101-ABC456"],               # Sensors (temperature, pressure, etc.)
    "ControlUnit": ["0173-101-AGW610007"],       # ECUs, controllers
    "UserInterface": ["0173-101-AGW612007"],     # HMIs, displays
    "Thermal": ["0173-101-AGW614007"],           # Heaters, coolers, fans
    "Fluidics": ["0173-101-AGW616007"],          # Pumps, valves, tanks
    "Structural": ["0173-101-AAA001001"],        # Frames, housings
    "Transmission": ["0173-101-ABZ789"],         # Gears, bearings
    "Protection": ["0173-101-AGW618007"],        # Fuses, breakers
    "Connectivity": ["0173-101-AGW620007"],      # Connectors, cables
    "SoftwareModule": ["0173-101-AGW622007"],    # Firmware, software
    "Consumable": ["0173-101-AGW624007"],        # Filters, lubricants
    "Fastener": ["0173-101-AAA634023"],          # Screws, bolts
}


def parse_eclass_xml(xml_files: List[Path]) -> Dict[str, Any]:
    """
    Parse all ECLASS XML files and extract:
    - All CATEGORIZATIONCLASSType → id, preferredname, definition
    - All ITEMCLASSCASEOFType → id, iscaseof classrefs
    """
    classes_by_id = {}
    case_of_mapping = {}  # class_id → list of item class ids

    for xml_file in xml_files:
        tree = ET.parse(xml_file)
        root = tree.getroot()

        # Parse CATEGORIZATIONCLASSType (application classes)
        for class_elem in root.findall(".//{http://www.eclass.eu/ontology}CATEGORIZATIONCLASSType"):
            class_id = class_elem.get("id")
            if not class_id:
                continue

            preferred_name_elem = class_elem.find(".//{http://www.eclass.eu/ontology}preferredname")
            name = preferred_name_elem.get("label", f"ECLASS Class {class_id}") if preferred_name_elem is not None else class_id

            classes_by_id[class_id] = {
                "id": class_id,
                "name": name,
                "type": "CATEGORIZATION",
            }

        # Parse ITEMCLASSCASEOFType (concrete item classes)
        for item_elem in root.findall(".//{http://www.eclass.eu/ontology}ITEMCLASSCASEOFType"):
            item_id = item_elem.get("id")
            if not item_id:
                continue

            # Extract iscaseof relationships
            case_of_refs = []
            for iscaseof_elem in item_elem.findall(".//{http://www.eclass.eu/ontology}iscaseof"):
                class_ref = iscaseof_elem.find(".//{http://www.eclass.eu/ontology}classref")
                if class_ref is not None:
                    case_of_refs.append(class_ref.get("ref"))

            if case_of_refs:
                classes_by_id[item_id] = {
                    "id": item_id,
                    "name": f"Item Class {item_id}",
                    "type": "ITEM",
                    "case_of": case_of_refs,
                }

                # Build reverse mapping: class → list of item classes
                for class_ref in case_of_refs:
                    if class_ref not in case_of_mapping:
                        case_of_mapping[class_ref] = []
                    case_of_mapping[class_ref].append(item_id)

    return classes_by_id, case_of_mapping


def build_domain_mapping(classes_by_id: Dict[str, Any], case_of_mapping: Dict[str, List[str]]) -> Dict[str, Any]:
    """
    Map your domain PartClass types to ECLASS classes and their allowable items.
    """
    part_class_mapping = {}

    for domain_class, eclass_class_ids in DOMAIN_TO_ECLASS.items():
        mapping = {
            "domain_class": domain_class,
            "eclass_class_ids": [],
            "eclass_case_item_ids": [],
            "eclass_classes": {},
        }

        # Find all case items for these ECLASS classes
        all_case_items = set()
        for class_id in eclass_class_ids:
            if class_id in case_of_mapping:
                all_case_items.update(case_of_mapping[class_id])
            if class_id in classes_by_id:
                mapping["eclass_classes"][class_id] = classes_by_id[class_id]

        mapping["eclass_class_ids"] = eclass_class_ids
        mapping["eclass_case_item_ids"] = list(all_case_items)

        part_class_mapping[domain_class] = mapping

    return part_class_mapping


def generate_part_class_bindings(mapping: Dict[str, Any]) -> List[PartClass]:
    """
    Generate example PartClass instances with ECLASS bindings populated.
    """
    examples = []

    for domain_class_name, eclass_mapping in mapping.items():
        # Create a sample instance of the domain class
        part = PartClass(
            part_id=f"{domain_class_name.lower()}-example-001",
            name=f"Example {domain_class_name}",
            type=domain_class_name,
            properties={"example": True},
        )

        # Bind ECLASS ontology
        part.bind_ontology(
            ontology_name="ECLASS",
            class_ids=eclass_mapping["eclass_class_ids"],
            case_item_ids=eclass_mapping["eclass_case_item_ids"],
            metadata={
                "version": "16.0",
                "total_items": len(eclass_mapping["eclass_case_item_ids"]),
                "classes": eclass_mapping["eclass_classes"],
            },
        )

        examples.append(part)

    return examples


def main():
    """Main entrypoint: parse ECLASS → generate mapping → save YAML."""
    print("🔍 Scanning ECLASS XML files...")
    xml_files = list(glob.glob(str(ECLASS_DIR / "*.xml")))
    if not xml_files:
        print(f"❌ No XML files found in {ECLASS_DIR}")
        return

    print(f"📖 Parsing {len(xml_files)} ECLASS files...")
    classes_by_id, case_of_mapping = parse_eclass_xml([Path(f) for f in xml_files])

    print("🏗️  Building domain mappings...")
    part_class_mapping = build_domain_mapping(classes_by_id, case_of_mapping)

    print("💾 Saving mapping to YAML...")
    with open(OUTPUT_YAML, "w") as f:
        yaml.dump({
            "eclass_version": "16.0",
            "total_classes": len(classes_by_id),
            "domain_mappings": part_class_mapping,
        }, f, default_flow_style=False, sort_keys=False)

    print(f"✅ Mapping saved: {OUTPUT_YAML}")

    # Generate example bindings
    examples = generate_part_class_bindings(part_class_mapping)
    print("\n📋 Example usage:")
    for part in examples[:3]:  # Show first 3
        print(f"  {part.type}: {len(part.allowed_item_types('ECLASS'))} ECLASS item types")
        print(f"    class_ids: {part.get_binding('ECLASS').class_ids[:2]}...")


if __name__ == "__main__":
    main()

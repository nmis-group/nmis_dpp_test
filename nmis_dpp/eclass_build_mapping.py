"""
eclass_build_mapping.py

Parses ECLASS XML files from ./ontology_data/eclass_16/dictionary_assets_en and generates
a YAML mapping that connects your domain PartClass types to ECLASS classes and their
allowable item types, using definition-based keyword matching only.

Author: Anmol Kumar, NMIS
"""

import glob
import yaml
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Any, Tuple
from part_class import PartClass

# eclass_build_mapping.py lives in nmis_dpp/, so go into ontology_data/eclass_16/dictionary_assets_en
ECLASS_DIR = (
    Path(__file__).resolve().parent
    / "ontology_data"
    / "eclass_16"
    / "dictionary_assets_en"
)
OUTPUT_YAML = "eclass_part_class_mapping.yaml"

# Namespace map for these ECLASS files
NS = {
    "dic": "urn:eclass:xml-schema:dictionary:5.0",
    "ontoml": "urn:iso:std:iso:is:13584:-32:ed-1:tech:xml-schema:ontoml",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
}

# Domain-level keyword heuristics (applied to definition text)
DOMAIN_KEYWORDS: Dict[str, List[str]] = {
    "PowerConversion": ["power supply", "converter", "inverter", "voltage", "current"],
    "EnergyStorage": ["battery", "accumulator", "storage", "cell", "energy storage"],
    "Actuator": ["actuator", "drive", "servo", "motion", "positioning"],
    "Sensor": ["sensor", "measurement", "measuring", "detector", "transducer"],
    "ControlUnit": ["controller", "control unit", "logic", "regulator", "control system"],
    "UserInterface": ["user interface", "display", "panel", "operator", "hmi"],
    "Thermal": ["heating", "cooling", "thermal", "temperature control", "heat"],
    "Fluidics": ["fluid", "hydraulic", "pneumatic", "valve", "pump"],
    "Structural": ["structural", "frame", "housing", "support", "chassis"],
    "Transmission": ["gear", "transmission", "drive train", "shaft", "coupling"],
    "Protection": ["protection", "protective", "safety", "fuse", "breaker"],
    "Connectivity": ["connector", "connection", "interface", "plug", "socket", "cable"],
    "SoftwareModule": ["software", "module", "firmware", "program", "logic"],
    "Consumable": ["consumable", "supply", "material", "lubricant", "filter"],
    "Fastener": ["screw", "bolt", "fastener", "nut", "washer"],
}


def extract_definition_text(class_elem: ET.Element) -> str:
    """Extract a single text string from <definition><text>…</text></definition>."""
    parts: List[str] = []
    for def_elem in class_elem.findall("./definition"):
        for text_elem in def_elem.findall("./text"):
            if text_elem.text:
                parts.append(text_elem.text.strip())
    return " ".join(parts)


def parse_eclass_xml(
    xml_files: List[Path],
) -> Tuple[Dict[str, Any], Dict[str, List[str]]]:
    """
    Parse all ECLASS XML files into:
      - classes_by_id: {id: {id, name, type, definition, case_of?}}
      - case_of_mapping: {base_class_id: [item_class_ids]}
    """
    classes_by_id: Dict[str, Any] = {}
    case_of_mapping: Dict[str, List[str]] = {}

    for xml_file in xml_files:
        tree = ET.parse(xml_file)
        root = tree.getroot()

        for class_elem in root.findall(".//ontoml:class", NS):
            class_id = class_elem.get("id")
            if not class_id:
                continue

            xsi_type = class_elem.get(f"{{{NS['xsi']}}}type", "")

            pref = class_elem.find("./preferred_name/label")
            name = (
                pref.text.strip()
                if pref is not None and pref.text
                else f"ECLASS Class {class_id}"
            )

            definition_text = extract_definition_text(class_elem)

            if xsi_type.endswith("CATEGORIZATION_CLASS_Type"):
                classes_by_id[class_id] = {
                    "id": class_id,
                    "name": name,
                    "type": "CATEGORIZATION",
                    "definition": definition_text,
                }

            elif xsi_type.endswith("ITEM_CLASS_CASE_OF_Type"):
                case_refs: List[str] = []
                for ic in class_elem.findall("./is_case_of"):
                    ref = ic.get("class_ref")
                    if ref:
                        case_refs.append(ref)

                classes_by_id[class_id] = {
                    "id": class_id,
                    "name": name,
                    "type": "ITEM",
                    "definition": definition_text,
                    "case_of": case_refs,
                }

                for ref in case_refs:
                    case_of_mapping.setdefault(ref, []).append(class_id)

    return classes_by_id, case_of_mapping


def matches_domain(definition: str, domain: str) -> bool:
    """Return True if the definition text seems to belong to the given domain."""
    text = (definition or "").lower()
    for kw in DOMAIN_KEYWORDS.get(domain, []):
        if kw in text:
            return True
    return False


def build_domain_mapping(
    classes_by_id: Dict[str, Any], case_of_mapping: Dict[str, List[str]]
) -> Dict[str, Any]:
    """
    Map domain PartClass types to ECLASS classes and their allowable items,
    using definition-based keyword matching only (no external IDs).
    """
    part_class_mapping: Dict[str, Any] = {}

    for domain_class in DOMAIN_KEYWORDS.keys():
        mapping = {
            "domain_class": domain_class,
            "eclass_class_ids": [],       # kept for schema compatibility, but unused
            "eclass_case_item_ids": [],
            "eclass_classes": {},
        }

        # 1) categorization classes selected purely by definition keywords
        for class_id, cls in classes_by_id.items():
            if cls.get("type") != "CATEGORIZATION":
                continue
            if matches_domain(cls.get("definition", ""), domain_class):
                mapping["eclass_classes"][class_id] = cls

        # 2) include item classes whose base class is in the selected set
        selected_base_ids = set(mapping["eclass_classes"].keys())
        all_case_items = set()
        for base_id in selected_base_ids:
            for item_id in case_of_mapping.get(base_id, []):
                all_case_items.add(item_id)

        mapping["eclass_case_item_ids"] = sorted(all_case_items)
        part_class_mapping[domain_class] = mapping

    return part_class_mapping


def generate_part_class_bindings(mapping: Dict[str, Any]) -> List[PartClass]:
    """
    Generate example PartClass instances with ECLASS bindings populated.
    class_ids is left empty because selection is semantic, not ID-driven.
    """
    examples: List[PartClass] = []

    for domain_class_name, eclass_mapping in mapping.items():
        part = PartClass(
            part_id=f"{domain_class_name.lower()}-example-001",
            name=f"Example {domain_class_name}",
            type=domain_class_name,
            properties={"example": True},
        )

        part.bind_ontology(
            ontology_name="ECLASS",
            class_ids=[],  # no explicit IDs; see metadata["classes"]
            case_item_ids=eclass_mapping["eclass_case_item_ids"],
            metadata={
                "version": "16.0",
                "total_items": len(eclass_mapping["eclass_case_item_ids"]),
                "classes": eclass_mapping["eclass_classes"],
            },
        )

        examples.append(part)

    return examples


def main() -> None:
    """Main entrypoint: parse ECLASS → generate mapping → save YAML."""
    print("🔍 Scanning ECLASS XML files...")
    xml_files = list((ECLASS_DIR).glob("*.xml"))
    if not xml_files:
        print(f"❌ No XML files found in {ECLASS_DIR}")
        return

    print(f"📖 Parsing {len(xml_files)} ECLASS files...")
    classes_by_id, case_of_mapping = parse_eclass_xml(xml_files)

    print("🏗️  Building domain mappings (definition-based)...")
    part_class_mapping = build_domain_mapping(classes_by_id, case_of_mapping)

    print("💾 Saving mapping to YAML...")
    with open(OUTPUT_YAML, "w") as f:
        yaml.dump(
            {
                "eclass_version": "16.0",
                "total_classes": len(classes_by_id),
                "domain_mappings": part_class_mapping,
            },
            f,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True,
        )

    print(f"✅ Mapping saved: {OUTPUT_YAML}")

    examples = generate_part_class_bindings(part_class_mapping)
    print("\n📋 Example usage:")
    for part in examples[:3]:
        binding = part.get_binding("ECLASS")
        print(f"  {part.type}: {len(binding.case_item_ids)} ECLASS item types")
        print(f"    example item_ids: {binding.case_item_ids[:3]}...")


if __name__ == "__main__":
    main()

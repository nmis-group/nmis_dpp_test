# Digital Product Passport

A modular Python package that enables manufacturing companies to create interoperable Digital Product Passports (DPPs) by mapping their existing business data to standardized DPP data models using automated semantic matching and intuitive configuration tools.

---
## Package Layout

```text
__nmis_dpp_test/__
├── __nmis_dpp/__
│   ├── __ontology_data/__ 
│   │   ├── __eclass_16/__ 
│   │   │   ├── __dictionary_assets_en/__ 
│   │   │   │   ├── `ECLASS16_0_ASSET_EN_SG_13.xml`
│   │   │   │   ├── ...     
│   │   │   │   └── `ECLASS16_0_ASSET_EN_SG_90.xml`
│   │   │   ├── __unitsml_en/__ 
│   │   │   │   └── `ECLASS16_0_UNITSML_EN.xml` 
│   │   │   └── `ECLASS_ASSET_XML_Read_Me_EN_v1.pdf` 
│   │   └── `README.md` 
│   ├── `__init__.py` 
│   ├── `eclass_build_mapping.py` # ECLASS build mapping 
│   ├── `model.py`         # Core models for DPP layers 
│   ├── `part_class.py`    # Universal part class set 
│   ├── `schema_base.py`   # Base schema for DPP layers 
│   ├── `schema_registry.py` # Schema registry 
│   └── `utils.py`         # Any helper functions 
├── __tests/__ 
│   ├── `test_model.py` 
│   ├── `test_part_class.py` 
│   ├── `test_schema_registry.py` 
│   └── `test_schema_registry_second.py` 
├── `pyproject.toml`  
├── `LICENSE.txt` 
└── `README.md` 
```
---

## Requirements
- Python 3.7+
- No external dependencies (uses Python dataclasses and standard library)

---

## Installation
### From PyPI
```shell
pip install nmis_dpp_test
```
### From Source
```shell
git clone https://github.com/nmis-group/nmis_dpp_test.git
cd nmis_dpp_test  
pip install .
```  


---

## Usage Example

We have created a simple python file to showcase the usage.
After installation run the file:

```shell
cd nmis_dpp_test
python3 usage.py
```

__usage.py__ ¬

```python
# Example usage for the nmis_dpp Digital Product Passport package

from nmis_dpp.model import (
    IdentityLayer, StructureLayer, LifecycleLayer, RiskLayer,
    SustainabilityLayer, ProvenanceLayer, DigitalProductPassport
)
from nmis_dpp.part_class import (
    Actuator, Sensor, PowerConversion
)
from nmis_dpp.utils import to_dict, to_json

# 1. Define parts using reusable part classes
motor = Actuator(
    part_id="A001",
    name="Drive Motor",
    type="Actuator",
    torque=2.1,
    speed=1750,
    duty_cycle=0.7,
    voltage=48,
    actuation_type="electric"
)
temperature_sensor = Sensor(
    part_id="S003",
    name="Temp Sensor",
    type="Sensor",
    sensor_type="temperature",
    range_min=-40,
    range_max=120,
    accuracy=0.25,
    drift=0.01,
    response_time=7
)
psu = PowerConversion(
    part_id="P001",
    name="PSU",
    type="PowerConversion",
    input_voltage=230,
    output_voltage=48,
    power_rating=350,
    efficiency=0.92
)

# 2. Build each passport layer
identity = IdentityLayer(
    global_ids={"gtin": "987654321", "serial": "SN1245"},
    make_model={"brand": "Acme", "model": "UnitX", "hw_rev": "A", "fw_rev": "2.0"},
    ownership={"manufacturer": "Acme Ltd", "owner": "BuyerOrg", "operator": "MaintainerX", "location": "Berlin"},
    conformity=["CE", "RoHS", "UKCA"]
)
structure = StructureLayer(
    hierarchy={
        "product": "UnitX",
        "components": [motor, temperature_sensor, psu]
    },
    parts=[motor, temperature_sensor, psu],
    interfaces=[
        {"type": "electrical", "details": {"voltage": 48, "connector": "XT60"}},
        {"type": "data", "details": {"protocol": "CAN"}}
    ],
    materials=[{"cas": "7439-89-6", "%mass": 70, "recyclable": "yes"}],
    bom_refs=["XWZ-002"]
)
lifecycle = LifecycleLayer(
    manufacture={"lot": "Batch77", "factory": "ACMEPlant", "date": "2025-03-18", "process": "injection", "co2e": 27.3},
    use={"counters": {"hours": 143}, "telemetry": {}},
    serviceability={"schedule": {"interval": "1Y"}, "repair_steps": ["Open housing", "Replace motor"], "repairability_score": 6},
    events=[{"event_type": "install", "timestamp": "2025-04-01"}],
    end_of_life={"disassembly": ["Unplug connectors"], "hazards": ["None"], "recovery_routes": ["Recycle", "Landfill"]}
)
risk = RiskLayer(
    criticality={"levels": "Safety", "llp": False, "mtbf": 20000},
    fmea=[{"failure_mode": "overheat", "effect": "shutdown", "mitigation": "cooling upgrade"}],
    security={"sbom": "link", "vulnerabilities": [], "signing_keys": ["pubkey-xyz"], "update_policy": "signed-only"}
)
sustainability = SustainabilityLayer(
    mass=5.0,
    energy={"standby": 2.0, "active": 15.0, "water_use": 0.0},
    recycled_content={"pcr_percent": 39, "bio": 2},
    remanufacture={"eligible": True, "grading_criteria": {"condition": "A"}},
)
provenance = ProvenanceLayer(
    signatures=[{"type": "manufacturer", "certificate": "certABC"}],
    trace_links=["EPCIS:event1", "NFC:TAG773"]
)

# 3. Create the product passport
passport = DigitalProductPassport(
    identity=identity,
    structure=structure,
    lifecycle=lifecycle,
    risk=risk,
    sustainability=sustainability,
    provenance=provenance
)

# 4. Serialize to dict and JSON for export or storage
passport_dict = to_dict(passport)
passport_json = to_json(passport, indent=2)

# Display or use the data
print("--- Digital Product Passport Object ---")
print(passport)
print("\n--- As Dictionary ---")
print(passport_dict)
print("\n--- As JSON ---")
print(passport_json)

```
---

## Quick Start Steps
1. Install with `pip` or from source.
2. Import model layers and part classes.
3. Create instances and assemble your passport.

---

## License
Distributed under the MIT License. See `LICENSE.txt` for details.

---



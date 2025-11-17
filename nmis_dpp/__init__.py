"""
dpp_passport package initializer.

This module exposes key Digital Product Passport layers and universal part classes
for easy import, along with serialization utilities.
"""

from .model import (
    IdentityLayer, StructureLayer, LifecycleLayer, RiskLayer,
    SustainabilityLayer, ProvenanceLayer, DigitalProductPassport
)
from .part_class import (
    PartClass, PowerConversion, EnergyStorage, Actuator, Sensor,
    ControlUnit, UserInterface, Thermal, Fluidics, Structural,
    Transmission, Protection, Connectivity, SoftwareModule,
    Consumable, Fastener
)
from .utils import to_dict, to_json, validate_part_class

__all__ = [
    # Layers
    "IdentityLayer", "StructureLayer", "LifecycleLayer", "RiskLayer",
    "SustainabilityLayer", "ProvenanceLayer", "DigitalProductPassport",
    # Part classes
    "PartClass", "PowerConversion", "EnergyStorage", "Actuator", "Sensor",
    "ControlUnit", "UserInterface", "Thermal", "Fluidics", "Structural",
    "Transmission", "Protection", "Connectivity", "SoftwareModule",
    "Consumable", "Fastener",
    # Utils
    "to_dict", "to_json", "validate_part_class"
]


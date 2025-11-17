"""
part_class.py

Defines universal, domain-neutral part classes for the Digital Product Passport system.
Each class lists standard, strongly-typed properties for that category, supporting broad product modeling and traceability.

Author: Anmol Kumar, NMIS
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict


@dataclass
class PartClass:
    """
    Base class for all part types.
    
    Attributes:
        part_id (str): Unique identifier for the part instance.
        name (str): Descriptive name of the part.
        type (str): The category of the part (e.g., 'Sensor', 'Actuator').
        properties (dict): Additional, flexible typed properties.
    """
    part_id: str
    name: str
    type: str
    properties: Dict[str, any] = field(default_factory=dict)


@dataclass
class PowerConversion(PartClass):
    """
    Represents power conversion devices (e.g., PSUs, inverters, alternators).
    
    Attributes:
        input_voltage (Optional[float]): Nominal input voltage in volts.
        output_voltage (Optional[float]): Nominal output voltage in volts.
        power_rating (Optional[float]): Max continuous output power in watts.
        efficiency (Optional[float]): Efficiency as a fraction (0-1).
    """
    input_voltage: Optional[float] = None
    output_voltage: Optional[float] = None
    power_rating: Optional[float] = None
    efficiency: Optional[float] = None


@dataclass
class EnergyStorage(PartClass):
    """
    Represents energy storage devices (e.g., batteries, capacitors).
    
    Attributes:
        capacity (Optional[float]): Storage capacity in Wh (batteries) or F (capacitors).
        voltage (Optional[float]): Nominal voltage in volts.
        chemistry (Optional[str]): Type of chemistry or dielectric.
        recharge_cycles (Optional[int]): Typical number of recharge cycles supported.
    """
    capacity: Optional[float] = None
    voltage: Optional[float] = None
    chemistry: Optional[str] = None
    recharge_cycles: Optional[int] = None


@dataclass
class Actuator(PartClass):
    """
    Represents actuators (e.g., motors, valves, servos).
    
    Attributes:
        torque (Optional[float]): Max torque in Nm.
        speed (Optional[float]): Max speed in rpm.
        duty_cycle (Optional[float]): Recommended duty cycle (% or 0-1).
        voltage (Optional[float]): Operating voltage in volts.
        actuation_type (Optional[str]): Type of actuation (electric, hydraulic, etc.).
    """
    torque: Optional[float] = None
    speed: Optional[float] = None
    duty_cycle: Optional[float] = None
    voltage: Optional[float] = None
    actuation_type: Optional[str] = None


@dataclass
class Sensor(PartClass):
    """
    Represents sensors (e.g., temperature, pressure, flow, vibration, IMU).
    
    Attributes:
        sensor_type (Optional[str]): Type of sensor (e.g., temperature, IMU).
        range_min (Optional[float]): Minimum measurable value.
        range_max (Optional[float]): Maximum measurable value.
        accuracy (Optional[float]): Sensor accuracy (% or units).
        drift (Optional[float]): Expected measurement drift per time.
        response_time (Optional[float]): Response time in ms.
    """
    sensor_type: Optional[str] = None
    range_min: Optional[float] = None
    range_max: Optional[float] = None
    accuracy: Optional[float] = None
    drift: Optional[float] = None
    response_time: Optional[float] = None


@dataclass
class ControlUnit(PartClass):
    """
    Represents control units (e.g., ECU, MCU boards, FADEC).
    
    Attributes:
        cpu_type (Optional[str]): Core or processor type.
        memory (Optional[float]): RAM size in MB.
        firmware_version (Optional[str]): Installed firmware version.
        io_count (Optional[int]): Number of input/output channels.
    """
    cpu_type: Optional[str] = None
    memory: Optional[float] = None
    firmware_version: Optional[str] = None
    io_count: Optional[int] = None


@dataclass
class UserInterface(PartClass):
    """
    Represents user interface devices (e.g., HMI, buttons, touchscreens, indicators).
    
    Attributes:
        ui_type (Optional[str]): UI type (touchscreen, button panel, etc.).
        display_size (Optional[float]): Size of display (inches, if applicable).
        input_methods (Optional[List[str]]): Supported input methods.
        indicator_count (Optional[int]): Number of indicators/LEDs.
    """
    ui_type: Optional[str] = None
    display_size: Optional[float] = None
    input_methods: Optional[List[str]] = None
    indicator_count: Optional[int] = None


@dataclass
class Thermal(PartClass):
    """
    Represents thermal devices (e.g., heaters, exchangers, fans).
    
    Attributes:
        power (Optional[float]): Power in watts.
        delta_t (Optional[float]): Max temperature difference managed.
        airflow (Optional[float]): Max airflow in CFM or L/min.
    """
    power: Optional[float] = None
    delta_t: Optional[float] = None
    airflow: Optional[float] = None


@dataclass
class Fluidics(PartClass):
    """
    Represents fluidic devices (e.g., pumps, tanks, lines, filters).
    
    Attributes:
        flow_rate (Optional[float]): Max flow rate (L/min or similar).
        pressure (Optional[float]): Max pressure (bar, psi).
        fluid_type (Optional[str]): Compatible fluids.
        volume (Optional[float]): Internal volume (for tanks) in L.
    """
    flow_rate: Optional[float] = None
    pressure: Optional[float] = None
    fluid_type: Optional[str] = None
    volume: Optional[float] = None


@dataclass
class Structural(PartClass):
    """
    Represents structural elements (e.g., housings, frames, blades, disks).
    
    Attributes:
        material (Optional[str]): Primary material.
        mass (Optional[float]): Component mass (kg).
        dimensions (Optional[Dict[str, float]]): Dict of named dimensions.
        load_rating (Optional[float]): Max load or stress (N or MPa).
    """
    material: Optional[str] = None
    mass: Optional[float] = None
    dimensions: Optional[Dict[str, float]] = None
    load_rating: Optional[float] = None


@dataclass
class Transmission(PartClass):
    """
    Represents transmission components (e.g., gears, bearings, belts, shafts).
    
    Attributes:
        torque_rating (Optional[float]): Max torque supported (Nm).
        speed_rating (Optional[float]): Max speed supported (rpm).
        transmission_type (Optional[str]): E.g., gear, belt, shaft.
    """
    torque_rating: Optional[float] = None
    speed_rating: Optional[float] = None
    transmission_type: Optional[str] = None


@dataclass
class Protection(PartClass):
    """
    Represents protection devices (e.g., fuses, breakers, EMI/RFI filters).
    
    Attributes:
        protection_type (Optional[str]): Type (fuse, breaker, filter).
        rating (Optional[float]): Protection rating (A, V, Hz).
        response_time (Optional[float]): Trip/response time (ms).
    """
    protection_type: Optional[str] = None
    rating: Optional[float] = None
    response_time: Optional[float] = None


@dataclass
class Connectivity(PartClass):
    """
    Represents connectivity components (e.g., harnesses, connectors, buses).
    
    Attributes:
        interface_type (Optional[str]): Data, power, or fluid interface type.
        connector_standard (Optional[str]): Reference standard (e.g., USB, Ethernet).
        pin_count (Optional[int]): Number of electrical pins/connections.
    """
    interface_type: Optional[str] = None
    connector_standard: Optional[str] = None
    pin_count: Optional[int] = None


@dataclass
class SoftwareModule(PartClass):
    """
    Represents software elements (e.g., firmware, control laws, DSP blocks).
    
    Attributes:
        version (Optional[str]): Module version.
        language (Optional[str]): Implementation language.
        license (Optional[str]): License identifier.
        checksums (Optional[Dict[str, str]]): Dict of checksums/hash values by algo.
    """
    version: Optional[str] = None
    language: Optional[str] = None
    license: Optional[str] = None
    checksums: Optional[Dict[str, str]] = None


@dataclass
class Consumable(PartClass):
    """
    Represents consumable elements (e.g., filters, seals, oils, coffee beans).

    Attributes:
        consumable_type (Optional[str]): Consumable product type.
        capacity (Optional[float]): Capacity or quantity (L, g, etc.).
        replacement_interval (Optional[str]): Suggested replacement interval.
    """
    consumable_type: Optional[str] = None
    capacity: Optional[float] = None
    replacement_interval: Optional[str] = None


@dataclass
class Fastener(PartClass):
    """
    Represents fastening elements (e.g., screws, rivets, adhesives).

    Attributes:
        fastener_type (Optional[str]): Kind (screw, bolt, adhesive).
        material (Optional[str]): Material of fastener.
        diameter (Optional[float]): Diameter (mm).
        length (Optional[float]): Length (mm).
        strength (Optional[float]): Tensile/shear strength (N or MPa).
    """
    fastener_type: Optional[str] = None
    material: Optional[str] = None
    diameter: Optional[float] = None
    length: Optional[float] = None
    strength: Optional[float] = None


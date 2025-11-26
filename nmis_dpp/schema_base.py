"""
schema_base.py

Abstract base class for all schema mappers. 
All schema (ECLASS, ISA-95 etc.) mappers must inherit from SchemaMapper and implement the required methods.

This design enables plug-in architecture for different schemas;
new schemas can be added without modifying the core logic.
    
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import asdict
import logging

from nmis_dpp.model import DigitalProductPassport, IdentityLayer, StructureLayer, LifecycleLayer, RiskLayer, SustainabilityLayer, ProvenanceLayer
from nmis_dpp.part_class import PartClass

logger = logging.getLogger(__name__)


class SchemaMapper(ABC):
    """
    Abstract base class for mapping Digital Product Passport (DPP) objects to various ontologies/standards.
    
    Subclasses must implement:
    - get_schema_name(): Return the name of the schema (e.g., "ECLASS", "ISA-95").
    - get_schema_version(): Return the version/release of the schema being mapped to.
    - map_identity_layer(): Convert IdentityLayer to schema-specific format.
    - map_structure_layer(): Convert StructureLayer to schema-specific format.
    - map_lifecycle_layer(): Convert LifecycleLayer to schema-specific format.
    - map_risk_layer(): Convert RiskLayer to schema-specific format.
    - map_sustainability_layer(): Convert SustainabilityLayer to schema-specific format.
    - map_provenance_layer(): Convert ProvenanceLayer to schema-specific format.
    - validate_mapping(): Ensure mapped data conforms to schema constraints.
    - get_context(): Return JSON-LD @context for the mapped schema.
    """
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the mapper with optional configuration.
        
        Args:
            config (Optional[Dict[str, Any]]): Configuration dictionary, e.g., loaded from YAML.
        """
        self.config = config or {}
        logger.info(f"Initialized {self.get_schema_name()} mapper.")
    
    @abstractmethod
    def get_schema_name(self) -> str:
        """
        Return the name of the schema this mapper targets.
        
        Returns:
            str: Schema name (e.g., "ECLASS", "ISA-95").
        """
        pass

    @abstractmethod
    def get_schema_version(self) -> str:
        """
        Return the version/release of the schema.
        
        Returns:
            str: Schema version (e.g., "12.0", "2.0.0").
        """
        pass
    
    @abstractmethod
    def map_identity_layer(self, layer: IdentityLayer) -> Dict[str, Any]:
        """
        Map IdentityLayer to schema-specific representation.
        
        Args:
            layer (IdentityLayer): The identity layer from DPP.
        
        Returns:
            Dict[str, Any]: Schema-compliant identity data.
        """
        pass

    @abstractmethod
    def map_structure_layer(self, layer: StructureLayer) -> Dict[str, Any]:
        """
        Map StructureLayer to schema-specific representation.
        
        Args:
            layer (StructureLayer): The structure layer from DPP.
        
        Returns:
            Dict[str, Any]: Schema-compliant structure data.
        """
        pass
    
    @abstractmethod
    def map_lifecycle_layer(self, layer: 'LifecycleLayer') -> Dict[str, Any]:
        """
        Map LifecycleLayer to schema-specific representation.
        
        Args:
            layer (LifecycleLayer): The lifecycle layer from DPP.
        
        Returns:
            Dict[str, Any]: Schema-compliant lifecycle data.
        """
        pass

    @abstractmethod
    def map_risk_layer(self, layer: 'RiskLayer') -> Dict[str, Any]:
        """
        Map RiskLayer to schema-specific representation.
        
        Args:
            layer (RiskLayer): The risk layer from DPP.
        
        Returns:
            Dict[str, Any]: Schema-compliant risk data.
        """
        pass
    
    @abstractmethod
    def map_sustainability_layer(self, layer: 'SustainabilityLayer') -> Dict[str, Any]:
        """
        Map SustainabilityLayer to schema-specific representation.
        
        Args:
            layer (SustainabilityLayer): The sustainability layer from DPP.
        
        Returns:
            Dict[str, Any]: Schema-compliant sustainability data.
        """
        pass

    @abstractmethod
    def map_provenance_layer(self, layer: 'ProvenanceLayer') -> Dict[str, Any]:
        """
        Map ProvenanceLayer to schema-specific representation.
        
        Args:
            layer (ProvenanceLayer): The provenance layer from DPP.
        
        Returns:
            Dict[str, Any]: Schema-compliant provenance data.
        """
        pass
    
    @abstractmethod
    def validate_mapping(self, mapped_data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate that mapped data conforms to schema requirements and constraints.
        
        Args:
            mapped_data (Dict[str, Any]): The mapped data to validate.
        
        Returns:
            tuple[bool, List[str]]: (is_valid, list_of_error_messages).
                If valid, returns (True, []).
                If invalid, returns (False, ["error1", "error2", ...]).
        """
        pass

    @abstractmethod
    def get_context(self) -> Dict[str, Any]:
        """
        Return JSON-LD @context for this schema.
        
        Returns:
            Dict[str, Any]: JSON-LD context mapping terms to IRIs/URIs.
                Example: {"@context": "https://schema.org/", ...}
        """
        pass
    
    def map_dpp(self, dpp: DigitalProductPassport) -> Dict[str, Any]:
        """
        Map an entire DigitalProductPassport to this schema.
        
        This is the main entry point. It calls all layer-specific mappers
        and aggregates the result.
        
        Args:
            dpp (DigitalProductPassport): The DPP object to map.
        
        Returns:
            Dict[str, Any]: Complete schema-compliant representation.
        
        Raises:
            ValueError: If mapping or validation fails.
        """
        try:
            logger.info(f"Starting mapping to {self.get_schema_name()}...")
            
            mapped = {
                "schema": self.get_schema_name(),
                "schema_version": self.get_schema_version(),
                "@context": self.get_context(),
                "identity": self.map_identity_layer(dpp.identity),
                "structure": self.map_structure_layer(dpp.structure),
                "lifecycle": self.map_lifecycle_layer(dpp.lifecycle),
                "risk": self.map_risk_layer(dpp.risk),
                "sustainability": self.map_sustainability_layer(dpp.sustainability),
                "provenance": self.map_provenance_layer(dpp.provenance),
            }
            
            # Validate the mapped data
            is_valid, errors = self.validate_mapping(mapped)
            if not is_valid:
                error_msg = f"Validation failed: {'; '.join(errors)}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            logger.info(f"Successfully mapped DPP to {self.get_schema_name()}.")
            return mapped
        
        except Exception as e:
            logger.error(f"Error during mapping: {str(e)}")
            raise
    
    def map_part_class(self, part: PartClass) -> Dict[str, Any]:
        """
        Map a single PartClass instance to schema-specific representation.
        
        Subclasses can override this to provide custom part mapping logic.
        
        Args:
            part (PartClass): The part to map.
        
        Returns:
            Dict[str, Any]: Schema-compliant part data.
        """
        # Default: return as-is, converted to dict
        return asdict(part)
    
    def get_mapping_config(self, key: str, default: Any = None) -> Any:
        """
        Retrieve a configuration value from the mapper's config.
        
        Useful for accessing schema-specific configuration loaded from YAML/JSON.
        
        Args:
            key (str): Configuration key (e.g., "properties_mapping", "required_fields").
            default (Any): Default value if key not found.
        
        Returns:
            Any: Configuration value or default.
        """
        return self.config.get(key, default)
    
    def __repr__(self) -> str:
        """String representation of the mapper."""
        return f"{self.__class__.__name__}(schema={self.get_schema_name()}, version={self.get_schema_version()})"
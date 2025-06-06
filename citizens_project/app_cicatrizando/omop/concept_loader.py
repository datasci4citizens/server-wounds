"""
Utility module to load and ensure OMOP concept IDs are properly loaded into the database
"""
import inspect
from django.db import transaction
from .omop_models import Concept

def get_all_constants_from_module(module):
    """
    Extract all constant values (uppercase variables) from a module
    
    Args:
        module: The module to extract constants from
    
    Returns:
        A dictionary of constant name -> value pairs
    """
    return {
        name: value for name, value in inspect.getmembers(module)
        if name.startswith('CID_') and isinstance(value, int)
    }

@transaction.atomic
def ensure_concepts_exist(module):
    """
    Ensure all concept IDs defined in a module are present in the database
    
    Args:
        module: The module containing CID_ constants (concept IDs)
    
    Returns:
        A list of created concept IDs
    """
    constants = get_all_constants_from_module(module)
    created_concepts = []
    
    for name, concept_id in constants.items():
        # Format the name from CID_EXAMPLE_NAME to "Example Name"
        concept_name = name[4:].replace('_', ' ').title()
        
        # Skip if concept already exists
        try:
            concept, created = Concept.objects.get_or_create(
                concept_id=concept_id,
                defaults={
                    'concept_name': concept_name,
                }
            )
            
            if created:
                created_concepts.append(concept)
        except Exception as e:
            print(f"Error creating concept {name} with ID {concept_id}: {str(e)}")
    
    return created_concepts

def register_concept(concept_id, concept_name):
    """
    Register a new concept in the database
    
    Args:
        concept_id: Integer ID for the concept
        concept_name: Human-readable name for the concept
    
    Returns:
        The created or existing Concept instance
    """
    try:
        concept, created = Concept.objects.get_or_create(
            concept_id=concept_id,
            defaults={
                'concept_name': concept_name,
            }
        )
        return concept, created
    except Exception as e:
        print(f"Error registering concept {concept_name} with ID {concept_id}: {str(e)}")
        return None, False

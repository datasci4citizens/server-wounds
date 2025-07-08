"""
Módulo utilitário para carregar e garantir que os IDs de conceitos OMOP estejam no banco de dados
Resolve problemas de circularidade entre Domain, Vocabulary, ConceptClass e Concept
"""
import inspect
from django.db import transaction
from django.utils import timezone
from .omop_models import Concept, Domain, Vocabulary, ConceptClass

def get_all_constants_from_module(module):
    """
    Extrai todas as constantes (variáveis em maiúsculas) de um módulo
    
    Args:
        module: O módulo do qual extrair as constantes
    
    Returns:
        Um dicionário de nome da constante -> valor
    """
    return {
        name: value for name, value in inspect.getmembers(module)
        if name.startswith('CID_') and isinstance(value, int)
    }

@transaction.atomic
def ensure_concepts_exist(module):
    """
    Garante que todos os IDs de conceito definidos em um módulo estejam presentes no banco de dados
    Resolve problemas de circularidade criando primeiro as dependências básicas
    
    Args:
        module: O módulo contendo constantes CID_ (IDs de conceito)
    
    Returns:
        Uma lista dos conceitos criados
    """
    # Primeiro, garante que existem registros básicos para resolver circularidade
    _ensure_basic_dependencies()
    
    constants = get_all_constants_from_module(module)
    created_concepts = []
    
    for name, concept_id in constants.items():
        # Formata o nome de CID_EXAMPLE_NAME para "Example Name"
        concept_name = name[4:].replace('_', ' ').title()
        
        # Pula se o conceito já existe
        try:
            concept, created = Concept.objects.get_or_create(
                concept_id=concept_id,
                defaults={
                    'concept_name': concept_name,
                    'domain_id': 'Metadata',  # Usa domain padrão
                    'vocabulary_id': 'None',  # Usa vocabulary padrão  
                    'concept_class_id': 'Undefined',  # Usa concept class padrão
                    'standard_concept': 'S',
                    'concept_code': name,
                    'valid_start_date': timezone.now().date(),
                    'valid_end_date': timezone.now().date(),
                    'invalid_reason': None
                }
            )
            
            if created:
                created_concepts.append(concept)
        except Exception as e:
            print(f"Erro ao criar conceito {name} com ID {concept_id}: {str(e)}")
    
    return created_concepts

def _ensure_basic_dependencies():
    """
    Garante que existem registros básicos nas tabelas de dependência para resolver circularidade
    """
    # Cria Vocabulary básico
    vocab_concept, _ = Concept.objects.get_or_create(
        concept_id=0,
        defaults={
            'concept_name': 'None',
            'domain_id': 'Metadata',
            'vocabulary_id': 'None',
            'concept_class_id': 'Undefined',
            'standard_concept': 'S',
            'concept_code': 'OMOP generated',
            'valid_start_date': timezone.now().date(),
            'valid_end_date': timezone.now().date(),
            'invalid_reason': None
        }
    )
    
    # Cria Vocabulary
    Vocabulary.objects.get_or_create(
        vocabulary_id='None',
        defaults={
            'vocabulary_name': 'OMOP Vocabulary',
            'vocabulary_reference': 'OMOP generated',
            'vocabulary_version': 'v1.0',
            'vocabulary_concept_id': vocab_concept.concept_id
        }
    )
    
    # Cria ConceptClass
    ConceptClass.objects.get_or_create(
        concept_class_id='Undefined',
        defaults={
            'concept_class_name': 'Undefined',
            'concept_class_concept_id': vocab_concept.concept_id
        }
    )
    
    # Cria Domain
    Domain.objects.get_or_create(
        domain_id='Metadata',
        defaults={
            'domain_name': 'Metadata',
            'domain_concept_id': vocab_concept.concept_id
        }
    )

def register_concept(concept_id, concept_name, domain_id='Metadata', vocabulary_id='None', concept_class_id='Undefined'):
    """
    Registra um novo conceito no banco de dados com todas as dependências
    
    Args:
        concept_id: ID inteiro para o conceito
        concept_name: Nome legível para o conceito
        domain_id: ID do domínio (padrão: 'Metadata')
        vocabulary_id: ID do vocabulário (padrão: 'None') 
        concept_class_id: ID da classe do conceito (padrão: 'Undefined')
    
    Returns:
        A instância do Concept criada ou existente
    """
    # Garante que as dependências existem
    _ensure_basic_dependencies()
    
    try:
        concept, created = Concept.objects.get_or_create(
            concept_id=concept_id,
            defaults={
                'concept_name': concept_name,
                'domain_id': domain_id,
                'vocabulary_id': vocabulary_id,
                'concept_class_id': concept_class_id,
                'standard_concept': 'S',
                'concept_code': concept_name.upper().replace(' ', '_'),
                'valid_start_date': timezone.now().date(),
                'valid_end_date': timezone.now().date(),
                'invalid_reason': None
            }
        )
        return concept, created
    except Exception as e:
        print(f"Erro ao registrar conceito {concept_name} com ID {concept_id}: {str(e)}")
        return None, False

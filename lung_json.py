####################################################################################
# Specification of target knowledge graph model. The classes in Python correspond
# to classes in RDF. Hence, the class diagram should follow the graph structure.
#
# The specification object is a dictionary (can be loaded from JSON file) containing
# the rdf:type for every python class, and the URI template. Furthermore, for every
# listed class property, it defines the RDF predicate used and whether it is a
# literal or an object. Optionally, there is a mapping to convert literals, or when
# defined as is_literal = False to convert local strings into URIs.
####################################################################################
from datetime import datetime

specification = {
    'namespaces': {
        'schema': 'http://schema.org/',
        'ex': 'http://example.org/',
        'foaf': 'http://xmlns.com/foaf/0.1/',
        'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
        'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
        'nci': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#',
        'roo': 'http://www.cancerdata.org/roo/'
    },
    'classes': {
        'Patient': {
            'rdf_type': 'nci:C16960',
            'uri_template': 'http://example.org/patient/{id}',
            'properties': {
                'diseases': {
                    'predicate': 'roo:P100008',
                    'is_literal': False
                }
            }
        },
        'Disease': {
            'rdf_type': 'nci:C2926',
            'uri_template': 'http://example.org/patient/{patient|id}/disease',
            'properties': {
                'overall_stage': {
                    'predicate': 'roo:P100025',
                    'is_literal': False
                },
                't_stage': {
                    'predicate': 'roo:P100244',
                    'is_literal': False
                },
                'n_stage': {
                    'predicate': 'roo:P100242',
                    'is_literal': False
                },
                'm_stage': {
                    'predicate': 'roo:P100241',
                    'is_literal': False
                },
                'diagnosis_date': {
                    'predicate': 'roo:P100040',
                    'is_literal': False
                }
            }
        },
        'OverallStage': {
            'rdf_type': 'nci:C28108',
            'uri_template': 'http://example.org/patient/{disease|patient|id}/disease/stage',
            'properties': {
                'stage': {
                    'predicate': 'rdf:type',
                    'is_literal': False,
                    'mapping': {
                        '0': 'nci:C28051',
                        'Occult': 'nci:C141461',
                        'I': 'nci:C27966',
                        'IA': 'nci:C27975',
                        'IA1': 'nci:C27983',
                        'IA2': 'nci:C27984',
                        'IA3': 'nci:C136485',
                        'IB': 'nci:C27976',
                        'II': 'nci:C28054',
                        'IIA': 'nci:C27967',
                        'IIB': 'nci:C27968',
                        'III': 'nci:C27970',
                        'IIIA': 'nci:C27977',
                        'IIIB': 'nci:C27978',
                        'IIIC': 'nci:C27982',
                        'IV': 'nci:C27971',
                        'IVA': 'nci:C27979',
                        'IVB': 'nci:C27980',
                    }
                }
            }
        },
        'TStage': {
            'rdf_type': 'nci:C48885',
            'uri_template': 'http://example.org/patient/{disease|patient|id}/disease/stage/t_stage',
            'properties': {
                'stage': {
                    'predicate': 'rdf:type',
                    'is_literal': False,
                    'mapping': {
                        'T0': 'nci:C48719',
                        'Tis': 'nci:C48738',
                        'T1': 'nci:C48720',
                        'T1a': 'nci:C48721',
                        'T1b': 'nci:C48722',
                        'T1c': 'nci:C48723',
                        'T1mi': 'nci:C95805',
                        'T2': 'nci:C48724',
                        'T2a': 'nci:C48725',
                        'T2b': 'nci:C48726',
                        'T3': 'nci:C48728',
                        'T4': 'nci:C48732',
                        'Tx': 'nci:C48737',
                    }
                }
            }
        },
        'NStage': {
            'rdf_type': 'nci:C48884',
            'uri_template': 'http://example.org/patient/{disease|patient|id}/disease/stage/n_stage',
            'properties': {
                'stage': {
                    'predicate': 'rdf:type',
                    'is_literal': False,
                    'mapping': {
                        'N0': 'nci:C48705',
                        "N1": 'nci:C48706',
                        "N2": 'nci:C48786',
                        "N3": 'nci:C48714',
                        "Nx": 'nci:C48718'
                    }
                }
            }
        },
        'MStage': {
            'rdf_type': 'nci:C48883',
            'uri_template': 'http://example.org/patient/{disease|patient|id}/disease/stage/m_stage',
            'properties': {
                'stage': {
                    'predicate': 'rdf:type',
                    'is_literal': False,
                    'mapping': {
                        'M0': 'nci:C48699',
                        "M1": 'nci:C48700',
                        "M1a": 'nci:C48701',
                        "M1b": 'nci:C48702',
                        "M1c": 'nci:C48703',
                        "Mx": 'nci:C48704'
                    }
                }
            }
        },
        'DiagnosisDate': {
            'rdf_type': 'nci:C25164',
            'uri_template': 'http://example.org/patient/{disease|patient|id}/disease/diagnosis_date',
            'properties': {
                'date': {
                    'predicate': 'roo:P100041',
                    'is_literal': True
                }
            }
        }
    }
}

class Patient:
    def __init__(self, id, diseases = None):
        self.id: int = id
        self.diseases: list['Disease'] = diseases
    
class Disease:
    def __init__(self, patient, overall_stage, t_stage, n_stage, m_stage, diagnosis_date):
        self.overall_stage: OverallStage = overall_stage
        self.t_stage: TStage = t_stage
        self.n_stage: NStage = n_stage
        self.m_stage: MStage = m_stage
        self.diagnosis_date: DiagnosisDate = diagnosis_date
        self.patient: Patient = patient

class OverallStage:
    def __init__(self, disease, stage):
        self.disease: Disease = disease
        self.stage: str = stage

class TStage:
    def __init__(self, disease, stage):
        self.disease: Disease = disease
        self.stage: str = stage

class NStage:
    def __init__(self, disease, stage):
        self.disease: Disease = disease
        self.stage: str = stage

class MStage:
    def __init__(self, disease, stage):
        self.disease: Disease = disease
        self.stage: str = stage

class DiagnosisDate:
    def __init__(self, disease, date):
        self.disease: Disease = disease
        self.date: datetime = date


####################################################################################
# Create instances (which is part of the ETL script, can be made with ChatGPT if you
# know the source and target structure
####################################################################################

# Create disease
disease = Disease(
    patient=None,  # Placeholder, will be set after patient is created
    overall_stage=OverallStage(disease=None, stage="I"),
    t_stage=TStage(disease=None, stage="T1"),
    n_stage=NStage(disease=None, stage="N1"),
    m_stage=MStage(disease=None, stage="M1"),
    diagnosis_date=DiagnosisDate(disease=None, date=datetime.now())
)

# Create a patient
patient = Patient(id=1, diseases=[disease])

# Update disease with the correct patient reference
disease.patient = patient
disease.overall_stage.disease = disease
disease.t_stage.disease = disease
disease.n_stage.disease = disease
disease.m_stage.disease = disease
disease.diagnosis_date.disease = disease

import rdf_serializer
print(rdf_serializer.class_to_rdf(patient, specification).serialize(format="turtle"))
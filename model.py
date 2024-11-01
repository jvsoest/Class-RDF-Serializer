specification = {
    'namespaces': {
        'schema': 'http://schema.org/',
        'ex': 'http://example.org/',
        'foaf': 'http://xmlns.com/foaf/0.1/',
        'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
        'rdfs': 'http://www.w3.org/2000/01/rdf-schema#'
    },
    'classes': {
        'Person': {
            'rdf_type': 'foaf:Person',
            'uri_template': 'ex:person/{id}',
            'properties': {
                'first_name': {
                    'predicate': 'foaf:firstName',
                    'is_literal': True
                },
                'last_name': {
                    'predicate': 'foaf:lastName',
                    'is_literal': True
                },
                'age': {
                    'predicate': 'foaf:age',
                    'is_literal': True
                },
                'knows': {
                    'predicate': 'foaf:knows',
                    'is_literal': False
                },
                'interests': {
                    'predicate': 'foaf:interest',
                    'is_literal': False,
                    'mapping': {
                        'Reading': 'ex:Reading',
                        'Hiking': 'ex:Hiking',
                        'Traveling': 'ex:Traveling',
                        'Photography': 'ex:Photography'
                    }
                },
                'pets': {
                    'predicate': 'schema:owns',
                    'is_literal': False
                }
            }
        },
        'Pet': {
            'rdf_type': 'schema:Pet',
            'uri_template': 'ex:pet/{name}',
            'properties': {
                'name': {
                    'predicate': 'schema:name',
                    'is_literal': True
                },
                'owner': {
                    'predicate': 'schema:owner',
                    'is_literal': False
                }
            }
        }
    }
}

class Person:
    def __init__(self, id, first_name, last_name, age=None, knows=None, interests=None, pets=None):
        self.id: int = id
        self.first_name: str = first_name
        self.last_name: str = last_name
        self.age: int = age
        self.knows: list['Person'] = knows
        self.interests: list['str'] = interests
        self.pets: list['Pet'] = pets
class Pet:
    def __init__(self, name, owner):
        self.name: str = name
        self.owner: Person = owner
from rdf_serializer import rdf_class, rdf_property

# Example mapping from local values to standardized codes
INTEREST_MAPPINGS = {
    "Reading": "http://example.org/interests/reading",
    "Hiking": "http://example.org/interests/hiking",
    "Traveling": "http://example.org/interests/traveling",
    "Photography": "http://example.org/interests/photography"
}

# Example usage of rdf_class and rdf_property decorators
@rdf_class(rdf_type="http://xmlns.com/foaf/0.1/Person", uri_template="http://example.org/person/{id}-{first_name}")
class Person:
    def __init__(self, id, first_name, last_name, age=None, knows=None, interests=None):
        self.id: int = id
        self._first_name: str = first_name
        self._last_name: str = last_name
        self._age: int = age
        self._knows: list['Person'] = knows
        self._interests: list[str] = interests
    
    # Getter
    @rdf_property("http://xmlns.com/foaf/0.1/firstName", is_literal=True)
    def first_name(self) -> str:
        return self._first_name
    
    # Getter
    @rdf_property("http://xmlns.com/foaf/0.1/lastName", is_literal=True)
    def last_name(self) -> str:
        return self._last_name
    
    # Getter
    @rdf_property("http://xmlns.com/foaf/0.1/age", is_literal=True)
    def age(self) -> int:
        return self._age
    
    # Getter
    @rdf_property("http://xmlns.com/foaf/0.1/knows", is_literal=False)
    def knows(self) -> list['Person']:
        return self._knows
    
    # Getter
    @rdf_property("http://xmlns.com/foaf/0.1/interest", is_literal=False)
    def interests(self) -> list[str]:
        # return self._interests
        return [INTEREST_MAPPINGS.get(value, value) for value in self._interests]
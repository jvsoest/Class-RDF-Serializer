import re
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF

# Decorator for classes to define rdf:type and URI template
def rdf_class(rdf_type, uri_template):
    def decorator(cls):
        cls._rdf_type = rdf_type  # Set the rdf:type
        cls._uri_template = uri_template  # Set the URI template
        return cls
    return decorator

# Decorator for attributes to define the RDF predicate and type (literal, object, or list)
def rdf_property(predicate, is_literal=True):
    def decorator(func):
        func._rdf_predicate = predicate  # Store the RDF predicate
        func._is_literal = is_literal  # Store whether it's a literal or object
        return property(func)
    return decorator

# Helper function to recursively fetch property values
def get_property_value(obj, property_chain):
    """Recursively fetch the value of a property chain (e.g., 'knows.id')."""
    properties = property_chain.split('.')
    current_value = obj
    for prop in properties:
        current_value = getattr(current_value, prop, None)
        if current_value is None:
            break
    return current_value

# Dynamic URI generation based on template
def build_uri_from_template(obj, uri_template):
    """Build a URI dynamically based on the object's properties and URI template."""
    pattern = re.compile(r'\{([^\}]+)\}')  # Match placeholders like {property}
    
    def replace_placeholder(match):
        property_chain = match.group(1)
        value = get_property_value(obj, property_chain)
        return str(value) if value else ''  # Convert the property value to a string
    
    # Replace each placeholder with the actual property value
    if uri_template is None:
        uri = obj
    else:
        uri = pattern.sub(replace_placeholder, uri_template)
    return uri

# Object-to-RDF function, updated to handle lists, literals, objects, and dynamic URI templates
def object_to_rdf(obj, base_uri="http://example.org/"):
    # Create an RDF graph
    graph = Graph()

    # Get RDF type and URI template from class metadata
    rdf_type = getattr(obj.__class__, '_rdf_type', None)
    uri_template = getattr(obj.__class__, '_uri_template', None)

    # Build the URI for the object using dynamic template resolution
    obj_uri = URIRef(build_uri_from_template(obj, uri_template))

    # Add RDF type for the object
    if rdf_type:
        graph.add((obj_uri, RDF.type, URIRef(rdf_type)))

    # Iterate over the attributes of the object
    for attr_name in dir(obj):
        attr_value = getattr(obj, attr_name, None)
        attr_method = getattr(obj.__class__, attr_name, None)
        
        attr_method = getattr(attr_method, "fget", None)

        # Check if this attribute has an RDF predicate defined via annotation
        if hasattr(attr_method, '_rdf_predicate') and attr_value is not None:
            predicate = URIRef(attr_method._rdf_predicate)  # RDF predicate from annotation
            
            # Handle cases where the attribute value is a list
            if isinstance(attr_value, list):
                for item in attr_value:
                    if attr_method._is_literal:
                        graph.add((obj_uri, predicate, Literal(item)))
                    else:
                        # Assume the object has an 'id' and a URI template
                        item_uri = URIRef(build_uri_from_template(item, getattr(item.__class__, "_uri_template", None)))
                        graph.add((obj_uri, predicate, item_uri))
                        # Recursively add the referenced object to the graph
                        graph += object_to_rdf(item, base_uri)
            else:
                # Handle literal or object predicates
                if attr_method._is_literal:
                    graph.add((obj_uri, predicate, Literal(attr_value)))
                else:
                    # Assume the object has an 'id' and a URI template
                    obj_ref_uri = URIRef(build_uri_from_template(attr_value, attr_value.__class__._uri_template))
                    graph.add((obj_uri, predicate, obj_ref_uri))
                    # Recursively add the referenced object to the graph
                    graph += object_to_rdf(attr_value, base_uri)

    return graph

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
        self.id = id
        self._first_name = first_name
        self._last_name = last_name
        self._age = age
        self._knows = knows  # This can be another Person instance or a list of Persons
        self._interests = interests  # This can be a list of interests (literal values)
    
    # Getter
    @rdf_property("http://xmlns.com/foaf/0.1/firstName", is_literal=True)
    def first_name(self):
        return self._first_name
    
    # Getter
    @rdf_property("http://xmlns.com/foaf/0.1/lastName", is_literal=True)
    def last_name(self):
        return self._last_name
    
    # Getter
    @rdf_property("http://xmlns.com/foaf/0.1/age", is_literal=True)
    def age(self):
        return self._age
    
    # Getter
    @rdf_property("http://xmlns.com/foaf/0.1/knows", is_literal=False)
    def knows(self):
        return self._knows
    
    # Getter
    @rdf_property("http://xmlns.com/foaf/0.1/interest", is_literal=False)
    def interests(self):
        # return self._interests
        return [INTEREST_MAPPINGS.get(value, value) for value in self._interests]

# Test with Person knowing another Person and having multiple interests
person1 = Person(id="123", first_name="John", last_name="Doe", age=30, interests=["Reading", "Hiking"])
person2 = Person(id="456", first_name="Jane", last_name="Smith", age=28, knows=[person1], interests=["Traveling", "Photography"])

# Convert the objects to RDF
person_rdf = object_to_rdf(person2)

# Serialize to Turtle format for display
print(person_rdf.serialize(format='turtle'))
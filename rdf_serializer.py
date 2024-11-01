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
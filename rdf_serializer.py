import re
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF

def get_nested_attr(obj, attr):
    for part in attr.split('|'):
        obj = getattr(obj, part)
    return obj

def generate_class_instance_uri(uri_template, class_instance, g) -> URIRef:
    """
    This function generates a URI for a class instance based on a URI template.

    Args:
        uri_template: A URI template string.
        class_instance: A Python class object.

    Returns:
        A URIRef object representing the URI of the class instance.
    """
    # uri_template = class_spec['uri_template']
    variables = re.findall(r'\{([\w\|]+)\}', uri_template)
    uri_values = {var: get_nested_attr(class_instance, var) for var in variables}
    class_uri = URIRef_replace_prefix(uri_template.format(**uri_values), g)
    return class_uri

def URIRef_replace_prefix(uri, g) -> str:
    """
    This function replaces the prefixes in a URI with their corresponding namespace.

    Args:
        uri: A URI string.

    Returns:
        A string with the prefixes replaced by their corresponding namespace.
    """
    # replace prefixes with namespaces
    for prefix, namespace in g.namespaces():
        uri = uri.replace(prefix + ":", namespace)
    return URIRef(uri)

def class_to_rdf(class_instance, specification, g=Graph()) -> Graph:
    """
    This function reads the properties of a class instance and converts them to RDF triples.

    Args:
        class_instance: An instance of a class with RDF annotations.

    Returns:
        A Graph object containing the RDF triples.
    """
    # add all namespaces
    for prefix, uri in specification['namespaces'].items():
        g.bind(prefix, URIRef(uri))

    class_name = class_instance.__class__.__name__
    class_spec = specification['classes'][class_name]

    instance_uri = generate_class_instance_uri(class_spec['uri_template'], class_instance, g)

    # Check if the instance already exists in the graph
    if (instance_uri, RDF.type, URIRef_replace_prefix(class_spec['rdf_type'], g)) in g:
        return g
    
    g.add((instance_uri, RDF.type, URIRef_replace_prefix(class_spec['rdf_type'], g)))

    for prop_name, prop_value in class_instance.__dict__.items():
        # skip if variable is None
        if prop_value is None:
            continue

        prop_spec = class_spec['properties'].get(prop_name)
        if prop_spec:
            if prop_spec['is_literal']:
                # attempt mapping, if it fails, use original value
                literal_value = prop_value
                if 'mapping' in prop_spec:
                    literal_value = prop_spec['mapping'].get(literal_value, literal_value)
                
                g.add((instance_uri, URIRef_replace_prefix(prop_spec['predicate'], g), Literal(literal_value)))
            else:
                # if it is a list, iterate over each item
                if isinstance(prop_value, list):
                    for item in prop_value:
                        # if the value is a string, perform mapping
                        if isinstance(item, str):
                            # attempt mapping, if it fails, use original value
                            literal_value = item
                            if 'mapping' in prop_spec:
                                literal_value = prop_spec['mapping'].get(literal_value, literal_value)
                            
                            item_uri = URIRef_replace_prefix(literal_value, g)
                            g.add((instance_uri, URIRef_replace_prefix(prop_spec['predicate'], g), item_uri))
                        else:
                            item_class_spec = specification['classes'][item.__class__.__name__]
                            item_uri = generate_class_instance_uri(item_class_spec['uri_template'], item, g)
                            g.add((instance_uri, URIRef_replace_prefix(prop_spec['predicate'], g), item_uri))
                            g = class_to_rdf(item, specification, g)
                else:
                    if isinstance(prop_value, str):
                        # attempt mapping, if it fails, use original value
                        literal_value = prop_value
                        if 'mapping' in prop_spec:
                            literal_value = prop_spec['mapping'].get(literal_value, literal_value)
                        
                        item_uri = URIRef_replace_prefix(literal_value, g)
                        g.add((instance_uri, URIRef_replace_prefix(prop_spec['predicate'], g), item_uri))
                    else:
                        item_class_spec = specification['classes'][prop_value.__class__.__name__]
                        item_uri = generate_class_instance_uri(item_class_spec['uri_template'], prop_value, g)
                        g.add((instance_uri, URIRef_replace_prefix(prop_spec['predicate'], g), item_uri))
                        g = class_to_rdf(prop_value, specification, g)
    return g
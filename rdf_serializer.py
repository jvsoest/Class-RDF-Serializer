import re
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF

def generate_class_instance_uri(uri_template, class_instance) -> URIRef:
    """
    This function generates a URI for a class instance based on a URI template.

    Args:
        uri_template: A URI template string.
        class_instance: A Python class object.

    Returns:
        A URIRef object representing the URI of the class instance.
    """
    # uri_template = class_spec['uri_template']
    variables = re.findall(r'\{(\w+)\}', uri_template)
    uri_values = {var: getattr(class_instance, var) for var in variables}
    class_uri = URIRef(uri_template.format(**uri_values))
    return class_uri

def class_to_rdf(class_instance, specification, g=Graph()) -> Graph:
    """
    This function reads the properties of a class instance and converts them to RDF triples.

    Args:
        class_instance: An instance of a class with RDF annotations.

    Returns:
        A Graph object containing the RDF triples.
    """
    print("==============================")
    print("class_instance: ", class_instance)
    # add all namespaces
    for prefix, uri in specification['namespaces'].items():
        g.bind(prefix, URIRef(uri))

    class_name = class_instance.__class__.__name__
    class_spec = specification['classes'][class_name]

    instance_uri = generate_class_instance_uri(class_spec['uri_template'], class_instance)

    # Check if the instance already exists in the graph
    if (instance_uri, RDF.type, URIRef(class_spec['rdf_type'])) in g:
        return g
    
    g.add((instance_uri, RDF.type, URIRef(class_spec['rdf_type'])))

    for prop_name, prop_value in class_instance.__dict__.items():
        # skip if variable is None
        if prop_value is None:
            continue

        prop_spec = class_spec['properties'].get(prop_name)
        if prop_spec:
            print("prop_spec: ", prop_spec)
            if prop_spec['is_literal']:
                g.add((instance_uri, URIRef(prop_spec['predicate']), Literal(prop_value)))
            else:
                # if it is a list, iterate over each item
                if isinstance(prop_value, list):
                    for item in prop_value:
                        # if the value is a string, perform mapping
                        if isinstance(item, str):
                            # attempt mapping, if it fails, use original value
                            item_uri = URIRef(prop_spec['mapping'].get(item, item))
                            g.add((instance_uri, URIRef(prop_spec['predicate']), item_uri))
                        else:
                            item_class_spec = specification['classes'][item.__class__.__name__]
                            item_uri = generate_class_instance_uri(item_class_spec['uri_template'], item)
                            g.add((instance_uri, URIRef(prop_spec['predicate']), item_uri))
                            g = class_to_rdf(item, specification, g)
                else:
                    item_class_spec = specification['classes'][prop_value.__class__.__name__]
                    item_uri = generate_class_instance_uri(item_class_spec['uri_template'], prop_value)
                    g.add((instance_uri, URIRef(prop_spec['predicate']), item_uri))
                    g = class_to_rdf(prop_value, specification, g)
    return g
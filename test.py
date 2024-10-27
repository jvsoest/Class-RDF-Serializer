from model import Person
from rdf_serializer import object_to_rdf

# Test with Person knowing another Person and having multiple interests
person1 = Person(id="123", first_name="John", last_name="Doe", age=30, interests=["Reading", "Hiking"])
person2 = Person(id="456", first_name="Jane", last_name="Smith", age=28, knows=[person1], interests=["Traveling", "Photography"])

# Convert the objects to RDF
person_rdf = object_to_rdf(person2)

# Serialize to Turtle format for display
print(person_rdf.serialize(format='turtle'))
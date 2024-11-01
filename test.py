from model import Person, Pet, specification
from rdf_serializer import class_to_rdf

# Test with Person knowing another Person and having multiple interests
person1 = Person(id="123", first_name="John", last_name="Doe", age=30, interests=["Reading", "Hiking"])
person2 = Person(id="456", first_name="Jane", last_name="Smith", age=28, knows=[person1], interests=["Traveling", "Photography"])
pet1 = Pet(name="Fluffy", owner=person2)
person2.pets = [pet1]

# Convert the objects to RDF
person_rdf = class_to_rdf(person2, specification)

# Serialize to Turtle format for display
print(person_rdf.serialize(format='turtle'))
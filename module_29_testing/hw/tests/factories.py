import factory
from faker import Faker
from app.models import Client, Parking

fake = Faker()

class ClientFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Client
        sqlalchemy_session_persistence = 'commit'

    name = factory.LazyAttribute(lambda x: fake.first_name())
    surname = factory.LazyAttribute(lambda x: fake.last_name())
    credit_card = factory.LazyAttribute(lambda x: fake.credit_card_number() if fake.boolean() else None)
    car_number = factory.LazyAttribute(lambda x: fake.bothify(text='??###??'))

class ParkingFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Parking
        sqlalchemy_session_persistence = 'commit'

    address = factory.LazyAttribute(lambda x: fake.address())
    opened = factory.LazyAttribute(lambda x: fake.boolean())
    count_places = factory.LazyAttribute(lambda x: fake.random_int(min=5, max=100))
    count_available_places = factory.LazyAttribute(lambda o: o.count_places)

# coding=utf-8

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from droid_database_setup import Droid, Base, DroidAccessories, User

""" This file contains the python code to create starter users, droids, and
    accessories for the droids for the droid catalog application.
"""

engine = create_engine('sqlite:///droidaccessorieswithusers.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

""" Create dummy users """
User1 = User(name="Dummy User", email="mmidcap@yahoo.com",
             picture="images/Beaker.jpg")
session.add(User1)
session.commit()

User2 = User(name="Dummy User 2", email="mrmidcap@yahoo.com",
             picture="url('/images/KingAir.jpg')")
session.add(User2)
session.commit()

User3 = User(name="Dummy User 3", email="midcapbills@yahoo.com",
             picture="url('/images/sad-puppy.jpg')")
session.add(User3)
session.commit()

""" Add droids """

droid1 = Droid(user_id=1, name="BB-8", droid_type="Astromech")

session.add(droid1)
session.commit()

droid2 = Droid(user_id=2, name="IG-88", droid_type="Battle")

session.add(droid2)
session.commit()

droid3 = Droid(user_id=3, name="C3-PO", droid_type="Protocol")

session.add(droid3)
session.commit()

""" Add droid items/accessories """

droidItem1 = DroidAccessories(
    name="Beeper",
    user_id=1,
    description="Enables droid's lovable beeping",
    accessory_type="Lingual",
    droid=droid1)

session.add(droidItem1)
session.commit()

droidItem2 = DroidAccessories(
    name="Plasma Torch",
    user_id=1,
    description="Epic cutting tool",
    accessory_type="Astromech",
    droid=droid1)

session.add(droidItem2)
session.commit()

droidItem3 = DroidAccessories(
    name="Rifle Blaster",
    user_id=2,
    description="Shoulder mounted blaster",
    accessory_type="Battle",
    droid=droid2)

session.add(droidItem3)
session.commit()

droidItem4 = DroidAccessories(
    name="Galactic Language Translator",
    user_id=3,
    description="Language interpreter, 12M languages",
    accessory_type="Lingual",
    droid=droid3)

session.add(droidItem4)
session.commit()


print "Droids and their accessories have been added!"

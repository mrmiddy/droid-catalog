# coding=utf-8

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))

""" Droid types: Maintenance, Astromech, Protocal, Battle """
class Droid(Base):
    __tablename__ = 'droid'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    droid_type = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    """Return object data in easily serializeable format"""
    @property
    def serialize(self):
       return {
           'name'         : self.name,
           'id'           : self.id,
           'type'         : self.droid_type,
           'creator'      : self.user_id
       }


""" Types: Tool, Weapon, Software, Hardware """
class DroidAccessories(Base):
    __tablename__ = 'droid_item'

    name =Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    accessory_type = Column(String(250))
    description = Column(String(250))
    droid_id = Column(Integer,ForeignKey('droid.id'))
    droid = relationship(Droid)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    """Return object data in easily serializeable format"""
    @property
    def serialize(self):
       return {
            'name'  : self.name,
            'id'    : self.id,
            'description'   : self.description,
            'accessory_type'    : self.accessory_type,
       }


engine = create_engine('sqlite:///droidaccessorieswithusers.db')


Base.metadata.create_all(engine)

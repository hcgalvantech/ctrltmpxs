# src/models.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Alumno(Base):
    __tablename__ = 'alumno'
    id = Column(Integer, primary_key=True)
    dni = Column(Integer, unique=True)
    apenom = Column(String)

class Inscriptos(Base):
    __tablename__ = 'inscriptos'
    id = Column(Integer, primary_key=True)
    iddni = Column(Integer)
    idtectun = Column(Integer)
    regular = Column(String)
    email = Column(String)

class Tecnicatura(Base):
    __tablename__ = 'tecnicatura'
    id = Column(Integer, primary_key=True)
    tectun = Column(String)

class Turnos(Base):
    __tablename__ = 'turnos'
    id = Column(Integer, primary_key=True)
    idtec = Column(Integer)
    idexa = Column(Integer)
    f_desde = Column(DateTime)
    f_hasta = Column(DateTime)
    tiempo = Column(Integer)
    regular = Column(String)

class Examen(Base):
    __tablename__ = 'examen'
    id = Column(Integer, primary_key=True)
    exalink = Column(String)

class Acceso(Base):
    __tablename__ = 'acceso'
    id = Column(Integer, primary_key=True)
    idins = Column(Integer)
    acceso = Column(DateTime)
    hora = Column(DateTime, nullable=True)
    link = Column(String, nullable=True)
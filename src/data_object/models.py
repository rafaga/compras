"""
Provides Abstrtaction layer to Access to Department table
based upon SQLalchemy objects
"""
#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# Autor: Rafael Amador Galván
# Fecha: 11/07/2022
from sqlalchemy import Column,String,Integer, Boolean, DateTime, Float, ForeignKey, func
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Periodo(Base):
    """
    Tabla Periodo
    """
    __tablename__ = 'periodo'

    id_periodo = Column(Integer, primary_key=True)
    descripcion = Column(String, nullable=False)
    fecha_inicio = Column(DateTime, nullable=False)
    fecha_fin = Column(DateTime, nullable=False)
    activo = Column(Boolean, nullable=True, server_default='1')

    solicitudes = relationship('Solicitud', cascade='all, delete')

    def __repr__(self) -> str:
        return (f'Periodo(id_periodo={self.id_periodo!r}, descripcion={self.descripcion!r}, '
                 'fecha_inicio={self.fecha_inicio!r}, fecha_fin={self.fecha_fin!r}), '
                 'activo={self.activo!r}')


class Departamento(Base):
    """
    Tabla Departamento
    """
    __tablename__ = 'departamento'

    id_departamento = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    clave = Column(String, nullable=False)

    usuarios = relationship('Usuario', cascade='all, delete')
    solicitudes = relationship('Solicitud', cascade='all, delete')

    def __repr__(self) -> str:
        return (f'Departamento(id_departamento={self.id_departamento!r}, '
                 'nombre={self.nombre!r}, clave={self.clave!r})')


class Grupo(Base):
    """
    tabla Grupo
    """
    __tablename__ = 'grupo'

    id_grupo = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)

    materiales = relationship('Material',cascade='all, delete')

    def __repr__(self) -> str:
        return f'Grupo(id_grupo={self.id_grupo!r}, nombre={self.nombre!r})'


class Material(Base):
    """
    Tabla Material
    """
    __tablename__ = 'material'

    id_material = Column(String, primary_key=True)
    id_grupo = Column(Integer, ForeignKey('grupo.id_grupo'), nullable=False)
    precio_unitario = Column(Float, nullable=False)
    unidad_medida = Column(String, nullable=False)
    descripcion_sap = Column(String, nullable=False)
    descripcion = Column(String, nullable=False)
    activo = Column(Boolean, nullable=True, server_default='1')

    solicitud = relationship('Solicitud', cascade='all, delete')

    def __repr__(self) -> str:
        return (f'Material(id_material={self.id_material!r}, id_grupo:{self.id_grupo!r}), '
                 'precio_unitario={self.precio_unitario!r}, unidad_medida={self.unidad_medida!r}, '
                 'descripcion_sap={self.descripcion_sap!r}, descripcion={self.descripcion!r}, '
                 'activo={self.activo!r})')


class Solicitud(Base):
    """
    Tabla Solicitudes
    """
    __tablename__ = 'solicitudes'

    id_material = Column(String, ForeignKey('material.id_material'),
                         primary_key=True)
    id_zona = Column(Integer, ForeignKey('zona.id_zona'),
                     primary_key=True)
    id_departamento = Column(Integer, ForeignKey('departamento.id_departamento'),
                             primary_key=True)
    id_periodo = Column(Integer, ForeignKey('periodo.id_periodo'),
                        primary_key=True)
    cantidad = Column(Float, nullable=False)
    fecha_registro = Column(DateTime, nullable=True, server_default=func.now())
    comentarios = Column(String, nullable=True)

    def __repr__(self) -> str:
        return (f'Solicitud(id_material={self.id_material!r}, id_zona={self.id_zona!r}, '
                'id_departamento={self.id_departamento!r}, id_periodo={self.id_periodo!r}, '
                'cantidad={self.cantidad!r}, fecha_registro={self.fecha_registro!r}, '
                'comentarios={self.comentarios!r})')


class Usuario(Base):
    """
    Tabla Usuarios
    """
    __tablename__ = 'usuario'

    id_usuario = Column(Integer, primary_key=True)
    token = Column(String, nullable=False)
    nombre = Column(String, nullable=False)
    id_zona = Column(Integer, ForeignKey('zona.id_zona'), nullable=False)
    id_departamento = Column(Integer, ForeignKey('departamento.id_departamento'),nullable=False)

    zonas = relationship('Zona', cascade='all, delete') # CHECAR

    def __repr__(self) -> str:
        return (f'Usuario(id_usuario={self.id_usuario!r}, token={self.token!r}, '
            'nombre={self.nombre!r}, id_zona={self.id_zona!r}, '
            'id_departamento={self.id_departamento!r})')


class Zona(Base):
    """
    tabla Zona
    """
    __tablename__ = 'zona'

    id_zona = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    centro_gestor = Column(String, nullable=False)
    id_responsable = Column(Integer,ForeignKey('usuario.id_usuario'), nullable=True)

    solicitudes = relationship('Solicitud', cascade='all, delete') # CHECAR
    usuarios = relationship('Usuario', cascade='all, delete') # CHECAR

    def __repr__(self) -> str:
        return (f'Zona(id_zona={self.id_zona}, nombre={self.nombre!r}, '
            'centro_gestor={self.centro_gestor!r}, id_responsable={self.id_responsable!r})')

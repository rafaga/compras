"""
provides an standarized interface to multiple database engines
"""
#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# Autor: Rafael Amador Galván
# Fecha: 11/07/2022
import enum
from pathlib import Path
import sqlite3
import mariadb


class DatabaseType(enum.Enum):
    """ Enum the types of database supported """
    NONE = 0
    SQLITE = 1
    MARIADB = 2


class DatabaseDriver():
    """Module that works as a simple abstraction layer for database operations"""
    # Internal Variables
    __database_type = None
    __data_source = None
    __connection = None
    __sq_connection = None

    # Propiedades
    @property
    def data_source(self):
        """propertuy that stores data source object"""
        return self.__data_source

    @data_source.setter
    def data_source(self, ds_object):
        # a validation should be done here
        if self.database_type == DatabaseType.SQLITE:
            cont = 0
            if ds_object is None:
                raise FileNotFoundError
            if isinstance(ds_object, dict):
                if ds_object.get('database') is None:
                    raise SyntaxError
                ds_object['database'] = self.parse_to_path(ds_object['database'])
                self.__data_source = ds_object
            else:
                tdict = {}
                tdict['database'] = self.parse_to_path(ds_object)
                self.__data_source = tdict
            if self.__data_source['database'].exists() and self.__data_source['database'].is_file():
                if self.__is_sqlite3(self.__data_source['database']):
                    self.__create_connection(self.__data_source)
            else:
                self.__create_connection(self.__data_source)
        if self.database_type == DatabaseType.MARIADB:
            cont = 0
            if isinstance(ds_object, str):
                data = ds_object.split(',')
                temp_object = {}
                for valor in data:
                    temp = valor.split('=')
                    temp_object[temp[0]] = temp[1]
                    if temp[0] in ('username','password','server','port','database'):
                        cont += 1
                if cont == 5:
                    self.__create_connection(temp_object)
            if isinstance(ds_object, dict):
                for key in ds_object.keys():
                    if key in ('username','password','server','port','database'):
                        cont += 1
                if cont != 5:
                    raise SyntaxError
                self.__create_connection(ds_object)
        if ds_object is None:
            self.__data_source = None

    @property
    def database_type(self):
        """ property that stores the database type of the object"""
        return self.__database_type

    @property
    def connection(self):
        """ returns the connection object to the database"""
        return self.__connection

    # Constructor
    def __init__(self, database_type=DatabaseType.NONE, datasource_object=None):
        if not isinstance(database_type, DatabaseType):
            raise IndexError
        if database_type is database_type.NONE:
            raise NotImplementedError
        self.__database_type = database_type
        if datasource_object is not None:
            self.data_source = datasource_object

    def __is_sqlite3(self, database_file):
        """Function that checks if given file has a valid SQLite format"""
        # SQLite database file header is 100 bytes
        if database_file.stat().st_size < 100:
            return False
        with open(database_file, 'rb') as file:
            header = file.read(100)
        return header[:16] == b'SQLite format 3\x00'

    def __create_connection(self, data_source):
        if self.database_type == DatabaseType.SQLITE:
            self.__connection = sqlite3.connect(data_source['database'])
        if self.database_type == DatabaseType.MARIADB:
            try:
                self.__connection = mariadb.connect(
                    user=data_source['username'],
                    password=data_source['password'],
                    host=data_source['server'],
                    port=data_source['port'],
                    database=data_source['database']
                )
            except mariadb.Error as exc:
                print(f"Error connecting to MariaDB Platform: {exc}")

    def parse_to_path(self, obj_to_parse):
        """ Parse a string into a path """
        temp_object = None
        if isinstance(obj_to_parse, Path):
            temp_object = obj_to_parse
        if isinstance(obj_to_parse, str):
            temp_object = Path(obj_to_parse)
        return temp_object

"""
Provides basic methods to configure the flask application
"""
#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# Autor: Rafael Amador Galván
# Fecha: 11/07/2022
from pathlib import Path
import json
from flask import current_app
from . import database_driver


def configure_app(file):
    """
    load the configuration file and set values into the app
    """
    obj_file = None
    with open(file.resolve(True), 'r', encoding="utf-8") as obj_file:
        obj_json = json.load(obj_file)
        config_type = obj_json.get("config")
        if config_type is None:
            return None
        subconf = obj_json.get(config_type)
        if obj_json.get('secret_key') is not None:
            subconf["secret_key"] = obj_json['secret_key']
        if subconf.get('driver') is not None:
            if subconf["driver"] == 'SQLITE':
                subconf["driver"] = database_driver.DatabaseType.SQLITE
                subconf['database'] = Path(current_app.instance_path).joinpath(subconf['database'])
            if subconf["driver"] == 'MARIADB':
                subconf["driver"] = database_driver.DatabaseType.MARIADB
        else:
            subconf["driver"] = database_driver.DatabaseType.NONE
    return subconf


def parse_flask_config(subconfig):
    """
    Loads the config object into Flask distionary to run the web app
    """
    if subconfig is None:
        return None
    config = {}
    # print(subconfig, file=sys.stdout)
    config["DRIVER"] = subconfig['driver']
    if subconfig['driver'] == database_driver.DatabaseType.SQLITE:
        config["DATABASE"] = subconfig['database']
    if subconfig['driver'] == database_driver.DatabaseType.MARIADB:
        config["DATABASE"] = subconfig['database']
        config["USERNAME"] = subconfig['username']
        config["PASSWORD"] = subconfig['password']
        config["PORT"] = subconfig['port']
        config["SERVER"] = subconfig['server']
    config["SECRET_KEY"] = subconfig['secret_key']
    return config

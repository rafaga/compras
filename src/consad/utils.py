"""
Provides methods to create config files and restores default settings
"""

import json
from pathlib import Path
from flask import url_for, current_app
from flask.cli import AppGroup
from data_object import ORMConnection, models

config_cli = AppGroup('user')
database_cli = AppGroup('database')

def get_res_url():
    """
    gets The url to the static resources in the application
    """
    urls = {}
    urls["topcoat"] = url_for('static', filename='css/topcoat-desktop-dark.css')
    urls["compras"] = url_for('static', filename='css/compras.css')
    urls["flexbox"] = url_for('static', filename='css/flexboxgrid.min.css')
    urls["bvselect_js"] = url_for('static', filename='js/bvselect.js')
    urls["bvselect_css"] = url_for('static', filename='css/bvselect.css')
    urls["simple_table_css"] = url_for('static', filename='css/style.css')
    urls["simple_table_module"] = url_for('static', filename='js/module.js')
    return urls


def is_logged_in(session=None):
    """
    Checks if user is logged in
    """
    if session.get('userid') is None:
        return False
    return True


@config_cli.command('create')
def create_config():
    """
    Prepare the configuration and create the config file
    """
    filename = 'config.json'
    j_obj=prepare_config()
    create_config_file(filename,j_obj)


def prepare_config():
    """
    Creates an empty config file
    """
    json_obj = {}
    json_obj['config'] = 'sqlite'
    json_obj['secret_key'] = ''

    # SQLITE parameters
    engine = {}
    engine['driver'] = 'SQLITE'
    engine['database'] = 'database.db'
    json_obj['sqlite'] = engine.copy()

    # MARIADB parameters
    engine['driver'] = 'MARIADB'
    engine['database'] = ''
    engine['server'] = ''
    engine['username'] = ''
    engine['password'] = ''
    engine['port'] = 3306
    json_obj['mariadb'] = engine.copy()
    return json_obj


def create_config_file(filename, json_config):
    """
    Create a Filename with config object
    """
    # encoding to JSON
    jenc = json.JSONEncoder()
    json_str=jenc.encode(json_config)

    if Path(current_app.instance_path).joinpath(filename).is_file():
        #Path(current_app.instance_path).joinpath(filename).unlink()
        raise FileExistsError
    with open(Path(current_app.instance_path).joinpath(filename),
          'wt', encoding='UTF-8') as file:
        file.write(json_str)


@database_cli.command('create')
def create_database():
    """
    Creates a database from scratch
    """
    o_conn=ORMConnection(current_app.config)
    models.Base.metadata.create_all(bind=o_conn.engine)

@database_cli.command('migrate')
def migrate_database():
    """
    Migrates the database the current version
    """
    raise NotImplementedError

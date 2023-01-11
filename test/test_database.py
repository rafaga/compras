"""
Provides test for application
"""
from pathlib import Path
import pytest
from consad import utils, config_reader
from data_object import ORMConnection, models


class TestUtils():
    """ Provides Test to config files """

    def test_databse_creation(self):
        """
        Test the connection
        """
        test_file=Path('.').joinpath('src').joinpath('instance').joinpath('test.json')
        json_obj=utils.create_config()
        flask_config=config_reader.configure_app(test_file)
        config_dict=config_reader.parse_flask_config(flask_config)
        utils.create_config_file(test_file,json_obj)
        with pytest.raises(FileNotFoundError):
            o_conn=ORMConnection(config_dict)
            models.Base.metadata.create_all(bind=o_conn.engine)
            test_file.unlink()

    def test_valid_config(self):
        """
        Check if config has a valid structure
        """
        json_obj=utils.create_config()
        if json_obj['secret_key'] == '':
            return True

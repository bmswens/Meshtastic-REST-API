# built in
import os
from unittest.mock import MagicMock

# 3rd party
from meshtastic.serial_interface import SerialInterface
from meshtastic.mesh_interface import MeshInterface
from meshtastic.node import Node
import pytest

# custom
# add to os.sys.path so that we don't have to make a package
this_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(os.path.dirname(this_dir), 'src')
os.sys.path.append(src_dir)
from app import create_app

class MockInterface(MeshInterface):
    def __init__(self, super):
        print('am fake')
        super.__init__()


@pytest.fixture()
def app():
    # mock SerialInterface to always return a MeshInterface whithout 
    # trying to connect over serial
    SerialInterface.__init__ = lambda x: None

    app = create_app()
    app.config.update({
        "TESTING": True,
    })

    # mock out the meshtastic interface
    # code yoinked from meshtastic tests
    iface = MagicMock(autospec=MeshInterface)
    anode = Node('foo', 'bar')

    nodes = {
        '!9388f81c': {
            'num': 2475227164,
            'user': {
                'id': '!9388f81c',
                'longName': 'Unknown f81c',
                'shortName': '?1C',
                'macaddr': 'RBeTiPgc',
                'hwModel': 'TBEAM'
            },
            'position': {},
            'lastHeard': 1640204888
        },
        "SN1": {
            'num': 2475227164,
            'user': {
                'id': 'SN1',
                'longName': 'Unknown f81c',
                'shortName': '?1C',
                'macaddr': 'RBeTiPgc',
                'hwModel': 'TBEAM'
            },
            'position': {"raw": "bad data"},
            'lastHeard': 1640204888
        }
    }

    iface.nodesByNum = {1: anode }
    iface.nodes = nodes

    myInfo = MagicMock(return_value=nodes["!9388f81c"])
    iface.myInfo = myInfo

    getMyUser = MagicMock(return_value=nodes['!9388f81c']['user'])
    iface.getMyUser = getMyUser

    app.interface = iface
    # other setup can go here

    yield app

    # clean up / reset resources here


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()

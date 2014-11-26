from pairbutton.app import create_app
from pairbutton.config import DevConfig, ProdConfig

import sure  # NOQA


def test_dev_config():
    app = create_app(DevConfig)
    app.debug.should.be.true
    app.testing.should.be.false


def test_prod_config():
    app = create_app(ProdConfig)
    app.debug.should.be.true
    app.testing.should.be.false

from pairbutton.app import create_app
from pairbutton.config import DevConfig, ProdConfig

import argparse


parser = argparse.ArgumentParser(description='Start the Pairbutton server.')
parser.add_argument(
    '-d', '--dev', action='store_true',
    help='Start in development mode. If omitted, the server defaults to '
         'production mode.'
)
args = parser.parse_args()

if args.dev:
    curr_config = DevConfig
else:
    curr_config = ProdConfig

app = create_app(curr_config)


if __name__ == '__main__':
    app.run()

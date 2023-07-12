import pbf

pbf.data_path = '/config/bot/data.yaml'
pbf.plugins_path = '/plugins'

from pbf.driver import Fastapi

if __name__ == '__main__':
    Fastapi.serve(1000)
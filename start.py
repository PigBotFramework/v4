from pbf.driver import Fastapi
import sys
sys.path.append('/www/gch/pbf/pbf')

if __name__ == '__main__':
    port = 1000 if len(sys.argv) < 2 else sys.argv[1]
    Fastapi.serve(port)
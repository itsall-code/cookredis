import sys
import os 

# Add the src directory to the path for testing
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from pyjson import Json

cross_redis_cfg_json = Json('../cfg/cross_db_cfg.json')
cross_redis_cfg_json.read_json_file()
[local_cross_cfg, source_cross_cfg] = cross_redis_cfg_json.get_cross_redis()


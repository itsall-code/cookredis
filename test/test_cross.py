import sys
import os 

# Add the src directory to the path for testing
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from pyjson import Json


delete_cfg = Json('../cfg/del_tb.json')
delete_cfg.read_json_file()

tb = delete_cfg.get_tb()

for i in iter(tb):
    print(i)



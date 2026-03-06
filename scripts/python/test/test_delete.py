from pyjson import Json


delete_cfg = Json('../cfg/del_tb.json')
delete_cfg.read_json_file()
# print(delete_cfg)
# delete_cfg.out_data()
tb = delete_cfg.get_tb()
# print(tb)
for i in iter(tb):
    print(i)



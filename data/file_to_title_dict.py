from functions_and_classes.cloud_io import dic_from_gc_json

file_to_title_dict = dic_from_gc_json('file_to_title_dict.json')
file_list = []
for file in file_to_title_dict.keys():
    file_list.append(file)

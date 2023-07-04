import json

with open('data.json', 'r', encoding='cp1251') as file:
    data = json.load(file)

with open('data_utf8.json', 'w', encoding='utf-8') as file:
    json.dump(data, file, ensure_ascii=False)
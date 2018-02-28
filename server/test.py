import json


f = open("database", 'r')
d = json.load(f)
print(d)
f.close()
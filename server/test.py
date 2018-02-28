import json


f = open("database", 'r')
d = json.load(f)
f.close()

for k,v in enumerate(d):
    print(k,v)
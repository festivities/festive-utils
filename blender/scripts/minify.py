import json

# replace
data = { ... }

minified = json.dumps(data, separators=(',', ':'))
print(minified)

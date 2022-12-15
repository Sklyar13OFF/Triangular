import json
with open("structured_triangular_pairs.json") as json_file:
    structured_pairs = json.load(json_file)
for i in structured_pairs:
    i['pair_a'] = i['pair_a'].upper()
    i['pair_b'] = i['pair_b'].upper()
    i['pair_c'] = i['pair_c'].upper()
with open('structured_triangular_pairs.json','w') as fp:
    json.dump(structured_pairs,fp)

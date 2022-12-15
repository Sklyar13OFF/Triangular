import json
import func_arbitrage

def step_0():
    structured_list = func_arbitrage.structure_triangular_pairs()


    with open("structured_triangular_pairs.json",'w') as fp:
        json.dump(structured_list,fp)

def step_1():
    with open("structured_triangular_pairs.json") as json_file:
        structured_pairs = json.load(json_file)
        for t_pair in structured_pairs:
            res = func_arbitrage.calc_triangular_arb_surface_rate(t_pair)
            print(res)


if __name__ == '__main__':
    #structured_pairs = step_0()
    step_1()



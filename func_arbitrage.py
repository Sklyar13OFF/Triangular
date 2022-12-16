from binance.spot import Spot
import asyncio,os
from binance.streams import AsyncClient,BinanceSocketManager
from time import sleep
from binance.streams import ThreadedWebsocketManager

import websocket
import json
from websocket import create_connection
from re import search
from binance.client import Client

list_of_stable_coins = ['USDC', 'BUSD', 'DAI', 'FRAX', 'USDP', 'TUSD', 'USDD', 'GUSD', 'USDN', 'USDT']
api_key = ''
api_secret = ''
client = Spot(api_key,api_secret)
klient = Client(api_key,api_secret)
async def main():
    client = await AsyncClient.create()
    bm = BinanceSocketManager(client)
    sts = bm.trade_socket("BTCUSDT")

    async with sts as sm:
        while True:
            res = await sm.recv()
            os.system('clear')
            print(res['p'])
def collect_coins():
    res = klient.get_all_coins_info()
    list_of_stable_coins = ['USDC','BUSD','DAI','FRAX','USDP','TUSD','USDD','GUSD','USDN','USDT']
    s = []
    for i in res:
        s.append(i['coin'])
    return s

def get_coin_tickers_for_stable():
    coins = collect_coins()
    pair_list = []
    res = client.book_ticker()

    for i in res:
        for j in list_of_stable_coins:
            if (i['symbol'].startswith(j)) and (i['symbol'].removeprefix(j) in coins):
                pair_list.append(i['symbol'])
            elif (i['symbol'].endswith(j)) and (i['symbol'].removesuffix(j) in coins):
                pair_list.append(i['symbol'])

    return pair_list

def get_coin_tickers_for_volatile():
    coins = collect_coins()
    list_of_stable_coins = ['USDC', 'BUSD', 'DAI', 'FRAX', 'USDP', 'TUSD', 'USDD', 'GUSD', 'USDN','USDT']
    pair_list = []
    res = client.book_ticker()

    for i in res:
        counter = 0
        for j in list_of_stable_coins:

            if (i['symbol'].startswith(j) is False) and (i['symbol'].endswith(j) is False):
                    counter += 1

        if counter == 10:
            pair_list.append(i['symbol'])
    return pair_list

def structure_stable_pairs():
    stable_tickers = get_coin_tickers_for_stable()
    list_of_structured_pairs = []
    for i in stable_tickers:
        for j in list_of_stable_coins:
            if i.startswith(j):
                i = j + "_" + i.removeprefix(j)
                list_of_structured_pairs.append(i)
            elif i.endswith(j):
                i = i.removesuffix(j) + "_" + j
                list_of_structured_pairs.append(i)
    s = set()
    for i in list_of_structured_pairs:
        s.add(i)
    list_of_structured_pairs = list(s)
    return list_of_structured_pairs

def structure_volatile_pairs():
    coins = collect_coins()
    vol_tickers = get_coin_tickers_for_volatile()
    list_of_structured_pairs = []
    for i in vol_tickers:
        for j in coins:
            if i.startswith(j):
                if i.removeprefix(j) in coins:
                    x = j + '_' + i.removeprefix(j)
                    list_of_structured_pairs.append(x)
            elif i.endswith(j):
                if i.removesuffix(j) in coins:
                    x = i.removesuffix(j) +'_'+ j
                    list_of_structured_pairs.append(x)
    s = set()
    for i in list_of_structured_pairs:
        s.add(i)
    list_of_structured_pairs = list(s)
    return list_of_structured_pairs

def structure_triangular_pairs():

    # Declare Variables
    triangular_pairs_list = []
    remove_duplicates_list = []
    stable_list = structure_stable_pairs()
    volatile_list = structure_volatile_pairs()

    # Get Pair A
    for pair_a in stable_list:
        pair_a_split = pair_a.split("_")
        a_base = pair_a_split[0]
        a_quote = pair_a_split[1]
        # Assign A to a Box
        a_pair_box = [a_base, a_quote]

        # Get Pair B
        for pair_b in volatile_list:
            pair_b_split = pair_b.split("_")
            b_base = pair_b_split[0]
            b_quote = pair_b_split[1]

            if (b_base in a_pair_box) or (b_quote in a_pair_box):

                    # Get Pair C
                for pair_c in structure_stable_pairs():
                    pair_c_split = pair_c.split("_")
                    c_base = pair_c_split[0]
                    c_quote = pair_c_split[1]

                        # Count the number of matching C items

                    combine_all = [pair_a, pair_b, pair_c]
                    pair_box = [a_base, a_quote, b_base, b_quote, c_base, c_quote]

                    counts_c_base = 0
                    for i in pair_box:
                        if i == c_base:
                            counts_c_base += 1

                    counts_c_quote = 0
                    for i in pair_box:
                        if i == c_quote:
                            counts_c_quote += 1

                            # Determining Triangular Match
                    if counts_c_base == 2 and counts_c_quote == 2 and c_base != c_quote:
                        combined = pair_a + "," + pair_b + "," + pair_c
                        unique_item = ''.join(sorted(combine_all))

                        if unique_item not in remove_duplicates_list:
                            match_dict = {
                                    "a_base": a_base,
                                    "b_base": b_base,
                                    "c_base": c_base,
                                    "a_quote": a_quote,
                                    "b_quote": b_quote,
                                    "c_quote": c_quote,
                                    "pair_a": pair_a,
                                    "pair_b": pair_b,
                                    "pair_c": pair_c,
                                    "combined": combined
                            }
                            triangular_pairs_list.append(match_dict)
                            remove_duplicates_list.append(unique_item)

    return triangular_pairs_list

def calc_triangular_arb_surface_rate(t_pair):

    client = Spot(api_key,api_secret)
    # Set Variables
    starting_amount = 100
    min_surface_rate = 0
    surface_dict = {}
    contract_2 = ""
    contract_3 = ""
    direction_trade_1 = ""
    direction_trade_2 = ""
    direction_trade_3 = ""
    acquired_coin_t2 = 0
    acquired_coin_t3 = 0
    calculated = 0

    # Extract Pair Variables
    a_base = t_pair["a_base"]
    a_quote = t_pair["a_quote"]
    b_base = t_pair["b_base"]
    b_quote = t_pair["b_quote"]
    c_base = t_pair["c_base"]
    c_quote = t_pair["c_quote"]
    pair_a = t_pair["pair_a"]
    pair_b = t_pair["pair_b"]
    pair_c = t_pair["pair_c"]
    btc_price = {'error': False}

    # Extract Price Information

    fiat_list = ['ZAR','UAH','TRY','RUB','SAR','RON','QAR','PLN','OMR','NGN','KZT','KWD','HUF','GBP','EUR','CZK','BRL','BHD','AUD','AED']


    a_ask = 0
    a_bid = 0

    def triangular_prices(msg):
        a_ask = msg['a']
        a_bid = msg['b']
        print(a_ask,a_bid)

    bsm = ThreadedWebsocketManager('Zw82anbEVcB286P2qYIPofX0zvswQ5O5E0SQNCnwKPPNsT5vYuERvtDx6v0pfy0B','PqPvNHqU8dv114vMgsv5r7NdYbOXCUhd43mDRr6yAY6H69hP78HioP6rIM2ToHYF')
    bsm.start()
    bsm.start_symbol_book_ticker_socket(callback=triangular_prices, symbol=pair_a)
    bsm.join()

    return [a_ask,a_bid]



from client import Client
from utils.consts import *

'''
API Key:
a4vDIBnO0dFKZemW8URNMawuyuU0eyRUI3VGh1wekSlNXDOk704iTPdMisSrYEx8
Secret Key:
T0GEN5C8c8U4YKDMNjbjQeE3HLRLTfTugpatoC9a3eTxIRV4C30aqifHKu2fIa68
'''


client = Client(api_key, api_secret)
print(client.ping())

symbol = 'BNBBTC'
orderid = 109845

# print(client.get_server_time())
# print(client.get_recent_trade(symbol))
#
# print(client.get_depth(symbol))
#
# print(client.get_recent_aggTrade(symbol))
# print(client.get_history_trade(symbol))
# print(client.get_kline(symbol, KLINE_INTERVAL_1MONTH))
# print(client.get_avg_price(symbol))
# print(client.get_ticker(symbol))
# print(client.get_recent_price(symbol))
# print(client.get_book_ticker(symbol))
#
# print(client.buy_limit(symbol, 1, 0.01))
# print(client.sell_limit(symbol, 1, 0.01))
# print(client.buy_symbol(symbol, 1))
# print(client.sell_symbol(symbol, 1))
#
# print(client.query_order(symbol, orderid))
# print(client.withdraw_order(symbol, orderid))

print(client.get_account())
print(client.get_exchange_info())
print(client.get_open_orders(symbol))
print(client.get_all_orders(symbol))
print(client.get_my_trades(symbol))

# coding=utf-8

import time
import hashlib
import requests
from urllib.parse import urlencode
from utils.consts import *
from utils.http import *
from utils.errors import *
from binance.client import Client

class Client:

    def __init__(self, key, secret):
        self.key = key
        self.secret = secret
        self.header = {"X-MBX-APIKEY": self.key}

    def _sign(self, params={}):
        data = params.copy()

        ts = str(int(1000 * time.time()))
        data.update({"timestamp": ts})

        h = urlencode(data)
        b = bytearray()
        b.extend(self.secret.encode())

        signature = hmac.new(b, msg=h.encode('utf-8'), digestmod=hashlib.sha256).hexdigest()
        data.update({"signature": signature})
        return data

    def _get_without_sign(self, path, params={}):
        query = urlencode(params)
        url = "%s?%s" % (path, query)
        proxies = {
            "http": shadowsocks_vpn,
            "https": shadowsocks_vpn
        }
        return requests.get(url, timeout=7,  proxies=proxies, verify=True).json()


    def _get(self, path, params={}):
        params.update({"recvWindow": 120000})
        query = urlencode(self._sign(params))
        url = "%s?%s" % (path, query)
        return requests.get(url, headers=self.header, timeout=30, verify=True).json()

    def _post(self, path, params={}):
        params.update({"recvWindow": 120000})
        query = urlencode(self._sign(params))
        url = "%s?%s" % (path, query)
        return requests.post(url, headers=self.header, timeout=30, verify=True).json()

    def _delete(self, path, params={}):
        params.update({"recvWindow": 120000})
        query = urlencode(self._sign(params))
        url = "%s?%s" % (path, query)
        return requests.delete(url, headers=self.header, timeout=30, verify=True).json()

    def ping(self):
        '''
        测试服务器连通性
        :return: {}
        :raise: BinanceRequestException, BinanceAPIException
        '''
        path = "%s/ping" % BASE_URL
        return self._get_without_sign(path)

    def get_server_time(self):
        '''
        获取服务器时间
        :return:
            {
              "serverTime": 1499827319559
            }
        :raise: BinanceRequestException, BinanceAPIException
        '''
        path = "%s/time" % BASE_URL
        return self._get_without_sign(path)

    def get_depth(self, symbol, limit=100):
        '''
        获取深度信息
        :param symbol: 市场
        :param limit: 默认 100; 最大 1000. 可选值:[5, 10, 20, 50, 100, 500, 1000]
        :return:
            {
              "lastUpdateId": 1027024,
              "bids": [
                [
                  "4.00000000",     // 价位
                  "431.00000000",   // 挂单量
                  []                // 请忽略.
                ]
              ],
              "asks": [
                [
                  "4.00000200",
                  "12.00000000",
                  []
                ]
              ]
            }
        '''
        params = {"symbol": symbol, "limit": limit}
        path = "%s/depth" % BASE_URL
        return self._get_without_sign(path, params)

    def get_recent_trade(self, symbol, limit=500):
        '''
        获取近期成交
        :param symbol: 市场
        :param limit: Default 500; max 1000.
        :return:
            [
              {
                "id": 28457,
                "price": "4.00000100",
                "qty": "12.00000000",
                "time": 1499865549590,
                "isBuyerMaker": true,
                "isBestMatch": true
              }
            ]
        '''
        params = {"symbol": symbol, "limit": limit}
        path = "%s/trades" % BASE_URL
        return self._get_without_sign(path, params)

    def get_recent_aggTrade(self, symbol, limit=500, fromId=None, startTime=None, endTime=None):
        '''
        与trades的区别是，同一个taker在同一时间同一价格与多个maker的成交会被合并为一条记录
        :param symbol:
        :param limit: 默认 500; 最大 1000.
        :param fromId: 从包含fromID的成交开始返回结果
        :param startTime: 从该时刻之后的成交记录开始返回结果
        :param endTime: 返回该时刻为止的成交记录
        :return:
        '''
        params = {"symbol": symbol, "limit": limit}
        if fromId:
            params["fromId"] = fromId
        if startTime:
            params['startTime'] = startTime
        if endTime:
            params['endTime'] = endTime
        if startTime and endTime and endTime - startTime < 1*60*60*1000:
            raise TimeIntervalError
        path = "%s/aggTrades" % BASE_URL
        return self._get_without_sign(path, params)

    def get_history_trade(self, symbol, limit=500):
        '''
        查询历史成交
        :param symbol: 市场
        :param limit: Default 500; max 1000.
        :return:
            [
              {
                "id": 28457,
                "price": "4.00000100",
                "qty": "12.00000000",
                "time": 1499865549590,
                "isBuyerMaker": true,
                "isBestMatch": true
              }
            ]
        '''
        path = "%s/historicalTrades" % self.BASE_URL
        params = {"symbol": symbol, "limit": limit}
        return self._get_no_sign(path, params)

    def get_ticker(self, symbol):
        path = "%s/ticker/24hr" % BASE_URL
        params = {"symbol": symbol}
        return self._get_without_sign(path, params)






    # def get_trades(self, symbol, limit=50):
    #     path = "%s/trades" % self.BASE_URL
    #     params = {"symbol": symbol, "limit": limit}
    #     return self._get_no_sign(path, params)
    #
    # def get_kline(self, symbol):
    #     path = "%s/klines" % self.BASE_URL
    #     params = {"symbol": symbol}
    #     return self._get_no_sign(path, params)
    #
    #
    # def _order(self, symbol, quantity, side, rate=None):
    #     params = {}
    #
    #     if rate is not None:
    #         params["type"] = "LIMIT"
    #         params["price"] = self._format(rate)
    #         params["timeInForce"] = "GTC"
    #     else:
    #         params["type"] = "symbol"
    #
    #     params["symbol"] = symbol
    #     params["side"] = side
    #     params["quantity"] = '%.8f' % quantity
    #
    #     return params
    #
    # def _format(self, price):
    #     return "{:.8f}".format(price)



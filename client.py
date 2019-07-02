# coding=utf-8

import time
import hmac
import hashlib
import requests
from urllib.parse import urlencode
from utils.consts import *
from utils.errors import *
from retrying import retry

proxies = {
    "http": shadowsocks_vpn,
    "https": shadowsocks_vpn
}

class Client:

    def __init__(self, key, secret):
        self.key = key
        self.secret = secret
        self.header = {"X-MBX-APIKEY": self.key}

    ###########################################
    ##########      http方法      #############
    ###########################################

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
        return self._response_handler(self._get_response('GET_NO_SIGN', url))
        # return requests.get(url, timeout=7,  proxies=proxies, verify=True).json()

    def _get(self, path, params={}):
        params.update({"recvWindow": 120000})
        query = urlencode(self._sign(params))
        url = "%s?%s" % (path, query)
        return self._response_handler(self._get_response('GET', url))

    def _post(self, path, params={}):
        params.update({"recvWindow": 120000})
        query = urlencode(self._sign(params))
        url = "%s?%s" % (path, query)
        return self._response_handler(self._get_response('POST', url))

    def _delete(self, path, params={}):
        params.update({"recvWindow": 120000})
        query = urlencode(self._sign(params))
        url = "%s?%s" % (path, query)
        return self._response_handler(self._get_response('DELETE', url))

    @retry(stop_max_attempt_number=7)
    def _get_response(self, method, url):
        if method == 'GET' or method == 'GET_NO_SIGN':
            response = requests.get(url, headers=self.header, timeout=30, verify=True, proxies=proxies)
        elif method == 'POST':
            response = requests.post(url, headers=self.header, timeout=30, verify=True, proxies=proxies)
        elif method == 'DELETE':
            response = requests.delete(url, headers=self.header, timeout=30, verify=True, proxies=proxies)
        return response


    def _response_handler(self, response):
        if not str(response.status_code).startswith('2'):
            raise BinanceAPIException(response)
        try:
            return response.json()
        except ValueError:
            raise BinanceRequestException('Invalid Response: %s' % response.text)

        
    ###########################################
    ##########       通用接口      #############
    ###########################################

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
        path = "%s/historicalTrades" % BASE_URL
        params = {"symbol": symbol, "limit": limit}
        return self._get_without_sign(path, params)

    def get_kline(self, symbol, interval, limit=500, startTime=None, endTime=None):
        '''
        K线数据, 每根K线的开盘时间可视为唯一ID
        :param symbol:
        :param interval:
        :param limit: Default 500; max 1000.
        :param startTime:
        :param endTime:
        :return:
            [
              [
                1499040000000,      // 开盘时间
                "0.01634790",       // 开盘价
                "0.80000000",       // 最高价
                "0.01575800",       // 最低价
                "0.01577100",       // 收盘价(当前K线未结束的即为最新价)
                "148976.11427815",  // 成交量
                1499644799999,      // 收盘时间
                "2434.19055334",    // 成交额
                308,                // 成交笔数
                "1756.87402397",    // 主动买入成交量
                "28.46694368",      // 主动买入成交额
                "17928899.62484339" // 请忽略该参数
              ]
            ]
        '''
        path = "%s/klines" % BASE_URL
        params = {"symbol": symbol, "interval": interval, 'limit': limit}
        if startTime:
            params['startTime'] = startTime
        if endTime:
            params['endTime'] = endTime
        return self._get_without_sign(path, params)

    def get_avg_price(self, symbol):
        '''
        当前平均价格
        :param symbol:
        :return:
            {
              "mins": 5,
              "price": "9.35751834"
            }
        '''
        path = "%s/avgPrice" % BASE_URL_V3
        params = {"symbol": symbol}
        return self._get_without_sign(path, params)

    def get_ticker(self, symbol):
        '''
        24hr价格变动情况
        :param symbol:
        :return:
        {
          "symbol": "BNBBTC",
          "priceChange": "-94.99999800",
          "priceChangePercent": "-95.960",
          "weightedAvgPrice": "0.29628482",
          "prevClosePrice": "0.10002000",
          "lastPrice": "4.00000200",
          "lastQty": "200.00000000",
          "bidPrice": "4.00000000",
          "askPrice": "4.00000200",
          "openPrice": "99.00000000",
          "highPrice": "100.00000000",
          "lowPrice": "0.10000000",
          "volume": "8913.30000000",
          "quoteVolume": "15.30000000",
          "openTime": 1499783499040,
          "closeTime": 1499869899040,
          "firstId": 28385,   // 首笔成交id
          "lastId": 28460,    // 末笔成交id
          "count": 76         // 成交笔数
        }
        OR

        [
          {
            "symbol": "BNBBTC",
            "priceChange": "-94.99999800",
            "priceChangePercent": "-95.960",
            "weightedAvgPrice": "0.29628482",
            "prevClosePrice": "0.10002000",
            "lastPrice": "4.00000200",
            "lastQty": "200.00000000",
            "bidPrice": "4.00000000",
            "askPrice": "4.00000200",
            "openPrice": "99.00000000",
            "highPrice": "100.00000000",
            "lowPrice": "0.10000000",
            "volume": "8913.30000000",
            "quoteVolume": "15.30000000",
            "openTime": 1499783499040,
            "closeTime": 1499869899040,
          "firstId": 28385,   // 首笔成交id
          "lastId": 28460,    // 末笔成交id
          "count": 76         // 成交笔数
          }
        ]
        '''
        path = "%s/ticker/24hr" % BASE_URL
        params = {"symbol": symbol}
        return self._get_without_sign(path, params)


    def get_recent_price(self, symbol):
        '''
        最新价格接口, 返回最近价格
        :param symbol:
        :return:
            {
              "symbol": "LTCBTC",
              "price": "4.00000200"
            }
            OR

            [
              {
                "symbol": "LTCBTC",
                "price": "4.00000200"
              },
              {
                "symbol": "ETHBTC",
                "price": "0.07946600"
              }
            ]
        '''
        path = "%s/ticker/price" % BASE_URL_V3
        params = {"symbol": symbol}
        return self._get_without_sign(path, params)

    def get_book_ticker(self, symbol):
        '''
        返回当前最优的挂单(最高买单，最低卖单)
        :param symbol:
        :return:
            {
              "symbol": "LTCBTC",
              "bidPrice": "4.00000000",//最优买单价
              "bidQty": "431.00000000",//挂单量
              "askPrice": "4.00000200",//最优卖单价
              "askQty": "9.00000000"//挂单量
            }
            OR

            [
              {
                "symbol": "LTCBTC",
                "bidPrice": "4.00000000",
                "bidQty": "431.00000000",
                "askPrice": "4.00000200",
                "askQty": "9.00000000"
              },
              {
                "symbol": "ETHBTC",
                "bidPrice": "0.07946700",
                "bidQty": "9.00000000",
                "askPrice": "100000.00000000",
                "askQty": "1000.00000000"
              }
            ]

        '''
        path = "%s/ticker/price" % BASE_URL_V3
        params = {"symbol": symbol}
        return self._get_without_sign(path, params)

    ###########################################
    ##########       订单处理      #############
    ###########################################

    def _order(self, symbol, quantity, side, price=None):
        params = {}

        if price:
            params["type"] = "LIMIT"
            params["price"] = '%.8f' % price
            params["timeInForce"] = "GTC"
        else:
            params["type"] = 'MARKET'

        params["symbol"] = symbol
        params["side"] = side
        params["quantity"] = '%.8f' % quantity

        return params

    def _order_path(self):
        '''
        虚拟下单 返回 "%s/order/test" % BASE_URL_V3
        真实下单 返回 "%s/order" % BASE_URL_V3
        :return:
        '''
        return "%s/order/test" % BASE_URL_V3

    def buy_limit(self, symbol, quantity, price):
        params = self._order(symbol, quantity, "BUY", price)
        return self._post(self._order_path(), params)

    def sell_limit(self, symbol, quantity, price):
        params = self._order(symbol, quantity, "SELL", price)
        return self._post(self._order_path(), params)

    def buy_symbol(self, symbol, quantity):
        params = self._order(symbol, quantity, "BUY")
        return self._post(self._order_path(), params)

    def sell_symbol(self, symbol, quantity):
        params = self._order(symbol, quantity, "SELL")
        return self._post(self._order_path(), params)

    def query_order(self, symbol, orderId):
        '''
        查询订单 (USER_DATA)
        :param symbol:
        :param orderId:
        :return:
            {
              "symbol": "LTCBTC",
              "orderId": 1,
              "clientOrderId": "myOrder1",
              "price": "0.1",
              "origQty": "1.0",
              "executedQty": "0.0",
              "cummulativeQuoteQty": "0.0",
              "status": "NEW",
              "timeInForce": "GTC",
              "type": "LIMIT",
              "side": "BUY",
              "stopPrice": "0.0",
              "icebergQty": "0.0",
              "time": 1499827319559,
              "updateTime": 1499827319559,
              "isWorking": true
            }
        '''
        path = "%s/order" % BASE_URL_V3
        params = {"symbol": symbol, "orderId": orderId}
        return self._get(path, params)

    def withdraw_order(self, symbol, order_id):
        '''
        撤销订单 (TRADE)
        :param symbol:
        :param order_id:
        :return:
            {
              "symbol": "LTCBTC",
              "orderId": 28,
              "origClientOrderId": "myOrder1",
              "clientOrderId": "cancelMyOrder1",
              "transactTime": 1507725176595,
              "price": "1.00000000",
              "origQty": "10.00000000",
              "executedQty": "8.00000000",
              "cummulativeQuoteQty": "8.00000000",
              "status": "CANCELED",
              "timeInForce": "GTC",
              "type": "LIMIT",
              "side": "SELL"
            }
        '''
        path = "%s/order" % BASE_URL_V3
        params = {"symbol": symbol, "orderId": order_id}
        return self._delete(path, params)

    ###########################################
    ##########       账户管理      #############
    ###########################################

    def get_account(self):
        '''
        账户信息 (USER_DATA)
        :return:
            {
              "makerCommission": 15,
              "takerCommission": 15,
              "buyerCommission": 0,
              "sellerCommission": 0,
              "canTrade": true,
              "canWithdraw": true,
              "canDeposit": true,
              "updateTime": 123456789,
              "balances": [
                {
                  "asset": "BTC",
                  "free": "4723846.89208129",
                  "locked": "0.00000000"
                },
                {
                  "asset": "LTC",
                  "free": "4763368.68006011",
                  "locked": "0.00000000"
                }
              ]
            }
        '''
        path = "%s/account" % BASE_URL_V3
        return self._get(path, {})


    def get_exchange_info(self):
        '''
        Exchange information
        :return:
        {
          "timezone": "UTC",
          "serverTime": 1508631584636,
          "rateLimits": [
            // These are defined in the `ENUM definitions` section under `Rate limiters (rateLimitType)`.
            // All limits are optional.
          ],
          "exchangeFilters": [
            // There are defined in the `Filters` section.
            // All filters are optional.
          ],
          "symbols": [{
            "symbol": "ETHBTC",
            "status": "TRADING",
            "baseAsset": "ETH",
            "baseAssetPrecision": 8,
            "quoteAsset": "BTC",
            "quotePrecision": 8,
            "orderTypes": [
              // These are defined in the `ENUM definitions` section under `Order types (orderTypes)`.
              // All orderTypes are optional.
            ],
            "icebergAllowed": false,
            "filters": [
              // There are defined in the `Filters` section.
              // All filters are optional.
            ]
          }]
        }
        '''
        path = "%s/exchangeInfo" % BASE_URL
        return self._get_without_sign(path)

    def get_open_orders(self, symbol):
        '''
        查看账户当前挂单 (USER_DATA)
        :param symbol:
        :return:
            [
              {
                "symbol": "LTCBTC",
                "orderId": 1,
                "clientOrderId": "myOrder1",
                "price": "0.1",
                "origQty": "1.0",
                "executedQty": "0.0",
                "cummulativeQuoteQty": "0.0",
                "status": "NEW",
                "timeInForce": "GTC",
                "type": "LIMIT",
                "side": "BUY",
                "stopPrice": "0.0",
                "icebergQty": "0.0",
                "time": 1499827319559,
                "updateTime": 1499827319559,
                "isWorking": true
              }
            ]
        '''
        path = "%s/openOrders" % BASE_URL_V3
        params = {"symbol": symbol}
        return self._get(path, params)

    def get_all_orders(self, symbol):
        '''
        查询所有订单（包括历史订单） (USER_DATA)
        :param symbol:
        :return:
            [
              {
                "symbol": "LTCBTC",
                "orderId": 1,
                "clientOrderId": "myOrder1",
                "price": "0.1",
                "origQty": "1.0",
                "executedQty": "0.0",
                "cummulativeQuoteQty": "0.0",
                "status": "NEW",
                "timeInForce": "GTC",
                "type": "LIMIT",
                "side": "BUY",
                "stopPrice": "0.0",
                "icebergQty": "0.0",
                "time": 1499827319559,
                "updateTime": 1499827319559,
                "isWorking": true
              }
            ]
        '''
        path = "%s/allOrders" % BASE_URL_V3
        params = {"symbol": symbol}
        return self._get(path, params)

    def get_my_trades(self, symbol, limit=50):
        '''
        获取某交易对的成交历史
        :param symbol:
        :param limit: Default 500; max 1000.
        :return:
            [
              {
                "symbol": "BNBBTC",
                "id": 28457,
                "orderId": 100234,
                "price": "4.00000100",
                "qty": "12.00000000",
                "commission": "10.10000000",
                "commissionAsset": "BNB",
                "time": 1499865549590,
                "isBuyer": true,
                "isMaker": false,
                "isBestMatch": true
              }
            ]
        '''
        path = "%s/myTrades" % BASE_URL_V3
        params = {"symbol": symbol, "limit": limit}
        return self._get(path, params)
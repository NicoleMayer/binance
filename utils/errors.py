from utils.log import setup_custom_logger

logger = setup_custom_logger('root')

class TimeIntervalError(Exception):
    def __init__(self):
        logger.error('TimeIntervalError')

    def __str__(self):
        return 'TimeIntervalError: end time should 1h after the start time'


class BinanceAPIException(Exception):

    def __init__(self, response):
        self.code = 0
        try:
            json_res = response.json()
        except ValueError:
            self.message = 'Invalid JSON error message from Binance: {}'.format(response.text)
        else:
            self.code = json_res['code']
            self.message = json_res['msg']
        logger.error(self.message)
        self.status_code = response.status_code
        self.response = response
        self.request = getattr(response, 'request', None)

    def __str__(self):  # pragma: no cover
        return 'APIError(code=%s): %s' % (self.code, self.message)


class BinanceRequestException(Exception):
    def __init__(self, message):
        self.message = message
        logger.error(self.message)

    def __str__(self):
        return 'BinanceRequestException: %s' % self.message


class BinanceOrderException(Exception):

    def __init__(self, code, message):
        self.code = code
        self.message = message
        logger.error(self.message)

    def __str__(self):
        return 'BinanceOrderException(code=%s): %s' % (self.code, self.message)
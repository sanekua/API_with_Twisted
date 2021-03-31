from twisted.internet import reactor
from twisted.web.client import Agent, readBody
from twisted.web.http_headers import Headers
import logging
import json
import urllib


def callback_body(body):
    api_data = json.loads(body).get('data')
    for i in range(len(api_data)):
        value = api_data[i]
        static_data = {'name': value.get(u'name'),
                       'data_added': value.get(u'date_added'),
                       'slug': value.get(u'slug'),
                       'symbol': value.get(u'symbol'), }
        dynamic_data = {'Info Crypto changes': value.get(u'quote'),
                        'last_updated': value.get(u'last_updated')}
        logging.info('Static data: {}, Dynamic data : {} '.format(
                                                                static_data, dynamic_data))
        with open('cryptocurrency.json', 'a') as f:
            json.dump((static_data, dynamic_data), f)
            f.write('\n')


def callback_request(response):
    d = readBody(response)
    d.addCallback(callback_body)
    return d


if __name__ == '__main__':
    parameters = {
        'start': '1',
        'limit': '50',
    }
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest?'
    url_with_parameters = urllib.urlencode(parameters)
    URL = url + url_with_parameters
    agent = Agent(reactor)
    logging.basicConfig(filename='cryptocurrency.log', level=logging.INFO,
                        format='%(asctime)s %(message)s', filemode='a')
    d = agent.request(
        'GET',
        URL,
        Headers({'User-Agent': ['Twisted Web Client Example'],
                 'X-CMC_PRO_API_KEY': ['966944dc-a9bf-4e30-8d34-b110b5f291a8'],
                 'Accepts': ['application/json'],
                 }),
    )
    d.addCallback(callback_request)

    def cbShutdown(ignored):
        reactor.stop()


    d.addBoth(cbShutdown)
    reactor.run()
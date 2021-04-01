from twisted.internet import reactor
from twisted.web.client import Agent, readBody
from twisted.web.http_headers import Headers
import logging
import json
import urllib


def create_empty_files():
    with open('modelling_api_data.json', 'w') as modeling_data, \
            open('monitoring_api_data.json', 'w') as monitoring_data:
        modeling_data.write('Modeling Data' + '\n')
        monitoring_data.write('Monitoring Data' + '\n')


def save_to_json(static_data, dynamic_data):
    with open('modelling_api_data.json', 'a') as modeling_data, \
            open('monitoring_api_data.json', 'a') as monitoring_data:
        json.dump(static_data, modeling_data, sort_keys=True, indent=4)
        json.dump(dynamic_data, monitoring_data, sort_keys=True, indent=2)
        modeling_data.write('\n')
        monitoring_data.write('\n')


def callback_body(body):
    create_empty_files()
    api_data = json.loads(body).get('data')
    #print api_data[0].get(u'name'), len(api_data)
    for i in range(len(api_data)):
        value = api_data[i]
        static_data = {value.get(u'name'): {'name': value.get(u'name'),
                                            'data_added': value.get(u'date_added'),
                                            'slug': value.get(u'slug'),
                                            'symbol': value.get(u'symbol')}}
        dynamic_data = {'Cryptocurrency name': value.get(u'name'),
                        'Information about Cryptocurrency': value.get(u'quote'),
                        'last_updated': value.get(u'last_updated')}
        logging.info('Static data: {}, Dynamic data : {}'.format(
                                                                static_data, dynamic_data))
        if value.get(u'name') in CRYPTOCURRENCY_LIST:
            save_to_json(static_data, dynamic_data)


def callback_request(response):
    d = readBody(response)
    d.addCallback(callback_body)
    return d


if __name__ == '__main__':
    """
    You can add to CRYPTOCURRENCY_LIST cryptocurrency in which you are 
    interested. Also you can add limit(limit=20) to parameters to display 
    first 50 Cryptocurrency on https://coinmarketcap.com/ website (default=50)
    Modelling and Monitored data about chosen cryptocurrency saved in 
    modeling_data.json and monitoring_data.json. If you want to see rating list
    data saved to cryptoccurency.log file
    """
    parameters = {
        'start': '1',
        'limit': '50',
    }
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest?'
    url_with_parameters = urllib.urlencode(parameters)
    URL = url + url_with_parameters
    agent = Agent(reactor)
    CRYPTOCURRENCY_LIST = [u'Bitcoin', u'Binance Coin', u'Cardano', u'Ethereum']
    logging.basicConfig(filename='cryptocurrency.log', level=logging.INFO,
                        format='%(asctime)s %(message)s', filemode='w')
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
import requests
import json
from config import INSALES_URL
import threading
import asyncio



'''
info = requests.get(INSALES_URL + '/' + 'collects.json', params={'collection_id': 20742662}).json()
#for i in info:
  #  print(i)

for i in info:
    product_information = requests.get(INSALES_URL + '/' + 'products/{}.json'.format(i['product_id'])).json()
    print(product_information)
'''


async def summm(arg):
    print(arg + 10)


def between_callback(collection_id):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.run_until_complete(summm(collection_id))
    loop.close()





c = [0, 1, 2, 3, 4, 5, 6, 7]

for cc in c:
    t = threading.Thread(target=between_callback, args=(cc,))
    t.start()
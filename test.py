import requests
import json
from config import INSALES_URL




info = requests.get(INSALES_URL + '/' + 'products/{}.json'.format(288432601)).json()
print(info)
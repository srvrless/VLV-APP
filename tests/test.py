import asyncio
from db.database import Database
from db.database_updater import DatabaseUpdater
from tools import json_save
from insales_api import InsalesApi
import platform
from tools import Translitor

if platform.system()=='Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

database = Database()
database_updater = DatabaseUpdater(database)
insales_api = InsalesApi()

async def download_json_tasks():
    # collections = await insales_api.get_collections()
    # await json_save("collections.json", collections)
    # products = await insales_api.get_all_products()
    # await json_save("products.json", products)
    # categories = await insales_api.get_categories()
    # await json_save("categories.json", categories)
    # option_names = await insales_api.get_option_names()
    # await json_save("option_names.json", option_names)
    # option_values = await insales_api.get_option_values()
    # await json_save("option_values.json", option_values)
    # properties = await insales_api.get_properties()
    # await json_save("properties.json", properties)
    # clients = await insales_api.get_clients()
    # await json_save("clients.json", clients)
    client_groups = await insales_api.get_client_groups()
    await json_save("client_groups.json", client_groups)
    pass

async def fill_json_tasks():
    collections = await database_updater.load_collections_from_json()
    await database_updater.update_collections(collections)

    categories = await database_updater.load_categories_from_json()
    await database_updater.update_categories(categories)

    option_names = await database_updater.load_option_names_from_json()
    await database_updater.update_option_names(option_names)

    option_values = await database_updater.load_option_values_from_json()
    await database_updater.update_option_values(option_values)

    properties = await database_updater.load_properties_from_json()
    await database_updater.update_properties(properties)

    products = await database_updater.load_products_from_json()
    await database_updater.update_products(products)

    await database_updater.update_search_products()

    client_groups = await database_updater.load_client_groups_from_json()
    await database_updater.update_client_groups(client_groups)

    clients = await database_updater.load_clients_from_json()
    await database_updater.update_client_addresses(clients)

    clients = await database_updater.load_clients_from_json()
    await database_updater.update_clients(clients)


# asyncio.run(download_json_tasks())
# asyncio.run(fill_json_tasks())

# result = asyncio.run(insales_api.login("to_ev@mail.ru", "00_22_0_At"))
# result = asyncio.run(insales_api.register("Евгений", "Токарев", "8(800)555-35-35", "tok736@gmail.com", "00_22_00_At", "00_22_00_At"))

# print(result)



"""

{
	"authenticity_token": "1iAEeseLUhQ6TgrEryP6hAaSGSPDhcW0COvMNco5-Uq0lSq_qAXkZCllSPd26GjBTZS2zNSoctGHWB9u3Ts83w",
	
}


info = requests.get(INSALES_URL + '/' + 'collects.json', params={'collection_id': 20742662}).json()
#for i in info:
  #  print(i)

for i in info:
    product_information = requests.get(INSALES_URL + '/' + 'products/{}.json'.format(i['product_id'])).json()
    print(product_information)
"""

"""
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

from urllib.parse import parse_qsl


print(dict(parse_qsl("a=1&b=2")))

"""


"""
info = ("name", "surname", "phone", "email", "passwod", "date_birh", "updated")

required = ("name", "surname", "phone", "email", "password")
possible = ("date_birth",)

all_args = required + possible

unnecessary = [k for k in info if k not in all_args]

print(unnecessary)
"""



"""
from database_filler import DatabaseFiller
from database import Database
from tools import json_load
from pprint import pprint

db = Database()
dbf = DatabaseFiller(db)

data = asyncio.run(json_load("products.json"))

# properties = set()

# for product in data:
#     for pr in product["properties"]:
#         properties.add(pr["id"])

# print(properties)

from collections import Counter

options = []

was_first = False

for product in data:
    for variant in product["variants"]:
        if len(variant["option_values"]) == 3 and not was_first:
            pprint(variant)
            was_first = True
        options.append(len(variant["option_values"]))

print(Counter(options))

"""
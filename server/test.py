import asyncio
from concurrent.futures import ProcessPoolExecutor
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
    # client_groups = await insales_api.get_client_groups()
    # await json_save("client_groups.json", client_groups)
    return "success"

async def fill_json_tasks():
    # collections = await database_updater.load_collections_from_json()
    # await database_updater.update_collections(collections)
    
    # categories = await database_updater.load_categories_from_json()
    # await database_updater.update_categories(categories)

    # option_names = await database_updater.load_option_names_from_json()
    # await database_updater.update_option_names(option_names)

    # properties = await database_updater.load_properties_from_json()
    # await database_updater.update_properties(properties)


    # option_values = await database_updater.load_option_values_from_json()
    # await database_updater.update_option_values(option_values)



    # await database_updater.update_search_products()

    # client_groups = await database_updater.load_client_groups_from_json()
    # await database_updater.update_client_groups(client_groups)

    # clients = await database_updater.load_clients_from_json()
    # await database_updater.update_client_addresses(clients)

    # clients = await database_updater.load_clients_from_json()
    # await database_updater.update_clients(clients)

    products = await database_updater.load_products_from_json()
    await database_updater.update_products(products)
    return "success"


# asyncio.run(download_json_tasks())
asyncio.run(fill_json_tasks())

# result = asyncio.run(insales_api.register("Евгений", "Токарев", "8(800)555-35-35", "tok736@gmail.com", "00_22_00_At", "00_22_00_At"))

# print(result)

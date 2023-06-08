from datetime import datetime
import json
from random import randint
import asyncio


class SessionProcessing:
    def __init__(self):
        return
        
    async def open_file(self):
        with open('sessions.json') as session_file:
            data = json.load(session_file)
        return data
    
    async def write_file(self, info):
        with open('sessions.json', 'w') as session_file:
            json.dump(info, session_file)
        return True
    
    async def create_session(self, email):
        opened_data = await self.open_file()

        opened_data[email] = {
            'session_id': randint(0, 100000000000000), 'timestamp': datetime.now().isoformat(),
            'logged_in': True, 'cart': [], 'opened': []}
        
        result = await self.write_file(opened_data)
        if result: 
            return



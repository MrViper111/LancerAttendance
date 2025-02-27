from motor.motor_asyncio import AsyncIOMotorCollection


class Users:

    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def create(self, name: str, email: str, position: str, admin: bool):
        await self.collection.insert_one({
            "email": email,
            "name": name,
            "position": position,
            "admin": admin,
            "score": 0
        })

    async def get(self, filter: dict):
        return self.collection.find_one(filter)

    async def get_all(self):
        return await self.collection.find().to_list()

    async def set_score(self, name: str, score: int):
        ...

    async def delete(self, name: str):
        filter = {"name": name}
        await self.collection.delete_one(filter)

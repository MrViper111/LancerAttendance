from pymongo.synchronous.collection import Collection


class Users:

    def __init__(self, collection: Collection):
        self.collection = collection

    def create(self, name: str, email: str, position: str, admin: bool):
        filter = {"email": email}
        document = self.collection.find_one(filter)

        if document:
            return False

        self.collection.insert_one({
            "email": email,
            "name": name,
            "position": position,
            "admin": admin,
            "score": 0
        })
        return True

    def update(self, email: str, position: str = None, score: int = None, admin: bool = False):
        filter = {"email": email}
        document = self.collection.find_one(filter)

        if not document:
            return False

        document["position"] = position if position else document["position"]
        document["score"] = score if score else document["score"]
        document["admin"] = admin if admin else False

        self.collection.replace_one(filter, document)
        return True

    def delete(self, email):
        filter = {"email": email}
        document = self.collection.find_one(filter)

        if not document:
            return False

        self.collection.delete_one(filter)
        return True

    def get(self, filter: dict):
        return self.collection.find_one(filter)

    def get_all(self):
        return self.collection.find({}, {"_id": 0}).to_list()

    def set_score(self, email: str, score: int):
        filter = {"email": email}
        document = self.collection.find_one(filter)

        if not document:
            return

        document["score"] = score
        self.collection.replace_one(filter, document)

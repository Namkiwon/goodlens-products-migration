from .database import DataBase

class Product(DataBase):
    def __init__(self):
        super(Product,self).__init__()
        self.products = self.db.products

    def add_product(self,product):
        query = product
        try:
            # result 은 upsert result를 가지고 있다.
            # r.raw_result를 보면 insert 될 시에는 upserted 키값을 가지고 있다.

            r = self.products.update_one(query,
                                         {"$set": product},
                                         upsert=True)
        except Exception as e:
            print(e)

        return r

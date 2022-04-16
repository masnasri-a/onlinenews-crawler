import pymongo
from dotenv import dotenv_values

conf = dotenv_values('.env')

def mongo_client():
    host_config = conf.get('MONGO_HOST')
    host = "mongodb://{}/".format(host_config)
    myclient = pymongo.MongoClient(host)
    mydb = myclient["crawler"]
    mycol = mydb["online_news_raw"]
    return myclient, mycol

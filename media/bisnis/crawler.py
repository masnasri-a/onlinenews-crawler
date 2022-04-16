from operator import mod
from statistics import mode
from bs4 import BeautifulSoup
import requests, time, datetime, logging
from util import util
from ingest import mongo_ingest
from dotenv import set_key, dotenv_values


conf = dotenv_values('.env')
last_link = str(conf.get('LAST_BISNISDOTCOM'))
logging.basicConfig(format='%(asctime)s : %(message)s', level=logging.INFO)

mongo_client, mongo_column = mongo_ingest.mongo_client()

list_link = []
def get_list_link():
    url = "https://market.bisnis.com/bursa-saham"
    page = requests.get(url)
    logging.info(page.status_code)
    soup = BeautifulSoup(page.content, 'html.parser')
    ul_list_news = soup.find('ul',class_="list-news")
    list_news = ul_list_news.find_all('li')
    for detail in list_news:
        a = detail.find('a')
        if a['href'] == last_link:
            break
        else:
            list_link.append(a['href'])



def crawler():
    for link in list_link:
        try:
            page = requests.get(link)
            soup = BeautifulSoup(page.content, 'html.parser')
            logging.info(link)
            title = soup.find('h1', class_='title-only').text

            desc = soup.find('div', class_="new-description")
            author = str(desc.find('a').text).replace('  ','').replace('\n','').replace('\r','')
            
            created_at = desc.find('span')
            dates = str(created_at.text).replace('  ','').replace('\n','').replace('|','').replace('\r','').replace('\xa0\xa0 ','').replace('WIB','').replace(':',' ').split(' ')
            dates[1] = util.month_converter(dates[1])
            date_str = ' '.join(dates)
            timestamp_str = datetime.datetime.strptime(date_str,"%d %m %Y %H %M")
            timestamp = datetime.datetime.timestamp(timestamp_str)

            main_image = soup.find('div', class_='main-image')
            image =main_image.find('img')['src']

            main_list_article = soup.find('div',class_="col-sm-10")
            list_article = main_list_article.find_all('p')
            articles = []
            for detail in list_article:
                articles.append(str(detail.text).replace('Bisnis.com, ','').replace('\r\n','').replace('  ','').replace('. Simak berita lainnya seputar topikartikel ini, di sini :  Bergabung dan dapatkan analisis informasi ekonomi dan bisnis melalui email Anda.',''))
            article = ' '.join(articles)
            
            model = {
                "title":title,
                "author":author,
                "created_at":int(timestamp),
                "image":image,
                "article":article
            }
            print(mongo_column.insert_one(model).inserted_id)
            print("=====================================================")
        except AttributeError:
            continue

def main():
    get_list_link()
    crawler()
    mongo_client.close()
    if len(last_link) < 1 :
        set_key('.env',"LAST_BISNISDOTCOM",str(list_link[0]))
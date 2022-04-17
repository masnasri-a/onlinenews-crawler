
from bs4 import BeautifulSoup
import requests
import datetime
import logging
from util import util
from ingest import mongo_ingest
from dotenv import set_key, dotenv_values


conf = dotenv_values('.env')
last_link = str(conf.get('LAST_KONTAN'))
logging.basicConfig(format='%(asctime)s : %(message)s', level=logging.INFO)

mongo_client, mongo_column = mongo_ingest.mongo_client()
time_now = datetime.datetime.now()
dates = "tanggal={}&bulan={}&tahun={}".format(time_now.day,'0'+str(time_now.month) if time_now.month < 10 else time_now.month,time_now.year)
# dates = '{}/{}/{}'.format(time_now.year,'0'+str(time_now.month) if time_now.month < 10 else time_now.month,time_now.day)
# dates = 'tanggal=16&bulan=04&tahun=2022'
list_link = []


def get_list_link():
    url = "https://www.kontan.co.id/search/indeks?kanal=investasi&{}&pos=indeks".format(dates)
    page = requests.get(url)
    logging.info(page.status_code)
    soup = BeautifulSoup(page.content, 'html.parser')
    ul_list_news = soup.find('div', class_="list-berita")
    list_news = ul_list_news.find_all('li')
    for detail in list_news:
        a = detail.find('a')
        if 'https:'+a['href'] == last_link:
            print('not found')
            break
        else:
            links = str(a['href'])
            list_link.append('https:'+links)


def crawler():
    for link in list_link:
        try:
            page = requests.get(link)
            soup = BeautifulSoup(page.content, 'html.parser')
            logging.info(link)
            title = soup.find('h1',class_="detail-desk").text

            date_str = soup.find('div',class_="fs14 ff-opensans font-gray").text.replace(':',' ').replace('  ','').replace(' / ',' ').split()
            date_str[2] = util.month_converter(date_str[2])
            del date_str[0]
            del date_str[-1]
            date_str = ' '.join(date_str)
            timestamp_str = datetime.datetime.strptime(
                date_str, "%d %m %Y %H %M")
            timestamp = datetime.datetime.timestamp(timestamp_str)

            image = soup.find('div',class_="img-detail-desk").find('img')
            image = (image['src'])
            list_article = []
            article = soup.find('div',class_="tmpt-desk-kon")
            for all_p in article.find_all('p'):
                text = all_p.text
                if 'Reporter: ' in text:
                    author  = str(text).replace('Reporter: ','').split(' | ')[0]
                else:
                    list_article.append(str(text).replace('\t',' ').replace('\n',''))
            article = ' '.join(list_article)
            model = {
                "title": title,
                "author": author,
                "created_at": int(timestamp),
                "image": image,
                "article": article,
                "media":"kontan",
                "url":link
            }
            print(mongo_column.insert_one(model).inserted_id)
            print("============================")
        except AttributeError:
            continue


def main():
    get_list_link()
    crawler()
    mongo_client.close()
    if len(list_link) > 0:
        set_key('.env', "LAST_KONTAN", str(list_link[0]))
    else:
    	pass
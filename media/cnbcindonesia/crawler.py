from bs4 import BeautifulSoup
import requests
import datetime
import logging
from util import util
from ingest import mongo_ingest
from dotenv import set_key, dotenv_values


conf = dotenv_values('.env')
last_link = str(conf.get('LAST_CNBCINDONESIA'))
logging.basicConfig(format='%(asctime)s : %(message)s', level=logging.INFO)

mongo_client, mongo_column = mongo_ingest.mongo_client()
time_now = datetime.datetime.now()
dates = '{}/{}/{}'.format(time_now.year,'0'+str(time_now.month) if time_now.month < 10 else time_now.month,time_now.day)
# dates = '2022/04/16'
list_link = []

def get_list_link():
    url = "https://www.cnbcindonesia.com/market/indeks/5/1?date="+str(dates)
    page = requests.get(url)
    logging.info(page.status_code)
    soup = BeautifulSoup(page.content, 'html.parser')
    ul_list_news = soup.find('ul', class_="gtm_indeks_feed")
    list_news = ul_list_news.find_all('li')
    for detail in list_news:
        a = detail.find('a')
        if a['href'] == last_link:
            print('not found')
            break
        else:
            links = str(a['href'])
            list_link.append(links)



def crawler():
    for link in list_link:
        try:
            page = requests.get(link)
            soup = BeautifulSoup(page.content, 'html.parser')
            logging.info(link)
            title_ = soup.find('div', class_='jdl')
            title = title_.find('h1').text

            author = soup.find('div',class_="detail_box").find('div').text.replace('Market - ','').replace(', CNBC Indonesia','')
#           
            date_str = soup.find('div',class_="detail_box").find('div',class_="date").text.replace(':', ' ').split(' ')
            date_str[1] = util.month_converter(date_str[1])
            date_str = ' '.join(date_str)
            timestamp_str = datetime.datetime.strptime(
                date_str, "%d %m %Y %H %M")
            timestamp = datetime.datetime.timestamp(timestamp_str)

            main_image = soup.find('div', class_='media_artikel').find('img')['src']

            main_list_article = soup.find('div', class_="detail_text")
            list_article = main_list_article.find_all('p')
            articles = []
            for detail in list_article:
                if '<p>' in str(detail):
                    articles.append(detail.text.replace('\t',''))      
                else: 
                    span = detail.find_all('span')
                    for detail_span in span:
                        articles.append(detail_span.text.replace('\t',''))                
# 
            article = ' '.join(articles)
            model = {
                "title": title,
                "author": author,
                "created_at": int(timestamp),
                "image": main_image,
                "article": article,
                "media":"cnbcindonesia",
                "url":link
            }
            print(mongo_column.insert_one(model).inserted_id)
            # exit()
            print("=====================================================")
        except AttributeError:
            continue


def main():
    get_list_link()
    crawler()
    mongo_client.close()
    if len(list_link) > 0:
        set_key('.env', "LAST_CNBCINDONESIA", str(list_link[0]))
    else:
    	pass
#coding:utf-8
#!python3
#Pythonista for iOS 
#获取豆瓣电影Top250排行榜并生成csv文件
from bs4 import BeautifulSoup as bs
from multiprocessing.dummy import Pool
import re, codecs, csv, requests
movies = []
url = [
    'https://movie.douban.com/top250?start=%s' % str(i)
    for i in range(0, 226, 25)
]

def soup(url):
    html = requests.get(url).text
    items = bs(html).find_all('div', 'item')
    for item in items:
        movie_seq = item.find('em', '').get_text()
        movie_name = item.find('span', 'title').get_text()
        movie_rating = item.find('span', 'rating_num').get_text()
        try:
            movie_quote = item.find('span', 'inq').get_text()
        except:
            movie_quote = '无'
        movie_info = item.find('div', 'bd').find('p', '').get_text()
        movie_year = re.findall('\d{4}', movie_info)[0]
        try:
            movie_actor = re.findall('(?<=主演:).*', movie_info)[0]
            movie_director = re.findall('(?<=导演:).+?(?=主演)', movie_info)[0]
        except:
            movie_actor = '未知'
            movie_director = re.findall('(?<=导演:).+?', movie_info)[0]
        movie_country = re.findall('(?<=\d./).*(?=/)', movie_info)[0]
        movie = (movie_seq,movie_name, movie_year, movie_country, movie_rating,
                 movie_director, movie_actor, movie_quote)
        movies.append(movie)

pool = Pool(60)
pool.map(soup, url)
pool.close()
pool.join()
with open('movies.csv', 'w', encoding='utf8', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['排名', '电影', '年代', '国家', '评分', '导演', '演员', '简介'])
    writer.writerows(movies)

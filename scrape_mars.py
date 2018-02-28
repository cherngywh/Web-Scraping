import time
from splinter import Browser
from bs4 import BeautifulSoup
import requests
import pandas as pd


def init_browser():
    # @NOTE: Replace the path with your actual path to the chromedriver
    executable_path = {"executable_path": "/usr/local/bin/chromedriver"}
    return Browser("chrome", **executable_path, headless=False)

def scrape():
    browser = init_browser()
    # create mars_data dict that we can insert into mongo
    mars_data = {}



    # visit nasa for news of mars
    browser = Browser('chrome', headless=False)
    url_news = 'https://mars.nasa.gov/news/'
    browser.visit(url_news)

    # create a soup object from the html
    html_news = browser.html
    soup_news = BeautifulSoup(html_news, 'html.parser')

    div1 = soup_news.find('div', class_='content_title')
    news_title = div1.find('a').text
    news_p = soup_news.find('div', class_='article_teaser_body').text
    
    # add them into mars_data dict
    mars_data['news_title'] = news_title
    mars_data['news_p'] = news_p
    
    

    # visit JPL Mars space images to get a big image
    browser = Browser('chrome', headless=False)
    url_img = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url_img)
    browser.click_link_by_partial_text('FULL IMAGE')

    # create a soup object from the html
    html_img = browser.html
    soup_img = BeautifulSoup(html_img, 'html.parser')

    home = soup_img.find('article', class_="carousel_item")
    link = home.a['data-fancybox-href']
    featured_image_url = 'https://www.jpl.nasa.gov' + link

    # add it into mars_data dict
    mars_data['featured_image_url'] = featured_image_url

    

    # visit twitter to get Mars Weather
    url_weather = 'https://twitter.com/marswxreport?lang=en'
    html_weather = requests.get(url_weather)
    soup_weather = BeautifulSoup(html_weather.text, 'html.parser')

    tweet = soup_weather.find('div', class_='stream')
    mars_weather = tweet.find(text="Mars Weather").findNext('p').text

    # add it into mars_data dict
    mars_data['mars_weather'] = mars_weather

    
    
    # visit Mars facts and create a table by pandas
    url_facts = 'https://space-facts.com/mars/'
    facts_table = pd.read_html(url_facts)
    df = facts_table[0]
    df.columns = ['Description', 'Value']
    df.set_index(['Description'], inplace = True)
    df.to_html('Mars_df.html')

    # Generate a html table from dataframe
    html_table = df.to_html()
    html_table.replace('\n','')

    soup_table = BeautifulSoup(open('mars_df.html'),'html.parser')

    # create a dictionaries for all cells to create a table in html
    mars_facts = {}
    mars_list = []
    ths = [x.text.strip(':') for x in soup_table.table('th') if x.text != '']
    column_list = ths[0:2]
    column_list.reverse()
    th = ths[2:]
    td = [y.text for y in soup_table.table('td')]
    mars_facts = dict([(i, j) for i, j in zip(th, td)])
    mars_list.append(mars_facts)

    # add them into mars_data dict
    mars_data['columns'] = column_list
    mars_data['mars_list'] = mars_list
    
    
    
    # get the hemisperes imgs
    url_hemisperes = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url_hemisperes)

    html_hemisperes = browser.html
    soup_hem = BeautifulSoup(html_hemisperes, 'html.parser')
    jpg_links = soup_hem.find_all('div', class_='description')

    Mars_Hemisperes = []
    for link in jpg_links:
        info = {}
        h3 = link.find('h3').text
        info['title'] = h3
        browser.click_link_by_partial_text(h3)
        html2 = browser.html
        soup2 = BeautifulSoup(html2, 'html.parser')
        url = soup2.find('img', class_='wide-image')['src']
        info['img_url'] = 'https://astrogeology.usgs.gov' + url
        Mars_Hemisperes.append(info)
        browser.click_link_by_partial_text('Back')
    
    # add it into mars_data dict
    mars_data['Mars_Hemisperes'] = Mars_Hemisperes

    return mars_data


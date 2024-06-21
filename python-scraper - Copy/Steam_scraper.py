import requests
from bs4 import BeautifulSoup
import os
import json
from lxml import etree
import asyncio
import aiohttp
from time import time
import itertools
from GameTagDic import tags_count, function, months as month_dic, tags as tag_dic 

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

link = 'https://store.steampowered.com/search/?ndl=1&ignore_preferences=1&page=1'
game = ''
head = {'cookie': 'sessionid=cd46137aee87759ca68f1347'}
page_data = []

def get_pagination():
    param = {
        'page': 1,
    }

    req = requests.get(link, headers=head, params=param)
    soup = BeautifulSoup(req.text, 'html.parser')
    page_item = soup.find('div', 'search_pagination_right').find_all('a')

    try:
        total_item = int(page_item[4].text)
    except Exception:
        pass
        try:
            total_item = int(page_item[3].text)
        except Exception:
            pass
            try:
                total_item = int(page_item[2].text)
            except Exception:
                pass
                try:
                    total_item = int(page_item[1].text)
                except Exception:
                    pass
                    try:
                        total_item = int(page_item[0].text)
                    except Exception:
                        pass
    return total_item

async def start_async():
    pages = get_pagination()
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(1, pages):
            tasks.append(asyncio.create_task(scrape_steam_games(session, i)))

        global page_data
        nested_page_data = await asyncio.gather(*tasks)
        page_data = list(itertools.chain.from_iterable(nested_page_data))


async def scrape_steam_games(session, page_num):

    params = {'page': page_num}
    complete = False
    while not complete:
        try:
            async with session.get(link, params=params) as response:
                text = await response.text()
                soup = etree.HTML(text)
                content = soup.xpath('//*[@id="search_resultsRows"]/a')
                complete = True
        except Exception as e:
            print(e)
    
    data = []
    for i in content:
        url = i.attrib['href']
        title = i.xpath('./div[2]/div[1]/span')[0].text

        try:
            discount_original = i.xpath('./div[2]/div[4]/div/div/div[2]/div[1]')[0].text
            price = i.xpath('./div[2]/div[4]/div/div/div[2]/div[2]')[0].text
        except IndexError:
            discount_original = ' '
            try:
                price = i.xpath('./div[2]/div[4]/div/div/div/div')[0].text
            except IndexError:
                price = 'none'
        try:
            release = i.xpath('./div[2]/div[2]')[0].text.replace('\n', ' ').replace('\r', ' ').replace(',', '').strip().split(' ')
            release = f'{release[2]}-{month_dic[release[1]]}-{release[0]}'
        except:
            release = None

        split_url = url.split('/')
        app_id = split_url[-3]
        image = f'https://cdn.cloudflare.steamstatic.com/steam/apps/{app_id}/header.jpg'

        try:
            tags = i.attrib['data-ds-tagids']
            tags = tags.replace('[', '').replace(']', '').split(',')
            tag_list = []
            for tag in tags:
                real_tag = tag_dic[int(tag)]
                tag_list.append(real_tag)
                tags_count[real_tag] += 1

            tags_string = ', '.join(tag_list)
        
        except Exception as e:
            if not str(e) == "'data-ds-tagids'":
                print(e)
            tags_string = 'None'
        

        scraped_data = {
            'title': title,
            'price': price,
            'discount_original': discount_original,
            'release': release,
            'tags': tags_string,
            'link': url,
            'image': image
        }
        data.append(scraped_data)

    print(f"completed {page_num}")
    return data

if __name__ == "__main__":
    start_time = time()
    asyncio.run(start_async())
    with open(f'C:\Users\Vasil\source\repos\GameCatalog\GameCatalog\JavaScript\json_data.json', 'w+') as outfile:
            json.dump(page_data, outfile)
    function()
    print(f"Execution time: {time() - start_time:.2f} seconds")

import requests
from bs4 import BeautifulSoup
from ebooklib import epub
import regex as re
from tqdm import tqdm
import time

import utils
from AbstractBook import AbstractBook
from fake_useragent import UserAgent


# Get the content of a chapter, works only with LightNovelPub
def get_chapter_content(url):
    user_agent = UserAgent().random
    r = requests.get(url, headers={'User-Agent': user_agent})
    while r.status_code != 200:
        if r.status_code == 429:
            time.sleep(1)
            r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            continue
        elif r.status_code != 200:
            utils.log(f"Error {r.status_code} when fetching chapter {url}.")
            exit(1)


    soup = BeautifulSoup(r.content, 'html.parser')
    s = soup.find('div', class_='titles')
    chap_title = str(s.find('span', class_='chapter-title').text)

    s2 = soup.find('div', id='chapter-container')

    chap_content_raw = s2.find_all('p')
    chap_content = ""

    for k in range(len(chap_content_raw)):  # watermarks remover
        reg_res = re.findall(r'<sub>', str(chap_content_raw[k]))
        if len(reg_res) == 0:
            chap_content += str(chap_content_raw[k])
        else:
            continue

    return chap_title, chap_content


class LightNovelPubBook(AbstractBook):
    def __init__(self, url0, path=""):
        super().__init__(url0, path)

    def get_author(self):
        self.author = str(self.soup0.find('div', class_='author').find_all('span')[1].text)

    def get_title(self):
        self.title = str(self.soup0.find('div', class_='main-head').find_all('h1')[0].text[1:-1])

    def get_cover(self):
        print("Getting cover...")
        s = self.soup0.find('div', class_='fixed-img')
        urls = re.findall(r'(https?://[^\s]+)', str(s))
        cover_url = urls[0][:-1]    # There is an " at the end, who knows why

        utils.download_image(cover_url, './cover.jpg')

    def get_chapter_link(self):
        print("Retrieving chapters URLs ...")
        r = requests.get(self.url0 + "/chapters", headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(r.content, 'html.parser')
        s = soup.find('div', class_="pagination-container")

        res = str(s.find_all('li')[-1])  # always takes the last, that's not what we want

        if len(s.find_all("li", attrs={"class": "PagedList-skipToLast"})):
            indx, indx_gt = res.index("page="), res.index("&gt;&gt;")  # Works when there is a >>
            nbr_pages = int(res[indx + 5:indx_gt - 2])
        elif len(s.find_all("li", attrs={"class": "PagedList-skipToNext"})):
            res = str(s.find_all('li')[-2])  # We don't take the last thing '>' if it is the last
            indx, indx_gt = res.index("page="), res.index("\">")
            nbr_pages = int(res[indx + 5:indx_gt])
        else:
            nbr_pages = 1  # There are less than 100 chapters


        for k in range(1, nbr_pages + 1):
            url = self.url0 + f"/chapters/page-{k}"
            soup = BeautifulSoup(requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).content, 'html.parser')
            s = soup.find('ul', class_="chapter-list")
            lis = s.find_all('li')
            for li in lis:
                li = str(li)
                index_href = li.index('href="') + len('href="')
                index_end = li.index('" title')
                self.url_list.append("https://www.lightnovelpub.com" + li[index_href:index_end])
        print("Done.")

    def import_chapter_to_book_with_url(self, _uid="0"):
        i = 0
        for link in tqdm(self.url_list, desc="Processing URLs", total=len(self.url_list)):
            chap_title, chap_content = get_chapter_content(link)
            if not _uid:
                chap = epub.EpubHtml(title=chap_title, file_name=(utils.delete_spaces(chap_title) + '.xhtml'), lang='en')
            else:
                chap = epub.EpubHtml(title=chap_title, file_name=(utils.delete_spaces(chap_title) + '.xhtml'), lang='en',
                                     uid=str(int(_uid) + i))  # it works now
            i += 1
            chap.set_content('<html><body><h1>' + chap_title + '</h1>' + chap_content + '</body></html>')
            self.add_chapter(chap)

            self.book.spine.append(chap)
            # print(chap, "\n")
            self.book.toc.append(chap)  # self.book.toc = self.book.toc + (chap,)

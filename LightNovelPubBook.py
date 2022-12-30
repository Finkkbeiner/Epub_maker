import ebooklib
import requests
from bs4 import BeautifulSoup
from ebooklib import epub
import regex as re
import shutil
import platform
import os
from tqdm import tqdm
from AbstractBook import AbstractBook


def input_url0():
    url0 = input("Enter the book URL: ")
    return url0


def display_header():
    print("\n")
    print("\t\t   フィンクバイヌ")
    print("\t\t⎡⎴⎴⎴⎴⎴⎴⎴⎴⎴⎴⎴⎴⎴⎴⎴⎴⎴⎴⎤")
    print("\t\t⎢    Epub Maker    ⎥")
    print("\t\t⎣__________________⎦")
    print("\n\tIt only works with lightnovelpub.com.\n")


def log(txt):
    file = open("log_epubMaker.txt", 'a')
    file.write(txt)
    file.close()


def remove_cover():
    os.remove("cover.jpg")


def remove_log_file():
    try:
        os.remove("log_epubMaker.txt")
    except FileNotFoundError:
        pass


def delete_spaces(txt):
    # Also prevents the issues with "/" when creating a file (not to make it a folder), also with "\""
    tmp = ""
    for k in range(len(txt)):
        if txt[k] == ' ':
            tmp += '_'
        elif txt[k] == '"':
            tmp += '\''
        elif txt[k] == "/":
            tmp += ":"
        else:
            tmp += txt[k]
    return tmp


def get_chapter_content(url):
    r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    if r.status_code != 200:
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


# @TODO Check if the path is indeed a file and has a good extension OK
def get_path_of_existing_book():
    is_file = False
    while not is_file:
        path = input("Enter existing book path: ")
        if os.path.isfile(path) and os.path.splitext(path)[1] == '.epub':
            break
        print("Please enter a valid path.")
    return path


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
        cover_url = urls[0][:-1]  # There is a " at the end, who knows why

        res = requests.get(cover_url, headers={'User-Agent': 'Mozilla/5.0'}, stream=True)
        if res.status_code == 200:
            current_os = platform.system()
            match current_os:
                case 'Linux':
                    with open('./cover.jpg', 'wb') as f:
                        shutil.copyfileobj(res.raw, f)
                    log("You're on Linux.")
                case 'Windows':  # idk if it works, I'm on linux
                    with open(f'{os.getcwd()}\\cover.jpg', 'wb') as f:
                        shutil.copyfileobj(res.raw, f)
                    log("You're on Windows. :/")
        else:
            log("The cover couldn't be downloaded.")

    def import_chapter_to_book_with_url(self, _uid="0"):
        i = 0
        for link in tqdm(self.url_list, desc="Processing URLs", total=len(self.url_list)):
            # print(link[len(self.url0):])
            chap_title, chap_content = get_chapter_content(link)
            if not _uid:
                chap = epub.EpubHtml(title=chap_title, file_name=(delete_spaces(chap_title) + '.xhtml'), lang='en')
            else:
                chap = epub.EpubHtml(title=chap_title, file_name=(delete_spaces(chap_title) + '.xhtml'), lang='en',
                                     uid=str(int(_uid) + i))  # it works now
            i += 1
            chap.set_content('<html><body><h1>' + chap_title + '</h1>' + chap_content + '</body></html>')
            self.add_chapter(chap)

            self.book.spine.append(chap)
            # print(chap, "\n")
            self.book.toc.append(chap)  # self.book.toc = self.book.toc + (chap,)

    def get_chapter_link(self):
        print("Retrieving chapters URLs ...")
        r = requests.get(self.url0 + "/chapters", headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(r.content, 'html.parser')
        s = soup.find('div', class_="pagination-container")

        res = str(s.find_all('li')[-1])  # always takes the last, that's not what we want

        # soup.find_all("a", attrs={"class": "sister"})   classes: PagedList-skipToLast   PagedList-skipToNext

        if len(s.find_all("li", attrs={"class": "PagedList-skipToLast"})):
            indx, indx_gt = res.index("page-"), res.index("&gt;&gt")  # Works when there is a >>
            nbr_pages = int(res[indx + 5:indx_gt - 2])
        elif len(s.find_all("li", attrs={"class": "PagedList-skipToNext"})):
            res = str(s.find_all('li')[-2])  # We don't take the last thing '>' if it is the last
            indx, indx_gt = res.index("page-"), res.index("\">")
            nbr_pages = int(res[indx + 5:indx_gt])
        else:
            nbr_pages = 1  # There are less than 100 chapters

        # print("Nbr de pages de 100 chap: ", nbr_pages)

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


def create_book():
    remove_log_file()
    url0 = input_url0()
    book = LightNovelPubBook(url0)

    print("Getting author, title...")
    book.get_author()
    book.get_title()
    book.set_title_author()

    book.set_lang_isbn()

    book.get_cover()
    book.set_cover()

    book.get_chapter_link()
    book.import_chapter_to_book_with_url()

    book.add_ncx_nav()

    book.get_css_style()
    book.set_css_style()

    book.write()
    remove_cover()


def update_book():
    url0 = input_url0()
    path = get_path_of_existing_book()
    book = LightNovelPubBook(url0, path)
    lst_chap = book.get_last_chapter()
    print(f"Last chapter (in the .epub): {lst_chap}.")

    book.select_needed_chapters(lst_chap)
    if len(book.url_list) == 0:
        print("No chapters to update.\nExiting...")
        return

    book.import_chapter_to_book_with_url(str(lst_chap))

    # Removing the old files and adding the new ones
    book.book.items.remove(book.book.get_item_with_id('nav'))
    book.book.items.remove(book.book.get_item_with_id('ncx'))
    book.add_ncx_nav()

    book.write()


if __name__ == "__main__":
    display_header()

    print('\t[1] Create an ebook')
    print('\t[2] Update an ebook')
    print('\t[_] Quit')

    choice = input("Your choice: ")
    try:
        if int(choice) == 1:
            create_book()
        elif int(choice) == 2:
            update_book()
        else:
            print("Exiting...")
    except ValueError:
        print("Exiting...")

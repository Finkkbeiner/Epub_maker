import requests
from bs4 import BeautifulSoup
from ebooklib import epub
import regex as re
import shutil
import platform
import os


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
        if (txt[k] == ' '):
            tmp += '_'
        elif (txt[k] == '"'):
            tmp += '\''
        elif (txt[k] == "/"):
            tmp += ":"
        else:
            tmp += txt[k]
    return tmp


def get_chapter_content(url):
    r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(r.content, 'html.parser')
    s = soup.find('div', class_='titles')

    chap_title = str(s.find('span', class_='chapter-title').text)

    s2 = soup.find('div', id='chapter-container')

    chap_content_raw = s2.find_all('p')
    chap_content = ""

    for k in range(len(chap_content_raw)):  # watermarks remover
        reg_res = re.findall(r'<sub>', str(chap_content_raw[k]))
        if (len(reg_res) == 0):
            chap_content += str(chap_content_raw[k])
        else:
            continue

    return chap_title, chap_content


class Book:
    def __init__(self, url0):
        self.url0 = url0
        self.url_list = []
        self.book = epub.EpubBook()
        self.style = ""
        self.soup0 = BeautifulSoup(requests.get(url0, headers={'User-Agent': 'Mozilla/5.0'}).content, 'html.parser')
        self.author = ""
        self.title = ""
        self.book.toc = ()

    def get_author(self):
        self.author = str(self.soup0.find('div', class_='author').find_all('span')[1].text)

    def get_title(self):
        self.title = str(self.soup0.find('div', class_='main-head').find_all('h1')[0].text[1:-1])

    def set_title_author(self):
        self.book.set_title(self.title)
        self.book.add_author(self.author)

    def set_lang_isbn(self, lang="en", isbn="No ISBN"):
        self.book.set_language(lang)
        self.book.set_identifier(isbn)

    def get_cover(self):
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

    def set_cover(self, path="cover.jpg"):
        try:
            self.book.set_cover("cover.jpg", open('cover.jpg', 'rb').read())
        except FileNotFoundError:
            log("The cover file was not found.")
            print("The cover file was not found.")

    def get_css_style(self):
        # @TODO Try to find a way to add a path as a parameter, if none entered, use the basic value
        self.style = '''
            BODY {color: white;}
            nav[epub|type~='toc'] > ol > li > ol  {
                list-style-type:square;
            }
            nav[epub|type~='toc'] > ol > li > ol > li {
                    margin-top: 0.3em;
            }
        '''

    def set_css_style(self):
        self.book.add_item(epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=self.style))

    def add_chapter(self, chapter):
        self.book.add_item(chapter)

    def add_ncx_nav(self):
        # Need to be added at the end, right before closing the ebook
        self.book.add_item(epub.EpubNcx())
        self.book.add_item(epub.EpubNav())

    def import_chapter_to_book_with_url(self):
        for link in self.url_list:
            print(link[len(self.url0):])
            chap_title, chap_content = get_chapter_content(link)
            chap = epub.EpubHtml(title=chap_title, file_name=(delete_spaces(chap_title) + '.xhtml'), lang='en')
            chap.set_content('<html><body><h1>' + chap_title + '</h1>' + chap_content + '</body></html>')
            self.add_chapter(chap)
            self.book.spine.append(chap)

            self.book.toc = self.book.toc + (chap,)

    def get_chapter_link(self):
        print("Retrieving chapters URLs ...")
        r = requests.get(self.url0 + "/chapters", headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(r.content, 'html.parser')
        s = soup.find('div', class_="pagination-container")
        res = str(s.find_all('li')[-1])
        try:
            indx, indx_gt = res.index("page-"), res.index("&gt")
            nbr_pages = int(res[indx + 5:indx_gt - 2])
        except ValueError:
            nbr_pages = 1       # There are less than 100 chapters

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

    def write(self):
        epub.write_epub(delete_spaces(str(self.title)) + '.epub', self.book, {})


if __name__ == "__main__":
    remove_log_file()
    display_header()
    url0 = input_url0()
    book = Book(url0)

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


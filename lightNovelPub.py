#!/usr/bin/env python3
# @TODO faire une fonction de log
# https://www.lightnovelpub.com/novel/lord-of-the-mysteries-wn-09092253/275-chapter-900
import requests
from bs4 import BeautifulSoup
from ebooklib import epub
import regex as re
import shutil


def log(txt):
    file = open("log.txt", 'a')
    file.write(txt)
    file.close()


def input_url0():
    print("\t\tCAREFUL, it only works with ligntNovelPub.com !\n")
    #nbr_of_chap = eval(input("Number of chapters : "))
    url = input("Enter the book URL : ")                    #+ "chapter-1/"
    return url                                              # , nbr_of_chap



def get_cover(url):
    r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(r.content, 'html.parser')
    s = soup.find('div', class_='fixed-img')
    #need to get the src value
    urls = re.findall(r'(https?://[^\s]+)', str(s))
    cover_url = urls[0][:-1]                            # There is a " at the end, who knows why
    #print(cover_url)

    res = requests.get(cover_url, headers={'User-Agent': 'Mozilla/5.0'}, stream = True)
    if res.status_code == 200:
        with open('./cover.jpg', 'wb') as f:
            shutil.copyfileobj(res.raw, f)
    else:
        print("The cover couldn't be downloaded.")



def get_chapter_content(url):
    r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(r.content, 'html.parser')
    s = soup.find('div', class_='titles')
    
    chap_title = str(s.find('span', class_='chapter-title').text)                       # Chapter title

    s2 = soup.find('div', id='chapter-container')

    chap_content_raw = s2.find_all('p')#[1:]                      # Chapter content
    chap_content = ""

    for k in range(len(chap_content_raw)):      # watermarks remover
        reg_res = re.findall(r'<sub>', str(chap_content_raw[k]))
        if (len(reg_res) == 0):
            chap_content += str(chap_content_raw[k])
        else:
            continue
            #print('Watermark deleted.')

    """ Useless for now
    if chap_title[0:7] != "Chapter":                 # If there isn't "Chapter" at the beginning of the chapter title
        chap_title = "Chapter " + chap_title
    """
    return chap_title, chap_content


# @TODO Some books start at chapter 0!
def get_author_title_nbrChap_urlTemplate(url):
    r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(r.content, 'html.parser')

    # Author
    s = soup.find('div', class_='author')
    author = str(s.find_all('span')[1].text)
    #print(f"Author : {author}\n")

    # Title
    s2 = soup.find('div', class_='main-head')
    title = str(s2.find_all('h1')[0].text[1:-1]) # [1:-1] because there is a \n a the beginning and at the end it seems
    #print(f"Title : {title}")

    # Number of chapter
    s3 = soup.find('div', class_='header-stats')
    nbrChap = int(s3.find_all('strong')[0].text)
    #print(f"nbrChap : {nbrChap}")

    # URL template   @TODO Try to simplifiate that
    # @TODO Some books have a name like -chapter-1-518116 -> indx = string.index("-1-") -> sauvegarder ce qu'il y a après dans une variable
    s4 = soup.find('nav', class_='links')
    urlTemplate = [];
    for link in s4.find_all('a'):
        if link.has_attr('href'):
            urlTemplate.append(link.attrs['href'])
    
    urlTemplate = urlTemplate[0]
    i = urlTemplate.index('-1')
    urlTemplateEnd = urlTemplate[i+2:]
    urlTemplate = 'https://www.lightnovelpub.com' + urlTemplate[:i+1]
    #urlTemplate =  'https://www.lightnovelpub.com' + urlTemplate[0][:-1]

    return author, title, nbrChap, urlTemplate, urlTemplateEnd


def initBook(title, author):
    book = epub.EpubBook()
    book.set_identifier('No ISBN')
    book.set_title(title)
    book.set_language('en')
    book.add_author(author)
    return book


def create_chapter(chap_name, xhtml_file):
    chap = epub.EpubHtml(title=chap_name, file_name=xhtml_file, lang='en')
    return chap

def add_chapter(book, chapter):
    book.add_item(chapter)

def add_cover(book, path):
    book.add_item(epub.EpubCover(path))

# Ca marche pas
def add_NCX_Nav(book):
    # Need to be added at the end
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())


def delete_spaces(txt):         # Also prevents the issues with "/" when creating a file (not to make it a folder), also with "\""
    tmp = ""
    for k in range(len(txt)):
        if(txt[k] == ' '):
            tmp += '_'
        elif (txt[k] == '"'):
            tmp += '\''
        elif (txt[k] == "/"):
            tmp += ":"
        else:
            tmp += txt[k]
    return tmp


def chap_to_xhtml(chap_title, chap_content, title):
    chap_title_unspaced = delete_spaces(chap_title)
    filename = "./temp/" + chap_title_unspaced
    xhtml_file = open(filename, 'w')

    content = '<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="en-EN">'
    content += '<head><title>' + title + '</title></head>'
    content += '<body xml:lang="en-EN"><div><h3>' + chap_title + '</h3>'
    content += str(chap_content) + '</div></body></html>'

    xhtml_file.write(content)
    xhtml_file.close()

def chap_to_xhtml2(chap_title, chap_content):
    c1 = epub.EpubHtml(title=chap_title, file_name=delete_spaces(chap_title), lang='en')
    c1.set_content(u'<html><body><h1>' + chap_title + '</h1>' + str(chap_content) + '</body></html>')
    return c1


#///////////////////  TOC (qui sert pas)  ///////////////////////
def create_toc(main_title):
    # à la fin, il manquera '</navMap></ncx>'
    f = open('./temp/toc.ncx', 'w')
    content = '<?xml version="1.0" encoding="utf-8" ?>'
    content += '<ncx version="2005-1" xmlns="http://www.daisy.org/z3986/2005/ncx/">'
    content += '<head></head><docTitle><text>' + main_title + '</text></docTitle><navMap>'

    f.write(content)
    f.close()

def add_navPoint(i, chap_title, chap_title_unspaced):
    content = f'<navPoint id="navPoint{i}"><navLabel><text>' + chap_title + '</text></navLabel>'
    content += f'<content src="./temp/{chap_title_unspaced}"/></navPoint>'
    f = open('./temp/toc.ncx', 'a')
    f.write(content)
    f.close()

def end_toc():
    f = open('./temp/toc.ncx', 'a')
    f.write('</navMap></ncx>')
    f.close()
#/////////////////////////////////////////////////




###################################################################################




if __name__ == "__main__":
    url = input_url0()
    #url = 'https://www.lightnovelpub.com/novel/the-beginning-after-the-end-web-novel-09092253'
    #print(url)

    get_cover(url)

    
    author, title, nbrChap, urlTemplate, urlTemplateEnd = get_author_title_nbrChap_urlTemplate(url)
    #url = 'https://www.lightnovelpub.com/novel/lord-of-the-mysteries-wn-09092253/'

    
    book = initBook(title + '.epub', author)
    book.spine = ['nav']

    # add cover image
    try:
        book.set_cover("cover.jpg", open('cover.jpg', 'rb').read())
    except FileNotFoundError:
        print("The cover file was not found.")
    
    
    #add all the chapters
    for k in range(1, nbrChap + 1):
        try:
            curr_url = urlTemplate + f'{k}' + urlTemplateEnd
            chap_title, chap_content = get_chapter_content(curr_url)
        except AttributeError:
            try:
                curr_url = urlTemplate + f'{k}'
                chap_title, chap_content = get_chapter_content(curr_url)
            except:
                print(f">- Chapter {k} failed -<")
                log(f">- Chapter {k} failed -<\n")
                continue

        print(f"{chap_title}")
        chap = epub.EpubHtml(title=chap_title, file_name=(delete_spaces(chap_title) + '.xhtml'), lang='en')
        chap.set_content('<html><body><h1>' + chap_title + '</h1>' + chap_content + '</body></html>')
        add_chapter(book, chap)
        book.spine.append(chap)

    #add_NCX_Nav(book)
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())


    # define CSS style
    style = 'BODY {color: white;}'
    nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)


    # add CSS file
    book.add_item(nav_css)

    epub.write_epub(delete_spaces(str(title)) + '.epub', book, {})
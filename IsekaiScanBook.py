import requests
from bs4 import BeautifulSoup
from ebooklib import epub
import regex as re
import utils
import shutil
import os
from tqdm import tqdm

from AbstractBook import AbstractBook


def get_chapter_content(url):
	""" Return the title of the chapter
		and the list of images URL to download
	"""
	chap_title = url[url.find('chapter'):]  # :-1
	content_list = []

	r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
	if r.status_code != 200:
		utils.log(f"Error {r.status_code} when fetching chapter {url}.")
		exit(1)

	soup = BeautifulSoup(r.content, 'html.parser')

	s = soup.find_all('div', class_="page-break")

	for div in s:
		div = str(div)
		index_href = div.index('data-src="\t\t\t\n\t\t\t') + len(
			'data-src="\t\t\t\n\t\t\t')  # Pas du tout casse couille
		index_end = div.find('" id="')
		content_list.append(div[index_href:index_end])

	# print(content_list)
	return chap_title.capitalize(), content_list


class IsekaiScanBook(AbstractBook):
	def __init__(self, url0, path=""):
		super().__init__(url0, path)

	def get_author(self):
		try:
			self.author = str(self.soup0.find('div', class_='author-content').find_all('a')[0].text)
		except AttributeError:
			self.author = "No author in source."
			utils.log("No author in source.")

	def get_title(self):
		self.title = str(self.soup0.find('div', class_='post-title').find_all('h1')[0].text)
		if self.title.startswith("\nHOT\n"):  # When the manga is trendy, there is a little label
			self.title = self.title[5:]

	def get_cover(self):
		print("Getting cover...")
		s = self.soup0.find('div', class_='summary_image')
		urls = re.findall(r'(https?://[^\s]+)', str(s))
		cover_url = urls[1][:-1]  # There is an " at the end
		utils.download_image(cover_url, 'cover.png')

	def get_chapter_link(self):
		s = self.soup0.find_all('li', class_="wp-manga-chapter")

		for li in tqdm(s, desc="Retrieving chapters URLs", total=len(s)):
			li = str(li)
			index_href = li.index('href="') + len('href="')
			index_end = li.find('/">')
			self.url_list.append(li[index_href:index_end])

		# Didn't find any easier way to do this
		ordered = []
		for link in self.url_list:
			ordered.insert(0, link)
		self.url_list = ordered

	def import_chapter_to_book_with_url(self, _uid="0"):
		try:
			os.mkdir('./temp')
		except FileExistsError:
			shutil.rmtree("./temp")
			os.mkdir('./temp')

		i = 0
		for chapter_link in tqdm(self.url_list, desc="Processing URLs", total=len(self.url_list)):
			chap_title, chap_content = get_chapter_content(chapter_link)

			if not _uid:
				chap = epub.EpubHtml(title=chap_title, file_name=(utils.delete_spaces(chap_title) + '.xhtml'),
									 lang='en')
			else:
				chap = epub.EpubHtml(title=chap_title, file_name=(utils.delete_spaces(chap_title) + '.xhtml'),
									 lang='en', uid=str(int(_uid) + i))
			i += 1

			content = ""
			for k in range(len(chap_content)):
				img_file_name = f'chapter{i}_img{k}.jpg'  # I hope it's always jpg (should because lighter)
				utils.download_image(chap_content[k], 'temp/' + img_file_name)  # Img is downloaded
				image_content = open('temp/' + img_file_name, "rb").read()  # Opening downloaded image
				img = epub.EpubItem(uid=f"{utils.delete_spaces(chap_title)}_img{k}", file_name=img_file_name,
									media_type="image/jpeg", content=image_content)

				content += f'<p class="container"><img alt="{img_file_name}" src={img_file_name} /></p>'

				self.book.add_item(img)

			chap.set_content(f'<h1>{chap_title}</h1>' + content)  # We don't need chapter name
			self.add_chapter(chap)

			self.book.spine.append(chap)
			self.book.toc.append(chap)
		shutil.rmtree("./temp")  # delete temporary file

from LightNovelPubBook import LightNovelPubBook
from IsekaiScanBook import IsekaiScanBook
import utils



def create_book(book):
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
	utils.remove_cover()


def update_book(book):
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
	utils.remove_log_file()
	utils.display_header()

	source = utils.choose_source()
	choice = utils.choose_create_update()

	url0 = utils.input_url0()     # Systematic

	if choice == utils.CREATE:
		if source == utils.LIGHTNOVELPUB:
			print("Create LightNovelPub")
			book = LightNovelPubBook(url0)
		elif source == utils.ISEKAISCAN:
			print("Create Manga sauce")
			book = IsekaiScanBook(url0)
			book.book.set_direction("rtl")  # reading right-to-left, but does not work
		# Common part (function)
		create_book(book)


	elif choice == utils.UPDATE:
		path = utils.get_path_of_existing_book()
		if source == utils.LIGHTNOVELPUB:
			print("Update LightNovelPub")
			book = LightNovelPubBook(url0, path)
		elif source == utils.ISEKAISCAN:
			print("Update Manga sauce")
			book = IsekaiScanBook(url0, path)
		# Common part (function)
		update_book(book)

	else:
		print("Exiting...")
		exit(-1)

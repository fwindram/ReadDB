# ReadDB v 0.0.4
# Francis Windram 2016
# Python 3.4
#
# Created:  21/12/16
# Modified: 24/12/16
#
# A Python3/SQL project for building and maintaining a book database.
#
# ===== TO DO LIST =====
# TODO - If extant, open SQLite db
# DONE - Else construct new DB on first run with required tables/columns
# DONE - ADD basic SQL logic for addition
# TODO - ADD basic SQL logic for deletion
# TODO - ADD SQL search functionality
# DONE - ADD auto-ISBN lookup for quick entry (using isbntools)
#       - isbnlib.meta() returns dict in the following style:
#     {
#         'Year':'yyyy',
#         'ISBN-13':'xxxxxxxxxxxxx',
#         'Publisher':'publisher',
#         'Authors':['Fore M. Sur', 'First Last'],
#         'Title':'The Title of the Book'
#         'Language':'language'
#     }
# TODO - ADD isbn_lookup error handling
# TODO - ADD csv import wrapper for list handler
# DONE - ADD ISBN list import logic to support csv reading
# TODO - ADD error logging
# TODO - ADD tkinter interface
# TODO - FIX title handling in author splitting code - use nameparser


import sqlite3
import isbnlib
# import logging
# from beeprint import pp     # beeprint for easy class debugging


class Book:

    bookid = "NULL"

    def __init__(self, year, isbn13, publisher, author_fname, author_sname, title, language):
        self.year = year
        self.isbn13 = isbn13
        self.publisher = publisher
        self.author_fname = author_fname
        self.author_sname = author_sname
        self.title = title
        self.language = language


# === DB Functions ===
def create_db(recreate=False):
    """Creates DB with correct tables (drops table if required)"""
    connection = sqlite3.connect("books.sqlite")
    cursor = connection.cursor()
    if recreate:
        try:
            print("Dropping table...")
            cursor.execute("""DROP TABLE employee;""")
            print("Table dropped.")
        except sqlite3.OperationalError:
            print("\n!!! === No table present === !!!\n")
    dbcreate_cmd = """
    CREATE TABLE books (
    bookid INTEGER PRIMARY KEY,
    title VARCHAR(255),
    surname VARCHAR(30),
    forename VARCHAR(30),
    isbn INTEGER(13),
    publisher VARCHAR(100),
    year INTEGER,
    language VARCHAR(30));"""
    print("Creating table...")
    cursor.execute(dbcreate_cmd)
    print("Table created.")

    connection.commit()
    connection.close()


def add_book(book):
    """Adds book to books.sqlite"""
    connection = sqlite3.connect("books.sqlite")
    cursor = connection.cursor()
    if book:
        try:
            # Construct SQL command with book metadata
            # (Eurgh, must be a nicer way to format this.)
            add_cmd = """INSERT INTO books (bookid, title, surname, forename, isbn, publisher, year, language)
            VALUES ({0}, "{1}", "{2}", "{3}", "{4}", "{5}", "{6}", "{7}");""".format(book.bookid, book.title,
                                                                                     book.author_sname,
                                                                                     book.author_fname, book.isbn13,
                                                                                     book.publisher, book.year,
                                                                                     book.language)
            cursor.execute(add_cmd)
        except sqlite3.OperationalError:
            print("Error adding book {0} to library".format(book.isbn13))
    else:
        print("No book object provided")
    connection.commit()
    connection.close()


# === Non-DB Functions ===
def isbn_lookup(isbn):
    """Looks up ISBN and spits out object with all necessary data for DB"""
    # b_meta test data
    b_meta = {'Year': '2015',
              'ISBN-13': '9780230769465',
              'Publisher': '',
              'Authors': ['Peter F. Hamilton', 'Piper-Verlag', 'Wolfgang Thon'],
              'Title': 'The abyss beyond dreams: a novel of the Commonwealth',
              'Language': ''
              }
    primary_author = ['']
    isbn_error = False
    if isbnlib.is_isbn10(isbn):
        isbn = isbnlib.to_isbn13(isbn)
    if isbnlib.is_isbn13(isbn):     # if ISBN provided is ISBN-13
        isbn = isbnlib.EAN13(isbn)  # convert to validated, canonical ISBN-13 (remove hyphens etc.)
        b_meta = isbnlib.meta(isbn)          # look up metadata, return dict
        primary_author = b_meta["Authors"][0].split(" ")
    else:
        isbn_error = True       # Exit flag

    book_inst = Book(
        b_meta["Year"],
        b_meta["ISBN-13"],
        b_meta["Publisher"],
        primary_author[0],
        primary_author[len(primary_author) - 1],
        b_meta["Title"],
        b_meta["Language"],
    )

    return book_inst, isbn_error


def booklist_parser(isbn_list):
    """Parses list of ISBNs and adds them to the database if valid."""
    iteration = 0
    errorcount = 0
    print("=== Parsing ISBN list. ===")
    for x in isbn_list:
        iteration += 1
        print("Processing ISBN {0} ({1}/{2})".format(x, iteration, len(isbn_list)))
        entry_meta = isbn_lookup(str(x))
        if entry_meta[1]:
            print("!!! ISBN error in {0}!!!".format(x))
            errorcount += 1
        else:
            entry_meta = entry_meta[0]
            add_book(entry_meta)
            print("{0} added".format(x))
    print("\n\n=== Book list parsed. ===\n"
          "Books added: {0}\n"
          "(Errors: {1})".format(len(isbn_list) - errorcount, errorcount))


def main():     # Test main for quick manual DB writing.
    # booktest = isbn_lookup("0904727203")[0]
    # pp(booktest)
    # add_book(booktest)
    # print("Book added.")
    isbns = [9780230769465, "9781844009824", 978184533657, "0904727203"]    # Should produce 3 book entries + 1 Error
    booklist_parser(isbns)

# create_db(recreate=False)
main()

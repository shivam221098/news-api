import sqlite3
from datetime import datetime
import get_news

DATABASE_FILENAME = "bookmark.db"


def database_setup():
    connection = sqlite3.connect(DATABASE_FILENAME)
    cursor = connection.cursor()
    cursor.execute("DROP TABLE IF EXISTS bookmarks")
    cursor.execute("DROP TABLE IF EXISTS bookmark_detail")
    cursor.execute("DROP TABLE IF EXISTS bookmark_sources")
    connection.commit()

    # Creating table for bookmarking news
    with connection:
        cursor.execute("""
                        CREATE TABLE bookmarks(
                            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL ,
                            source_id TEXT,
                            source_name TEXT,
                            author TEXT,
                            title TEXT,
                            description TEXT,
                            url TEXT,
                            url_to_image TEXT,
                            published_at DATETIME,
                            content TEXT,
                            fetched_at DATETIME DEFAULT NOW
                        )
            """)

    # creating table for saving news details
    # type field is a type of news (top-headlines or regular news)
    with connection:
        cursor.execute("""
        CREATE TABLE bookmark_detail(
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            country TEXT,
            category TEXT,
            sources TEXT,
            type TEXT,
            bookmark_id INTEGER,
            FOREIGN KEY (bookmark_id) REFERENCES bookmarks(id) ON DELETE CASCADE 
                    )
        """)
    connection.commit()

    # Creating table for bookmarking news sources
    with connection:
        cursor.execute("""
        CREATE TABLE bookmark_sources(
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            source_id TEXT,
            source_name TEXT,
            description TEXT,
            url TEXT,
            category TEXT,
            language TEXT,
            country TEXT,
            fetched_on DATETIME DEFAULT NOW
        )
        """)

    connection.close()  # Closes the connection to database


# Saving specified article(news) in database. i.e bookmarked
def save_bookmark(articles, type):  # @articles are all articles in request dictionary
    try:
        filter_by = get_news.filter_by
        print("\nThe number of news which you want to bookmark")
        number = int(input("Enter: "))
        article = articles[number - 1]
        connection = sqlite3.connect(DATABASE_FILENAME)
        cursor = connection.cursor()

        # Saving article details in database
        cursor.execute("""
            INSERT INTO bookmarks(source_id, source_name, author, title, description, 
                        url, url_to_image, published_at, content) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (article.get("source").get("id"), article.get("source").get("name"), article.get("author"), article.get("title"),
              article.get("description"), article.get("url"), article.get("urlToImage"),
              datetime.strptime(article.get("publishedAt"), "%Y-%m-%dT%H:%M:%SZ"), article.get("content")))
        connection.commit()

        # Getting id of article that is to be bookmarked
        cursor.execute("""
            SELECT id FROM bookmarks WHERE url = ?
            """, (article.get("url"),))
        bookmark_id = cursor.fetchone()

        # Saving all the filter details in database. @filter_details are the details on which data is fetched
        cursor.execute("""
            INSERT INTO bookmark_detail(country, category, sources, type, bookmark_id) VALUES (?, ?, ?, ?, ?)
        """, (filter_by.get("country"), filter_by.get("category"), filter_by.get("sources"),
              type, bookmark_id[0]))

        connection.commit()
        connection.close()  # Closes the connection
        print(f"\nNews number {number} bookmarked successfully.\n")
    except Exception as e:
        if e is IndexError:
            print(f"News number {number} is not present")

        elif e is sqlite3.IntegrityError:
            print("\nSomething went wrong. A log is created in your directory. "
                  "Please contact developer for more information.\n")


def show_bookmarks():
    connection = sqlite3.connect(DATABASE_FILENAME)  # Opens connection with the database
    cursor = connection.cursor()

    cursor.execute("""
        SELECT source_id, source_name, author, title, description, url, url_to_image, published_at, content FROM bookmarks
    """)  # Query
    all_bookmarks = cursor.fetchall()
    bookmark_dict = {}

    if len(all_bookmarks) == 0:  # if there is no bookmark in the databse then dictionary with status error is returned.
        bookmark_dict.update({"status": "error", "message": "No data"})
    else:
        bookmark_dict.update({"status": "ok"})

    articles = []
    for bookmark in all_bookmarks:

        # converting date and time in actual format "%Y-%m-%dT%H:%M:%SZ"
        # bookmark is tuple and it's values can't be changed, first it's converted into list then
        # datetime is changed and again converted into tuple
        bookmark = list(bookmark)
        date_format = bookmark[7].split()
        bookmark[7] = date_format[0] + "T" + date_format[1] + "Z"
        bookmark = tuple(bookmark)

        # appending all articles fetched from bookmarks in @articles list
        articles.append({"source": {'id': bookmark[0], 'name': bookmark[1]}, 'author': bookmark[2], 'title': bookmark[3],
                         'description': bookmark[4], "url": bookmark[5], "urlToImage": bookmark[6],
                         'publishedAt': bookmark[7], "content": bookmark[8]})

    # Addinf some more information in @bookmark_dict
    bookmark_dict.update({"totalResults": len(articles), 'articles': articles})

    # Finally returning fetched results
    return bookmark_dict


def save_sources_bookmark(sources):
    try:
        print("\nThe number of sourece which you want to bookmark")
        number = int(input("Enter: "))

        source = sources[number - 1]

        connection = sqlite3.connect(DATABASE_FILENAME)
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO bookmark_sources(source_id, source_name, description, url, category, language, country) 
            VALUES (?, ?, ?, ?, ?, ?, ?) """, (
            source.get("id"), source.get("name"), source.get("description"),
            source.get("url"), source.get("category"),
            source.get("language"), source.get("country")
        ))

        connection.commit()  # Saves the changes
        connection.close()  # Closes the connection
        print(f"\nSource {number} bookmarked successfully.\n")

    except Exception as e:
        if e is IndexError:
            print(f"News number {number} is not present")
        if e is sqlite3.IntegrityError:
            print("\nSomething went wrong. A log is created in your directory. "
                  "Please contact developer for more information.\n")


def show_bookmarked_sources():
    connection = sqlite3.connect(DATABASE_FILENAME)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT source_id, source_name, description, url, category, language, country FROM bookmark_sources
    """)

    all_bookmarks = cursor.fetchall()
    sources = []
    bookmark_dict = {}

    if len(all_bookmarks) == 0:
        bookmark_dict.update({"status": "error", "message": "No data"})
    else:
        bookmark_dict.update({"status": "ok"})

    for source in all_bookmarks:
        sources.append({"id": source[0],
                        "name": source[1],
                        "description": source[2],
                        "url": source[3],
                        "category": source[4],
                        "language": source[5],
                        "country": source[6]})

    bookmark_dict.update({"sources": sources})

    return bookmark_dict

if __name__ == '__main__':
    dt = "2020-10-18 12:00:00"
    print(datetime.strptime(dt, "%Y-%m-%d %H:%M:%S"))
    database_setup()
    print(show_bookmarks())
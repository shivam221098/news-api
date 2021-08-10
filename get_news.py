import requests
import os
import logging
import sqlite3
from datetime import datetime
from bookmark_db import DATABASE_FILENAME

KEY = os.environ.get("NEWS_KEY")  # API key fetched from system environment variables

filter_by = {"status": "ok"}


# This class is taking all the required parameters from user and fetches the news content from newsapi.org
class News:
    def __init__(self, news_type, country=None, category=None, sources=None, q=None, language=None, pagesize=100):
        global filter_by
        self.query = {}  # @query dictionary is the dictionary of parameters to be passed with request
        self.news_type = news_type  # type of news to be fetched e.g. top-headlines, everything or from sources

        # if any of the parameter is not none then it will be added in @query dictionary
        if country:
            self.query.update({"country": country})
        if category:
            self.query.update({"category": category})
        if sources:
            self.query.update({"sources": sources})
        if q:
            self.query.update({"q": q})
        if pagesize:
            self.query.update({"pageSize": pagesize})
        if language:
            self.query.update({"language": language})
        self.query.update({"apiKey": KEY})

    # Function for fetching top-headlines news from newsapi.org
    def fetch_news_headlines(self):
        global filter_by
        try:
            db = False
            filter_by = self.query  # Updating @filter_by with all the available details regarding news

            db_data = get_news_from_db(self.query, self.news_type)
            if db_data.get("status") == "ok":
                db = True
                return db_data, db

            request = requests.get("https://newsapi.org/v2/" + self.news_type, params=self.query).json()
            return request, db
        except requests.exceptions.ConnectionError:
            return {"status": "error", "message": "Internet unavailable"}

    # Function for fetching all news that is on newsapi.org
    def fetch_everything(self, qInTitle, domains, excludeDomains, from_date, to_date, sortBy):
        global filter_by
        # updating the query dictionary with all fields if they are available (i.e. not None)
        if qInTitle:
            self.query.update({"qInTitle": qInTitle})
        if domains:
            self.query.update({"domains": domains})
        if excludeDomains:
            self.query.update({"excludeDomains": excludeDomains})
        if from_date and to_date:
            self.query.update({"from": from_date, "to": to_date})
        if sortBy:
            self.query.update({"sortBy": sortBy})

        try:
            filter_by = self.query  # Updating @filter_by with all the available details regarding news
            request = requests.get("https://newsapi.org/v2/" + self.news_type, params=self.query).json()
            return request
        except requests.exceptions.ConnectionError:
            return {"status": "error", "message": "Internet unavailable"}

    def all_sources(self):
        global filter_by
        try:
            filter_by = self.query  # Updating @filter_by with all the available details regarding news
            # TODO:
            # print(self.query)
            request = requests.get("https://newsapi.org/v2/" + self.news_type, params=self.query).json()
            return request
        except requests.exceptions.ConnectionError:
            return {"status": "error", "message": "Internet unavailable"}

    def return_filter(self):
        return self.query


if __name__ == '__main__':
    news = News("top-headlines", country="us", category="sports", q="trump")
    print(news.fetch_news_headlines())

"""
*********************************************************************************************************
    This section helps to make a copy of fetched news, so that application doesn't call server for news
     everytime this will increase data fetching speed and API calls will be reduced.
    for top-headlines data will be kept for one hour.
    for regular news data will be kept for six hour.
*********************************************************************************************************
"""


def cache_setup():
    connection = sqlite3.connect(DATABASE_FILENAME)
    cursor = connection.cursor()

    cursor.execute("DROP TABLE IF EXISTS news_cache")
    cursor.execute("DROP TABLE IF EXISTS source_cache")
    cursor.execute("DROP TABLE IF EXISTS fetch_details")
    connection.commit()

    # @sort field informs about news popularity
    cursor.execute("""
        CREATE TABLE news_cache(
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            source_id TEXT,
            source_name TEXT,
            author TEXT,
            title TEXT,
            description TEXT,
            url TEXT,
            url_to_image TEXT,
            published_at DATETIME,
            content TEXT,
            sort TEXT,
            fetched_at DATETIME DEFAULT CURRENT_TIMESTAMP 
            )
        """)

    # this table is meant for storing details that will be used for retrieval of (news or source) data
    cursor.execute("""
        CREATE TABLE fetch_details(
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            country TEXT,
            category TEXT,
            sources TEXT,
            type_of_news TEXT,
            domains TEXT,
            news_cache_id INTEGER,
            source_cache_id INTEGER,
            FOREIGN KEY(news_cache_id) REFERENCES news_cache(id) ON DELETE CASCADE,
            FOREIGN KEY (source_cache_id) REFERENCES source_cache(id) ON DELETE CASCADE 
        )
        """)

    # this table stores the cache of source details
    cursor.execute("""
        CREATE TABLE source_cache(
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            source_id TEXT,
            source_name TEXT,
            description TEXT,
            url TEXT,
            category TEXT,
            language TEXT,
            country TEXT,
            fetched_on DATETIME DEFAULT CURRENT_TIMESTAMP 
            )
        """)

    connection.commit()  # Saves the changes
    connection.close()  # Closes the connection


# @news_cache will capture all the news fetched from the internet
def news_cache(fetched_news, type_of_news):
    connection = sqlite3.connect(DATABASE_FILENAME)
    cursor = connection.cursor()

    articles = fetched_news.get("articles")

    for article in articles:
        # This query will insert all the data into @news_cache table
        cursor.execute("""
                INSERT INTO news_cache(source_id, source_name, author, title, description, 
                            url, url_to_image, published_at, content, sort) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
            article.get("source").get("id"), article.get("source").get("name"), article.get("author"),
            article.get("title"),
            article.get("description"), article.get("url"), article.get("urlToImage"),
            datetime.strptime(article.get("publishedAt"), "%Y-%m-%dT%H:%M:%SZ"), article.get("content"),
            article.get("sortBy")))

        # getting id of above inserted data
        cursor.execute("""SELECT id from news_cache ORDER BY fetched_at DESC""")
        news_id = cursor.fetchone()
        # Saving data on which data will be retrieved
        cursor.execute("""INSERT INTO fetch_details(country, category, sources, type_of_news, domains, news_cache_id)
            VALUES (?, ?, ?, ?, ?, ?)""", (filter_by.get("country"), filter_by.get("category"),
                                           filter_by.get("sources"), type_of_news, filter_by.get("domains"), news_id[0]))

        connection.commit()

    connection.close()


# @source_cache will capture all the sources data fetched from the internet
def source_cache(fetched_sources, type_of_news):  # @type_of_news is "sources" here.
    connection = sqlite3.connect(DATABASE_FILENAME)
    cursor = connection.cursor()

    sources = fetched_sources.get("sources")

    for source in sources:
        cursor.execute("""
                    INSERT INTO source_cache(source_id, source_name, description, url, category, language, country) 
                    VALUES (?, ?, ?, ?, ?, ?, ?) """, (
            source.get("id"), source.get("name"), source.get("description"),
            source.get("url"), source.get("category"),
            source.get("language"), source.get("country")
        ))

        cursor.execute("""SELECT id from source_cache ORDER BY fetched_at DESC""")

        source_id = cursor.fetchone()

        cursor.execute("""INSERT INTO fetch_details(country, category, sources, type_of_news, domains, source_cache_id)
                    VALUES (?, ?, ?, ?, ?, ?)""", (filter_by.get("country"), filter_by.get("category"),
                                                   filter_by.get("sources"), type_of_news,
                                                   filter_by.get("domains"), source_id))

        connection.commit()

    connection.close()


def make_query(params, key):
    if params.get(key) is None:
        return f"{key} is null and "
    return f"{key} = '{params.get(key)}' and "


# @get_news_from_db will fetch all news or sources from the database
def get_news_from_db(params, type_of_news):
    connection = sqlite3.connect(DATABASE_FILENAME)
    cursor = connection.cursor()

    news_content = {}
    articles = []

    # Making a query for fetching news from database
    if type_of_news == "top-headlines":
        headlines_field_list = ["country", "category", "sources", "domains", "source_cache_id"]
        query = "SELECT news_cache_id FROM fetch_details WHERE "

        query += make_query(params, headlines_field_list[0])
        query += make_query(params, headlines_field_list[1])
        query += make_query(params, headlines_field_list[2])
        query += make_query(params, headlines_field_list[3])
        query += make_query(params, headlines_field_list[4])

        query += f"type_of_news = '{type_of_news}'"
        cursor.execute(query)
        inside_query = cursor.fetchall()

        if len(inside_query) > 0:
            news_content.update({"status": "ok", "totalResults": len(inside_query)})
        else:
            news_content.update({"status": "error", "message": "No data"})

        for i in range(len(inside_query)):
            cursor.execute(f"SELECT * FROM news_cache WHERE id = ({inside_query[i][0]})")
            single_news = cursor.fetchone()

            single_news = list(single_news)
            date_format = single_news[8].split()
            single_news[8] = date_format[0] + "T" + date_format[1] + "Z"
            single_news = tuple(single_news)

            articles.append({"source": {"id": single_news[1], "name": single_news[2]}, "author": single_news[3],
                             "title": single_news[4], "description": single_news[5], "url": single_news[6],
                             "urlToImage": single_news[7], "publishedAt": single_news[8], "content": single_news[9]})

        news_content.update({"articles": articles})

        connection.close()

        return news_content

    elif type_of_news == "sources":
        connection = sqlite3.connect(DATABASE_FILENAME)
        cursor = connection.cursor()

        # TODO:


def news_format():
    pass




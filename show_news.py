from time import sleep
import concurrent.futures
from get_news import News, news_cache, source_cache
from filter_news import initial_filter, after_fetch_filter, initial_sources_filter, get_help
from bookmark_db import save_bookmark, show_bookmarks, save_sources_bookmark, show_bookmarked_sources, database_setup
from datetime import datetime


def operation_on_fetched_news(fetched_news, type_of_news):
    print("L - Load more news \t\t\tB - Bookmark a news \t\t\tM - Main Menu\t\t\t", end="")
    print("F - Filter more" if type_of_news == "top-headlines" else "")
    choice = input("Enter any of the above options: ")
    if choice.lower() == "l":
        return "continue"
    elif choice.lower() == "b":
        save_bookmark(fetched_news.get("articles"), type_of_news)
        return operation_on_fetched_news(fetched_news, type_of_news)
    elif choice.lower() == "m":
        main()
    elif choice.lower() == "f" and type_of_news == "top-headlines":
        print_news(after_fetch_filter(fetched_news), type_of_news)
    else:
        print("Invalid choice. Please try again")
        return operation_on_fetched_news(fetched_news, type_of_news)


def operation_on_news_sources(fetched_sources):
    print("L - Load more sources \t\t\tB - Bookmark a source \t\t\tM - Main Menu\t\t\t")
    choice = input("Enter any of the above options: ")
    if choice.lower() == "l":
        return "continue"
    elif choice.lower() == "b":
        save_sources_bookmark(fetched_sources.get("sources"))
        return operation_on_news_sources(fetched_sources)
    elif choice.lower() == "m":
        main()
    else:
        print("Invalid choice. Please try again")
        return operation_on_news_sources(fetched_sources)


# Function for printing fetched news from API
def print_news(fetched_news, type_of_news):
    # @fetched_news is the dictionary which is fetched from newsapi.org
    # @type_of_news is the string which shows which type of news is fetched (example - "top-headlines" or "all news" )

    count = 0  # Count of news articles
    if fetched_news.get("status") == "ok" and len(fetched_news.get("articles")) > 0:
        while count < len(fetched_news.get("articles")):
            articles = fetched_news.get("articles")

            # Printing all news in well formatted form
            print(f"""
                            {count + 1}. {articles[count].get("title")}

Description - {articles[count].get("description")} 
{articles[count].get("content")}
Source name - {articles[count].get("source").get("name")}, Author - {articles[count].get("author")}
Read full article at - {articles[count].get("url")}
View related images at - {articles[count].get("urlToImage")}
Published Date: {datetime.strptime(articles[count].get("publishedAt"), "%Y-%m-%dT%H:%M:%SZ").date()}
Published Time: {datetime.strptime(articles[count].get("publishedAt"), "%Y-%m-%dT%H:%M:%SZ").time()}
            """)
            count += 1

            # After displaying 10 news this "if" block will ask user for some other options
            # If @type_of_news is None, we are printing bookmarks.
            if count % 10 == 0 and type_of_news is not None:
                print(f"{len(articles) - count} more results.")
                further_process = operation_on_fetched_news(fetched_news, type_of_news)
                if further_process == 'continue':
                    continue
                else:
                    break

        if count < 10:
            print("B - Bookmark a news\t\t\tM - Main Menu")
            ch = input("Enter: ")
            if ch.lower() == "b":
                save_bookmark(fetched_news.get("articles"), type_of_news)
            elif ch.lower() == "m":
                main()
            else:
                print("Redirecting to main menu...")
                sleep(2)

    elif fetched_news.get("status") == "error":
        print(f"Something happened during news fetching. Possible error: ({fetched_news.get('message')})")

    # if there are zero article in @fetched_news this elif block will be executed
    elif len(fetched_news.get("articles")) == 0:
        print("\nNo news to show. Check back after some time.")

    else:
        print("\nSomething went wrong. Please refer to the log for more information.")


def print_news_sources(fetched_sources):
    count = 0
    if fetched_sources.get("status") == "ok" and len(fetched_sources.get("sources")) > 0:
        news_sources = fetched_sources.get("sources")
        while count < len(news_sources):
            print(f"""
        {count + 1}. Source ID - {news_sources[count].get("id")}, Source name - {news_sources[count].get("name")}
Description - {news_sources[count].get("description")}
Know more about this source - {news_sources[count].get("url")}
Source category - {news_sources[count].get("category")}
Source language (code) - {news_sources[count].get("language")}
Sources country (code) - {news_sources[count].get("country")}
            """)
            count += 1

            if count % 10 == 0:
                print(f"{len(news_sources) - count} more results.")
                further_process = operation_on_news_sources(fetched_sources)
                if further_process == "continue":
                    continue
                else:
                    break

        if count < 10:
            print("B - Bookmark a source\t\t\tM - Main Menu")
            ch = input("Enter: ")
            if ch.lower() == "b":
                save_sources_bookmark(fetched_sources.get("sources"))
            elif ch.lower() == "m":
                main()
            else:
                print("Redirecting to main menu...")
                sleep(2)

    elif fetched_sources.get("status") == "error":
        print(f"Something happened during sources fetching. Possible error: ({fetched_sources.get('message')})")

    elif len(fetched_sources.get("sources")) == 0:
        print("\nNo news to show. Check back after some time.")

    else:
        print("\nSomething went wrong. Please refer to the log for more information.")


def choice_1():
    print("Enter details for fetching news \nIf you want to set a parameter, write after it, otherwise hit 'enter'\n"
          "Enter '/help' for help section\n")
    # Initializing initial filter and passing all parameters in a instance of @News
    filter_by = initial_filter("headlines")
    news = News("top-headlines", filter_by.get("country"), filter_by.get("category"), filter_by.get("sources"),
                filter_by.get("q"))
    fetched, db = news.fetch_news_headlines()
    if db:
        print_news(fetched, "top-headlines")  # Printing fetched news

    else:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.submit(print_news, fetched, "top-headlines")
            executor.submit(news_cache, fetched, "top-headlines")


def choice_2():
    print("Enter details for fetching news \nIf you want to set a parameter, write after it, otherwise hit 'enter'\n"
          "Enter '/help' for help section\n")
    # Initializing initial filter and passing all parameters in a instance of @News
    filter_by = initial_filter("everything")
    news = News("everything", sources=filter_by.get("sources"), q=filter_by.get("q"), language=filter_by.get("language"))
    all_news = news.fetch_everything(filter_by.get("qInTitle"), filter_by.get("domains"),
                                     filter_by.get("excludeDomains"),
                                     filter_by.get("from"), filter_by.get("to"),
                                     filter_by.get("sortBy"))
    # TODO:
    print_news(all_news, "everything")  # Printing fetched news


def choice_3():
    print("""
    1 for viewing all news sources
    2 for viewing specific sources (Apply some filters)
    '/help' for help section.""")
    ch = input("\tEnter: ")
    if ch == "1":
        news = News("sources")
        # TODO:
        print_news_sources(news.all_sources())

    elif ch == "2":
        filter_by = initial_sources_filter()
        news = News("sources", category=filter_by.get("category"),
                    country=filter_by.get("country"),
                    language=filter_by.get("language"))
        # TODO:
        print_news_sources(news.all_sources())

    elif ch == "/help":
        get_help()


def more_options():
    print("""
    1 for all bookmarked news
    2 for all bookmarked sources
    '/help' for help section""")
    choice = input("\tEnter: ")
    if choice == "1":
        print_news(show_bookmarks(), None)
    elif choice == "2":
        print_news_sources(show_bookmarked_sources())
    elif choice == "/help":
        get_help()
    else:
        print("Invalid input")
        more_options()


def main():
    print("""
    1 for top headlines
    2 for all news
    3 for viewing sources of news
    4 for more options
    '/help' for help section""")
    choice = input("\tEnter: ")
    if choice == "1":
        choice_1()
    elif choice == "2":
        choice_2()
    elif choice == "3":
        choice_3()
    elif choice == "4":
        more_options()
    elif choice.lower() == "/help":
        get_help()
    else:
        print("Invalid input")
        main()


if __name__ == '__main__':
    main()

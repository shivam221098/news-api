from get_news import News

sortBy = {
    "1": "relevancy",
    "2": "popularity",
    "3": "publishedAt"
}


# Function for making datetime string in that format which is needed in newsapi.org (example - 2020-10-19T14:02:08)
def actual_time_format(time):
    actual_time = time = time.split()
    if len(actual_time) == 0:
        actual_time = ''
    elif len(time) == 1:
        actual_time = time[0]
    elif len(time) == 2:
        actual_time = time[0] + "T" + time[1]
    return actual_time


# @get_help is a help section for user which will help user to enter correct inputs
def get_help():
    with open("help.txt", "r", encoding="utf-8") as file:
        for line in file.readlines():
            print(line.strip())


# This function is for applying some initial filters to the news contents for fetching news
def initial_filter(type_of_news):
    country = category = qInTitle = domains = excludeDomains = from_date = to_date = language = ""
    sort = 3

    if type_of_news == "headlines":  # parameters that are only required for fetching top headlines
        country = input("Enter country code: ")
        if country.lower() == "/help":  # After every input, input is compared with "/help" to make sure user
            get_help()                  # doesn't need any help if the input is "/help" @get_help will be called.

        category = input("Enter category of news: ")
        if category.lower() == "/help":
            get_help()

    if not country and not category:  # newsapi.org doesn't allow to @sources parameter with @country and @category
        sources = input("A comma-separated or single word string of identifiers"
                        " for the [news sources] or blogs you want headlines from: ")
    else:
        sources = None
    if sources:
        if sources.lower() == "/help":
            get_help()

    if type_of_news == "everything":  # parameters that are only required for fetching everything
        qInTitle = input("Keywords or phrases to [search for in the article title only]. ")
        if qInTitle.lower() == "/help":
            get_help()

    q = input("Keywords or phrases to [search for in the article title and body]: ")
    if q.lower() == "/help":
        get_help()

    if type_of_news == "everything":  # parameters that are only required for fetching everything
        domains = input("A comma-separated string of domains (eg bbc.co.uk, techcrunch.com,"
                        " engadget.com) to restrict the search to. ")
        if domains.lower() == "/help":
            get_help()

        excludeDomains = input('A comma-seperated string of domains (eg bbc.co.uk, techcrunch.com, engadget.com)'
                               ' [to remove from the results]. ')
        if excludeDomains.lower() == "/help":
            get_help()

        from_date = input("A date and optional time for the oldest article allowed."
                          " This should be in ISO 8601 format (e.g. 2020-10-19 or 2020-10-19 14:02:08) "
                          "Default: the oldest. ")
        from_date = actual_time_format(from_date)
        if from_date.lower() == "/help":
            get_help()

        to_date = input("A date and optional time for the newest article allowed. "
                        "This should be in ISO 8601 format (e.g. 2020-10-19 or 2020-10-19 14:02:08)"
                        " Default: the newest ")
        to_date = actual_time_format(to_date)
        if to_date.lower() == "/help":
            get_help()

        language = input("Enter [language] for news: ")
        if language.lower() == "/help":
            get_help()

        print("The order to sort the articles in")
        for key, value in sortBy.items():
            print(f"{key} for sorting according to {value}")
        sort = input("Enter: ")
        if sort.lower() == "/help":
            get_help()

    # returning the dictionary with the parameters by which our news content is to be filtered
    if type_of_news == "headlines":
        return {"country": country, "category": category, "sources": sources, "q": q}
    elif type_of_news == "everything":
        return {
            "q": q,
            "qInTitle": qInTitle,
            "sources": sources,
            "domains": domains,
            "excludeDomains": excludeDomains,
            "from": from_date,
            "to": to_date,
            "language": language,
            "sortBy": sortBy.get(sort)
        }


def after_fetch_filter(fetched_news):
    print("\nApply some more filters \nIf you want to set a parameter, write after it, otherwise hit 'enter'\n"
          "Enter '/help' for help section\n")
    sources = input("From sources: ")
    if sources.lower() == "/help":
        get_help()

    keyword = input("Any specific keyword or phrases in title:")
    if keyword.lower() == "/help":
        get_help()

    if sources is None:
        sources = ""
    if keyword is None:
        keyword = ""

    new_article = []
    articles = fetched_news.get("articles")

    for article in articles:
        if sources in article.get("source").get("name").lower() and keyword in article.get("title"):
            new_article.append(article)

    fetched_news.update({"articles": new_article})
    return fetched_news


def initial_sources_filter():
    print("Enter details for fetching sources \nIf you want to set a parameter, write after it, otherwise hit 'enter'\n"
          "Enter '/help' for help section\n")

    category = input("Enter [category] of news sources: ")
    if category.lower() == "/help":
        get_help()

    country = input("Enter country code: ")
    if country.lower() == "/help":  # After every input, input is compared with "/help" to make sure user
        get_help()                  # doesn't need any help if the input is "/help" @get_help will be called.

    language = input("Enter [language] for news: ")
    if language.lower() == "/help":
        get_help()

    return {"category": category, "country": country, "language": language}


if __name__ == '__main__':
    news = News("top-headlines", country="us", category="sports")
    print(after_fetch_filter(news.fetch_news_headlines()))
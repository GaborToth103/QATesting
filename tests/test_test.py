import requests

def get_next_page(language_code: str = "hu", starting_page_title: str = "Szeged") -> requests.Request:
    api_url = f"https://{language_code}.wikipedia.org/w/api.php"

    def get_next_page(apfrom: str):
        return apfrom

    S = requests.Session()

    PARAMS = {
        "action": "query",
        "format": "json",
        "list": "allpages",
        "apfrom": get_next_page(starting_page_title),
        "aplimit": 500,
    }


    R = S.get(url=api_url, params=PARAMS)
    data = R.json()
    for page in data["query"]["allpages"]:
        print(page['title'])
    next_page_title = data["query"]["allpages"][0]["title"]
    starting_page_title = data["query"]["allpages"][1]["title"]

    page_url = f"https://hu.wikipedia.org/wiki/{next_page_title}"

    request = requests.get(page_url)
    return request

if __name__ == "__main__":
    get_next_page()
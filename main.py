from html_scraper import html_scraper
from html_structurer import order_structurer


def main():
    html_scraper()
    order_structurer('html_data/')

if __name__ == "__main__":
    main()
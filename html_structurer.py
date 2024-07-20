from bs4 import BeautifulSoup
import os
from agents import HTMLParser
import json


html_dir = 'html_data/'
def get_html_paths(html_dir):
    html_files = os.listdir(html_dir)
    html_files = [file for file in html_files if file.endswith('.html')]
    html_paths = [os.path.join(html_dir, file) for file in html_files]
    return html_paths

def get_html_data(html_path):
    with open(html_path, 'r') as file:
        html_data = file.read()
    return html_data

def get_div_relevant_keys(html_data):
    # find all divs containing data-component paymentDetails or shipments
    soup = BeautifulSoup(html_data, 'html.parser')
    html_text = soup.find_all('div', {'id': ['orderDetails', 'shipments']})
    return html_text

def structure_html_text(html_text, html_parser):
    order_json = html_parser.get_order_details(html_text)
    return order_json


def order_structurer(html_dir, ouput_dir='structured_order_data/'):
    # create output directory if it does not exist
    if not os.path.exists(ouput_dir):
        os.makedirs(ouput_dir)
    html_paths = get_html_paths(html_dir)
    html_parser = HTMLParser(parser_model='gpt-4o-mini')
    for html_path in html_paths:
        print("Processing: ", html_path)
        html_data = get_html_data(html_path)
        html_text = get_div_relevant_keys(html_data)
        order_json = structure_html_text(html_text, html_parser)
        
        # append the order data to jsonl file called order_data.jsonl in output_dir
        with open(os.path.join(ouput_dir, 'order_data.jsonl'), 'a') as file:
            json.dump(order_json, file)
            file.write('\n')


if __name__ == '__main__':
    order_structurer(html_dir)


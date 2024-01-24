import time
import json
import gzip
import requests
from bs4 import BeautifulSoup


class AmazonScraper:
    def scrape(self, url):
        #set header
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        }

        # Downloading html content of amazon page
        print("Downloading %s" % url)
        response = requests.get(url, headers=headers)

        #Check if we encounter any error
        if response.status_code > 500:
            if "To discuss automated access to Amazon data please contact" in response.text:
                print(
                    "Page %s was blocked by Amazon. Please try using better proxies\n" % url)
            else:
                print("Page %s must have been blocked by Amazon as the status code was %d" % (
                    url, response.status_code))
            return None

        soup = BeautifulSoup(response.text, 'html.parser')

        #a empty dictionary to store product data
        product_data = {
            'products': []
        }

        # Iterating each product container on the page
        for product_elem in soup.select('div.puis-card-container.s-card-container.s-overflow-hidden.aok-relative.puis-include-content-margin.puis.puis-v2rh3j15wdcp4q29xeaptoa72x6.s-latency-cf-section.puis-card-border'):
            # Extract product details from the current product container
            product = {
                'product_Name': product_elem.select_one('span.a-size-medium.a-color-base.a-text-normal').text.strip(),
                'selling_price': product_elem.select_one('span.a-price-whole').text.strip(),
                'mrp': product_elem.select_one('span.a-offscreen').text.strip(),
                'discount': product_elem.select_one('span.a-letter-space').text.strip(),
                'brand_name': product_elem.select_one('span.a-size-medium.a-color-base').text.strip(),
                'product_reviews': product_elem.select_one('span.a-size-base.s-underline-text').text.strip(),
                'image_url': product_elem.select_one('img.s-image')['src']
            }

            #adding the the product details to the product_data dictionary
            product_data['products'].append(product)

        return product_data


def main():
    amazon_scraper = AmazonScraper()

    url_list = [
        {'url': 'https://www.amazon.in/s?k=laptops&crid=3BYGBX4GKO5O1&sprefix=laptop%2Caps%2C308&ref=nb_sb_noss_1',
         'city': 'Delhi'},
        {'url': 'https://www.amazon.in/s?k=laptops&crid=2N8QUJD3Z57WR&sprefix=laptop%2Caps%2C313&ref=nb_sb_noss_1',
         'city': 'Bengaluru'},
    ]

    # Iterate through each URL in the list
    for item in url_list:
        url = item['url']
        city = item['city']

        output_filename = f'amazon_results_{city}.ndjson.gz'
        with gzip.open(output_filename, 'wb') as outfile:
            data = amazon_scraper.scrape(url) # Scrape current URL
            
            if data:
                # Iterate through each product in the scraped data
                for product in data['products']:
                    # Convert product dictionary to JSON string
                    product_json = json.dumps(product, ensure_ascii=False)
                    outfile.write((product_json + '\n').encode('utf-8'))
                    print(f"Saving Product for {city}: {product['product_Name']}")
                    time.sleep(5) #add delay between requests


if __name__ == "__main__":
    main()

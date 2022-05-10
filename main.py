import requests
import os
import subprocess
import urllib.request
from bs4 import BeautifulSoup
import tldextract

web_pages = ['https://understandingdata.com/',
             'https://understandingdata.com/data-engineering-services/',
             'https://www.internetingishard.com/html-and-css/links-and-images/']

url_dictionary = {}

for page in web_pages:

    # extract the domain name
    domain_name = tldextract.extract(page).registered_domain
    print(f"The domain name: {domain_name}")

    # request the webpage
    r = requests.get(page)

    # check the page status
    if r.status_code == 200:

        # create a url dictionary entry for future use
        url_dictionary[page] = []

        # parse the HTML content
        soup = BeautifulSoup(r.content, 'html.parser')

        # find all the images
        images = soup.findAll('img')

        url_dictionary[page].extend(images)

    else:
        print('failed!')

all_images = []

# make a clean dict with pages that have more than 1 image
cleaned_dictionary = {key: value for key,
                      value in url_dictionary.items() if len(value) > 0}

for key, images in cleaned_dictionary.items():
    # create a clean url and domain name for every page
    clean_urls = []
    domain_name = tldextract.extract(key).registered_domain

    # loop every image per url
    for image in images:
        # extract source
        source_image_url = image.attrs['src']

        # clean the data
        if source_image_url.startswith("//"):
            pass
        elif domain_name not in source_image_url and 'http' not in source_image_url:
            url = 'https://' + domain_name + source_image_url
            all_images.append(url)
        else:
            all_images.append(source_image_url)


def extract_images(image_urls_list: list, directory_path):

    # Changing directory into a specific folder:
    os.chdir(directory_path)

    # Downloading all of the images
    for img in image_urls_list:
        file_name = img.split('/')[-1]

        # Let's try both of these versions in a loop [https:// and https://www.]
        url_paths_to_try = [img, img.replace('https://', 'https://www.')]
        for url_image_path in url_paths_to_try:
            print(url_image_path)
            try:
                r = requests.get(img, stream=True)
                if r.status_code == 200:
                    with open(file_name, 'wb') as f:
                        for chunk in r:
                            f.write(chunk)
            except Exception as e:
                pass


extract_images(all_images, "./")

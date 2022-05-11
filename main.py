import requests
import os
from bs4 import BeautifulSoup
import tldextract
import concurrent.futures
import csv


web_pages = []
url_dictionary = {}

# path for saving the images
directory = "images"

# read from a csv file and add each record to web_pages
with open('source.csv', mode='r', encoding='utf-8-sig') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
    for row in spamreader:
        print(row[0])
        web_pages.append(row[0])

for page in web_pages:

    # extract the domain name
    domain_name = tldextract.extract(page).registered_domain

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

# function to extract a single image


def extract_single_image(img):
    file_name = img.split('/')[-1]

    # Let's try both of these versions in a loop [https:// and https://www.]
    url_paths_to_try = [img, img.replace('https://', 'https://www.')]
    for url_image_path in url_paths_to_try:
        print(f"getting image from :{url_image_path}")
        try:
            r = requests.get(img, stream=True)
            if r.status_code == 200:
                with open(file_name, 'wb') as f:
                    for chunk in r:
                        f.write(chunk)
            return "Completed"
        except Exception as e:
            return "Failed"


for key, images in cleaned_dictionary.items():
    # create a clean url and domain name for every page
    clean_urls = []
    domain_name = tldextract.extract(key).registered_domain

    # loop every image per url
    for image in images:
        print(image)
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

# create a directory and change to that directory
try:
    os.mkdir(directory)
except FileExistsError as e:
    print("Directory already exists")

os.chdir(f"{directory}")

# run the job concurrently
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    future_to_url = {executor.submit(
        extract_single_image, image_url) for image_url in all_images}

    for future in concurrent.futures.as_completed(future_to_url):
        try:
            url = future_to_url[future]
        except Exception as e:
            pass

        try:
            data = future.result()
        except Exception as exc:
            print('%r generated an exception: %s' % (url, exc))

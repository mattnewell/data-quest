# TODO: Logging
# TODO: Does smart_open handle errors, retries, and backoff?
import time
import boto3
import requests
from bs4 import BeautifulSoup
from smart_open import open

headers = {
    'User-Agent': 'matthew.newell@rearc.io'
}

endpoint = 'https://download.bls.gov'
path = '/pub/time.series/pr/'


def chunk_to_s3(url):
    # session = boto3.Session(profile_name='sandbox')
    # s3_client = session.client('s3')
    # with requests.get(url, stream=True, headers=headers) as r:
    #     r.raise_for_status()
    #     # chunk_size is in bytes. in the real world, 8 KiB would be tiny and inefficient, but proves point
    #     for chunk in r.iter_content(chunk_size=8192):
    #         if chunk:
    #             s3_client.put_object(Body=chunk, Bucket='newell-data-quest', Key=url.split('/')[-1])
    session = boto3.Session(profile_name='sandbox')
    with (open(url, 'rb', transport_params={'headers': headers}) as fin):
        with open(f's3://newell-data-quest/{url.split("/")[-1]}',
                  'wb',
                  transport_params={'client': session.client('s3')}) as fout:
            while True:
                # chunk_size is in bytes. in the real world, 8 KiB would be small and inefficient, but proves point
                chunk = fin.read(8192)
                if not chunk:
                    break
                fout.write(chunk)


def list_urls(endpoint, path):
    response = requests.get(endpoint + path, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        raw_anchors = soup.find_all('a', href=True)
        links = [endpoint + links['href'] for links in raw_anchors if links['href']]
        return links[1:len(links)]


start = time.time()
files = list_urls(endpoint, path)
for file in files:
    chunk_to_s3(file)
end = time.time()
print(end-start)

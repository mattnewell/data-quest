# TODO: Logging
# TODO: Does smart_open handle errors, retries, and backoff?
import time
import boto3
import requests
from bs4 import BeautifulSoup
from smart_open import open

# NOTE: These are super-hardcoded, and could be more flexible
session = boto3.Session(profile_name='sandbox')
bucket = 's3://newell-data-quest'
headers = {
    'User-Agent': 'matthew.newell@rearc.io'
}
bls_endpoint = 'https://download.bls.gov'
productivity_path = '/pub/time.series/pr/'


def source_bls_productivity():
    url = list_urls(bls_endpoint, productivity_path)
    for file in url:
        chunk_to_s3(file, file.split("/")[-1])


def source_datausa_nation_pop():
    chunk_to_s3('https://datausa.io/api/data?Geography=01000US&measure=Population', 'datausa_nation_pop.json')


def list_urls(endpoint, path):
    response = requests.get(endpoint + path, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        raw_anchors = soup.find_all('a', href=True)
        links = [endpoint + links['href'] for links in raw_anchors if links['href']]
        return links[1:len(links)]


def chunk_to_s3(source_url, s3_key):
    with (open(source_url, 'rb', transport_params={'headers': headers}) as fin):
        # NOTE: There is a requirement in README.md to not upload the same file twice. If that's talking about change
        # detection, then this doesn't meet that requirement. But that's a remarkably complex and opinionated problem
        # to solve.
        with open(f'{bucket}/{s3_key}',
                  'wb',
                  transport_params={'client': session.client('s3')}) as fout:
            while True:
                # chunk_size is in bytes. in the real world, 8 KiB would be small and inefficient, but proves point
                chunk = fin.read(8192)
                if not chunk:
                    break
                fout.write(chunk)


source_bls_productivity()
source_datausa_nation_pop()

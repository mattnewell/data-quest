import requests
from bs4 import BeautifulSoup
from smart_open import open

bucket = 's3://newell-data-quest'
headers = {
    'User-Agent': 'matthew.newell@rearc.io'
}
bls_endpoint = 'https://download.bls.gov'
productivity_path = '/pub/time.series/pr/'


def source_bls_productivity():
    urls = list_urls(bls_endpoint, productivity_path)
    for file in urls:
        chunk_to_s3(file, file.split("/")[-1])


def list_urls(endpoint, path):
    response = requests.get(endpoint + path, headers=headers)
    if response.ok:
        soup = BeautifulSoup(response.text, 'html.parser')
        raw_anchors = soup.find_all('a')
        # raw_anchors are relative, make them absolute
        links = [endpoint + links['href'] for links in raw_anchors]
        return links[1:len(links)]


def source_datausa_nation_pop():
    chunk_to_s3('https://datausa.io/api/data?Geography=01000US&measure=Population', 'datausa_nation_pop.json')


# TODO: Real world would need efficient error handling, retries and backoff.
def chunk_to_s3(source_url, s3_key):
    with open(source_url, 'rb', transport_params={'headers': headers}) as fin:
        # NOTE: There is a requirement in README.md to not upload the same file twice. If that's talking about change
        # detection, then this doesn't meet that requirement. But that's a remarkably complex and opinionated problem
        # to solve.
        with open(f'{bucket}/{s3_key}', 'wb') as fout:
            while True:
                # chunk_size is in bytes. in the real world, 8 KiB would be small and inefficient, but proves point
                chunk = fin.read(8192)
                if not chunk:
                    break
                fout.write(chunk)


def handler(event, context):
    requests.packages.urllib3.util.connection.HAS_IPV6 = False
    source_bls_productivity()
    source_datausa_nation_pop()

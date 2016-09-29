"""
Fetch records from JCAP benchmarking DB
"""
import sys
import requests
from bs4 import BeautifulSoup
import pymongo

base_url = 'https://internal.solarfuelshub.org/jcapresources/benchmarking/catalysts_for_iframe/view/jcapbench_catalyst/'


def main():
    client = MongoClient()
    db = client.jcap
    coll = db.benchmarking
    for i in range(101,102):
        url = base_url + str(i)
        r = requests.get(url)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text)
            data, legend = soup.body.find_all('table')
            record = data_to_json(data)
            coll.insert(record)
            
def data_to_json(data):
    result = {}
    for row in data.find_all('tr'):
        name = '_'.join(row['id'].split('__')[0].split('_')[2:])
        labels = row.find('td', class_='w2p_fl').label
        label_text = ' '.join(labels.strings).strip()
        if label_text.endswith(':'):
            label_text = label_text[:-1]
        value = row.find('td', class_='w2p_fw').string
        result[name] = [label_text, value]
    return result
    
if __name__ == '__main__':
    sys.exit(main())
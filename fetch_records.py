"""
Fetch records from JCAP benchmarking DB
"""
import re
import sys
import time

import requests
from bs4 import BeautifulSoup
import pymongo

base_url = 'https://internal.solarfuelshub.org/jcapresources/benchmarking/catalysts_for_iframe/view/jcapbench_catalyst/'


def main():
    client = pymongo.MongoClient()
    db = client.test
    coll = db.jcap
    for i in range(60, 200):
        print('Trying benchmark material #{:d}'.format(i))
        url = base_url + str(i)
        t0 = time.time()
        r = requests.get(url)
        t1 = time.time()
        print('Request took {:.1f} seconds'.format(t1 - t0))
        if (r.status_code == 200 and
            'Detailed view of your selected record' in r.text):
            soup = BeautifulSoup(r.text, 'html.parser')
            data, legend = soup.body.find_all('table')
            record = data_to_json(data)
            identifier = '{name}_{reaction}'.format(
                    name=record['catalyst_name']['value']['text'],
                    reaction=record['reaction_type']['value']['text'])
            idnum = 0
            while coll.find({'_id': identifier}).count() > 0:
                idnum += 1
                if idnum == 1:
                    identifier = identifier + '_' + str(idnum)
                else:
                    identifier = identifier.split('_')[0] + '_' + str(idnum)
            record['_id'] = identifier
            coll.insert(record)
            print('Added: {}'.format(identifier))
            
def data_to_json(data):
    result = {}
    for row in data.find_all('tr'):
        name = '_'.join(row['id'].split('__')[0].split('_')[2:])
        labels = row.find('td', class_='w2p_fl').label
        label_text = ' '.join(labels.strings).strip()
        if label_text.endswith(':'):
            label_text = label_text[:-1]
        # Extract value and try to find the
        # first numeric token, which is typically the mean
        # or non-annotated value
        value = str(row.find('td', class_='w2p_fw').string)
        num = re.search('-?[0-9.]+', value)
        has_num, value_num = False, 0
        if num is not None:
            num_str = value[num.start():num.end()]
            try:
                value_num = float(num_str)
                has_num = True
            except:
                pass
        result[name] = {
            'label': label_text,
            'value': {
                'text': value,
                'num': value_num,
                'is_numeric': has_num
            }
        }
    return result
    
if __name__ == '__main__':
    sys.exit(main())
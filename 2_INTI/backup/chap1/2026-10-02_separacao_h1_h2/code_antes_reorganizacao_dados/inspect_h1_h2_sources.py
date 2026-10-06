import json,re
from pathlib import Path
from html.parser import HTMLParser
from data_common import DATA

class Links(HTMLParser):
    def __init__(self): super().__init__(); self.urls=[]
    def handle_starttag(self,tag,attrs):
        if tag=='a': self.urls.extend(v for k,v in attrs if k=='href')

def links(path):
    p=Links(); p.feed(Path(path).read_text(encoding='utf-8',errors='replace')); return p.urls

if __name__=='__main__':
    d=DATA/'raw/tabular/source_documents'
    a=json.loads((d/'ibama_autos_20260930.json').read_text())
    print('IBAMA',[(r['name'],r['url']) for r in a['result']['resources']][:9])
    for name,term in [('worldbank','xlsx'),('gaez_v4','gaez'),('mma_amazonia','portaria')]:
        print(name,[u for u in links(d/f'{name}_20260930.html') if term in u.lower()])
    print('PAM',str(json.loads((DATA/'raw/tabular/ibge/t1612_1974_1983.json').read_text()))[:1800])

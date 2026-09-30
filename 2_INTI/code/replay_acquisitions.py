"""Replay the actual, recorded download requests, including discovery documents.

Mutable upstream endpoints may no longer return the old snapshot. A mismatch is
reported, never silently accepted as reproduction of the original vintage.
"""
import argparse,json
from data_common import DATA,fetch,sha256

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--retry-failures',action='store_true');args=p.parse_args()
    requests={}
    for log in sorted((DATA/'catalog').glob('acquisition*.jsonl')):
        for line in log.read_text(encoding='utf-8').splitlines():
            r=json.loads(line)
            if r.get('status')=='BAIXADO' or args.retry_failures:requests[(r['arquivo_local'],r['url'])]=(log.name,r)
    errors=[]
    for log,r in requests.values():
        try:
            target=fetch(r['url'],r['arquivo_local'].removeprefix('2_INTI/data/'),r['fonte'],r.get('versao',''),manifest=log)
            if r.get('sha256') and sha256(target)!=r['sha256']:raise ValueError('Upstream snapshot changed: expected '+r['sha256'])
        except Exception as e:errors.append({'arquivo':r['arquivo_local'],'erro':str(e)})
    (DATA/'catalog/replay_result.json').write_text(json.dumps(errors,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Requests:',len(requests),'errors:',len(errors))
    if errors:raise SystemExit(1)

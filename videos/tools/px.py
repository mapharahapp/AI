import sys,json,urllib.request,urllib.parse,os
k=os.environ['PIXABAY_API_KEY']
for q in sys.argv[1:]:
    u='https://pixabay.com/api/videos/?'+urllib.parse.urlencode({'key':k,'q':q,'per_page':8,'safesearch':'true'})
    d=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'curl/8'})))
    print('##',q,d['totalHits'])
    for h in d['hits']:
        v=h['videos']; best=v['large'] if v['large']['url'] else v['medium']
        print(h['id'],h['duration'],f"{best['width']}x{best['height']}",h['tags'][:70])

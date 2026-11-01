import sys,json,urllib.request,urllib.parse,os,time
k=os.environ['PIXABAY_API_KEY']
kind=sys.argv[1]  # v or i
for q in sys.argv[2:]:
    base='https://pixabay.com/api/videos/?' if kind=='v' else 'https://pixabay.com/api/?'
    u=base+urllib.parse.urlencode({'key':k,'q':q,'per_page':10,'safesearch':'true'})
    for a in range(4):
        try:
            d=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'curl/8'})));break
        except Exception as e:
            time.sleep(3*(a+1))
    else:
        print('##',q,'FAILED');continue
    print('##',q,d['totalHits'])
    for h in d['hits']:
        if kind=='v':
            v=h['videos']; best=v['large'] if v['large']['url'] else v['medium']
            print(' ',h['id'],f"{h['duration']}s",f"{best['width']}x{best['height']}",h['tags'][:80])
        else:
            print(' ',h['id'],f"{h['imageWidth']}x{h['imageHeight']}",h['tags'][:80])
    time.sleep(1.2)

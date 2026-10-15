import sys,json,urllib.request,os
k=os.environ['PIXABAY_API_KEY']
H={'User-Agent':'curl/8'}
def get(u): return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=H)))
for a in sys.argv[1:]:
    kind,i=a.split(':')
    if kind=='v':
        h=get(f'https://pixabay.com/api/videos/?key={k}&id={i}')['hits'][0]['videos']
        v=h['medium'] if h['medium']['url'] and h['medium']['width']>=1280 else h['large']
        out=f'clips/{i}.mp4'
    else:
        v={'url':get(f'https://pixabay.com/api/?key={k}&id={i}')['hits'][0]['largeImageURL']}
        out=f'img/{i}.jpg'
    if not os.path.exists(out):
        open(out,'wb').write(urllib.request.urlopen(urllib.request.Request(v['url'],headers=H)).read())
    print(out, os.path.getsize(out))

# usage: prev.py out.jpg i:ID v:ID ...  -> contact sheet of previews with labels
import sys,json,urllib.request,urllib.parse,os,time,io
from PIL import Image,ImageDraw,ImageFont
k=os.environ['PIXABAY_API_KEY']
def get(u):
    for a in range(4):
        try: return urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'curl/8'})).read()
        except Exception as e: time.sleep(2*(a+1))
    raise SystemExit('fail '+u)
tiles=[]
for it in sys.argv[2:]:
    kind,i=it.split(':')
    if kind=='i':
        d=json.loads(get('https://pixabay.com/api/?'+urllib.parse.urlencode({'key':k,'id':i})))
        url=d['hits'][0]['webformatURL']
    else:
        d=json.loads(get('https://pixabay.com/api/videos/?'+urllib.parse.urlencode({'key':k,'id':i})))
        v=d['hits'][0]['videos']; url=(v['medium'].get('thumbnail') or v['small'].get('thumbnail'))
    im=Image.open(io.BytesIO(get(url))).convert('RGB'); im.thumbnail((360,360))
    t=Image.new('RGB',(360,390),'white'); t.paste(im,(0,0)); ImageDraw.Draw(t).text((5,365),it,fill='black')
    tiles.append(t); time.sleep(0.8)
cols=4; rows=(len(tiles)+cols-1)//cols
sheet=Image.new('RGB',(cols*360,rows*390),'white')
for n,t in enumerate(tiles): sheet.paste(t,((n%cols)*360,(n//cols)*390))
sheet.save(sys.argv[1],quality=80)

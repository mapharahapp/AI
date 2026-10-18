"""Download Pixabay b-roll into clips/ and img/ (run from the episode's work dir).
usage: python3 dl.py v:VIDEO_ID i:IMAGE_ID ...
Videos: the smallest rendition that fills 1080x1920 after a cover crop without upscaling,
else the largest one. Images: largeImageURL (max 1280 px, all a standard API key gets).
"""
import sys, json, urllib.request, urllib.error, http.client, os, time
k = os.environ['PIXABAY_API_KEY']
H = {'User-Agent': 'curl/8'}  # Pixabay rejects Python's default User-Agent
def fetch(u):
    for n in range(6):  # Pixabay answers 429 when requests come too fast; big files can get cut off
        try:
            return urllib.request.urlopen(urllib.request.Request(u, headers=H)).read()
        except (urllib.error.HTTPError, http.client.IncompleteRead, ConnectionError) as e:
            if (isinstance(e, urllib.error.HTTPError) and e.code != 429) or n == 5:
                raise
            time.sleep(10 * (n + 1))
def get(u): return json.loads(fetch(u))
for a in sys.argv[1:]:
    kind, i = a.split(':')
    if kind == 'v':
        rs = [r for r in get(f'https://pixabay.com/api/videos/?key={k}&id={i}')['hits'][0]['videos'].values() if r['url']]
        fill = [r for r in rs if max(1080 / r['width'], 1920 / r['height']) <= 1]
        v = min(fill, key=lambda r: r['width'] * r['height']) if fill else max(rs, key=lambda r: r['width'] * r['height'])
        out = f'clips/{i}.mp4'
    else:
        v = {'url': get(f'https://pixabay.com/api/?key={k}&id={i}')['hits'][0]['largeImageURL']}
        out = f'img/{i}.jpg'
    if not os.path.exists(out):
        data = fetch(v['url'])  # fetch first, so a failed download leaves no empty file behind
        open(out, 'wb').write(data)
    print(out, os.path.getsize(out))

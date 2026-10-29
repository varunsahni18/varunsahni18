"""Package the selected design at the domain root, without review-only controls."""
from pathlib import Path
import argparse,json,shutil,datetime
from urllib.parse import urlsplit
from bs4 import BeautifulSoup
R=Path(__file__).resolve().parents[1]
a=argparse.ArgumentParser();a.add_argument('--output',required=True);a.add_argument('--assets',default=str(R/'assets'));args=a.parse_args();out=Path(args.output).resolve();out.mkdir(parents=True,exist_ok=True)
shutil.copytree(Path(args.assets),out/'assets',dirs_exist_ok=True)
shutil.copy2(Path(args.assets)/'documents/Varun_Sahni_resume.pdf',out/'resume.pdf')
for name in ['shared.css','art.css','dark.css','studio.js','concepts.js','icons.svg','dark-mark.svg']:
 (out/'design').mkdir(exist_ok=True);shutil.copy2(R/'design'/name,out/'design'/name)
shutil.copytree(R/'design/media',out/'design/media',dirs_exist_ok=True)
# The review switcher is omitted; the systems animation remains.
p=out/'design/concepts.js';s=p.read_text();s=s[s.index('(()=>{',s.index('})();')+5):];p.write_text(s)
paths=[]
for f in sorted((R/'dark').rglob('*.html')):
 relative=f.relative_to(R/'dark');path='/'+str(relative.parent).replace('\\','/')+'/' if relative.name=='index.html' else '/'+str(relative)
 if path=='/./':path='/'
 s=BeautifulSoup(f.read_text(),'html.parser')
 for x in s.select('.concept-switcher,link[href="/design/concepts.css"]'):x.decompose()
 for x in s.find_all(True):
  for attr in ['href','src','data-project','data-search-index']:
   if str(x.get(attr,'')).startswith('/dark/'):x[attr]=x[attr][5:]
 for anchor in s.select('a[href]'):
  if anchor['href'].split('?')[0]=='/assets/documents/Varun_Sahni_resume.pdf':anchor['href']='/resume.pdf'
 s.body['data-search-index']='/design/search.json'
 canonical='https://www.varunsahni.in'+path
 tag=s.new_tag('link',rel='canonical',href=canonical);s.head.append(tag)
 desc=s.select_one('meta[name=description]')['content']
 for prop,value in [('og:title',s.title.get_text()),('og:description',desc),('og:type','article' if '/blog/20' in path else 'website'),('og:url',canonical),('og:image','https://www.varunsahni.in/assets/images/varun-linkedin.png'),('og:image:alt','Varun Sahni'),('og:site_name','Varun Sahni')]:s.head.append(s.new_tag('meta',attrs={'property':prop,'content':value}))
 s.head.append(s.new_tag('meta',attrs={'name':'twitter:card','content':'summary'}))
 s.head.append(s.new_tag('meta',attrs={'name':'site-release','content':'2026-10-29.2'}))
 for asset in s.select('link[rel=stylesheet],script[src]'):
  key='src' if asset.name=='script' else 'href'
  if asset[key].startswith('/design/'):asset[key]=asset[key].split('?')[0]+'?v=20261029-2'
 target=out/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(str(s));paths.append(path)
index=json.loads((R/'dark/design/search.json').read_text())
for x in index:x['path']=x['path'][5:]
(out/'design/search.json').write_text(json.dumps(index,ensure_ascii=False))
(out/'.nojekyll').touch();(out/'CNAME').write_text('www.varunsahni.in\n')
(out/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: https://www.varunsahni.in/sitemap.xml\n')
(out/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>https://www.varunsahni.in'+p+'</loc></url>' for p in paths if p!='/404.html')+'</urlset>')
print(json.dumps({'pages':len(paths),'output':str(out),'domain':'www.varunsahni.in'}))

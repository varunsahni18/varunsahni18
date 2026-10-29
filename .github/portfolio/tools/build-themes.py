"""Generate the public theme comparison and dedicated New York entry point."""
from pathlib import Path
from bs4 import BeautifulSoup
import argparse,html,json
p=argparse.ArgumentParser();p.add_argument('--directory',required=True);args=p.parse_args();r=Path(args.directory)
themes=[
 {'id':'mint','name':'Mint','bg':'#080d11','ink':'#f0f6f4','muted':'#8b9da3','accent':'#a6f6d7','tag':'Recommended','copy':'The most cohesive fit for the current site. The mint accent keeps the globe, project illustrations, and navigation in the same visual language.'},
 {'id':'cobalt','name':'Cobalt','bg':'#0b1021','ink':'#f2f5ff','muted':'#a5b3d1','accent':'#a9c5ff','tag':'Cool / dark','copy':'A navy background and pale blue accents. A quieter alternative with clear text contrast, though less distinctive than Mint or New York.'},
 {'id':'paper','name':'Paper','bg':'#f5f1e8','ink':'#282a24','muted':'#606356','accent':'#8b4028','tag':'Warm / light','copy':'Warm paper, charcoal text, and rust accents. Comfortable for reading the longer case studies; the technical illustrations keep their original colors.'},
 {'id':'new-york','name':'New York','bg':'#f3f1e9','ink':'#171917','muted':'#56594f','accent':'#234c37','tag':'City edition','copy':'The strongest personal direction. Transit colors, bold type, route markers, and a skyline connect the portfolio to life at NYU and in New York.'}
]
def luminance(h):
 rgb=[int(h[i:i+2],16)/255 for i in (1,3,5)];v=[x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4 for x in rgb];return sum(a*b for a,b in zip(v,[.2126,.7152,.0722]))
def contrast(a,b):
 x,y=sorted([luminance(a),luminance(b)]);return (y+.05)/(x+.05)
base=BeautifulSoup((r/'index.html').read_text(),'html.parser')
ny=BeautifulSoup(str(base),'html.parser');ny.html['data-default-theme']='new-york';ny.html['data-theme']='new-york';ny.title.string='New York edition | Varun Sahni'
ny.select_one('meta[property="og:title"]')['content']='New York edition | Varun Sahni'
(r/'new-york').mkdir(exist_ok=True);(r/'new-york/index.html').write_text(str(ny))
s=BeautifulSoup(str(base),'html.parser');s.title.string='Compare website themes | Varun Sahni';s.select_one('link[rel=canonical]')['href']='https://www.varunsahni.in/themes/'
s.select_one('meta[name=description]')['content']='Compare Mint, Cobalt, Paper, and New York themes for Varun Sahni’s portfolio.'
s.select_one('meta[property="og:title"]')['content']='Compare website themes | Varun Sahni'
s.select_one('meta[property="og:description"]')['content']=s.select_one('meta[name=description]')['content']
s.select_one('meta[property="og:url"]')['content']='https://www.varunsahni.in/themes/'
for a in s.select('.rail a[aria-current]'):a.attrs.pop('aria-current',None);a['class']=[c for c in a.get('class',[]) if c!='is-current']
body='''<section class="theme-intro page-pad"><p class="overline">WEBSITE THEMES / 04 DIRECTIONS</p><h1>Pick a different view.</h1><p>Four complete themes, with the same projects and content. Open one to browse the site in that style.</p><div class="theme-verdict"><strong>Best fit for the main site: Mint.</strong><p>It gives the globe and technical illustrations the most consistent setting. New York is the more personal alternative, with a clearer connection to where I live and study.</p></div></section><section class="theme-grid page-pad" aria-label="Theme previews">'''
for i,t in enumerate(themes):
 link='/new-york/' if t['id']=='new-york' else '/?theme='+t['id']
 body+=f'''<article class="theme-card"><div class="theme-card-head"><span>0{i+1} / {html.escape(t['tag'])}</span><div class="theme-swatches" aria-label="Theme palette">'''+''.join(f'<i style="background:{t[k]}" aria-hidden="true"></i>' for k in ['bg','ink','accent'])+f'''</div></div><div class="theme-frame"><iframe title="{t['name']} homepage preview" src="/?theme={t['id']}&amp;preview=1" tabindex="-1" loading="lazy" aria-hidden="true"></iframe><a class="theme-preview-link" href="{link}" data-theme-link aria-label="Open the full {t['name']} theme"></a></div><div class="theme-card-copy"><h2>{t['name']}</h2><p>{html.escape(t['copy'])}</p><a class="action" href="{link}" data-theme-link>Explore {t['name']} <svg class="icon" aria-hidden="true"><use href="/design/icons.svg#arrow-up"></use></svg></a></div></article>'''
body+='''</section><section class="theme-results page-pad"><h2>Readability comparison.</h2><p>Contrast ratios below compare each palette’s text and links against its page background. Layout and interaction checks also cover the homepage and project pages at desktop and phone widths. These checks are a design review, not a visitor preference study.</p><div class="theme-table-scroll"><table><caption class="sr-only">Palette contrast ratios</caption><thead><tr><th scope="col">Theme</th><th scope="col">Main text</th><th scope="col">Secondary text</th><th scope="col">Links</th></tr></thead><tbody>'''
for t in themes:
 ratios=[contrast(t[k],t['bg']) for k in ['ink','muted','accent']];assert min(ratios)>=4.5
 t['ratios']={k:round(v,2) for k,v in zip(['text','secondary','links'],ratios)}
 body+='<tr><th scope="row">'+t['name']+'</th>'+''.join(f'<td>{v:.1f}:1</td>' for v in ratios)+'</tr>'
body+='''</tbody></table></div><p class="theme-method">All four palettes exceed 4.5:1 for the text/background pairs shown. Project illustrations retain their original palettes.</p></section>'''
s.select_one('main').clear();s.select_one('main').append(BeautifulSoup(body,'html.parser'))
(r/'themes').mkdir(exist_ok=True);(r/'themes/index.html').write_text(str(s))
(r/'design/theme-evaluation.json').write_text(json.dumps(themes,indent=2)+'\n')
index=json.loads((r/'design/search.json').read_text())
index.extend([{'title':'Compare website themes','path':'/themes/','type':'Page'},{'title':'New York edition','path':'/new-york/','type':'Page'}])
(r/'design/search.json').write_text(json.dumps(index,ensure_ascii=False))
sitemap=r/'sitemap.xml';sitemap.write_text(sitemap.read_text().replace('</urlset>','<url><loc>https://www.varunsahni.in/themes/</loc></url></urlset>'))
print(json.dumps({'themes':len(themes),'comparison':'/themes/','newYork':'/new-york/'}))

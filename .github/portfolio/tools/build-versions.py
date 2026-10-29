"""Build three complete local design directions over one curated content source."""
from pathlib import Path
import runpy,json,re,html
from bs4 import BeautifulSoup
R=Path(__file__).resolve().parents[1]
C=runpy.run_path(str(R/'tools/build-editorial.py'),run_name='__main__')
D=C['D'];P=C['P'];BY=C['BY'];POSTS=C['posts'];PAGES=C['PAGES'];STEPS=C['steps']
e=C['e'];ic=C['ic'];img=C['img'];link=C['link'];action=C['action'];caption=C['caption'];art=C['artwork'];quote=C['quote'];journal=C['journal'];RESUME=C['RESUME']
DARK_PROJECTS=json.loads((R/'source/dark-projects.json').read_text())
def dark_project(p):return {**p,**DARK_PROJECTS[p['slug']],**({'video':'/assets/demos/cabinai.mp4','image':'/assets/demos/cabinai-poster.jpg'} if p['slug']=='cabinai' else {})}
AWARDS=[
 ('2026','1st overall · Sweesh','Trust in the Hiring Funnel · team win. Sweesh lets people and institutions vouch for each other.','/credentials/'),
 ('2026','Jury Award · CabinAI','Qualcomm SparQ · solo entry among 166 teams','/work/cabinai/'),
 ('2025','Finalist · Code Buddy','Qualcomm SparQ · presented to the Qualcomm CTO','/work/code-buddy/'),
 ('2023','CCIB SCPay Award','Standard Chartered · Jenkins to Azure DevOps migration','/credentials/'),
 ('2022','DAAD Scholarship','Mixed-reality research · TU Braunschweig','/work/igcsm-life-cycle-anaysis/'),
 ('BPL','Silver medal · Mixed doubles','BITS Premier League · tennis','/beyond/')
]
PLAY='<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M9 5.5 19 12 9 18.5Z"/></svg>'
def demo(p,where='case'):
 if not p['video']:return ''
 href=('#project-demo' if where=='case' else '/work/'+p['slug']+'/#project-demo')
 return f'<a class="demo-open" data-demo-mode="{"inline" if where=="case" else "modal"}" data-project="/work/{p["slug"]}/" href="{href}" data-video="{e(p["video"])}" data-poster="{e(p["image"])}" data-title="{e(p["title"])}">{PLAY}Play demo</a>'
MONOGRAM='<svg viewBox="0 0 48 40" aria-hidden="true" class="vs-mark"><path d="M3 7 14 33 25 7M43 9H33a6 6 0 0 0 0 12h3a6 6 0 0 1 0 12H24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="square" stroke-linejoin="miter"/></svg>'
BASE={path:(R/path.lstrip('/')/('index.html' if path.endswith('/') else '')).read_text() for path,*_ in PAGES}
# Literal path helper also handles the 404 file.
def file_at(base,path):
 p=base/path.lstrip('/');return p/'index.html' if path.endswith('/') else p
CONCEPTS=[('editorial','Bold editorial','01'),('dark','Immersive dark','02'),('minimal','Minimal studio','03')]
def dock(concept,path):
 return '<nav class="concept-switcher" aria-label="Website design versions"><a href="/compare/">Compare designs</a><label><span class="sr-only">Switch website design</span><select aria-label="Switch website design">'+''.join(f'<option value="/{slug}{path}" {"selected" if concept==slug else ""}>{n} / {name}</option>' for slug,name,n in CONCEPTS)+'</select></label></nav>'
def localize(doc,concept,path):
 s=BeautifulSoup(doc,'html.parser')
 if concept=='dark':
  for node in s.find_all(string=lambda x:x and '—' in x):
   value=str(node)
   if node.parent.name=='title':value=value.replace(' — ',' | ')
   elif 'role-date' in node.parent.get('class',[]):value=value.replace('—','–')
   elif node.parent.find_parent(class_='toolbox'):value=value.replace(' — ',': ')
   else:value=value.replace(' — ', ', ').replace('—', ',').replace('checks , but with LLM reasoning', 'checks with LLM reasoning')
   node.replace_with(value)
  for tag in s.find_all(True):
   for attr in ['content','aria-label','data-title','data-name','data-alt','alt']:
    if attr in tag.attrs and isinstance(tag[attr],str):tag[attr]=tag[attr].replace(' — ', ', ').replace('—', ', ')
 for a in s.select('a[href]'):
  h=a['href']
  if h.startswith('/') and not h.startswith(('/resume.pdf','/assets/','/design/','/compare/','/editorial/','/dark/','/minimal/')):a['href']='/'+concept+h
 s.body['data-concept']=concept;s.body['data-search-index']='/'+concept+'/design/search.json'
 s.head.append(BeautifulSoup('<link rel="stylesheet" href="/design/concepts.css"><script src="/design/concepts.js" defer></script>','html.parser'))
 s.body.append(BeautifulSoup(dock(concept,path),'html.parser'))
 return str(s)
def shell(concept,path,title,body,active,desc):
 dark=concept=='dark'; name='VARUN SAHNI' if dark else 'Varun Sahni'
 if dark and path=='/':title='M.S. Computer Science, NYU Courant'
 if dark and path.startswith('/work/') and path!='/work/':desc=DARK_PROJECTS[path.strip('/').split('/')[-1]]['summary']
 nav=''.join(link(h,t,'nav-item'+(' is-current' if active==t else '')) for t,h in C['NAV'])
 fonts='Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500;600' if dark else 'Inter:wght@400;500;600;700'
 logo=link('/',('<span class="brand-avatar" aria-hidden="true"><img src="/assets/images/varun-linkedin.png" alt="" width="40" height="40"></span><span class="brand-name">Varun Sahni</span>' if dark else 'vs<span>.</span>'),'concept-logo')
 end=(f'<footer class="signal-footer"><p>CONTACT</p><h2>{link("/contact/","Say hello."+ic("arrow-up"))}</h2><div>{link("mailto:sahnicoder@gmail.com","sahnicoder@gmail.com")}{link("https://github.com/varunsahni18","GitHub ↗",external=True)}{link("https://www.linkedin.com/in/varun-sahni-profile/","LinkedIn ↗",external=True)}<span>NEW YORK · © 2026</span></div></footer>' if dark else f'<footer class="quiet-footer"><p>Thanks for stopping by.</p>{link("mailto:sahnicoder@gmail.com","sahnicoder@gmail.com ↗")}<div><span>Varun Sahni · New York</span>{link("https://github.com/varunsahni18","GitHub ↗",external=True)}{link("https://www.linkedin.com/in/varun-sahni-profile/","LinkedIn ↗",external=True)}<span>© 2026</span></div></footer>')
 if dark and path=='/contact/':end=f'<footer class="contact-footer page-pad"><span>Varun Sahni · New York</span>{link("/","Back to home "+ic("arrow"))}<span>© 2026</span></footer>'
 return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(title)} | Varun Sahni</title><meta name="description" content="{e(desc)}"><meta name="theme-color" content="{'#080d11' if dark else '#ffffff'}"><link rel="icon" href="/design/{concept}-mark.svg"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family={fonts}&display=swap" rel="stylesheet"><link rel="stylesheet" href="/design/shared.css"><link rel="stylesheet" href="/design/art.css"><link rel="stylesheet" href="/design/{concept}.css"><script src="/design/studio.js?v=6" defer></script></head><body><a href="#main" class="skip">Skip to content</a><header class="mobile-bar">{logo}{"" if dark else "<span>VARUN SAHNI</span>"}<button class="menu-button" aria-expanded="false" aria-controls="rail">Menu {ic('menu')}</button></header><header class="rail" id="rail"><div class="rail-brand">{logo}{"" if dark else "<span>"+name+"</span>"}</div><nav aria-label="Main navigation">{nav}</nav><div class="header-tools"><button class="search-open" aria-label="Search the website">{ic('search')}</button>{link(RESUME,'Résumé '+ic('arrow-up'),'resume-link',True)}</div></header><div class="site-canvas"><main id="main">{body}</main>{end}</div><dialog class="search-dialog" aria-labelledby="search-title"><div class="dialog-top"><h2 id="search-title">Find something</h2><button class="search-close" aria-label="Close search">{ic('close')}</button></div><input type="search" aria-label="Search projects and pages" placeholder="Projects, articles, experience…" id="site-search" autocomplete="off"><div class="search-results" aria-live="polite"></div><p class="search-help">TAB TO EXPLORE · ENTER TO OPEN · ESC TO CLOSE</p></dialog><dialog class="media-dialog" aria-label="Image viewer"><button class="media-close" aria-label="Close image">{ic('close')}</button><div class="media-content"></div></dialog><dialog class="demo-dialog" aria-labelledby="demo-title"><div class="dialog-top"><h2 id="demo-title">Project demo</h2><button class="demo-close" aria-label="Close demo">{ic("close")}</button></div><p class="demo-status" role="status" aria-live="polite"></p><video controls playsinline preload="none"></video><div class="demo-links"><a class="demo-project-link" href="/work/">Open project</a><a class="demo-file-link" href="/work/" target="_blank" rel="noopener">Open video</a></div></dialog></body></html>'''
def chronology(concept):
 minimal=concept=='minimal';h='My journey' if minimal else 'Experience & education'
 intro='<p>From BITS Pilani to New York, with a few turns along the way.</p>' if minimal else ''
 t=f'<section class="{concept}-journey" id="home-journey"><div class="section-intro"><span class="overline">THE JOURNEY</span><h2>{h}</h2>{intro}</div><div class="route-map" data-vertical="{"true" if minimal else "false"}"><svg class="route-line" aria-hidden="true"><path/></svg><ol class="route-stops">'
 for i,(date,name,copy,href,mark) in enumerate(STEPS if minimal else reversed(STEPS)):
  if not minimal and name=='NYU Courant':copy='M.S. Computer Science · 2026–2028 expected'
  t+=f'<li class="route-stop stop-{i+1}">{link(href,f"<span>{mark}</span>","route-node"+(" current" if name=="NYU Courant" else ""))}<div class="route-copy"><p class="route-date">{date}{" / NOW" if name=="NYU Courant" else ""}</p><h3>{name}</h3><p>{copy}</p></div></li>'
 return t+'</ol></div>'+action('/journey/','Full experience & education')+'</section>'
def dark_home():
 t=f'''<section class="dark-hero"><div class="dark-hero-content"><div class="hero-story"><div class="hero-heading"><h1>Varun Sahni</h1></div><p class="hero-degree">M.S. Computer Science · NYU Courant</p><p class="dark-intro">I build AI agents, developer tools, and on-device assistants. At Qualcomm, I architected Code Buddy, a code-review platform used by 12,000+ engineers.</p><p class="dark-context">Previously at Qualcomm and AMD.</p><div class="hero-actions">{action('#selected-work','Explore my work')}{link(RESUME,'View résumé '+ic('arrow-up'),'quiet-link',True)}</div></div><div class="orb-stage"><canvas class="systems-field" aria-hidden="true"></canvas><a class="orb-tag tag-one" href="/work/code-buddy/">01 / Code Buddy {ic('arrow-up')}</a><a class="orb-tag tag-two" href="/work/cabinai/">02 / CabinAI {ic('arrow-up')}</a><a class="orb-tag tag-three" href="/work/myai/">03 / MyAI {ic('arrow-up')}</a><a class="orb-tag tag-four" href="/work/healthsense/">04 / HealthSense {ic('arrow-up')}</a><a class="orb-tag tag-five" href="/work/digital-twin-mapmyindia/">05 / Digital Map {ic('arrow-up')}</a></div></div><div class="hero-scroll">{link('#selected-work','Explore below '+ic('down'))}</div></section>'''
 featured=[dark_project(BY[x]) for x in ['code-buddy','cabinai','myai']]
 t+='<section class="dark-reel" id="selected-work"><div class="section-intro reel-heading"><div>'+caption('SELECTED WORK')+'<h2>Selected projects.</h2></div>'+action('/work/','All 23 projects')+'</div><div class="reel-navigation"><div class="feature-tabs" role="tablist" aria-label="Selected projects">'
 for i,p in enumerate(featured):t+=f'<button role="tab" id="tab-{p["slug"]}" aria-controls="panel-{p["slug"]}" aria-selected="{"true" if i==0 else "false"}" tabindex="{0 if i==0 else -1}">0{i+1} / {p["title"]}</button>'
 t+='</div><div class="reel-arrows"><button data-reel-step="-1" aria-label="Previous project">'+ic('back')+'</button><button data-reel-step="1" aria-label="Next project">'+ic('arrow')+'</button></div></div>'
 for i,p in enumerate(featured):
  t+=f'<article class="feature-panel dark-reel-panel" role="tabpanel" id="panel-{p["slug"]}" aria-labelledby="tab-{p["slug"]}" {"hidden" if i else ""}><div class="reel-image">{link("/work/"+p["slug"]+"/",art(p),"project-cover")}</div><div class="reel-copy"><p class="overline">{e(p["group"])}</p><h3>{p["title"]}</h3><p>{e(p["summary"])}</p><div class="project-actions">{action("/work/"+p["slug"]+"/","Open project")}{demo(p,"home")}</div><div class="reel-index">0{i+1}<span>/ 03</span></div></div></article>'
 t+='</section>'+dark_awards()
 lead=D['leadership'][0]
 t+=f'<section class="dark-community"><div>{caption("BEYOND THE TERMINAL")}<h2>Labs &amp; leadership.</h2><p>At BITS Pilani, I led a 40-member AR/VR team, helped establish student labs, and organized a VR Experience Zone at Oasis.</p>{action("/beyond/","Labs, leadership & life")}</div><figure>{img(lead["images"][0]["src"],lead["images"][0]["alt"])}<figcaption>KALIPATNAPU AR/VR LAB / BITS PILANI</figcaption></figure></section>'
 t+='<section class="dark-recommendations"><div class="section-intro">'+caption('RECOMMENDATIONS')+'<h2>Recommendations.</h2></div><div class="colleagues">'+''.join(quote(c) for c in D['recommendations'])+'</div></section><section class="dark-writing"><div class="section-intro reel-heading"><div>'+caption('WRITING')+'<h2>Writing.</h2></div>'+action('/writing/','All articles')+'</div>'+''.join(journal(p,i) for i,p in enumerate(POSTS[:2]))+'</section>'
 main=BeautifulSoup(t,'html.parser')
 sections={x.get('class',[None])[0]:x for x in main.find_all('section',recursive=False)}
 return ''.join(str(sections[k]) for k in ['dark-hero','dark-reel','home-awards','dark-recommendations'])+chronology('dark')+''.join(str(sections[k]) for k in ['dark-writing','dark-community'])

def dark_awards():
 return '<section class="home-awards" id="home-awards"><div class="award-heading">'+caption('AWARDS & RECOGNITION')+'<h2>Awards & distinctions.</h2>'+link('/credentials/','Certificates & details '+ic('arrow'),'text-link')+'</div><div class="home-award-list">'+''.join('<a href="'+href+'"><span>'+year+'</span><div><h3>'+title+'</h3><p>'+copy+'</p></div>'+ic('arrow-up')+'</a>' for year,title,copy,href in AWARDS if year!='BPL')+'</div></section>'
def dark_contact():
 return f'''<section class="dark-contact page-pad"><div class="contact-copy">{caption('CONTACT')}<h1>Get in touch<span>.</span></h1><p class="contact-deck">Email me about AI systems, developer tools, research, or a project.</p><div class="contact-email"><span>THE BEST WAY TO REACH ME</span>{link('mailto:sahnicoder@gmail.com','sahnicoder@gmail.com '+ic('arrow-up'))}<button class="copy-email" data-copy="sahnicoder@gmail.com">Copy email address {ic('copy')}</button><p class="copy-status" role="status" aria-live="polite"></p></div><div class="contact-networks">{link('https://www.linkedin.com/in/varun-sahni-profile/','LinkedIn '+ic('arrow-up'),external=True)}{link('https://github.com/varunsahni18','GitHub '+ic('arrow-up'),external=True)}{link('https://leetcode.com/u/sahnicoder/','LeetCode '+ic('arrow-up'),external=True)}{link(RESUME,'Résumé '+ic('arrow-up'),external=True)}</div></div><aside class="contact-profile"><figure>{img('/assets/images/varun-linkedin.png','Varun Sahni')}</figure><div><h2>Varun Sahni</h2><p>M.S. Computer Science<br>NYU Courant · 2026–2028</p><p class="profile-location">New York, NY</p>{link("https://www.google.com/maps/search/?api=1&query=New+York+NY","View map "+ic("arrow-up"),"contact-map",True)}{link('mailto:vs3606@nyu.edu','vs3606@nyu.edu '+ic('arrow-up'),'text-link')}</div></aside></section>'''

def minimal_home():
 t=f'''<section class="minimal-hero"><div class="minimal-intro"><p class="overline">ENGINEER · NEW YORK</p><h1>I’m Varun.<br>I build software<br>and study at NYU.</h1><p>I’m pursuing my M.S. in Computer Science at <strong>NYU Courant</strong>, focusing on machine learning, LLMs, and AI systems.</p><p>Previously, I built GenAI developer tooling at Qualcomm and worked on performance engineering at AMD.</p><div class="intro-links">{link('/work/','Selected work '+ic('arrow'))}{link(RESUME,'Résumé '+ic('arrow-up'),external=True)}{link('mailto:sahnicoder@gmail.com','Email '+ic('arrow-up'))}</div></div><figure class="minimal-portrait">{img('/assets/images/VarunSahniImage.jpg','Varun Sahni',True)}<figcaption>Always exploring.</figcaption></figure></section><section class="minimal-selected" id="selected-work"><div class="section-intro minimal-section-heading"><div><h2>Selected work</h2><p>A few projects that explain what I like building.</p></div>{link('/work/','All 23 projects '+ic('arrow'),'text-link')}</div>'''
 for p in [BY['code-buddy'],BY['cabinai'],BY['myai']]:
  t+=f'<article class="minimal-project"><a href="/work/{p["slug"]}/" class="project-cover">{art(p)}</a><div><p class="overline">{e(p["group"])}</p><h3>{link("/work/"+p["slug"]+"/",e(p["title"]))}</h3><p>{e(p["summary"])}</p>{link("/work/"+p["slug"]+"/","Read about the project "+ic("arrow"),"text-link")}</div></article>'
 t+='</section>'+chronology('minimal')
 t+='<section class="minimal-recommendations"><div class="section-intro"><h2>Kind words</h2><p>From colleagues at Qualcomm and AMD.</p></div><div class="colleagues">'+''.join(quote(c) for c in D['recommendations'])+'</div></section>'
 t+=f'<section class="minimal-beyond"><h2>Outside work</h2><p>At BITS Pilani, I led a 40-member AR/VR team, helped establish student labs, and organized hands-on experiences at Oasis. Away from a screen, I’m usually playing a sport or exploring somewhere new.</p>{link("/beyond/","Communities, hobbies & more "+ic("arrow"),"text-link")}</section><section class="minimal-writing"><div class="section-intro minimal-section-heading"><h2>Writing</h2>{link("/writing/","All articles "+ic("arrow"),"text-link")}</div>'+''.join(journal(p,i) for i,p in enumerate(POSTS[:2]))+'</section>'
 return t

def work(concept):
 dark=concept=='dark';title='Projects';copy='AI systems, mobile apps, games, and spatial computing.' if dark else 'A collection of systems, apps, games, and experiments. Use the filters to find something specific.'
 t=f'<header class="page-head page-pad">{caption("23 PROJECTS / 2020–2026")}<h1>{title}</h1><p class="page-deck">{copy}</p></header><section class="archive page-pad"><div class="work-controls"><div class="filters" role="group" aria-label="Filter projects">'+''.join(f'<button data-filter="{g}" aria-pressed="{"true" if i==0 else "false"}">{g}</button>' for i,g in enumerate(C['groups']))+'</div><label class="project-search">'+ic('search')+'<input type="search" aria-label="Find a project" placeholder="Find a project"></label></div><p class="results-count" aria-live="polite">23 projects</p><div class="'+concept+'-project-archive">'
 for i,p in enumerate(P):
  if dark:p=dark_project(p)
  t+=f'<article class="work-row {concept}-archive-project" data-group="{e(p["group"])}" data-name="{e(p["title"]+" "+p["summary"]+" "+p["tags"])}" data-project="{p["slug"]}"><a href="/work/{p["slug"]}/" class="project-cover">{art(p)}</a><div class="archive-copy"><span class="index-no">{i+1:02} / {e(p["group"])}</span><h2>{link("/work/"+p["slug"]+"/",e(p["title"]))}</h2><p>{e(p["summary"])}</p><div class="project-actions">{link("/work/"+p["slug"]+"/","View project "+ic("arrow-up"),"text-link")}{demo(p,"archive") if dark else ""}</div></div></article>'
 return t+'</div><div class="empty-state" hidden><h2>No matching projects.</h2><p>Try another keyword or category.</p><button class="clear-filters action">Reset filters '+ic('arrow')+'</button></div></section>'

def project(concept,p,i):
 dark=concept=='dark'
 if dark:p=dark_project(p)
 project_links=list({h:(h,t) for h,t in reversed(p['links'])}.values())[::-1] if dark else p['links']
 resources=''.join(link(h,e(t)+ic('arrow-up'),'resource-link',h.startswith('http')) for h,t in project_links);n=P[(i+1)%len(P)]
 head=f'<header class="concept-case-head">{link("/work/","← All projects","back-link")}<p class="overline">{e(p["group"])}</p><h1>{e(p["title"])}</h1><p class="case-summary">{e(p["summary"])}</p><p class="case-tags">{e(p["tags"])}</p>{demo(p) if dark else ""}</header>'
 visual='<div class="concept-case-art">'+art(p)+'</div>'
 t=f'<section class="{concept}-case-hero">'+head+visual+'</section>'
 detail='<h2>What I built</h2><ul class="detail-list">'+''.join('<li>'+e(x)+'</li>' for x in p['bullets'])+'</ul>' if p['bullets'] else '<h2>The project</h2><p>The demonstration and linked materials document this project.</p>'
 if dark:detail='<h2>About the project</h2><p class="project-overview">'+e(p['overview'])+'</p>'+ (detail if p['bullets'] else '')
 t+='<section class="case-body page-pad"><aside>'+caption('RESOURCES')+resources+'</aside><div class="case-reading">'+detail
 if p['video']:t+=f'<figure class="case-video" id="project-demo"><h2>Project demo</h2><video controls playsinline preload="none" aria-label="{e(p["title"])} project demo" poster="{e(p["image"])}"><source src="{e(p["video"])}" type="video/mp4"></video><figcaption><span class="inline-video-status" role="status" aria-live="polite">Project recording</span>{link("/assets/videos/CabinAI_Demo.mp4","Full recording "+ic("arrow-up"),"text-link",True) if p["slug"]=="cabinai" else ""}</figcaption></figure>'
 elif p['image'] and p['title'] in ['MyAI','HealthSense']:t+='<figure class="case-screenshot">'+img(p['image'],p['title']+' interface')+'<figcaption>From the project</figcaption></figure>'
 t+='</div></section><section class="next-work page-pad">'+caption('NEXT PROJECT')+link('/work/'+n['slug']+'/',e(n['title'])+ic('arrow-up'))+'</section>'
 return t
# Reuse the verified content of long-form sections, with new layout systems and headings.
RENAME={'THE JOURNEY.':'Experience & education','BEYOND\nTHE CODE.':'Beyond work','THE MILESTONES.':'Awards & credentials','NOTEBOOK.':'Writing','SAY HELLO.':'Get in touch','WHERE I’VE WORKED':'Experience','WHERE I’VE STUDIED':'Education','THE PROBLEMS I LIKE':'Interests','THE TOOLBOX':'Tools & coursework','AWAY FROM THE DESK':'Away from the desk','CREDENTIALS':'Credentials','LET’S COMPARE NOTES.':'Let’s connect','WRONG TURN.':'Page not found'}
def interior(path,concept):
 main=BeautifulSoup(BASE[path],'html.parser').select_one('main')
 for h in main.select('h1,h2'):
  key=h.get_text().strip();key2=h.get_text('\n',strip=True)
  if key in RENAME:h.clear();h.append(RENAME[key])
  elif key2 in RENAME:h.clear();h.append(RENAME[key2])
  elif key=='NYUCOURANT':h.clear();h.append('NYU Courant')
 if concept=='dark' and path=='/beyond/':
  stories=main.select('.leadership-story')
  for index,title,role,dates in [(0,'Kalipatnapu AR/VR Lab','President · BITS Pilani','May 2023 – June 2024'),(1,'Coding Club','Blockchain Department Coordinator · BITS Pilani','July 2022 – May 2023'),(7,'ACM Club','App Developer · BITS Pilani','')]:
   story=stories[index];heading=story.select_one('h2');heading.string=title
   meta=BeautifulSoup('<p class="leadership-meta">'+e(role)+'</p>','html.parser');heading.insert_after(meta)
   if dates:story.select_one('.overline').string=dates
  for index,asset,alt in [(1,'coding-club-linkedin.jpg','Coding Club BITS Pilani official logo'),(7,'bits-acm-linkedin.jpg','BITS ACM official logo')]:
   panel=stories[index].select_one('.leadership-photo');panel.clear();panel['class'].append('logo-panel')
   panel.append(BeautifulSoup(img('/assets/images/'+asset,alt), 'html.parser'))
 if concept=='dark':
  for image in main.select('.article-byline img'):image['src']='/assets/images/varun-linkedin.png'
  if path=='/journey/':
   bio=main.select_one('.longer-bio details')
   for paragraph in bio.select('p'):paragraph.decompose()
   for text in [
    'At Qualcomm, I architected Code Buddy, a multi-agent code-review platform used by 12,000+ engineers across 4,000+ repositories. It delivered over two million automated reviews. I also built agents for modem hotline triage and interactive protocol workflows, combining source-code retrieval, tool calls, and validation.',
    'My independent work explores on-device AI. CabinAI combines driver monitoring, voice, gestures, and local retrieval with cloud reasoning. MyAI runs local tools and quantized language-model inference on Android. HealthSense explores biosignal classification and explanations through an experimental dashboard. CabinAI won the SparQ 2026 Jury Award as a solo entry among 166 teams.',
    'Before Qualcomm, I worked on C++ performance engineering at AMD and deployment pipelines at Standard Chartered. At BITS Pilani, I helped establish student labs and led a 40-member AR/VR team. A DAAD Scholarship took me to TU Braunschweig for mixed-reality research. I now study Computer Science at NYU Courant.'
   ]:bio.append(BeautifulSoup('<p>'+e(text)+'</p>','html.parser'))
   main.select_one('.study-block .overline').string='EDUCATION'
   main.select_one('.study-years').replace_with(BeautifulSoup('<div class="study-years"><span class="year-range">2026–2028</span><p><span>August 2026 – May 2028</span><span>Expected graduation</span></p></div>','html.parser'))
  if path=='/beyond/':
   deck=main.select_one('.page-deck')
   if deck:deck.decompose()
  if path=='/credentials/':
   main.select_one('.award-index').clear()
   for year,title,copy,href in AWARDS:main.select_one('.award-index').append(BeautifulSoup('<article><span>'+year+'</span><h2>'+e(title)+'</h2><p>'+e(copy)+'</p></article>','html.parser'))
  for h in main.select('h2'):
   if h.get_text(strip=True)=='Away from the desk':h.string='Sports & interests'

 return main.decode_contents()
for concept,_,_ in CONCEPTS:
 for path,title,active,desc in PAGES:
  if concept=='editorial':doc=BASE[path]
  else:
   if path=='/':body=dark_home() if concept=='dark' else minimal_home()
   elif path=='/contact/' and concept=='dark':body=dark_contact()
   elif path=='/work/':body=work(concept)
   elif path.startswith('/work/'):
    slug=path.strip('/').split('/')[-1];p=BY[slug];body=project(concept,p,P.index(p))
   else:body=interior(path,concept)
   doc=shell(concept,path,title,body,active,desc)
  dest=file_at(R/concept,path);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(localize(doc,concept,path))
 index=[{**x,'title':('M.S. Computer Science, NYU Courant' if concept=='dark' and x['path']=='/' else x['title']),'path':'/'+concept+x['path']} for x in C['SEARCH']];target=R/concept/'design/search.json';target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(index,ensure_ascii=False))
# Keep existing local root links working, and make the version switcher visible there too.
for path,*_ in PAGES:file_at(R,path).write_text(localize(BASE[path],'editorial',path))
print(json.dumps({'versions':3,'pagesPerVersion':len(PAGES),'totalVersionPages':len(PAGES)*3,'comparison':'/compare/'}))

from pathlib import Path
import json,html,re,math,datetime
from bs4 import BeautifulSoup
import markdown,yaml
R=Path(__file__).resolve().parents[1]
D=json.loads((R/'source/content.json').read_text())
import shutil
ASSETS=R/'assets' if (R/'assets').exists() else R.parents[1]/'assets'
shutil.copy2(ASSETS/'documents/Varun_Sahni_resume.pdf',R/'resume.pdf')
P=D['projects']; BY={p['slug']:p for p in P}; RESUME='/resume.pdf'
def e(x):return html.escape(str(x),quote=True)
def ic(n):return f'<svg class="icon" aria-hidden="true"><use href="/design/icons.svg#{n}"/></svg>'
def img(src,alt,early=False):return f'<img src="{e(src)}" alt="{e(alt)}" loading="{"eager" if early else "lazy"}" decoding="async">'
def link(url,text,cls='',external=False):return f'<a href="{e(url)}" class="{cls}"'+(' aria-current="page"' if 'is-current' in cls else '')+(' aria-label="Send an email"' if text.startswith('<svg') and text.endswith('</svg>') else '')+(' target="_blank" rel="noopener noreferrer"' if external else '')+f'>{text}</a>'
def action(url,text,cls=''):return link(url,e(text)+ic('arrow-up'),'action '+cls)
def caption(text):return f'<p class="overline">{text}</p>'
from project_art import cover as artwork
NAV=[('Home','/'),('Work','/work/'),('Journey','/journey/'),('Writing','/writing/'),('Beyond','/beyond/'),('Credentials','/credentials/'),('Contact','/contact/')]
SEARCH=[]
PAGES=[]
def write(path,title,body,active='',desc='Varun Sahni. M.S. Computer Science at NYU Courant. Previously Qualcomm and AMD. AI agents, developer tools, and systems.'):
 dest=R/path.lstrip('/'); dest=dest/'index.html' if path.endswith('/') else dest;dest.parent.mkdir(parents=True,exist_ok=True)
 nav=''.join(link(h,f'<span class="nav-no">0{i+1}</span><span>{t}</span><span class="nav-arrow">↗</span>','nav-item '+('is-current' if active==t else '')) for i,(t,h) in enumerate(NAV))
 shell=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(title)} — Varun Sahni</title><meta name="description" content="{e(desc)}"><meta name="theme-color" content="#f2f2f0"><link rel="icon" href="/design/studio-mark.svg" type="image/svg+xml"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;500;600;700;800&family=DM+Sans:wght@400;500;600;700&display=swap" rel="stylesheet"><link rel="stylesheet" href="/design/studio.css?v=3"><script src="/design/studio.js?v=3" defer></script></head><body><a class="skip" href="#main">Skip to content</a><header class="mobile-bar">{link('/','VS<span>↗</span>','signature')}<span>NEW YORK, NY</span><button class="menu-button" aria-expanded="false" aria-controls="rail">Menu {ic('menu')}</button></header><aside class="rail" id="rail"><div class="rail-top">{link('/','VS<span>↗</span>','signature')}<p>VARUN SAHNI<br><span>ENGINEER &amp; NYU CS</span></p></div><nav aria-label="Main navigation">{nav}</nav><div class="rail-bottom"><button class="search-open">{ic('search')} Search <kbd>⌘ K</kbd></button>{link(RESUME,'Download résumé '+ic('download'),'rail-resume',True)}<div class="rail-social">{link('https://github.com/varunsahni18',ic('github')+'<span>GitHub</span>',external=True)}{link('https://www.linkedin.com/in/varun-sahni-profile/',ic('linkedin')+'<span>LinkedIn</span>',external=True)}</div><span class="rail-location"><i></i> NEW YORK, NY</span></div></aside><div class="site-canvas"><main id="main">{body}</main><footer class="endcap"><div class="endcap-head"><span>HAVE A PROJECT, AN IDEA,<br>OR A GOOD QUESTION?</span>{link('mailto:sahnicoder@gmail.com',ic('arrow-up'),'endcap-arrow')}</div><h2>{link('/contact/','LET’S TALK<span>↗</span>')}</h2><div class="endcap-links">{link('mailto:sahnicoder@gmail.com','sahnicoder@gmail.com')}{link('https://github.com/varunsahni18','GitHub ↗',external=True)}{link('https://www.linkedin.com/in/varun-sahni-profile/','LinkedIn ↗',external=True)}<span>© 2026 VARUN SAHNI</span></div></footer></div><dialog class="search-dialog" aria-labelledby="search-title"><div class="dialog-top"><h2 id="search-title">LOOKING FOR SOMETHING?</h2><button class="search-close" aria-label="Close search">{ic('close')}</button></div><input type="search" aria-label="Search projects and pages" placeholder="A project, a topic, a chapter…" id="site-search" autocomplete="off"><div class="search-results" aria-live="polite"></div><p class="search-help">TAB TO EXPLORE · ENTER TO OPEN · ESC TO CLOSE</p></dialog><dialog class="media-dialog" aria-label="Image viewer"><button class="media-close" aria-label="Close image">{ic('close')}</button><div class="media-content"></div></dialog></body></html>'''
 dest.write_text(shell)
 PAGES.append((path,title,active,desc))
 SEARCH.append({'title':title,'path':path,'type':'Article' if path.startswith('/blog/20') else 'Project' if path.startswith('/work/') and path!='/work/' else 'Page'})

def page_head(kicker,title,description=''):
 return f'<header class="page-head page-pad">{caption(kicker)}<h1>{title}</h1>'+ (f'<p class="page-deck">{description}</p>' if description else '')+'</header>'

def quote(c):
 return f'<article class="colleague"><div class="colleague-person">{img(c["photo"],c["name"])}<div><h3>{e(c["name"])}</h3><p>{e(c["role"])}</p></div>{ic("arrow-up")}</div><blockquote>“{e(c["preview"])}”</blockquote><details><summary>Full recommendation {ic("plus")}</summary><div class="expanded-copy">'+''.join('<p>'+e(t)+'</p>' for t in c['paragraphs'])+f'<p class="small">{e(c["meta"])}</p>{link(c["profile"],"LinkedIn recommendation ↗",external=True)}</div></details></article>'

posts=[]
for f in sorted((R/'source/site-snapshot/_posts').glob('*.md'),reverse=True):
 _,front,body=f.read_text().split('---',2);m=yaml.safe_load(front);date=f.name[:10];y,mo,d=date.split('-');path=f'/blog/{y}/{mo}/{d}/{f.stem[11:]}/'
 body=markdown.markdown(body,extensions=['fenced_code','tables','toc']); soup=BeautifulSoup(body,'html.parser')
 for h in soup.select('h2,h3'):
  if not h.get('id'):h['id']=re.sub('[^a-z0-9]+','-',h.get_text().lower()).strip('-')
 posts.append({'title':m['title'],'date':date,'path':path,'body':str(soup),'excerpt':soup.find('p').get_text(' ',strip=True),'minutes':max(2,math.ceil(len(soup.get_text().split())/220)),'tags':m.get('tags',[]),'toc':[(h.get_text(),h['id']) for h in soup.select('h2')]})
def journal(p,i):
 return link(p['path'],f'<span class="journal-number">0{i+1}</span><div><p class="overline">{p["date"]} <b>·</b> {p["minutes"]} MIN READ</p><h3>{e(p["title"])}</h3><p class="journal-excerpt">{e(p["excerpt"][:170])}…</p></div>{ic("arrow-up")}','journal-entry')

# Home: one identity spread, an interactive work spread, a graphic chronology.
hero=f'''<section class="identity page-pad"><div class="edition-line"><span>SOFTWARE ENGINEER / M.S. COMPUTER SCIENCE</span><span>BASED IN NEW YORK {ic('pin')}</span></div><h1 class="mast-name"><span>VARUN</span> <span>SAHNI<span class="accent">.</span></span></h1><div class="identity-grid"><figure class="identity-photo">{img('/assets/images/VarunSahniImage.jpg','Varun Sahni',True)}<figcaption>VARUN / AWAY FROM THE TERMINAL</figcaption></figure><div class="identity-copy"><h2>AI agents.<br>Developer tools.<br>On-device systems.</h2><p>I’m an engineer pursuing my M.S. in Computer Science at <strong>NYU Courant</strong>. Before New York, I built GenAI tooling at Qualcomm and worked on performance systems at AMD.</p>{action('#selected-work','Explore the work','dark-action')}</div><div class="now-column"><p class="overline">RIGHT NOW</p><h3>NYU<br>COURANT</h3><p>M.S. Computer Science<br>2026 — 2028</p><div class="past-note"><span>BEFORE THAT</span><p>Qualcomm <small>2024–26</small><br>AMD <small>2024</small><br>BITS Pilani <small>2020–24</small></p></div>{link(RESUME,'Résumé '+ic('arrow-up'),'text-link',True)}</div></div><div class="identity-bottom"><span>SELECTED WORK &amp; EVERYTHING THAT LED HERE</span>{link('#selected-work','SCROLL TO EXPLORE '+ic('down'))}</div></section>'''
featured=[BY['code-buddy'],BY['cabinai'],BY['myai']]
feature='<section class="selected-spread" id="selected-work"><div class="spread-top"><div>'+caption('01 / SELECTED WORK')+'<h2>SELECTED<br>PROJECTS.</h2></div>'+action('/work/','All 23 projects')+'</div><div class="feature-tabs" role="tablist" aria-label="Selected projects">'
for i,p in enumerate(featured):feature+=f'<button role="tab" id="tab-{p["slug"]}" aria-controls="panel-{p["slug"]}" aria-selected="{"true" if i==0 else "false"}" tabindex="{0 if i==0 else -1}">0{i+1} / {e(p["title"])}</button>'
feature+='</div>'
for i,p in enumerate(featured):
 contexts=[('QUALCOMM / 2024–2026','Code review, at engineering scale.','A code-review platform for 12,000+ engineers and 4,000+ repositories. My work spanned review agents, dependency-aware retrieval, fix generation, and evaluation.'),('SPARQ TECHFEST / 2026','Seven agents. One cabin.','A solo hackathon prototype combining driver monitoring, local safety decisions, voice, retrieval, and selective cloud reasoning. Jury Award winner among 166 teams.'),('ANDROID / ON-DEVICE AI','An assistant with no internet permission.','A local Android assistant with deterministic routing, caching, tools, and Genie-backed inference. A build guard keeps network permission out of the default APK.')][i]
 feature+=f'<article class="feature-panel" id="panel-{p["slug"]}" role="tabpanel" aria-labelledby="tab-{p["slug"]}" {"hidden" if i else ""}><div class="feature-art">{link("/work/"+p["slug"]+"/",artwork(p),"project-cover")}</div><div class="feature-story">{caption(contexts[0])}<h3>{e(p["title"])}</h3><p class="feature-line">{contexts[1]}</p><p>{contexts[2]}</p>{action("/work/"+p["slug"]+"/","Inside the project")}</div></article>'
feature+='</section>'
steps=[('2020–24','BITS Pilani','Computer science. Apps, games, and student-led labs.','/journey/','BITS'),('2022','Invoxel','AR galleries, spatial anchors, and museum interactions.','/work/art-gallery/','AR'),('2022–23','TU Braunschweig','DAAD scholarship. Mixed-reality research with HoloLens.','/work/igcsm-life-cycle-anaysis/','TU'),('2023','Standard Chartered','SC Pay deployment pipelines and Azure DevOps migration.','/journey/','SC'),('2024','AMD','Parallel C++ trace processing and performance engineering.','/journey/','AMD'),('2024–26','Qualcomm','Code Buddy, AI agents, retrieval, and developer tooling.','/work/code-buddy/','Q'),('2026–28','NYU Courant','M.S. Computer Science. A new chapter in New York.','/journey/','NYU')]
journey='<section class="route-spread page-pad" id="home-journey"><div class="spread-top"><div>'+caption('02 / THE JOURNEY')+'<h2>FROM BITS<br>TO NYU.</h2></div><p>From BITS Pilani to New York.<br>Follow the turns.</p></div><div class="route-map"><svg class="route-line" aria-hidden="true"><path/></svg><ol class="route-stops">'
for i,(date,name,copy,href,mark) in enumerate(steps):journey+=f'<li class="route-stop stop-{i+1}">{link(href,f"<span>{mark}</span>","route-node"+(" current" if i==6 else ""))}<div class="route-copy"><p class="route-date">{date}{" / NOW" if i==6 else ""}</p><h3>{e(name)}</h3><p>{copy}</p></div></li>'
journey+='</ol></div>'+action('/journey/','Experience & education')+'</section>'
lead=D['leadership'][0];leadimg=lead['images'][0]['src'] if lead['images'] else '/assets/images/VarunSahniImage.jpg'
community=f'<section class="community-spread page-pad"><div class="community-copy">{caption("03 / OUTSIDE THE CODE")}<h2>AR/VR<br>AT BITS.</h2><p class="community-lead">A 40-person team.<br>A lab built by students.</p><p>As founding president of the Kalipatnapu AR/VR Lab, I helped students turn experiments into immersive experiences — including the VR Experience Zone at Oasis.</p>{action("/beyond/","The people & projects")}</div><figure>{img(leadimg,"Kalipatnapu AR/VR Lab at BITS Pilani")}<figcaption>KALIPATNAPU AR/VR LAB / BITS PILANI</figcaption></figure></section>'
recs='<section class="recommendation-spread page-pad"><div class="spread-top"><div>'+caption('04 / RECOMMENDATIONS')+'<h2>PEOPLE I’VE<br>WORKED WITH.</h2></div></div><div class="colleagues">'+''.join(quote(c) for c in D['recommendations'])+'</div></section>'
notes='<section class="journal-spread page-pad"><div class="spread-top"><div>'+caption('05 / WRITING')+'<h2>FROM MY<br>NOTEBOOK.</h2></div>'+action('/writing/','All articles')+'</div>'+''.join(journal(p,i) for i,p in enumerate(posts[:2]))+'</section>'
write('/','Engineer, NYU CS',hero+feature+journey+community+recs+notes,'Home')

# Work is an index with a live visual preview, rather than a card catalog.
groups=['All','AI systems','Spatial & AR','Apps & web','Games','Systems & research']
filters='<div class="work-controls"><div class="filters" role="group" aria-label="Filter projects">'+''.join(f'<button data-filter="{g}" aria-pressed="{"true" if i==0 else "false"}">{g}</button>' for i,g in enumerate(groups))+'</div><label class="project-search">'+ic('search')+'<input type="search" aria-label="Find a project" placeholder="Search the archive"></label></div>'
archive=page_head('23 PROJECTS / AI, SOFTWARE & SPATIAL COMPUTING','WORK<span class="accent">.</span>','A project index, from enterprise systems to experiments. Hover or focus a project to preview it; open it for the details.')+'<section class="archive page-pad">'+filters+'<p class="results-count" aria-live="polite">23 projects</p><div class="work-index"><div class="work-rows">'
for i,p in enumerate(P):
 archive+=f'<article class="work-row" data-group="{e(p["group"])}" data-name="{e(p["title"]+" "+p["summary"]+" "+p["tags"])}" data-project="{p["slug"]}"><a class="work-row-link" href="/work/{p["slug"]}/"><span class="index-no">{i+1:02}</span><div><h2>{e(p["title"])}</h2><p>{e(p["group"])}</p></div>{ic("arrow-up")}</a><div class="mobile-work-art">{artwork(p)}</div><template class="project-preview-template"><div class="preview-art">{artwork(p)}</div><div class="preview-caption"><h3>{e(p["title"])}</h3><p>{e(p["summary"])}</p>{action("/work/"+p["slug"]+"/","View project")}</div></template></article>'
archive+='</div><aside class="work-preview" aria-label="Project preview"><div class="preview-art">'+artwork(P[0])+'</div><div class="preview-caption"><h3>'+e(P[0]['title'])+'</h3><p>'+e(P[0]['summary'])+'</p>'+action('/work/code-buddy/','View project')+'</div></aside></div><div class="empty-state" hidden><h2>NO MATCHES.</h2><p>Try another project name or category.</p><button class="clear-filters action">Reset filters '+ic('arrow-up')+'</button></div></section>'
write('/work/','Work',archive,'Work')

for i,p in enumerate(P):
 resources=''.join(link(h,e(t)+ic('arrow-up'),'resource-link',h.startswith('http')) for h,t in p['links'])
 head=f'<header class="case-head page-pad">{link("/work/","← ALL PROJECTS","back-link")}{caption(e(p["group"]))}<h1>{e(p["title"])}</h1><p class="case-summary">{e(p["summary"])}</p><div class="case-tags">{e(p["tags"])}</div></header>'
 stats={'Code Buddy':[('12K+','Engineers'),('4K+','Repositories'),('2M+','Reviews')],'CabinAI':[('7','Agents'),('166','Teams at SparQ'),('2026','Jury Award')],'MyAI':[('4','Routing tiers'),('0','Internet permission'),('Genie','Local inference')],'HealthSense':[('5','Signal types'),('1D CNN','ECG component'),('ONNX','Model export')]}.get(p['title'],[])
 nums='<div class="case-numbers">'+''.join(f'<div><strong>{n}</strong><span>{t}</span></div>' for n,t in stats)+'</div>' if stats else ''
 detail='<h2>THE ENGINEERING</h2><ul class="detail-list">'+''.join('<li>'+e(t)+'</li>' for t in p['bullets'])+'</ul>' if p['bullets'] else '<h2>THE PROJECT</h2><p>The demonstration and linked resources below document this project.</p>'
 media=''
 if p['video']:media=f'<figure class="case-video"><video controls preload="none" poster="{e(p["image"])}"><source src="{e(p["video"])}" type="video/mp4"></video><figcaption>ORIGINAL PROJECT DEMONSTRATION</figcaption></figure>'
 elif p['image'] and p['title'] in ['MyAI','HealthSense']:media='<figure class="case-screenshot">'+img(p['image'],p['title']+' project interface')+'<figcaption>FROM THE PROJECT</figcaption></figure>'
 n=P[(i+1)%len(P)]
 body=head+'<div class="case-visual">'+artwork(p)+'</div><section class="case-body page-pad"><aside><p class="overline">PROJECT RESOURCES</p>'+resources+'</aside><div class="case-reading">'+nums+detail+media+'</div></section><section class="next-work page-pad">'+caption('NEXT PROJECT')+link('/work/'+n['slug']+'/',e(n['title'])+ic('arrow-up'))+'</section>'
 write('/work/'+p['slug']+'/',p['title'],body,'Work',p['summary'])

# Journey: chronological experience index, with all original detail available.
j=page_head('EXPERIENCE / EDUCATION / INTERESTS','THE JOURNEY<span class="accent">.</span>')+f'<section class="study-block page-pad"><div>{caption("CURRENT CHAPTER / NEW YORK")}<h2>NYU<br>COURANT</h2></div><div><h3>M.S. Computer Science</h3><p>New York University<br>Courant Institute of Mathematical Sciences</p><p>Machine Learning · LLMs · AI Systems</p>{action(RESUME,"Download résumé")}</div><div class="study-years">2026<br><span>— 2028</span><p>August 2026 — May 2028<br>Expected graduation</p></div></section><section class="experience-section page-pad"><div class="section-label">'+caption('01 / EXPERIENCE')+'<h2>WHERE I’VE WORKED</h2></div>'
roles=[('Qualcomm','Software Engineer, GenAI / LLM Systems','JUL 2024 — AUG 2026'),('AMD','Software Development Intern, Performance / Systems','JAN — JUN 2024'),('Standard Chartered','Software Development Intern','MAY — JUL 2023'),('Invoxel Technologies','Software Development Engineer','JUN — JUL 2022')]
for i,(name,role,date) in enumerate(roles):
 d=D['career'][i]
 j+=f'<article class="role-record"><div class="role-date">{date}</div><div class="role-title"><h3>{name}</h3><p>{role}</p></div><div class="role-copy"><p>{e(d["bullets"][0])}</p><details><summary>Role details {ic("plus")}</summary><ul>'+''.join('<li>'+e(t)+'</li>' for t in d['bullets'][1:])+'</ul>'
 if d['images']:j+='<div class="role-media">'+''.join(link(x['src'],img(x['src'],x['alt']),external=True) for x in d['images'])+'</div>'
 j+='</details></div></article>'
j+='</section><section class="education-section page-pad"><div class="section-label">'+caption('02 / EDUCATION')+'<h2>WHERE I’VE STUDIED</h2></div>'
for i,d in enumerate(D['education']):
 desc=['M.S. Computer Science / 2026–2028 expected','B.E. Computer Science / 2020–2024 / GPA 8.11','Higher Secondary / 2008–2020 / 91.6%'][i]
 j+=f'<article class="education-record"><span>0{i+1}</span><div><h3>{e(d["title"])}</h3><p>{desc}</p><details><summary>Study, activities & distinctions {ic("plus")}</summary><ul>'+''.join('<li>'+e(t)+'</li>' for t in d['bullets'])+'</ul></details></div></article>'
j+='</section><section class="interest-section page-pad"><div class="section-label">'+caption('03 / AREAS OF INTEREST')+'<h2>THE PROBLEMS I LIKE</h2></div><div class="interest-list">'+''.join(f'<article><span>0{i+1}</span><h3>{e(d["title"])}</h3><p>{e(d["text"])}</p></article>' for i,d in enumerate(D['interests']))+'</div></section>'
j+='<section class="toolbox page-pad"><div class="section-label">'+caption('04 / TOOLS & COURSEWORK')+'<h2>THE TOOLBOX</h2></div><div class="tool-columns"><div><h3>Languages</h3><p>C · C++ · Python · Java · Kotlin · JavaScript · SQL · Bash · C#</p><h3>ML & LLM systems</h3><p>PyTorch · Hugging Face · LangChain · vLLM · Ollama · RAG · LoRA / QLoRA · Evaluation · Agent orchestration</p><h3>Edge & infrastructure</h3><p>ONNX Runtime · QNN · Hexagon NPU · Qualcomm Genie · INT4 / INT8 · Linux · Docker · Kubernetes · Redis · Flask · Azure DevOps · Git</p></div><div><details><summary>Coursework '+ic('plus')+'</summary><ul>'+''.join('<li>'+e(t)+'</li>' for t in D['coursework'])+'</ul></details><details><summary>Skill profile '+ic('plus')+'</summary>'+''.join('<p>'+e(t['title'])+' — '+e(t['value'])+'</p>' for t in D['skills'])+'</details></div></div></section>'
snapshot=BeautifulSoup((R/'source/site-snapshot/site.html.txt').read_text(),'html.parser')
j+='<section class="page-pad longer-bio"><details><summary>The longer biography '+ic('plus')+'</summary>'+''.join('<p>'+e(p.get_text(' ',strip=True))+'</p>' for p in snapshot.select('.about-story-content > p'))+'</details>'+action('/credentials/','Awards & credentials')+'</section>'
write('/journey/','Journey',j,'Journey')

# Community and hobbies: original content in a photo-led editorial sequence.
b=page_head('LABS / LEADERSHIP / LIFE','BEYOND<br>THE CODE<span class="accent">.</span>','The student communities I helped build, and the things that take me away from a screen.')+'<section class="leadership-index page-pad">'
for i,d in enumerate(D['leadership']):
 b+='<article class="leadership-story"><div class="leadership-photo">'+(img(d['images'][0]['src'],d['images'][0]['alt']) if d['images'] else '<span>'+f'{i+1:02}'+'</span>')+'</div><div>'+caption(f'{i+1:02} / COMMUNITY')+'<h2>'+e(d['title'].replace('↗',''))+'</h2><ul>'+''.join('<li>'+e(t)+'</li>' for t in d['bullets'])+'</ul><div class="leadership-resources">'+''.join(link(h,e(t)+ic('arrow-up'),'resource-link',True) for h,t in d['links'])+'</div>'+('<div class="leadership-gallery">'+''.join(img(x['src'],x['alt']) for x in d['images'][1:])+'</div>' if len(d['images'])>1 else '')+'</div></article>'
b+='</section><section class="hobby-section page-pad"><div class="section-label">'+caption('OFF THE CLOCK')+'<h2>AWAY FROM THE DESK</h2></div><div class="hobby-mosaic">'+''.join('<figure>'+img(h['image'],h['title'])+'<figcaption>'+e(h['title'])+'</figcaption></figure>' for h in D['hobbies'])+'</div></section>'
write('/beyond/','Beyond work',b,'Beyond')

awards=[('2026','1st place / Trust in the Hiring Funnel','Built Sweesh, where people and institutions vouch for each other.'),('2026','SparQ Qualcomm TechFest / Jury Award','CabinAI, competing solo against 166 teams.'),('2025','SparQ Qualcomm TechFest / Finalist','Presented Code Buddy’s multi-agent architecture to the Qualcomm CTO.'),('2023','CCIB SCPay Award','Jenkins-to-Azure DevOps migration at Standard Chartered.'),('2022','DAAD Scholarship','Mixed-reality research at TU Braunschweig, Germany.')]
c=page_head('AWARDS / SCHOLARSHIPS / CERTIFICATES','THE MILESTONES<span class="accent">.</span>')+'<section class="award-index page-pad">'+''.join(f'<article><span>{y}</span><h2>{e(t)}</h2><p>{e(d)}</p></article>' for y,t,d in awards)+'</section><section class="cert-section page-pad"><div class="section-label">'+caption('THE DOCUMENTS')+'<h2>CREDENTIALS</h2></div><div class="certificate-wall">'
for x in D['credentials']:
 c+=f'<article><button class="image-zoom" data-image="{e(x["image"])}" data-alt="{e(x["title"])}" aria-label="Enlarge {e(x["title"])}">{img(x["image"],x["title"])}<span>{ic("expand")}</span></button><h3>{e(x["title"])}</h3><p>{e(x["date"])}</p>{link(x["link"],"View credential ↗","text-link",True)}</article>'
c+='</div><div class="credential-downloads">'+action('/assets/certificates.zip','Download certificate archive')+link('https://drive.google.com/drive/folders/1ky_I7KIyYBAr-Ouu7qTVsZ8Ue1IQ_e5k?usp=sharing','Certificate folder ↗','text-link',True)+'</div></section>'
write('/credentials/','Credentials',c,'Credentials')

w=page_head('ARCHITECTURE / SYSTEMS / THINGS I’M LEARNING','NOTEBOOK<span class="accent">.</span>','Four long-form articles on AI systems, software architecture, and the decisions behind them.')+'<section class="journal-archive page-pad">'+''.join(journal(p,i) for i,p in enumerate(posts))+'</section>'
write('/writing/','Writing',w,'Writing');write('/blog/','Blog',w,'Writing')
for p in posts:
 body=f'<header class="article-head page-pad">{link("/writing/","← ALL WRITING","back-link")}{caption(p["date"]+" / "+str(p["minutes"])+" MIN READ")}<h1>{e(p["title"])}</h1><div class="article-byline">{img("/assets/images/profile_picture.png","Varun Sahni")}<p>VARUN SAHNI<br><span>NYU Courant · Previously Qualcomm</span></p></div></header><section class="article-body page-pad"><aside class="article-toc">{caption("ON THIS PAGE")}' + ''.join(link('#'+id,e(t)) for t,id in p['toc'])+'</aside><article class="prose">'+p['body']+'</article></section>'
 write(p['path'],p['title'],body,'Writing',p['excerpt'][:170])

ct=page_head('NEW YORK / OPEN TO A CONVERSATION','SAY HELLO<span class="accent">.</span>')+f'<section class="contact-spread page-pad"><div class="contact-intro"><h2>LET’S COMPARE NOTES.</h2><p>AI systems, an interesting engineering problem, or something you’re building. The best way to reach me is by email.</p>{link("mailto:sahnicoder@gmail.com","sahnicoder<br>@gmail.com "+ic("arrow-up"),"big-email")}</div><div class="contact-facts"><div><span>LOCATION</span><h3>New York, NY</h3>{link("https://www.google.com/maps/search/?api=1&query=New+York+NY","View map ↗",external=True)}</div><div><span>CURRENTLY</span><h3>M.S. CS / NYU Courant</h3>{link("mailto:vs3606@nyu.edu","vs3606@nyu.edu ↗")}</div><div><span>ELSEWHERE</span>{link("https://github.com/varunsahni18","GitHub ↗",external=True)}{link("https://www.linkedin.com/in/varun-sahni-profile/","LinkedIn ↗",external=True)}{link("https://leetcode.com/u/sahnicoder/","LeetCode ↗",external=True)}{link(RESUME,"Résumé ↗",external=True)}</div></div></section>'
write('/contact/','Contact',ct,'Contact')
write('/404.html','Page not found',page_head('404 / PAGE NOT FOUND','WRONG TURN<span class="accent">.</span>')+'<div class="page-pad not-found">'+action('/','Back to the beginning')+'</div>')
(R/'design/content.json').write_text(json.dumps(D,ensure_ascii=False,indent=2))
(R/'design/search.json').write_text(json.dumps(SEARCH,ensure_ascii=False))
print(json.dumps({'pages':len(PAGES),'projects':len(P),'articles':len(posts),'design':'studio'}))

from html import escape as esc

def icon(n):
 return f'<svg class="icon" aria-hidden="true"><use href="/design/icons.svg#{n}"/></svg>'
def image(src,alt,*args,**kwargs):
 return f'<img src="{esc(src)}" alt="{esc(alt)}" loading="lazy" decoding="async">'

def cover(p,large=False):
 kind=p['slug']
 if kind=='code-buddy':
  return f'''<div class="project-art code-art"><div class="art-top"><span>{icon('code')} CODE BUDDY</span><span>01 / AGENT SYSTEMS</span></div><div class="review-window"><div class="window-top"><i></i><i></i><i></i><span>review.pipeline</span></div><div class="code-lines"><div><b>01</b><span class="muted">// From a change to a verified fix</span></div><div><b>02</b><span>const <strong>review</strong> = await agents.run({'{'}</span></div><div class="indent"><b>03</b><span>detect: <em>issues</em>,</span></div><div class="indent"><b>04</b><span>verify: <em>tests + guardrails</em>,</span></div><div class="indent"><b>05</b><span>deliver: <em>actionable fixes</em></span></div><div><b>06</b><span>{'}'});</span></div></div><div class="review-result">{icon('check-circle')} From detection to a self-validating fix</div></div><div class="art-bottom"><span>12,000+ engineers</span><span>4,000+ repositories {icon('arrow-up')}</span></div></div>'''
 if p['title']=='CabinAI':
  return f'''<div class="project-art cabin-art"><div class="art-top"><span>{icon('car')} CABIN AI</span><span>EDGE ↔ CLOUD</span></div><svg class="car-drawing" viewBox="0 0 560 250" aria-hidden="true"><path d="M70 180V152Q70 130 108 125L160 73Q180 58 215 58H350Q370 58 390 85L425 125Q490 130 490 150V180H453M130 180H387"/><path d="M170 119L205 78H335Q350 78 368 119ZM280 78V119M80 150H120M450 148H480"/><circle cx="160" cy="177" r="34"/><circle cx="420" cy="177" r="34"/><circle cx="160" cy="177" r="16"/><circle cx="420" cy="177" r="16"/><path class="signal" d="M255 35Q280 10 305 35M264 43Q280 28 296 43"/><path class="road" d="M40 224H520"/></svg><div class="agent-tags"><span>{icon('eye')} Perception</span><span>{icon('shield')} Safety</span><span>{icon('mic')} Voice</span></div><div class="art-bottom"><span>7 agents. One shared intelligence.</span><span>{icon('award')} SparQ winner</span></div></div>'''
 if p['title']=='HealthSense':
  return f'''<div class="project-art health-art"><div class="art-top"><span>{icon('pulse')} HEALTHSENSE</span><span>WEARABLE INTELLIGENCE</span></div><div class="signal-stack"><svg viewBox="0 0 560 200" aria-hidden="true"><path d="M0 50H55L65 45L75 55L85 50H105L115 20L125 85L138 45L150 50H205L218 43L230 57L243 50H270L282 15L296 89L310 45L322 50H385L400 40L411 60L425 50H452L465 20L478 80L490 48L505 50H560"/><path d="M0 135Q20 85 40 135T80 135T120 135T160 135T200 135T240 135T280 135T320 135T360 135T400 135T440 135T480 135T520 135T560 135"/></svg><span>EEG · ECG · PPG · EMG · IMU</span></div><div class="art-bottom"><span>5 signals · ECG CNN + heuristics</span><span>System prototype {icon('arrow-up')}</span></div></div>'''
 if p['title']=='MyAI':
  return f'''<div class="project-art myai-art"><div class="art-top"><span>{icon('phone')} MY AI</span><span>PRIVATE BY DESIGN</span></div><div class="phone-composition"><div class="phone-device"><div class="phone-notch"></div><span class="phone-greeting">A little help.<br><em>Entirely yours.</em></span><div class="phone-prompt">{icon('spark')} On-device intelligence</div><div class="phone-lock">{icon('lock')} No internet permission</div></div><div class="phone-chips"><span>{icon('cpu')} INT4 inference</span><span>{icon('zap')} Local model runtime</span><span>{icon('shield')} No network permission</span></div></div></div>'''
 if kind in ['compiler-construction','live-train-status','kxr-smithy-simulation']:
  return f'<div class="project-art illustrated-art">{image("/design/media/"+kind+".svg",p["title"]+" — project illustration")}</div>'
 if kind in ['cliffside-conquest','digital-twin-mapmyindia']:
  return f'<div class="project-art footage-art {kind}">{image(p["image"],p["title"]+" — frame from the project video")}<span class="footage-label">{icon("play")} Actual project footage</span></div>'
 return f'<div class="project-art image-art">{image(p["image"],p["title"])}<span class="art-image-tag">{esc(p["group"])}</span></div>'

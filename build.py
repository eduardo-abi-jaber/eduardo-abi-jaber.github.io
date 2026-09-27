"""Build the website with Python 3 (standard library only)."""
from pathlib import Path
import json, re, shutil, hashlib
from html import escape as esc

ROOT=Path(__file__).parent
OUT=ROOT/'dist'
OUT.mkdir(exist_ok=True)
shutil.copytree(ROOT/'assets',OUT/'assets',dirs_exist_ok=True)
PUBS=json.loads((ROOT/'publications.json').read_text())
LINKS=json.loads((ROOT/'source-links.json').read_text())
CONFIG=json.loads((ROOT/'site.json').read_text())
STYLE_VERSION=hashlib.sha256((ROOT/'assets/style.css').read_bytes()).hexdigest()[:12]
EMAIL='eduardo.abi-jaber@polytechnique.edu'
SCHOLAR='https://scholar.google.com/citations?user=U35GhtAAAAAJ'
def link(label):
    for a in LINKS:
        if a['label'].lower()==label.lower():return a['url']
    for a in LINKS:
        if label.lower() in a['label'].lower():return a['url']
    raise ValueError('Missing source link: '+label)
def ext(url,label,cls=''):
    attrs=' target="_blank" rel="noopener noreferrer"' if url.startswith(('https://','http://','//')) else ''
    return f'<a href="{esc(url,quote=True)}" class="{cls}"{attrs}>{esc(label)}</a>'
def intro(kicker,title,description):
    return f'<div class="page-intro"><p class="eyebrow">{kicker}</p><h1>{title}</h1><p class="lead">{description}</p></div>'
def paper(p,number=None):
    dates=re.findall(r'\b20\d{2}\b',p['details'])
    year=dates[0] if dates else 'Accepted'
    detail=re.sub(r'\s*\(Jupyter notebook\)', '',p['details'])
    detail=detail.replace('🌟','').replace(' ( )','').strip()
    detail_html=esc(detail)
    journals=('Bernoulli','Finance and Stochastics','Finance & Stochastics','Mathematical Finance','Quantitative Finance','Stochastic Systems','Stochastic Processes and their Applications','Annals of Applied Probability','The Annals of Applied Probability','Electronic Journal of Probability','Electronic Communications in Probability','SIAM Journal on Financial Mathematics','SIAM Journal on Control and Optimization','Statistics & Probability Letters','Risk Magazine','Risk Magazine (Cutting Edge Section)')
    for a in p['links'][1:]:
        if a['label'] in journals and '/editorial-board' not in a['url']:
            detail_html=detail_html.replace(esc(a['label']),ext(a['url'],a['label'],'journal-link'),1)
    marker=f'[{number}]' if number is not None else esc(year)
    actions='' 
    for a in p['links'][1:]:
        if 'notebook' in a['label'].lower():actions+=ext(a['url'],'Code / notebook')
    actions_html=f'<div class="paper-actions">{actions}</div>' if actions else ''
    return f'<article class="paper"><div class="paper-year">{marker}</div><div><h3>{ext(p["url"],p["title"])}</h3><p>{detail_html}</p>{actions_html}</div></article>'
def page(filename,title,description,content):
    nav=''
    for file,label in [('research.html','Research'),('publications.html','Publications'),('people.html','People'),('teaching.html','Teaching'),('talks.html','Talks')]:
        current=' aria-current="page"' if file==filename else ''
        nav+=f'<a href="{file}"{current}>{label}</a>'
    canonical=CONFIG.get('site_url','').rstrip('/')
    canonical_tag=f'<link rel="canonical" href="{esc(canonical)}/{filename if filename!="index.html" else ""}">' if canonical else ''
    text=f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)} | Eduardo Abi Jaber</title><meta name="description" content="{esc(description,quote=True)}">{canonical_tag}<link rel="icon" href="assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="assets/style.css?v={STYLE_VERSION}"><script src="assets/site.js" defer></script></head>
<body><a class="skip" href="#main">Skip to content</a><header class="site-header"><div class="wrap header-inner"><a class="brand" href="index.html">Eduardo Abi Jaber<span>.</span></a><button class="menu-toggle" aria-expanded="false" aria-controls="navigation" type="button">Menu</button><nav id="navigation" aria-label="Main navigation">{nav}</nav></div></header>
<main id="main" class="wrap">{content}</main><footer class="wrap footer"><div class="footer-top"><div><a class="footer-name" href="index.html">Eduardo Abi Jaber</a><p>Professor of Applied Mathematics<br>École Polytechnique · CMAP</p></div><div class="footer-links">{ext('mailto:'+EMAIL,'Email')}{ext(SCHOLAR,'Google Scholar')}</div></div><div class="footer-bottom">© {CONFIG['copyright_year']} Eduardo Abi Jaber</div></footer></body></html>'''
    (OUT/filename).write_text(text)

# Small monochrome symbols retain visible labels for clarity and accessibility.
ICONS={
    'arXiv':'<path d="M6 3l12 18M18 3L6 21" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M4 8l4-5 3 5M13 16l3 5 4-5" fill="none" stroke="currentColor" stroke-width="1.4"/>',
    'Google Scholar':'<path d="M2 9l10-7 10 7-10 7z" fill="currentColor"/><path d="M6 13v6c4 3 8 3 12 0v-6" fill="none" stroke="currentColor" stroke-width="1.8"/>',
    'LinkedIn':'<rect x="2" y="2" width="20" height="20" rx="2" fill="currentColor"/><path d="M7 10v8M11 18v-8M11 14c0-5 6-5 6 0v4" fill="none" stroke="white" stroke-width="2"/><circle cx="7" cy="6.5" r="1.2" fill="white"/>',
    'Email':'<rect x="2" y="4" width="20" height="16" rx="2" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M3 6l9 7 9-7" fill="none" stroke="currentColor" stroke-width="1.6"/>'
}
def profile_link(label,url):
    icon=f'<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">{ICONS[label]}</svg>'
    return ext(url,label,'profile-link').replace('>'+esc(label)+'</a>','>'+icon+'<span>'+esc(label)+'</span></a>')
profile_links=''.join(profile_link(label,url) for label,url in [
    ('arXiv',CONFIG['arxiv_url']),('Google Scholar',SCHOLAR),
    ('LinkedIn',CONFIG['linkedin_url']),('Email','mailto:'+EMAIL)])

portrait=CONFIG.get('portrait','')
if portrait:
    if not (ROOT/portrait).is_file():raise FileNotFoundError(portrait)
    photo=f'<img src="{esc(portrait)}" alt="Portrait of Eduardo Abi Jaber" width="600" height="750">'
else:photo='<span class="portrait-monogram" aria-hidden="true">EAJ</span><span class="portrait-caption">Eduardo Abi Jaber</span>'
hero=f'''<section class="hero"><div><p class="eyebrow">École Polytechnique · Applied Mathematics</p><h1>Mathematics<br>with <em>memory.</em></h1><p class="intro">I am <strong>Eduardo Abi Jaber</strong>, Professor of Applied Mathematics at École Polytechnique, in the Mathematical Finance group at CMAP.</p><p class="description">My research develops the mathematics of stochastic systems with memory, from probabilistic foundations to models and methods for finance, energy and learning.</p><div class="links profile-links">{profile_links}</div></div><figure class="portrait-wrap"><div class="portrait">{photo}</div></figure></section>
<div class="research-band"><div>Volterra processes</div><div>Path signatures &amp; learning</div><div>Mathematical Finance</div><div>Volatility Modeling</div></div>'''
latest='<section class="section"><div class="section-top"><div><p class="eyebrow">Recent work</p><h2>New papers</h2></div><a class="text-link" href="publications.html">All publications</a></div>'+''.join(paper(p) for p in PUBS[:3])+'</section>'
events=CONFIG['upcoming']
def event(e):return f'<article class="event"><div class="meta">{esc(e["date"])} · {esc(e["place"])}</div><h3>{ext(e["url"],e["name"])}</h3><p>{esc(e.get("topic",""))}</p></article>'
next_events='<section class="section split"><div><h2>Upcoming talks</h2><a class="text-link" href="talks.html">Talks &amp; minicourses</a></div><div class="events">'+''.join(event(e) for e in events[:3])+'</div></section>'
page('index.html','Home','Eduardo Abi Jaber, Professor of Applied Mathematics at École Polytechnique. Stochastic systems with memory, Volterra processes, control and path signatures.',hero+latest+next_events)

# research=intro('Research','Modelling, controlling<br>and learning memory.','Many stochastic systems depend on the path that brought them to their present state. I develop mathematical foundations and computational methods for this dependence on history.')
# topics=[('01','Volterra processes and volatility','Volterra processes provide a flexible language for memory through kernels that weight the influence of past events. My work addresses existence, uniqueness, affine and polynomial structures, and the approximation and simulation of these processes.','These foundations lead to models that can be calibrated and simulated, with applications to volatility and the management of financial and energy-market risks.','Affine Volterra processes'),('02','Control and decisions with memory','When risk or the effects of an action persist over time, decisions must account for their history. I study stochastic control, portfolio allocation, optimal execution and interactions between agents.','The methods include operator Riccati equations and integral equations of Fredholm type, with applications ranging from financial trading to electricity storage.','Optimal Liquidation with Signals: the General Propagator Case'),('03','Path signatures and learning','Path signatures encode information about trajectories. My research uses them to construct path-dependent processes, price and hedge derivatives, and learn temporal dependencies from data.','The Exponentially Fading Memory Signature represents the past with a decreasing, parametrised memory, connecting signature methods to stationary time series and sequential learning.','Exponentially Fading Memory Signature')]
# for number,title,p1,p2,work in topics:
#    research+=f'<section class="research-block"><span class="number">{number}</span><div><h2>{title}</h2><p>{p1}</p><p>{p2}</p>{ext(link(work),work,"text-link")}</div></section>'
# research+='''<section class="partners"><h3>Research in dialogue with industry</h3><p>Problems from finance and energy motivate new mathematical questions and guide the development of practical methods. Collaborations include ENGIE Global Markets, AXA Investment Managers, BNP Paribas, CACIB and GEFIP.</p><p>Examples include joint historical and implied calibration in energy markets with ENGIE, and joint SPX–VIX volatility modelling with AXA Investment Managers.</p></section>'''
# research+='<section class="section"><p class="eyebrow">Academic service &amp; recognition</p><div class="service"><p><strong>Associate editor</strong> of Mathematical Finance, Finance and Stochastics, and the International Journal of Theoretical and Applied Finance, since 2026.</p><p><strong>AMIES PhD Award (2019)</strong> for doctoral research in collaboration with industry; <strong>Bachelier Finance Society Junior Scholar Award (2018)</strong>.</p><p>'+ext(link('Volterra Processes in Finance'),'Habilitation: Volterra Processes in Finance (2024)','text-link')+'</p><p>'+ext(link('Stochastic invariance and stochastic Volterra equations'),'PhD thesis (2018)','text-link')+'</p></div></section>'
# page('research.html','Research','Research on Volterra processes, stochastic control and path signatures, with applications in finance and energy.',research)
# pubintro='<div class="page-intro"><h1>Publications</h1></div>'
# page('publications.html','Publications','Research papers and preprints by Eduardo Abi Jaber, with manuscript and code links.',pubintro+'<div class="page-body">'+''.join(paper(p,len(PUBS)-i) for i,p in enumerate(PUBS))+'</div>')

people=intro('Research group','People','Doctoral and postdoctoral research at the intersection of probability, mathematical finance and learning.')
for group in CONFIG['people']:
    people+=f'<section><h2 class="subhead">{esc(group["title"])}</h2><div class="people-grid">'
    for person in group['members']:
        name=ext(person['url'],person['name']) if person.get('url') else esc(person['name'])
        people+=f'<article class="person"><h3>{name}</h3><p class="dates">{esc(person["dates"])} · {esc(person["institution"])}</p><p>{esc(person.get("supervision",""))}</p>'
        if person.get('partner'):people+=f'<p>CIFRE partnership: {esc(person["partner"])}</p>'
        if person.get('position'):people+=f'<p class="position">Now: {esc(person["position"])}</p>'
        if person.get('award'):people+=f'<p class="award">{esc(person["award"])}</p>'
        people+='</article>'
    people+='</div></section>'
people+='<p class="service">Édouard Motte was a visiting doctoral researcher in 2025. My teaching and mentoring also include master’s research projects and internships in academia and industry.</p>'
page('people.html','People','Current doctoral researchers, postdoctoral researchers and alumni supervised by Eduardo Abi Jaber.',people+'<div class="page-body"></div>')

teaching=intro('Teaching','From foundations<br>to applications.','Courses in stochastic modelling, memory, quantitative finance and learning, for graduate students and practitioners.')
for c in CONFIG['courses']:
    teaching+=f'<article class="course"><div class="label">{esc(c["level"])}</div><div><h3>{esc(c["title"])}</h3><p>{esc(c["institution"])}</p><p>{esc(c["description"])}</p>'
    if c.get('url'):teaching+=ext(c['url'],'Course information','text-link')
    teaching+='</div></article>'
teaching+='''<section class="partners"><h3>Academic leadership</h3><p>Head of the third-year Applied Mathematics track at École Polytechnique since 2024, with responsibility for internship modules and practitioner seminars since 2022.</p><p>Previously Director of Studies of the M2 IRFA programme at Université Paris 1 Panthéon-Sorbonne (2020–2022).</p></section>'''
page('teaching.html','Teaching','Graduate courses and professional education in stochastic modelling, quantitative finance and machine learning.',teaching+'<div class="page-body"></div>')

talks=intro('Talks &amp; minicourses','Sharing ideas.','Selected lectures and upcoming presentations, alongside an archive of conferences and seminars.')
talks+='<h2 class="subhead">Upcoming</h2><div class="events">'+''.join(event(e) for e in events)+'</div><h2 class="subhead">Selected lectures &amp; minicourses</h2><div class="events">'
for e in CONFIG['selected_talks']:talks+=event(e)
talks+='</div>'
for group in CONFIG.get('talk_archive',[]):
    talks+=f'<details class="archive"><summary>{esc(group["title"])}</summary><ul>'
    for item in group['items']:talks+=f'<li>{ext(item["url"],item["text"]) if item.get("url") else esc(item["text"])}</li>'
    talks+='</ul></details>'
page('talks.html','Talks','Upcoming talks, invited lectures and minicourses by Eduardo Abi Jaber.',talks+'<div class="page-body"></div>')
(OUT/'.nojekyll').touch()
print('Built six pages in',OUT)

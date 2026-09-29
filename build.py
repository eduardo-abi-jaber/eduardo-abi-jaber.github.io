"""Build the website with Python 3 (standard library only)."""
from pathlib import Path
import json, re, shutil, hashlib
from html import escape as esc

ROOT=Path(__file__).parent
OUT=ROOT/'dist'
# Rebuild from a clean output directory so removed pages cannot linger.
if OUT.exists(): shutil.rmtree(OUT)
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
PERSON_LINKS={}
for publication in PUBS:
    for entry in publication['links'][1:]:
        if publication['details'].startswith('with ') and entry['label'] in publication['details'].split(', 20')[0]:
            if not any(term in entry['label'] for term in ('Finance','Probability','Stochastic','Magazine','Journal','Awards','notebook')):
                PERSON_LINKS[entry['label']]=entry['url']
for group in CONFIG['people']:
    for person in group['members']:
        if person.get('url'): PERSON_LINKS[person['name']]=person['url']
PERSON_LINKS['Edouard Motte']=PERSON_LINKS['Édouard Motte']
def linked_text(text,extra=None):
    destinations=dict(PERSON_LINKS)
    if extra: destinations.update(extra)
    names=sorted((name for name in destinations if name in text),key=len,reverse=True)
    if not names: return esc(text)
    pattern=re.compile('|'.join(re.escape(name) for name in names))
    result=[];cursor=0
    for match in pattern.finditer(text):
        result.append(esc(text[cursor:match.start()]))
        result.append(ext(destinations[match.group()],match.group(),'inline-link'))
        cursor=match.end()
    result.append(esc(text[cursor:]))
    return ''.join(result)

def intro(kicker,title,description):
    return f'<div class="page-intro"><p class="eyebrow">{kicker}</p><h1>{title}</h1><p class="lead">{description}</p></div>'
def paper(p,number=None,show_year=True):
    dates=re.findall(r'\b20\d{2}\b',p['details'])
    year=dates[0] if dates else 'Accepted'
    detail=re.sub(r'\s*\(Jupyter notebook\)', '',p['details'])
    detail=detail.replace('🌟','🌟 ').replace(' ( )','').strip()
    journal_links={}
    for entry in p['links'][1:]:
        if entry['label'] not in PERSON_LINKS and '/editorial-board' not in entry['url'] and 'notebook' not in entry['label'].lower():
            journal_links[entry['label']]=entry['url']
    detail_html=linked_text(detail,journal_links)
    marker=f'[{number}]' if number is not None else esc(year)
    actions='' 
    for a in p['links'][1:]:
        if 'notebook' in a['label'].lower():actions+=ext(a['url'],'Code / notebook')
    actions_html=f'<div class="paper-actions">{actions}</div>' if actions else ''
    marker_html=f'<div class="paper-year">{marker}</div>' if show_year or number is not None else ''
    return f'<article class="paper">{marker_html}<div><h3>{ext(p["url"],p["title"])}</h3><p>{detail_html}</p>{actions_html}</div></article>'
def page(filename,title,description,content):
    nav=''
    for file,label in [('publications.html','Publications'),('people.html','Research Group'),('teaching.html','Teaching'),('talks.html','Talks')]:
        current=' aria-current="page"' if file==filename else ''
        nav+=f'<a href="{file}"{current}>{label}</a>'
    canonical=CONFIG.get('site_url','').rstrip('/')
    canonical_tag=f'<link rel="canonical" href="{esc(canonical)}/{filename if filename!="index.html" else ""}">' if canonical else ''
    text=f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)} | Eduardo Abi Jaber</title><meta name="description" content="{esc(description,quote=True)}">{canonical_tag}<link rel="icon" href="assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="assets/style.css?v={STYLE_VERSION}"><script src="assets/site.js" defer></script></head>
<body><a class="skip" href="#main">Skip to content</a><header class="site-header"><div class="wrap header-inner"><a class="brand" href="/">Eduardo Abi Jaber<span>.</span></a><button class="menu-toggle" aria-expanded="false" aria-controls="navigation" type="button">Menu</button><nav id="navigation" aria-label="Main navigation">{nav}</nav></div></header>
<main id="main" class="wrap">{content}</main><footer class="wrap footer"><div class="footer-top"><div><a class="footer-name" href="/">Eduardo Abi Jaber</a><p>Professor of Applied Mathematics<br>École Polytechnique · CMAP</p></div><div class="footer-links">{ext('mailto:'+EMAIL,'Email')}{ext(SCHOLAR,'Google Scholar')}</div></div><div class="footer-bottom">© {CONFIG['copyright_year']} Eduardo Abi Jaber</div></footer></body></html>'''
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
hero=f'''<section class="hero"><div><p class="eyebrow">École Polytechnique · Applied Mathematics</p><h1>Mathematics<br>with <em>memory.</em></h1><p class="intro">I am <strong>Eduardo Abi Jaber</strong>, Professor of Applied Mathematics at École Polytechnique, in the Mathematical Finance group at CMAP.</p><p class="description">My research develops the mathematics of stochastic systems with memory, from probabilistic foundations to models and methods for quantitative finance, energy markets and machine learning.</p><p class="description">
I enjoy building a
<a class="text-link" href="people.html">research group</a>
and developing ideas together with doctoral students,
postdoctoral researchers and collaborators.
</p>
<p class="description">
I defended my
<a class="text-link" href="https://hal.science/tel-04493022"
target="_blank" rel="noopener noreferrer">Habilitation à Diriger des Recherches</a>
in 2024 and my
<a class="text-link" href="https://tel.archives-ouvertes.fr/tel-01956320/"
target="_blank" rel="noopener noreferrer">PhD thesis</a>
in 2018.
</p><div class="links profile-links">{profile_links}</div></div><figure class="portrait-wrap"><div class="portrait">{photo}</div></figure></section>
<div class="research-band"><div>Volterra processes</div><div>Path signatures &amp; learning</div><div>Mathematical Finance</div><div>Volatility Modeling</div></div>'''
academic_info='<section class="section academic-overview"><div><h2>Current teaching</h2><ul class="teaching-list">'
for course in CONFIG['courses']:
    academic_info+=f'<li>{ext(course["url"],course["title"],"inline-link")}<span>{esc(course["institution"])}</span></li>'
academic_info+='</ul></div><div class="service-awards"><h2>Academic service</h2><p>I serve as Associate Editor for '+ext('https://onlinelibrary.wiley.com/journal/14679965','Mathematical Finance','inline-link')+', '+ext('https://link.springer.com/journal/780/editorial-board','Finance and Stochastics','inline-link')+' and '+ext('https://www.worldscientific.com/page/ijtaf/editorial-board','International Journal of Theoretical and Applied Finance','inline-link')+', since 2026.</p><h2>Awards</h2><ul><li>'+ext('https://www.agence-maths-entreprises.fr/a/?q=fr/prix-de-these','AMIES PhD Award','inline-link')+', best PhD in applied mathematics in collaboration with industry, 2019.</li><li>'+ext('http://www.bachelierfinance.org/awards/junior-scholar-award.html','Bachelier Finance Society Junior Scholar Award','inline-link')+', most outstanding paper, 2018.</li></ul></div></section>'
latest='<section class="section latest-section"><div class="section-top"><h2>New papers</h2><a class="text-link" href="publications.html">All publications</a></div><div class="paper-grid">'+''.join(paper(p,show_year=False) for p in PUBS[:6])+'</div></section>'
MONTHS=['January','February','March','April','May','June','July','August','September','October','November','December']
MONTH_PATTERN='(?:'+'|'.join(MONTHS+['Otcober'])+')'
ARCHIVE_DATE=re.compile(r'\b'+MONTH_PATTERN+r'\s+\d{1,2}(?:\s*[-–]\s*(?:'+MONTH_PATTERN+r'\s+)?\d{1,2})?,?\s+20\d{2}')

def archive_event(item):
    # Keep the original archive text in site.json; derive its presentation here.
    match=ARCHIVE_DATE.search(item['text'])
    if not match: raise ValueError('Missing archive date: '+item['text'])
    date=match.group().replace('Otcober','October')
    prefix=item['text'][:match.start()].strip(' ,.')
    name,sep,place=prefix.partition(', ')
    # Edition labels belong to the event name, rather than its location.
    while re.match(r'(?i)(?:#?\d|\d+(?:st|nd|rd|th))',place):
        edition,sep,place=place.partition(', ')
        name+=', '+edition
    topic=item['text'][match.end():].strip(' ,. ')
    distinctions=list(dict.fromkeys(m.title() for m in re.findall(r'(?i)\b(invited|plenary|keynote)\b',topic)))
    topic=re.sub(r'(?i)\s*\(\s*(?:invited|plenary|keynote)\s*\)', '', topic).strip()
    return dict(name=name,place=place,date=date,topic=topic,url=item.get('url',''),distinctions=distinctions)

def event_sort_key(e):
    year=int(re.search(r'20\d{2}',e['date']).group())
    month=next((i+1 for i,m in enumerate(MONTHS) if m in e['date']),0)
    day=re.search(r'\b(\d{1,2})\b',e['date'])
    return year,month,int(day.group()) if day else 0

def agenda(events):
    html='';last_year=None
    for e in events:
        year=re.search(r'20\d{2}',e['date']).group()
        if year!=last_year:
            if last_year: html+='</div>'
            html+=f'<h3 class="agenda-year">{year}</h3><div class="agenda">'
            last_year=year
        short_date=re.sub(r',?\s*'+year+r'\b','',e['date'])
        url=e.get('url','')
        name=ext(url,e['name']) if url and url not in ('http://a','https://a') else esc(e['name'])
        badges=''.join(f'<strong class="talk-distinction">{esc(label)}</strong>' for label in e.get('distinctions',[]))
        badges=f'<div class="talk-badges">{badges}</div>' if badges else ''
        place=f'<p class="agenda-place">{esc(e["place"])}</p>' if e.get('place') else ''
        topic=f'<p>{linked_text(e["topic"])}</p>' if e.get('topic') else ''
        html+=f'<article class="agenda-row"><div class="agenda-date">{esc(short_date)}</div><div>{badges}<h4>{name}</h4>{place}{topic}</div></article>'
    return html+('</div>' if last_year else '')

next_events='<section class="section agenda-section"><div class="section-top"><h2>Upcoming talks</h2><a class="text-link" href="talks.html">Past talks &amp; minicourses</a></div>'+agenda(CONFIG['upcoming'])+'</section>'
page('index.html','Home','Eduardo Abi Jaber, Professor of Applied Mathematics at École Polytechnique. Stochastic systems with memory, Volterra processes, control and path signatures.',hero+academic_info+latest+next_events)

pubintro='<div class="page-intro"><h1>Publications and Preprints</h1></div>'
page('publications.html','Publications','Research papers and preprints by Eduardo Abi Jaber, with manuscript and code links.',pubintro+'<div class="page-body">'+''.join(paper(p,len(PUBS)-i) for i,p in enumerate(PUBS))+'</div>')

people='<div class="page-intro"><h1>Research Group</h1><p class="lead">I enjoy building a collaborative team where we develop ideas together, learn from one another and explore new mathematical questions. If you are interested in joining the group, please '+ext('mailto:'+EMAIL,'get in touch','inline-link')+'.</p></div>' 
for group in CONFIG['people']:
    people+=f'<section><h2 class="subhead">{esc(group["title"])}</h2><div class="people-grid">'
    for person in group['members']:
        name=ext(person['url'],person['name']) if person.get('url') else esc(person['name'])
        people+=f'<article class="person"><h3>{name}</h3><p class="dates">{esc(person["dates"])}{(" · "+esc(person["institution"])) if person["institution"] else ""}</p><p>{linked_text(person.get("supervision",""))}</p>'
        if person.get('thesis_title'):
            label=ext(person['thesis_url'],person['thesis_title'],'inline-link')
            note=f'<span class="thesis-note">{esc(person["thesis_link_note"])}</span>' if person.get('thesis_link_note') else ''
            people+=f'<p class="thesis"><strong>PhD thesis:</strong> {label}{note}</p>'
        if person.get('partner'):people+=f'<p>CIFRE partnership: {esc(person["partner"])}</p>'
        if person.get('position'):people+=f'<p class="position">Now: {esc(person["position"])}</p>'
        if person.get('award'):people+=f'<p class="award">{esc(person["award"])}</p>'
        people+='</article>'
    people+='</div></section>'
page('people.html','Research Group','Current doctoral researchers, postdoctoral researchers and alumni supervised by Eduardo Abi Jaber.',people+'<div class="page-body"></div>')

teaching=intro('Teaching','From foundations<br>to applications.','Courses in stochastic modelling, memory, quantitative finance and learning, for graduate students and practitioners.')
for c in CONFIG['courses']:
    teaching+=f'<article class="course"><div class="label">{esc(c["level"])}</div><div><h3>{esc(c["title"])}</h3><p>{esc(c["institution"])}</p><p>{esc(c["description"])}</p>'
    if c.get('url'):teaching+=ext(c['url'],'Course information','text-link')
    teaching+='</div></article>'
teaching+="""<section class="section"><h2>Previous teaching</h2>
<details class="archive" open><summary>Lectures</summary><ul>
<li><strong>2022–2025 · École Polytechnique:</strong> Deep Learning in Finance (MSc Data Science in Finance, École Polytechnique–HEC).</li>
<li><strong>2021–2022 · ENSAE:</strong> Numerical Methods in Financial Engineering (3A, 12h); Introduction to Mathematical Finance (2A, 18h).</li>
<li><strong>2019–2022 · Université Paris 1 Panthéon-Sorbonne:</strong> Market Risk Measures (M2, 18h); Calibration in Quantitative Finance (M2, 18h); Topics in Machine Learning (M2, 18h).</li>
</ul></details><details class="archive" open><summary>Tutorial classes</summary><ul>
<li><strong>2022 · École Polytechnique:</strong> Markov Chains and Martingales (MAP432, 20h).</li>
"""
teaching+='<li><strong>2019–2022 · Université Paris 1 Panthéon-Sorbonne:</strong> Mathematics of Insurance and Risks ('+ext('http://www.m2irfa.fr/','M2')+', 16h); Mathematical Finance (M1, 24h); Integration and Probability ('+ext('https://www.pantheonsorbonne.fr/ufr/ufr27/acces-l1/licence-miashs/','L3')+', 42h); Analysis ('+ext('https://www.pantheonsorbonne.fr/ufr/ufr27/acces-l1/licence-miashs/','L3')+', 42h); Linear Algebra (L2, 30h).</li><li><strong>2016–2018 · Université Paris Dauphine:</strong> Jump Processes, Valuation and No Arbitrage ('+ext('https://www.ceremade.dauphine.fr/mastermasef/fr/','M2 MASEF')+').</li></ul></details></section>'
page('teaching.html','Teaching','Graduate courses and professional education in stochastic modelling, quantitative finance and machine learning.',teaching+'<div class="page-body"></div>')

talks='<div class="page-intro"><h1>Talks &amp; minicourses</h1></div>'
talks+='<div class="section-jumps" aria-label="Talk sections"><a href="#minicourses">Minicourses</a><a href="#conferences">Conferences</a><a href="#seminars">Seminars</a></div>'
talks+='<section class="section agenda-section" id="minicourses"><h2>Minicourses</h2>'+agenda(sorted(CONFIG['minicourses'],key=event_sort_key,reverse=True))+'</section>'
for group in CONFIG.get('talk_archive',[]):
    title=group['title'].replace(' archive','')
    events=sorted((archive_event(item) for item in group['items']),key=event_sort_key,reverse=True)
    talks+=f'<section class="section agenda-section" id="{title.lower()}"><h2>{esc(title)}</h2>'+agenda(events)+'</section>'
page('talks.html','Talks & minicourses','Conferences, seminars and minicourses by Eduardo Abi Jaber.',talks+'<div class="page-body"></div>')
# Standalone preview: deliberately absent from the site navigation.
from research_preview import render as render_research_preview
render_research_preview(ROOT, OUT, PUBS, paper, page)
(OUT/'.nojekyll').touch()
print('Built',len(list(OUT.glob('*.html'))),'pages in',OUT)

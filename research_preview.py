"""Unlisted research preview. Does not alter navigation on existing pages."""
import json
from html import escape


def render(root, out, publications, paper, page):
    themes=json.loads((root/'research-preview.json').read_text())
    lookup={p['url']:(p,len(publications)-i) for i,p in enumerate(publications)}
    all_urls=[u for t in themes for g in t['groups'] for u in g['papers']]
    assert len(all_urls)==len(set(all_urls))==len(publications), 'Each publication must appear in exactly one theme'
    assert set(all_urls)==set(lookup), 'Preview grouping must match the publication list'
    cards=''
    for n,t in enumerate(themes,1):
        count=sum(len(g['papers']) for g in t['groups'])
        cards+=f'<a class="theme-card" href="#{t["id"]}"><span class="theme-index">0{n}</span><h2>{t["name"]}</h2><p>{t["question"]}</p><span class="theme-count">{count} papers <span aria-hidden="true">↗</span></span></a>'
    content='''<link rel="stylesheet" href="assets/research-preview.css">
<script src="assets/research-preview.js" defer></script>
<div class="research-preview">
<section class="research-hero"><p class="eyebrow">Research · A thematic view</p>
<h1>How does the past<br>shape <em>what comes next?</em></h1>
<p class="research-lead">I develop mathematics for stochastic systems with memory, connecting probability with models and methods for finance, energy markets and learning.</p>
<p class="research-intro">My research moves between the foundations of these systems, the tools we need to compute with them, and the decisions they help us make. Four themes offer different ways into this work.</p>
</section><div class="theme-map">'''+cards+'''</div>
<section class="memory-demo" aria-labelledby="memory-title"><div class="memory-copy"><p class="eyebrow">An intuition for memory</p><h2 id="memory-title">How much of the past<br>should we remember?</h2>
<p>A memory kernel assigns a weight to each past observation. Move the slider to compare a system that forgets quickly with one that keeps a longer history.</p>
<label for="memory-half-life">Memory half-life <output id="memory-value" for="memory-half-life">2 time units</output></label>
<input id="memory-half-life" type="range" min="0.5" max="8" value="2" step="0.1" disabled>
<div class="slider-ends"><span>Short memory</span><span>Long memory</span></div>
<p class="memory-summary" id="memory-summary" aria-live="polite">An observation 4 time units ago retains 25% of its original weight.</p>
<noscript><p>Enable JavaScript to adjust the memory half-life. The chart shows a half-life of 2 time units.</p></noscript></div>
<div class="memory-figure"><svg id="memory-chart" viewBox="0 0 560 320" role="img" aria-labelledby="memory-chart-title memory-chart-desc"><title id="memory-chart-title">Exponential memory kernel</title><desc id="memory-chart-desc">Weight decreases with time since an observation. With a half-life of 2, the weight is 0.5 after 2 time units and 0.25 after 4.</desc>
<g class="chart-grid"><path d="M55 35H525 M55 145H525 M55 255H525"/></g>
<g class="chart-labels"><text x="43" y="40" text-anchor="end">1</text><text x="43" y="150" text-anchor="end">0.5</text><text x="43" y="260" text-anchor="end">0</text><text x="55" y="279" text-anchor="middle">0</text><text x="290" y="279" text-anchor="middle">5</text><text x="525" y="279" text-anchor="middle">10</text><text x="55" y="20">Relative weight</text><text x="290" y="310" text-anchor="middle">Time since observation</text></g>
<path id="memory-area" class="memory-area" d="M55 255 L55 35 L149 145 L243 200 L337 227.5 L431 241.25 L525 248.125 L525 255Z"/>
<path id="memory-curve" class="memory-curve" d="M55 35 L149 145 L243 200 L337 227.5 L431 241.25 L525 248.125"/>
<circle id="memory-dot" cx="243" cy="200" r="5"/>
</svg><p class="figure-caption">An illustrative exponential kernel. Volterra models allow more general memory kernels.</p>
<details class="math-note"><summary>The mathematical idea</summary><p>Here, the weight at lag <var>s</var> is <span class="formula">K(s) = 2<sup>−s/h</sup></span>, where <var>h</var> is the half-life. Every additional <var>h</var> time units halves the weight. The kernel is normalized to K(0) = 1; its total area is not held fixed.</p><p>This is a simple illustration of memory weighting, rather than a simulation of a particular model or signature.</p></details></div></section>
<div class="research-chapters">'''
    for n,t in enumerate(themes,1):
        content+=f'<section class="research-chapter" id="{t["id"]}"><div class="chapter-label"><span>0{n}</span><p>{t["name"]}</p><a href="#research-themes">All themes ↑</a></div><div class="chapter-content"><h2>{t["question"]}</h2><p class="chapter-intro">{t["intro"]}</p><p>{t["contribution"]}</p><p class="research-connection">{t["connection"]}</p><h3 class="reading-label">A few starting points</h3><div class="featured-research">'
        for u in t['featured']:
            p,num=lookup[u]
            group=next(g['name'] for g in t['groups'] if u in g['papers'])
            content+=f'<div class="research-paper"><p class="paper-topic">{escape(group)}</p>{paper(p,num)}</div>'
        remaining=sum(len(g['papers']) for g in t['groups'])-len(t['featured'])
        content+=f'</div><details class="theme-papers"><summary>Explore {remaining} more '+('paper' if remaining==1 else 'papers')+' in this theme<span aria-hidden="true">+</span></summary>'
        for g in t['groups']:
            urls=[u for u in g['papers'] if u not in t['featured']]
            if urls:
                content+=f'<h4>{escape(g["name"])}</h4>'
                content+=''.join(paper(*lookup[u]) for u in urls)
        content+='</details></div></section>'
    content+='''</div><section class="research-end"><h2>Continue exploring.</h2><p>For the full chronological list, visit <a class="inline-link" href="publications.html">Publications</a>. To meet the people behind this work, visit the <a class="inline-link" href="people.html">Research Group</a>.</p><a class="text-link" href="mailto:eduardo.abi-jaber@polytechnique.edu">Discuss a research question</a></section></div>'''
    content=content.replace('<div class="theme-map">','<div class="theme-map" id="research-themes">')
    page('research-preview.html','Research preview','A thematic exploration of research in Volterra processes, path signatures, volatility and stochastic invariance.',content)
    p=out/'research-preview.html'
    p.write_text(p.read_text().replace('</head>','<meta name="robots" content="noindex, nofollow"></head>'))

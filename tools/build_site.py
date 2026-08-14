# -*- coding: utf-8 -*-
"""Generate the multi-page tonyseo.com static site from the single-file portfolio."""
import io, os, re, shutil, zipfile

# All paths are relative to the repository root, so this runs on any machine.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'tools', 'source', 'portfolio-source.html')
FONT = os.path.join(ROOT, 'tools', 'assets', 'bricolage.woff2')
LOGOS_DIR = os.path.join(ROOT, 'tools', 'assets', 'logos')
FAV_DIR = os.path.join(ROOT, 'tools', 'assets', 'favicon')
AVATAR = os.path.join(ROOT, 'tools', 'assets', 'avatar.png')
OUT = os.path.join(ROOT, 'site')
ZIP = os.path.join(ROOT, 'site-deploy.zip')
DOMAIN = 'https://tonyseo.com'
TODAY = '2026-08-13'

html = io.open(SRC, encoding='utf-8').read()

# ---------- extract CSS, replace embedded font with file reference ----------
css = html[html.index('<style>') + 7 : html.index('</style>')]
css = re.sub(r"src: url\(data:font/woff2;base64,[^)]+\) format\('woff2'\);",
             "src: url(/assets/bricolage.woff2) format('woff2');", css)
assert 'data:font' not in css, 'font strip failed'
css += """
  .tab-btn[aria-current="page"] { background: var(--green-tint); color: var(--green-deep); }
  .crumbs { font-size: 11.5px; color: var(--ink-3); margin: 26px 0 0; }
  .crumbs a { color: var(--ink-3); text-decoration: none; }
  .crumbs a:hover { color: var(--green); }
  .case-h1 {
    font-family: 'Bricolage Grotesque', system-ui, sans-serif;
    font-weight: 750; font-size: clamp(28px, 4.6vw, 48px);
    line-height: 1.06; letter-spacing: -0.015em;
    margin: 14px 0 26px; text-wrap: balance; max-width: 24ch;
  }
  .prevnext { display: flex; justify-content: space-between; gap: 14px; margin-top: 26px; flex-wrap: wrap; }
  .prevnext a { font-size: 14px; font-weight: 650; color: var(--green-deep); text-decoration: none; }
  .prevnext a:hover { color: var(--green); }
  .index-cards { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }
  .icard {
    background: var(--surface); border: 1px solid var(--line); border-radius: 16px;
    overflow: hidden; text-decoration: none; color: inherit; display: flex; flex-direction: column;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
  }
  .icard:hover { transform: translateY(-3px); box-shadow: var(--shadow); }
  .icard-body { padding: 18px 22px 20px; }
  .icard-body h2 { font-family: 'Bricolage Grotesque', system-ui, sans-serif; font-weight: 730; font-size: 21px; margin: 0 0 4px; }
  .icard-body .ind { font-size: 12.5px; color: var(--ink-3); }
  .icard-body .sum { font-size: 14px; color: var(--ink-2); margin: 8px 0 10px; }
  .icard-body .go { font-size: 13.5px; font-weight: 650; color: var(--green-deep); }
  @media (max-width: 760px) { .index-cards { grid-template-columns: 1fr; } }
  @media (prefers-reduced-motion: reduce) { .icard { transition: none; } }
"""

# ---------- extract shared blocks ----------
def block(start_marker, end_marker, s=html):
    i = s.index(start_marker)
    j = s.index(end_marker, i) + len(end_marker)
    return s[i:j]

panel_home = block('<main id="panel-home"', '</main>')
panel_about = block('<main id="panel-about"', '</main>')
panel_work = block('<main id="panel-work"', '</main>')
panel_brands = block('<main id="panel-brands"', '</main>')
footer = block('<footer>', '</footer>')

# ---------- shared transforms ----------
CASE_HREF = {
    'case-tickpick': '/case-studies/tickpick/',
    'case-adquick': '/case-studies/adquick/',
    'case-macduggal': '/case-studies/mac-duggal/',
    'case-flossy': '/case-studies/flossy/',
    'case-impact': '/case-studies/impact-dog-crates/',
    'case-anyma': '/case-studies/anyma/',
}

def transform(s):
    # avatar images -> file
    s = s.replace('<img class="av" ', '<img class="av" src="/assets/avatar.png" ')
    # logo images -> files
    s = re.sub(r'<img class="clogo([^"]*)" data-logo="([a-z]+)"', r'<img class="clogo\1" src="/assets/logos/\2.png"', s)
    # goto buttons -> real links
    def btn_to_link(m):
        cls, goto, case = m.group(1), m.group(2), m.group(3)
        if case and case in CASE_HREF:
            href = CASE_HREF[case]
        elif goto == 'work':
            href = '/case-studies/'
        elif goto == 'about':
            href = '/about/'
        elif goto == 'brands':
            href = '/brands/'
        else:
            href = '/'
        return '<a class="%s" href="%s">' % (cls, href)
    s = re.sub(r'<button class="([^"]+)" data-goto="(\w+)"(?: data-case="([\w-]+)")?>', btn_to_link, s)
    s = s.replace('</button>', '</a>')
    return s

panel_home, panel_about, panel_work, panel_brands = [transform(x) for x in (panel_home, panel_about, panel_work, panel_brands)]

def inner_main(p):
    p = re.sub(r'^<main[^>]*>', '', p)
    return re.sub(r'</main>$', '', p)

home_inner = inner_main(panel_home)
about_inner = inner_main(panel_about)
brands_inner = inner_main(panel_brands)

# about + brands: first h2 becomes the page h1
about_inner = about_inner.replace('<h2>It started', '<h1 style="font-size: clamp(28px, 4.6vw, 46px); font-family: \'Bricolage Grotesque\', system-ui, sans-serif; font-weight: 750; line-height: 1.08; letter-spacing: -0.01em; margin: 0; text-wrap: balance;">It started', 1).replace("brother's website.</h2>", "brother's website.</h1>", 1)
brands_inner = brands_inner.replace("<h2>Brands I've worked with.</h2>", '<h1 style="font-size: clamp(28px, 4.6vw, 46px); font-family: \'Bricolage Grotesque\', system-ui, sans-serif; font-weight: 750; line-height: 1.08; letter-spacing: -0.01em; margin: 0; text-wrap: balance;">Brands I\'ve worked with.</h1>', 1)

# ---------- case articles ----------
articles = {}
for cid in CASE_HREF:
    art = block('<article class="case reveal" id="%s">' % cid, '</article>', panel_work)
    articles[cid] = art

def banner_of(article_html):
    return block('<svg class="art"', '</svg>', article_html)

CASES = [
    dict(cid='case-tickpick', slug='tickpick', name='TickPick', industry='Ticket marketplace',
         title='LLM SEO Case Study: +843% Revenue From AI Search Traffic',
         desc='How traditional SEO signals won ChatGPT referrals for a ticket marketplace: +1,844% LLM-driven sessions, +843% revenue from AI traffic, and 17x share of organic.',
         h1='The LLM SEO case study: +843% revenue from AI search traffic.',
         sum='Proof that traditional SEO wins traffic inside ChatGPT, with revenue to show for it.'),
    dict(cid='case-adquick', slug='adquick', name='AdQuick', industry='Out-of-home advertising platform',
         title='GEO Case Study: +86% Form Submissions From AI Search',
         desc='A generative engine optimization prompt cluster that made one brand the cited answer for billboard advertising: +48% LLM-driven traffic and +86% form submissions.',
         h1='The GEO case study: owning one category in AI answers.',
         sum='A focused generative engine optimization prompt cluster that turned AI visibility into demand.'),
    dict(cid='case-macduggal', slug='mac-duggal', name='Mac Duggal', industry='Luxury occasion wear',
         title='Link Building Case Study: #29 to #2 on a 93,000-Search Keyword',
         desc='Twelve months of anchor-mapped link building for luxury fashion collection pages: +181% non-branded clicks, 25 to 2,060 page-one keywords, +2,500% LLM traffic.',
         h1='The link building case study: #29 to #2 on a 93k keyword.',
         sum='Anchor-mapped link building that put two collection pages at position 2 on head terms.'),
    dict(cid='case-flossy', slug='flossy', name='Flossy', industry='Affordable dental care',
         title='SEO Content Strategy Case Study: 160 to 58,000 Monthly Organic Visits',
         desc='A 195-piece content engine plus link building outranked legacy health publishers on dental keywords: +36,265% organic traffic and 45,000+ ranking keywords.',
         h1='The content strategy case study: 160 to 58k monthly visits.',
         sum='A 195-piece content engine that outranked legacy health publishers in a brutal vertical.'),
    dict(cid='case-impact', slug='impact-dog-crates', name='Impact Dog Crates', industry='Premium pet e-commerce',
         title='E-commerce SEO Case Study: Winning Head Terms With Link Building',
         desc='Anchor-specific link building aimed straight at head terms for a pet e-commerce brand: +39% non-branded clicks and +1,215% homepage non-branded clicks year over year.',
         h1='The e-commerce SEO case study: go broad, win the head terms.',
         sum='Anchor-specific link building aimed at the big keywords, and the homepage became a landing page.'),
    dict(cid='case-anyma', slug='anyma', name='Anyma', industry='Electronic music artist',
         title='Brand SERP Case Study: #1 on Google in Two Months',
         desc='A link building sprint that put a world-touring electronic artist at #1 on Google for his own name: +350% domain rating and +282% keyword rankings in eight weeks.',
         h1='The brand SERP case study: #1 on Google in two months.',
         sum='A two-month link building sprint that put a touring artist at #1 for his own name.'),
]

# ---------- page shell ----------
NAV_ITEMS = [('/', 'Home'), ('/about/', 'About'), ('/case-studies/', 'Case Studies'), ('/brands/', 'Brands')]

def nav(active):
    links = []
    for href, label in NAV_ITEMS:
        cur = ' aria-current="page"' if href == active else ''
        links.append('<a class="tab-btn" href="%s"%s>%s</a>' % (href, cur, label))
    return ('<nav class="nav"><div class="nav-in">'
            '<a class="brand" href="/"><img class="av" src="/assets/avatar.png" alt="" width="30" height="30">'
            '<span class="bn mono">Anthony Jackson</span></a>'
            '<div class="tabs">%s</div>'
            '<div class="navlinks">'
            '<a href="https://www.linkedin.com/in/anthony-jackson-seo/" target="_blank" rel="noopener">LinkedIn</a>'
            '<a href="mailto:tjackson15.17@gmail.com">Email</a>'
            '</div></div></nav>') % ''.join(links)

PERSON_LD = '''<script type="application/ld+json">
{"@context":"https://schema.org","@type":"Person","name":"Anthony Jackson","jobTitle":"Associate Director of SEO & AI Search","worksFor":{"@type":"Organization","name":"GR0","url":"https://gr0.com"},"url":"https://tonyseo.com/","email":"mailto:tjackson15.17@gmail.com","sameAs":["https://www.linkedin.com/in/anthony-jackson-seo/"],"knowsAbout":["SEO","Generative Engine Optimization","AI Search","Link Building","Content Strategy"],"alumniOf":{"@type":"CollegeOrUniversity","name":"Northern Michigan University"}}
</script>'''

def breadcrumb_ld(name, url):
    return ('<script type="application/ld+json">'
            '{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":['
            '{"@type":"ListItem","position":1,"name":"Home","item":"https://tonyseo.com/"},'
            '{"@type":"ListItem","position":2,"name":"Case Studies","item":"https://tonyseo.com/case-studies/"},'
            '{"@type":"ListItem","position":3,"name":"%s","item":"%s"}]}'
            '</script>') % (name, url)

REVEAL_JS = '''<script>
(function () {
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var els = document.querySelectorAll('.reveal');
  if (reduce || !('IntersectionObserver' in window)) {
    els.forEach(function (el) { el.classList.add('in'); });
    return;
  }
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
    });
  }, { threshold: 0.1 });
  els.forEach(function (el) { io.observe(el); });
})();
</script>'''

def page(path, title, desc, active, body, extra_ld='', og_type='website'):
    url = DOMAIN + path
    return '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%s</title>
<meta name="description" content="%s">
<link rel="canonical" href="%s">
<meta property="og:title" content="%s">
<meta property="og:description" content="%s">
<meta property="og:url" content="%s">
<meta property="og:type" content="%s">
<meta property="og:image" content="%s/og-image.png">
<meta property="og:site_name" content="Anthony Jackson · tonyseo.com">
<meta name="twitter:card" content="summary">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="stylesheet" href="/assets/style.css">
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-BQMVXYMTKY"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'G-BQMVXYMTKY');
</script>
%s
</head>
<body>
%s
<div class="wrap">
%s
%s
</div>
%s
</body>
</html>
''' % (title, desc, url, title, desc, url, og_type, DOMAIN, extra_ld, nav(active), body, footer, REVEAL_JS)

# ---------- build output tree ----------
if os.path.exists(OUT):
    for child in os.listdir(OUT):
        p = os.path.join(OUT, child)
        if os.path.isdir(p):
            shutil.rmtree(p, ignore_errors=True)
        else:
            try:
                os.remove(p)
            except OSError:
                pass
os.makedirs(os.path.join(OUT, 'assets', 'logos'), exist_ok=True)

def write(path, content):
    full = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    io.open(full, 'w', encoding='utf-8').write(content)

write(os.path.join('assets', 'style.css'), css)

# home
write('index.html', page(
    '/', 'Anthony Jackson | SEO & AI Search Portfolio · GEO, LLM SEO, Link Building',
    'SEO and AI search portfolio with receipts: +843% revenue from ChatGPT traffic, #29 to #2 rankings, and GEO campaigns for 17 brands. By Anthony Jackson.',
    '/', home_inner, PERSON_LD))

# about
write(os.path.join('about', 'index.html'), page(
    '/about/', "From My Brother's Website to AI Search Director | About Anthony Jackson",
    'How a 2016 SEO experiment became a career in search and generative engine optimization: freelance work, Head of SEO Operations, and AI search work at GR0 today.',
    '/about/', about_inner, PERSON_LD))

# case studies index
cards = []
for c in CASES:
    banner = banner_of(articles[c['cid']])
    cards.append('''<a class="icard reveal" href="/case-studies/%s/">%s<span class="icard-body"><h2>%s</h2><span class="ind">%s</span><span class="sum" style="display:block">%s</span><span class="go" style="display:block">Read the case study &rarr;</span></span></a>''' % (
        c['slug'], banner, c['name'], c['industry'], c['sum']))
index_body = '''<main>
<section class="block" style="padding-top: clamp(36px, 5vw, 56px);">
  <div class="sec-head">
    <p class="k mono">Selected campaigns</p>
    <h1 style="font-size: clamp(28px, 4.6vw, 46px); font-family: 'Bricolage Grotesque', system-ui, sans-serif; font-weight: 750; line-height: 1.08; letter-spacing: -0.01em; margin: 0; text-wrap: balance;">SEO &amp; GEO case studies with real numbers.</h1>
    <p class="note">Six campaigns spanning LLM SEO, generative engine optimization, anchor-text link building, and content strategy at scale. I ran every one end to end at GR0 and wrote the published case studies myself.</p>
  </div>
  <div class="index-cards">%s</div>
</section>
</main>''' % ''.join(cards)
write(os.path.join('case-studies', 'index.html'), page(
    '/case-studies/', 'SEO & GEO Case Studies With Real Numbers | LLM SEO, Link Building, Content',
    'Six SEO case studies with verified results: LLM SEO revenue growth, generative engine optimization, anchor-text link building, and content strategy at scale.',
    '/case-studies/', index_body, PERSON_LD))

# individual case pages
for i, c in enumerate(CASES):
    prev_c = CASES[i - 1] if i > 0 else CASES[-1]
    next_c = CASES[i + 1] if i < len(CASES) - 1 else CASES[0]
    url = '%s/case-studies/%s/' % (DOMAIN, c['slug'])
    body = '''<main>
<p class="crumbs mono"><a href="/">Home</a> / <a href="/case-studies/">Case Studies</a> / %s</p>
<h1 class="case-h1">%s</h1>
<section style="padding: 0 0 8px;">
<div class="cases">
%s
</div>
<div class="prevnext">
  <a href="/case-studies/%s/">&larr; %s</a>
  <a href="/case-studies/%s/">%s &rarr;</a>
</div>
</section>
</main>''' % (c['name'], c['h1'], articles[c['cid']], prev_c['slug'], prev_c['name'], next_c['slug'], next_c['name'])
    write(os.path.join('case-studies', c['slug'], 'index.html'), page(
        '/case-studies/%s/' % c['slug'], c['title'] + ' | Tony Jackson', c['desc'],
        '/case-studies/', body, breadcrumb_ld(c['name'], url), og_type='article'))

# brands
write(os.path.join('brands', 'index.html'), page(
    '/brands/', "Brands I've Worked With | E-commerce, Health & Marketplace SEO",
    '17 brands across e-commerce, healthcare, food, fashion, finance, and entertainment, including TickPick, HelloFresh, Bark, and Kizik. Six with published SEO case studies.',
    '/brands/', brands_inner, PERSON_LD))

# ---------- assets ----------
shutil.copy(FONT, os.path.join(OUT, 'assets', 'bricolage.woff2'))
shutil.copy(AVATAR, os.path.join(OUT, 'assets', 'avatar.png'))
shutil.copy(AVATAR, os.path.join(OUT, 'og-image.png'))
for f in os.listdir(LOGOS_DIR):
    shutil.copy(os.path.join(LOGOS_DIR, f), os.path.join(OUT, 'assets', 'logos', f))
for f in ['favicon.ico', 'favicon-32.png', 'apple-touch-icon.png']:
    shutil.copy(os.path.join(FAV_DIR, f), os.path.join(OUT, f))

# ---------- robots + sitemap ----------
write('robots.txt', 'User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n' % DOMAIN)

urls = [('/', '1.0'), ('/about/', '0.8'), ('/case-studies/', '0.9'), ('/brands/', '0.7')] + \
       [('/case-studies/%s/' % c['slug'], '0.8') for c in CASES]
sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for u, pr in urls:
    sm.append('  <url><loc>%s%s</loc><lastmod>%s</lastmod><priority>%s</priority></url>' % (DOMAIN, u, TODAY, pr))
sm.append('</urlset>')
write('sitemap.xml', '\n'.join(sm) + '\n')

# ---------- zip ----------
if os.path.exists(ZIP):
    os.remove(ZIP)
with zipfile.ZipFile(ZIP, 'w', zipfile.ZIP_DEFLATED) as z:
    for root, _, files in os.walk(OUT):
        for f in files:
            full = os.path.join(root, f)
            z.write(full, os.path.relpath(full, OUT))

# ---------- report ----------
count = sum(len(files) for _, _, files in os.walk(OUT))
print('files written:', count)
for root, _, files in os.walk(OUT):
    rel = os.path.relpath(root, OUT)
    for f in sorted(files):
        if f.endswith('.html') or f in ('robots.txt', 'sitemap.xml'):
            print(' ', os.path.join(rel, f) if rel != '.' else f)
print('zip KB:', round(os.path.getsize(ZIP) / 1024))

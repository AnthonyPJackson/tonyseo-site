# tonyseo.com

Personal SEO & AI Search portfolio for Anthony Jackson. Live at [tonyseo.com](https://tonyseo.com), hosted on Netlify.

## Structure

```
site/                  The deployed website (static HTML/CSS, no framework)
  index.html           Home
  about/               About + career timeline
  case-studies/        Index + 6 individual case study pages
  brands/              Client roster
  assets/              Shared CSS, font, avatar, brand logos
  sitemap.xml, robots.txt, favicons
tools/
  build_site.py        Generator that builds site/ from the source file
  source/portfolio-source.html   Single-file content source
  assets/              Generator inputs (font, logos, favicon, avatar)
netlify.toml           Tells Netlify to publish the site/ folder
```

## Making changes

Two ways:

1. **Small edits**: edit the files in `site/` directly. They are plain HTML and CSS.
2. **Regenerate everything**: edit `tools/source/portfolio-source.html` (all the content lives there), then run:

```
python tools/build_site.py
```

That rebuilds `site/` and drops a fresh `site-deploy.zip` at the repo root.

## Deploying

Netlify serves the `site/` folder. Once this repo is linked to the Netlify project, any push to `main` deploys automatically. Until then, drag `site-deploy.zip` onto the tonyseo.com project at app.netlify.com.

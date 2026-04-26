# Static Documentation Website — Setup Guide

## Context & Goals

You have a Bitbucket repository with multiple folders, each containing markdown documents and `index.md` files. The objective is to stand up a polished, searchable, auto-rebuilding static documentation site using **MkDocs** with the **Material for MkDocs** theme — and to understand the broader landscape of alternatives.

This guide covers three things:

1. The optimum MkDocs + Material configuration with all recommended plugins.
2. A comparative analysis of alternative static-site generators for documentation.
3. A Bitbucket Pipeline that regenerates the site on every push.

---

## Part 1 — MkDocs + Material Theme (Optimum Setup)

### 1.1 Project Structure

Your repository should follow this layout. MkDocs expects a `docs/` directory by default, but you can point it at your existing folder structure.

```
repo-root/
├── mkdocs.yml                  # Central configuration
├── docs/                       # All your markdown content
│   ├── index.md                # Site homepage
│   ├── folder-a/
│   │   ├── index.md
│   │   ├── page-one.md
│   │   └── page-two.md
│   ├── folder-b/
│   │   ├── index.md
│   │   └── deep-topic.md
│   └── assets/
│       ├── images/
│       └── stylesheets/
│           └── extra.css       # Custom overrides (optional)
├── overrides/                  # Theme template overrides (optional)
│   └── main.html
├── requirements.txt            # Python dependencies
├── bitbucket-pipelines.yml     # CI/CD pipeline
└── Dockerfile                  # (Optional) for containerised builds
```

> **Key point:** If your markdown files currently live in the repo root rather than a `docs/` folder, set `docs_dir: .` in `mkdocs.yml` — but a dedicated `docs/` directory is cleaner and avoids MkDocs trying to process your `README.md`, pipeline files, etc.

### 1.2 Dependencies (requirements.txt)

```txt
mkdocs>=1.6
mkdocs-material>=9.5
mkdocs-minify-plugin>=0.8
mkdocs-redirects>=1.2
mkdocs-git-revision-date-localized-plugin>=1.2
mkdocs-git-authors-plugin>=0.9
mkdocs-glightbox>=0.4
mkdocs-awesome-pages-plugin>=2.9
mkdocs-macros-plugin>=1.0
mkdocs-print-site-plugin>=2.5
mkdocs-section-index>=0.3
```

Install locally with:

```bash
pip install -r requirements.txt
```

### 1.3 Full mkdocs.yml Configuration

This is a production-grade configuration with every major plugin enabled and annotated.

```yaml
# ==============================================================
# Site Metadata
# ==============================================================
site_name: "Your Project Documentation"
site_url: "https://your-domain.com/docs/"    # Canonical URL
site_author: "Your Team"
site_description: "Internal documentation for Your Project"
repo_url: "https://bitbucket.org/your-workspace/your-repo"
repo_name: "your-workspace/your-repo"
edit_uri: "src/main/docs/"                    # Enables "Edit on Bitbucket" links

# ==============================================================
# Build Directories
# ==============================================================
docs_dir: docs
site_dir: site                                # Output directory

# ==============================================================
# Theme — Material for MkDocs
# ==============================================================
theme:
  name: material
  custom_dir: overrides                       # For template overrides
  language: en
  
  features:
    # --- Navigation ---
    - navigation.instant                      # XHR-based navigation (SPA feel)
    - navigation.instant.progress             # Loading progress indicator
    - navigation.tracking                     # URL updates on scroll
    - navigation.tabs                         # Top-level sections as tabs
    - navigation.tabs.sticky                  # Tabs stay visible on scroll
    - navigation.sections                     # Render top-level as sections
    - navigation.expand                       # Expand all sections by default
    - navigation.indexes                      # index.md becomes section landing page
    - navigation.top                          # Back-to-top button
    - navigation.path                         # Breadcrumbs (Insiders only)
    
    # --- Table of Contents ---
    - toc.follow                              # TOC follows scroll position
    - toc.integrate                           # TOC integrates into left nav
    
    # --- Search ---
    - search.suggest                          # Auto-complete suggestions
    - search.highlight                        # Highlight matches on target page
    - search.share                            # Shareable search deep links
    
    # --- Content ---
    - content.code.copy                       # Copy button on code blocks
    - content.code.annotate                   # Code annotations
    - content.tabs.link                       # Linked content tabs
    - content.tooltips                        # Improved tooltips
    - content.action.edit                     # Edit-this-page link
    - content.action.view                     # View source link
    
    # --- Header ---
    - header.autohide                         # Auto-hide header on scroll
    - announce.dismiss                        # Dismissable announcements
  
  palette:
    # Light mode
    - media: "(prefers-color-scheme: light)"
      scheme: default
      primary: indigo
      accent: indigo
      toggle:
        icon: material/brightness-7
        name: Switch to dark mode
    # Dark mode
    - media: "(prefers-color-scheme: dark)"
      scheme: slate
      primary: indigo
      accent: indigo
      toggle:
        icon: material/brightness-4
        name: Switch to light mode
  
  font:
    text: Inter
    code: JetBrains Mono
  
  icon:
    repo: fontawesome/brands/bitbucket
    edit: material/pencil
    view: material/eye
    logo: material/book-open-page-variant
  
  favicon: assets/images/favicon.png

# ==============================================================
# Plugins
# ==============================================================
plugins:
  # --- Core ---
  - search:
      lang: en
      separator: '[\s\-\.]+'                 # Better tokenisation
  
  # --- Navigation ---
  - awesome-pages                             # .pages files for custom ordering
  - section-index                             # index.md as clickable section headers
  
  # --- Git Integration ---
  - git-revision-date-localized:
      enable_creation_date: true
      type: timeago                           # "2 days ago" style
      fallback_to_build_date: true            # Handles files not in git
  - git-authors:                              # Show contributors per page
      show_contribution: true
      show_line_count: true
  
  # --- Content Enhancement ---
  - glightbox:                                # Image lightbox
      touchNavigation: true
      loop: false
      effect: zoom
      slide_effect: slide
      width: 100%
      height: auto
      zoomable: true
      draggable: true
  - macros:                                   # Jinja2 templating in markdown
      include_dir: docs/includes
  
  # --- Build Optimisation ---
  - minify:
      minify_html: true
      minify_js: true
      minify_css: true
      htmlmin_opts:
        remove_comments: true
  
  # --- Redirects (for restructuring) ---
  - redirects:
      redirect_maps: {}                       # Add old-path: new-path mappings
  
  # --- Print / Export ---
  - print-site:
      add_to_navigation: false
      print_page_title: "Full Documentation"
      enabled: true

# ==============================================================
# Social Cards (requires Insiders OR manual setup)
# ==============================================================
# If using Material for MkDocs Insiders:
# plugins:
#   - social:
#       cards_layout: default/variant
#       cards_layout_options:
#         background_color: "#4051b5"

# ==============================================================
# Markdown Extensions
# ==============================================================
markdown_extensions:
  # --- Python Markdown ---
  - abbr                                      # Abbreviation tooltips
  - admonition                                # Callout boxes
  - attr_list                                 # Add HTML attributes
  - def_list                                  # Definition lists
  - footnotes                                 # Footnotes
  - md_in_html                                # Markdown inside HTML
  - tables                                    # Standard tables
  - toc:
      permalink: true                         # Anchor links on headings
      permalink_title: "Link to this section"
      toc_depth: 3

  # --- PyMdown Extensions ---
  - pymdownx.arithmatex:                      # LaTeX math
      generic: true
  - pymdownx.betterem:
      smart_enable: all
  - pymdownx.caret                            # Superscript / insert
  - pymdownx.mark                             # Highlighted text
  - pymdownx.tilde                            # Subscript / strikethrough
  - pymdownx.critic                           # Track-changes markup
  - pymdownx.details                          # Collapsible admonitions
  - pymdownx.emoji:
      emoji_index: !!python/name:material.extensions.emoji.twemoji
      emoji_generator: !!python/name:material.extensions.emoji.to_svg
  - pymdownx.highlight:
      anchor_linenums: true
      line_spans: __span
      pygments_lang_class: true
      auto_title: true
  - pymdownx.inlinehilite
  - pymdownx.keys                             # Keyboard key rendering
  - pymdownx.smartsymbols                     # Smart quotes, arrows, etc.
  - pymdownx.snippets:                        # Include external files
      auto_append:
        - docs/includes/abbreviations.md
  - pymdownx.superfences:                     # Fenced code + diagrams
      custom_fences:
        - name: mermaid
          class: mermaid
          format: !!python/name:pymdownx.superfences.fence_code_format
  - pymdownx.tabbed:
      alternate_style: true
      slugify: !!python/object/apply:pymdownx.slugs.slugify
        kwds:
          case: lower
  - pymdownx.tasklist:
      custom_checkbox: true

# ==============================================================
# Extra Configuration
# ==============================================================
extra:
  generator: false                            # Hide "Made with MkDocs"
  
  social:
    - icon: fontawesome/brands/bitbucket
      link: https://bitbucket.org/your-workspace
      name: Bitbucket
  
  analytics:
    provider: google
    property: G-XXXXXXXXXX                    # Replace with your GA4 ID
  
  consent:
    title: Cookie consent
    description: >-
      We use cookies to recognise your repeated visits and preferences,
      as well as to measure the effectiveness of our documentation.
  
  # Version selector (if publishing multiple versions)
  version:
    provider: mike

extra_css:
  - assets/stylesheets/extra.css

extra_javascript:
  - https://unpkg.com/mathjax@3/es5/tex-mml-chtml.js

# ==============================================================
# Navigation (explicit — or remove to use auto-discovery)
# ==============================================================
# Option A: Let awesome-pages + section-index handle it automatically
# Option B: Define explicitly:
#
# nav:
#   - Home: index.md
#   - Section A:
#     - folder-a/index.md
#     - Page One: folder-a/page-one.md
#     - Page Two: folder-a/page-two.md
#   - Section B:
#     - folder-b/index.md
#     - Deep Topic: folder-b/deep-topic.md
```

### 1.4 Automatic Navigation with awesome-pages

Instead of manually maintaining the `nav:` tree in `mkdocs.yml`, drop a `.pages` file into any folder to control ordering:

```yaml
# docs/folder-a/.pages
title: Section A
arrange:
  - index.md
  - page-one.md
  - page-two.md
  - ...                # Everything else in alphabetical order
```

When you add a new markdown file, it automatically appears in the navigation (alphabetically after any explicitly listed files). No config changes needed.

### 1.5 Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Serve with live reload
mkdocs serve

# Build static site
mkdocs build --strict    # --strict fails on warnings
```

---

## Part 2 — Comparative Alternatives

Below is an analysis of every serious alternative to MkDocs + Material for hosting a static documentation site. Docusaurus is excluded per your request.

### 2.1 Comparison Matrix

| Tool | Language | Config | Learning Curve | Search | Theme Quality | Plugin Ecosystem | Best For |
|---|---|---|---|---|---|---|---|
| **MkDocs + Material** | Python | YAML | Low | Built-in (lunr.js) | Excellent | Rich | Docs with zero friction |
| **Sphinx** | Python | Python (conf.py) | High | Built-in | Good (furo theme) | Very Rich | API docs, technical/scientific |
| **Hugo** | Go | TOML/YAML | Medium | Needs plugin | Varies by theme | Moderate | Large sites needing speed |
| **Astro Starlight** | Node.js | TypeScript | Medium | Built-in (Pagefind) | Excellent | Growing | Modern component-driven docs |
| **VitePress** | Node.js | TypeScript | Medium | Built-in (MiniSearch) | Excellent | Small but focused | Vue ecosystem docs |
| **Nextra** | Node.js | JS/MDX | Medium | Built-in (FlexSearch) | Very Good | Small | Next.js ecosystem |
| **mdBook** | Rust | TOML | Low | Built-in | Minimal | Very Small | Rust-style book format |
| **Zola** | Rust | TOML | Medium | Built-in (elasticlunr) | Varies | Small | Speed-focused simple sites |
| **Jekyll** | Ruby | YAML | Medium | Needs plugin | Varies | Large | GitHub Pages native |
| **Docsify** | JavaScript | HTML | Very Low | Built-in | Good | Moderate | No-build SPA docs |

### 2.2 Detailed Breakdown

**Sphinx + Furo Theme**
The original Python documentation engine. It natively supports reStructuredText and, via MyST-Parser, Markdown. Sphinx excels at auto-generating API documentation from docstrings, cross-referencing between documents, and producing multi-format output (HTML, PDF, EPUB). The Furo theme gives it a modern look competitive with Material. The tradeoff is configuration complexity — `conf.py` is a full Python file, and the learning curve is steep for non-developers.

**Hugo + Docsy / Doks Theme**
Hugo is the fastest static site generator, compiling thousands of pages in under a second. The Docsy theme (used by Kubernetes docs) and Doks theme provide documentation-grade layouts. Hugo uses Go templates, which have an unconventional syntax. It lacks a built-in search out of the box — you bolt on Algolia, Pagefind, or Lunr.js. Hugo is the right choice when you have a very large content base (5,000+ pages) and build speed matters.

**Astro Starlight**
Starlight is Astro's official documentation theme and is one of the strongest newer entrants. It uses the Astro framework (component islands architecture), ships near-zero JavaScript by default, and integrates Pagefind for full-text search. It supports MDX, which means you can embed interactive components directly in markdown. Starlight's design is polished and accessible out of the box. The tradeoff is that the ecosystem is younger and you need Node.js tooling.

**VitePress**
Built by the Vue.js team as the successor to VuePress. It uses Vite under the hood for near-instant hot module replacement during development. VitePress supports Vue components inline in Markdown and has a clean default theme tuned for documentation. Search is built in via MiniSearch. It is ideal if your team already uses Vue or if you want a fast, opinionated, minimal-config setup.

**Nextra**
A Next.js-based documentation generator. If your team lives in the React/Next.js ecosystem, Nextra lets you write MDX (Markdown + JSX) and deploy to Vercel trivially. It provides file-system routing, a clean docs theme, and FlexSearch integration. The downside is that it carries the full weight of the Next.js build system.

**mdBook**
The Rust ecosystem's documentation standard (used for "The Rust Programming Language" book). Configuration is a single `book.toml`. It produces clean, readable HTML with built-in search. It does one thing well — linear book-style documentation — and lacks the plugin richness of MkDocs or Sphinx.

**Zola**
A single-binary static site generator written in Rust. Zero dependencies, extremely fast builds, built-in Sass compilation, and search via elasticlunr. Zola is a strong choice if you want simplicity and speed without a Node.js or Python toolchain. The theme ecosystem is smaller, so you may need to build or adapt a docs theme.

**Docsify**
Unique in that it does not build static HTML — it loads markdown files at runtime in the browser via JavaScript. This means zero build step: you push markdown, it is live immediately. The tradeoff is that it is not truly static (worse for SEO, no pre-rendered HTML), and performance degrades on large sites.

### 2.3 Recommendation

For your use case (markdown-heavy, folder-structured, index.md per folder, Bitbucket-hosted, CI/CD rebuild), **MkDocs + Material** remains the optimal choice because:

- Your existing folder/index.md structure maps directly to MkDocs conventions.
- Zero JavaScript toolchain required (Python only).
- The awesome-pages plugin means new files auto-appear in navigation.
- The Material theme provides search, dark mode, social cards, and mobile responsiveness with no custom code.
- Bitbucket Pipelines integration is straightforward (see Part 3).

If you ever outgrow MkDocs (need interactive components, have 10,000+ pages, or want MDX), **Astro Starlight** or **VitePress** would be the natural next step.

---

## Part 3 — Bitbucket Pipeline for Auto-Regeneration

### 3.1 Pipeline Configuration (bitbucket-pipelines.yml)

This pipeline triggers on every push to `main` and deploys the built site. Two deployment targets are shown: Bitbucket Downloads (simplest) and AWS S3 + CloudFront (production-grade).

```yaml
image: python:3.12-slim

definitions:
  caches:
    pip: ~/.cache/pip

  steps:
    - step: &build-docs
        name: Build Documentation
        caches:
          - pip
        script:
          - apt-get update && apt-get install -y --no-install-recommends git
          - pip install --upgrade pip
          - pip install -r requirements.txt
          - mkdocs build --strict
        artifacts:
          - site/**

    - step: &deploy-s3
        name: Deploy to S3
        script:
          - pipe: atlassian/aws-s3-deploy:1.1.0
            variables:
              AWS_ACCESS_KEY_ID: $AWS_ACCESS_KEY_ID
              AWS_SECRET_ACCESS_KEY: $AWS_SECRET_ACCESS_KEY
              AWS_DEFAULT_REGION: "us-east-1"
              S3_BUCKET: "your-docs-bucket"
              LOCAL_PATH: "site"
              DELETE_FLAG: "true"               # Remove old files
              ACL: "public-read"
              CACHE_CONTROL: "max-age=3600"

    - step: &invalidate-cache
        name: Invalidate CloudFront
        script:
          - pipe: atlassian/aws-cloudfront-invalidate:0.6.0
            variables:
              AWS_ACCESS_KEY_ID: $AWS_ACCESS_KEY_ID
              AWS_SECRET_ACCESS_KEY: $AWS_SECRET_ACCESS_KEY
              AWS_DEFAULT_REGION: "us-east-1"
              DISTRIBUTION_ID: $CLOUDFRONT_DISTRIBUTION_ID
              PATHS: "/*"

pipelines:
  # ── Trigger on every push to main ──
  branches:
    main:
      - step: *build-docs
      - step: *deploy-s3
      - step: *invalidate-cache

  # ── Manual trigger for other branches (preview builds) ──
  custom:
    build-preview:
      - step: *build-docs

  # ── Pull request builds (validate only, no deploy) ──
  pull-requests:
    "**":
      - step:
          name: Validate Documentation
          caches:
            - pip
          script:
            - apt-get update && apt-get install -y --no-install-recommends git
            - pip install --upgrade pip
            - pip install -r requirements.txt
            - mkdocs build --strict
```

### 3.2 Alternative Deployment Targets

**GitHub Pages (via Bitbucket Mirror)**
If you mirror to GitHub, you can use `mkdocs gh-deploy` which pushes the built site to a `gh-pages` branch.

**Netlify**
Add a `netlify.toml` to your repo root:

```toml
[build]
  command = "pip install -r requirements.txt && mkdocs build --strict"
  publish = "site"

[build.environment]
  PYTHON_VERSION = "3.12"
```

Netlify can connect directly to Bitbucket and will auto-build on every push.

**Cloudflare Pages**
Similar to Netlify — connect your Bitbucket repo, set the build command to `pip install -r requirements.txt && mkdocs build`, and the output directory to `site`.

**Self-Hosted (Nginx / Caddy)**
Build in the pipeline, then `rsync` or `scp` the `site/` directory to your server. Caddy is especially simple — point it at the directory and it handles HTTPS automatically.

### 3.3 How Auto-Regeneration Works

The flow is:

1. You add, edit, or delete a markdown file in your Bitbucket repository.
2. You push to `main` (or merge a pull request).
3. Bitbucket Pipelines detects the push and runs the pipeline.
4. The pipeline installs dependencies, runs `mkdocs build --strict`, and deploys the output.
5. The site is live with your changes within 2–3 minutes.

For the "awesome-pages" plugin, new files are automatically picked up in the navigation without touching `mkdocs.yml`. The only time you need to edit configuration is when you want to change the order of sections or add explicit navigation overrides.

---

## Part 4 — Production Hardening Checklist

These are additional steps for a robust production deployment:

- **Custom domain + HTTPS**: Use Cloudflare, AWS ACM, or Let's Encrypt for TLS. All deployment targets above support custom domains.
- **404 page**: Create `docs/404.md` — Material will render it as your custom 404 page.
- **Robots.txt and sitemap**: MkDocs generates `sitemap.xml` automatically. Add a `docs/robots.txt` if needed.
- **Versioning with mike**: The `mike` tool lets you publish multiple versions of your docs side by side (e.g., `v1.0`, `v2.0`, `latest`). The `extra.version.provider: mike` config in the YAML above enables the version selector dropdown.
- **Social cards**: If you use Material Insiders (paid sponsor tier), enable the `social` plugin for auto-generated Open Graph images. Alternatively, generate them manually and place in `docs/assets/images/social/`.
- **Offline support**: Material supports `offline` plugin for downloadable documentation.
- **Access control**: For internal docs, deploy behind a VPN, use Cloudflare Access, or add HTTP basic auth via your web server.

---

## Part 5 — Quick-Start Commands

```bash
# 1. Clone your repo
git clone git@bitbucket.org:your-workspace/your-repo.git
cd your-repo

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate    # Linux/Mac
# .venv\Scripts\activate     # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Serve locally with live reload
mkdocs serve
# → Open http://127.0.0.1:8000

# 5. Build for production
mkdocs build --strict

# 6. Deploy (if using GitHub Pages mirror)
mkdocs gh-deploy --force
```

---

## Appendix — Placeholder for Future Additions

The following sections will be added in subsequent iterations:

- **Claude Code Customization** — Configuration and workflow for using Claude Code with this documentation setup.
- **GitHub Copilot Customization** — Configuration and workflow for using GitHub Copilot with this documentation setup.

---

*Generated as a setup reference. Adapt paths, URLs, and credentials to your specific environment.*

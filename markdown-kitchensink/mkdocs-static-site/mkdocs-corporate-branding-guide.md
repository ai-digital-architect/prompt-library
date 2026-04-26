# MkDocs Material — Corporate Branding & Custom Theme Guide

## Overview

You have a corporate CSS file with your organisation's colour palette, typography, and branding guidelines. This guide walks through every layer of customisation available in Material for MkDocs — from simple colour overrides to a fully white-labelled documentation site — so you can apply your corporate identity systematically.

The customisation layers, from lightest to deepest:

1. **CSS custom properties** — Override Material's design tokens (colours, fonts, spacing).
2. **Additional CSS** — Layer corporate styles on top of the theme.
3. **Theme configuration** — Palette, font, logo, favicon, icons via `mkdocs.yml`.
4. **Template overrides** — Replace individual HTML components (header, footer, nav).
5. **Partial overrides** — Modify smaller fragments (analytics, social, consent).
6. **Full custom theme** — Extend Material as a base and build your own child theme.

Most corporate branding projects need layers 1–4 only.

---

## Step 1 — Project Structure for Theming

Extend your existing MkDocs project with these directories:

```
repo-root/
├── mkdocs.yml
├── docs/
│   ├── index.md
│   ├── assets/
│   │   ├── images/
│   │   │   ├── logo.svg              # Corporate logo (SVG preferred)
│   │   │   ├── logo-dark.svg         # Dark-mode variant (optional)
│   │   │   ├── favicon.png           # 32x32 or 64x64
│   │   │   └── social-card.png       # 1200x630 OG image fallback
│   │   └── stylesheets/
│   │       ├── corporate.css          # Your existing corporate CSS
│   │       ├── overrides.css          # Material-specific token overrides
│   │       └── components.css         # Custom component styles (optional)
│   └── ...
├── overrides/
│   ├── main.html                      # Master template override
│   ├── partials/
│   │   ├── header.html                # Custom header
│   │   ├── footer.html                # Custom footer
│   │   ├── logo.html                  # Logo rendering logic
│   │   └── copyright.html             # Copyright bar
│   └── assets/
│       └── stylesheets/
│           └── extra.css              # Injected automatically by Material
└── requirements.txt
```

---

## Step 2 — Map Your Corporate CSS to Material's Design Tokens

Material for MkDocs exposes its entire design system through CSS custom properties. The key is to map your corporate palette onto these tokens rather than fighting the theme with brute-force overrides.

### 2.1 The Complete Token Map

Create `docs/assets/stylesheets/overrides.css`. This file maps every major Material token to your corporate values.

```css
/* =================================================================
   docs/assets/stylesheets/overrides.css
   Corporate Design Token Overrides for Material for MkDocs
   ================================================================= */

/* ── ROOT TOKENS (apply to both light and dark modes) ── */
:root {
  /* ·· Primary Brand Colour ·· */
  /* Material uses a numeric scale: 50 (lightest) to 900 (darkest) */
  /* Generate your scale from your primary brand hex at:             */
  /* https://materialpalettes.com  or  https://m3.material.io       */
  --md-primary-fg-color:          #1B3A6B;   /* Your primary brand colour  */
  --md-primary-fg-color--light:   #3A6BAD;   /* Lighter variant            */
  --md-primary-fg-color--dark:    #0F2444;   /* Darker variant             */
  --md-primary-bg-color:          #FFFFFF;   /* Text on primary background */
  --md-primary-bg-color--light:   #FFFFFFB3; /* Text on primary (muted)   */

  /* ·· Accent / Secondary Colour ·· */
  --md-accent-fg-color:           #E8A317;   /* Accent for links, hover   */
  --md-accent-fg-color--transparent: #E8A31733; /* 20% opacity variant    */
  --md-accent-bg-color:           #FFFFFF;
  --md-accent-bg-color--light:    #FFFFFFB3;

  /* ·· Typography ·· */
  --md-text-font: "Your Corporate Font", "Inter", -apple-system,
                  BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  --md-code-font: "Your Mono Font", "JetBrains Mono", "Fira Code",
                  ui-monospace, SFMono-Regular, monospace;
  --md-text-font-size:            0.95rem;   /* Base font size */

  /* ·· Typographic Scale ·· */
  --md-typeset-font-size:         1rem;

  /* ·· Admonition Accent (custom branded callouts) ·· */
  --md-admonition-fg-color:       var(--md-default-fg-color);
  --md-admonition-bg-color:       var(--md-default-bg-color);

  /* ·· Code Block Colours ·· */
  --md-code-fg-color:             #2D3748;
  --md-code-bg-color:             #F7F8FA;
  --md-code-hl-color:             #E8A31733; /* Highlight accent */
  --md-code-hl-number-color:      #D63384;
  --md-code-hl-string-color:      #2B8A3E;
  --md-code-hl-keyword-color:     #1B3A6B;
  --md-code-hl-comment-color:     #6C757D;
  --md-code-hl-function-color:    #6F42C1;
  --md-code-hl-special-color:     #E8A317;

  /* ·· Footer ·· */
  --md-footer-bg-color:           #0F2444;
  --md-footer-bg-color--dark:     #091832;
  --md-footer-fg-color:           #FFFFFFB3;
  --md-footer-fg-color--light:    #FFFFFF73;
  --md-footer-fg-color--lighter:  #FFFFFF33;
}

/* ── LIGHT MODE ── */
[data-md-color-scheme="default"] {
  --md-default-fg-color:          #1A1A2E;   /* Body text                 */
  --md-default-fg-color--light:   #555570;   /* Secondary text            */
  --md-default-fg-color--lighter: #90909F;   /* Tertiary / muted text     */
  --md-default-fg-color--lightest:#DDDDE5;   /* Borders, dividers         */
  --md-default-bg-color:          #FFFFFF;   /* Page background           */
  --md-default-bg-color--light:   #F5F5F8;   /* Sidebar / card background */
  --md-default-bg-color--lighter: #EEEFF2;   /* Hover states              */
  --md-default-bg-color--lightest:#E0E1E6;   /* Active states             */

  /* ·· Shadows ·· */
  --md-shadow-z1: 0 2px 4px rgba(27,58,107,0.08);
  --md-shadow-z2: 0 4px 12px rgba(27,58,107,0.12);
  --md-shadow-z3: 0 8px 24px rgba(27,58,107,0.16);
}

/* ── DARK MODE ── */
[data-md-color-scheme="slate"] {
  --md-default-fg-color:          #E8E8ED;
  --md-default-fg-color--light:   #B0B0BE;
  --md-default-fg-color--lighter: #7A7A8E;
  --md-default-fg-color--lightest:#3A3A4E;
  --md-default-bg-color:          #0F1219;
  --md-default-bg-color--light:   #1A1E28;
  --md-default-bg-color--lighter: #252A36;
  --md-default-bg-color--lightest:#2F3545;

  /* ·· Adjust primary/accent for dark backgrounds ·· */
  --md-primary-fg-color:          #3A7BD5;
  --md-accent-fg-color:           #F0B840;

  /* ·· Code blocks in dark mode ·· */
  --md-code-fg-color:             #E0E0E8;
  --md-code-bg-color:             #1A1E28;
  --md-code-hl-keyword-color:     #7AAFFF;
  --md-code-hl-string-color:      #6DD670;
  --md-code-hl-comment-color:     #7A7A8E;
  --md-code-hl-function-color:    #C9A0FF;

  /* ·· Shadows (lighter in dark mode) ·· */
  --md-shadow-z1: 0 2px 4px rgba(0,0,0,0.3);
  --md-shadow-z2: 0 4px 12px rgba(0,0,0,0.4);
  --md-shadow-z3: 0 8px 24px rgba(0,0,0,0.5);
}
```

### 2.2 How to Generate Your Colour Scale

Your corporate CSS likely defines a handful of hex values. Material needs a full scale. Use this process:

1. Take your primary brand colour (e.g. `#1B3A6B`).
2. Go to [Material Design 3 Theme Builder](https://m3.material.io/theme-builder) or [Coolors Contrast Checker](https://coolors.co/contrast-checker).
3. Generate a palette with accessible contrast ratios (WCAG AA minimum: 4.5:1 for text, 3:1 for large text).
4. Map the generated values onto the tokens above.

Minimum colours you need from your corporate palette:

| Role | Token | Typical Usage |
|---|---|---|
| Primary | `--md-primary-fg-color` | Header, nav tabs, active indicators |
| Primary Light | `--md-primary-fg-color--light` | Hover states, lighter accents |
| Primary Dark | `--md-primary-fg-color--dark` | Pressed states, deep backgrounds |
| Accent | `--md-accent-fg-color` | Links, buttons, interactive elements |
| Text Primary | `--md-default-fg-color` | Body text |
| Text Secondary | `--md-default-fg-color--light` | Captions, metadata |
| Background | `--md-default-bg-color` | Page background |
| Surface | `--md-default-bg-color--light` | Cards, sidebar |

---

## Step 3 — Corporate Font Loading

### 3.1 Self-Hosted Fonts (recommended for corporate environments)

Place font files in `docs/assets/fonts/` and reference them in your CSS:

```css
/* docs/assets/stylesheets/overrides.css — add at the top */

@font-face {
  font-family: "Corporate Sans";
  src: url("../fonts/CorporateSans-Regular.woff2") format("woff2"),
       url("../fonts/CorporateSans-Regular.woff") format("woff");
  font-weight: 400;
  font-style: normal;
  font-display: swap;
}

@font-face {
  font-family: "Corporate Sans";
  src: url("../fonts/CorporateSans-Medium.woff2") format("woff2");
  font-weight: 500;
  font-style: normal;
  font-display: swap;
}

@font-face {
  font-family: "Corporate Sans";
  src: url("../fonts/CorporateSans-Bold.woff2") format("woff2");
  font-weight: 700;
  font-style: normal;
  font-display: swap;
}

@font-face {
  font-family: "Corporate Mono";
  src: url("../fonts/CorporateMono-Regular.woff2") format("woff2");
  font-weight: 400;
  font-style: normal;
  font-display: swap;
}

:root {
  --md-text-font: "Corporate Sans", -apple-system, BlinkMacSystemFont, sans-serif;
  --md-code-font: "Corporate Mono", ui-monospace, monospace;
}
```

### 3.2 Disable Google Fonts

By default, Material loads fonts from Google Fonts. To disable this (important for corporate privacy/compliance):

```yaml
# mkdocs.yml
theme:
  font: false    # Disables Google Fonts entirely
```

This ensures all font loading comes from your self-hosted files.

---

## Step 4 — Logo, Favicon & Icons

### 4.1 mkdocs.yml Configuration

```yaml
theme:
  name: material
  logo: assets/images/logo.svg          # Header logo
  favicon: assets/images/favicon.png    # Browser tab icon
  icon:
    repo: fontawesome/brands/bitbucket  # Repository icon
    edit: material/pencil
    view: material/eye
    admonition:
      note: material/information
      tip: material/lightbulb
      warning: material/alert
      danger: material/fire
```

### 4.2 Dark-Mode Logo Switching

If your corporate logo needs a different version for dark mode, override the logo partial:

```html
<!-- overrides/partials/logo.html -->
{% if config.theme.logo %}
  <img
    src="{{ config.theme.logo | url }}"
    alt="{{ config.site_name }}"
    class="md-logo__image md-logo__image--light"
  />
  <img
    src="{{ 'assets/images/logo-dark.svg' | url }}"
    alt="{{ config.site_name }}"
    class="md-logo__image md-logo__image--dark"
  />
{% else %}
  {% include ".icons/" ~ config.theme.icon.logo ~ ".svg" %}
{% endif %}
```

Add corresponding CSS:

```css
/* docs/assets/stylesheets/components.css */

/* Light mode: show light logo, hide dark logo */
[data-md-color-scheme="default"] .md-logo__image--dark  { display: none; }
[data-md-color-scheme="default"] .md-logo__image--light { display: inline; }

/* Dark mode: show dark logo, hide light logo */
[data-md-color-scheme="slate"] .md-logo__image--light { display: none; }
[data-md-color-scheme="slate"] .md-logo__image--dark  { display: inline; }

/* Logo sizing */
.md-logo__image {
  height: 1.6rem;
  width: auto;
}
```

---

## Step 5 — Custom Component Styles

Create `docs/assets/stylesheets/components.css` for deeper branding of specific UI elements:

```css
/* =================================================================
   docs/assets/stylesheets/components.css
   Corporate Component Overrides
   ================================================================= */

/* ── Header / Navigation Bar ── */
.md-header {
  background: linear-gradient(135deg,
    var(--md-primary-fg-color--dark) 0%,
    var(--md-primary-fg-color) 100%
  );
  box-shadow: var(--md-shadow-z2);
}

.md-header__title {
  font-weight: 600;
  letter-spacing: 0.02em;
}

/* ── Tabs (top-level navigation) ── */
.md-tabs {
  background-color: var(--md-primary-fg-color--dark);
  border-bottom: 2px solid var(--md-accent-fg-color);
}

.md-tabs__link--active {
  border-bottom: 2px solid var(--md-accent-fg-color);
  font-weight: 600;
}

/* ── Sidebar ── */
.md-sidebar {
  border-right: 1px solid var(--md-default-fg-color--lightest);
}

.md-nav__link--active {
  color: var(--md-accent-fg-color);
  font-weight: 600;
  border-left: 3px solid var(--md-accent-fg-color);
  padding-left: calc(0.6rem - 3px);
}

/* ── Search Bar ── */
.md-search__input {
  background-color: var(--md-primary-fg-color--light);
  border-radius: 8px;
  color: var(--md-primary-bg-color);
}

.md-search__input::placeholder {
  color: var(--md-primary-bg-color--light);
}

[data-md-color-scheme="slate"] .md-search__input {
  background-color: var(--md-default-bg-color--lighter);
}

/* ── Content Area ── */
.md-typeset h1 {
  color: var(--md-primary-fg-color);
  font-weight: 700;
  border-bottom: 2px solid var(--md-accent-fg-color);
  padding-bottom: 0.4rem;
}

.md-typeset h2 {
  color: var(--md-primary-fg-color--light);
  font-weight: 600;
}

.md-typeset a {
  color: var(--md-accent-fg-color);
  text-decoration: none;
  border-bottom: 1px solid transparent;
  transition: border-color 0.2s ease;
}

.md-typeset a:hover {
  border-bottom-color: var(--md-accent-fg-color);
}

/* ── Admonitions (branded callouts) ── */
/* Override the default admonition accent colours to match brand */
.md-typeset .admonition.note,
.md-typeset details.note {
  border-color: var(--md-primary-fg-color);
}
.md-typeset .note > .admonition-title,
.md-typeset .note > summary {
  background-color: var(--md-primary-fg-color--light);
  color: var(--md-primary-bg-color);
}

.md-typeset .admonition.tip,
.md-typeset details.tip {
  border-color: var(--md-accent-fg-color);
}
.md-typeset .tip > .admonition-title,
.md-typeset .tip > summary {
  background-color: var(--md-accent-fg-color);
  color: #1A1A2E;
}

/* ── Buttons ── */
.md-typeset .md-button--primary {
  background-color: var(--md-primary-fg-color);
  border-color: var(--md-primary-fg-color);
  color: var(--md-primary-bg-color);
  border-radius: 6px;
  font-weight: 600;
  text-transform: none;
  letter-spacing: 0.01em;
  transition: all 0.2s ease;
}

.md-typeset .md-button--primary:hover {
  background-color: var(--md-primary-fg-color--dark);
  box-shadow: var(--md-shadow-z2);
}

/* ── Tables ── */
.md-typeset table:not([class]) {
  border-collapse: collapse;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: var(--md-shadow-z1);
}

.md-typeset table:not([class]) thead {
  background-color: var(--md-primary-fg-color);
  color: var(--md-primary-bg-color);
}

.md-typeset table:not([class]) thead th {
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.75rem;
  letter-spacing: 0.05em;
  padding: 0.8rem 1rem;
}

.md-typeset table:not([class]) tbody tr:nth-child(even) {
  background-color: var(--md-default-bg-color--light);
}

/* ── Code Blocks ── */
.md-typeset pre > code {
  border-radius: 8px;
  border: 1px solid var(--md-default-fg-color--lightest);
}

.md-typeset code {
  border-radius: 4px;
  padding: 0.1em 0.4em;
  font-size: 0.85em;
}

/* ── Footer ── */
.md-footer {
  border-top: 3px solid var(--md-accent-fg-color);
}

/* ── Back to Top Button ── */
.md-top {
  background-color: var(--md-primary-fg-color);
  color: var(--md-primary-bg-color);
  border-radius: 50%;
}

.md-top:hover {
  background-color: var(--md-accent-fg-color);
}

/* ── Content Tabs ── */
.md-typeset .tabbed-labels > label.tabbed-alternate--active {
  color: var(--md-accent-fg-color);
  border-color: var(--md-accent-fg-color);
}

/* ── Cookie Consent Banner ── */
.md-consent {
  background-color: var(--md-primary-fg-color--dark);
  color: var(--md-primary-bg-color);
}

.md-consent__button--accept {
  background-color: var(--md-accent-fg-color);
  color: #1A1A2E;
}
```

---

## Step 6 — Template Overrides

### 6.1 Custom Header with Corporate Banner

```html
<!-- overrides/main.html -->
{% extends "base.html" %}

{% block announce %}
  <style>
    .corporate-banner {
      background: var(--md-primary-fg-color--dark);
      color: var(--md-primary-bg-color);
      font-size: 0.75rem;
      padding: 0.3rem 1rem;
      text-align: center;
      font-weight: 500;
      letter-spacing: 0.03em;
    }
    .corporate-banner a {
      color: var(--md-accent-fg-color);
      text-decoration: underline;
    }
  </style>
  <div class="corporate-banner">
    Internal Documentation — Confidential &amp; Proprietary
  </div>
{% endblock %}

{% block content %}
  {{ super() }}
{% endblock %}
```

### 6.2 Custom Footer

```html
<!-- overrides/partials/footer.html -->
<footer class="md-footer">
  <!-- Navigation (previous/next) -->
  {% if page.previous_page or page.next_page %}
    <nav class="md-footer__inner md-grid" aria-label="Footer">
      {% if page.previous_page %}
        <a href="{{ page.previous_page.url | url }}"
           class="md-footer__link md-footer__link--prev">
          <div class="md-footer__button md-icon">
            {% include ".icons/material/arrow-left.svg" %}
          </div>
          <div class="md-footer__title">
            <span class="md-footer__direction">Previous</span>
            {{ page.previous_page.title }}
          </div>
        </a>
      {% endif %}
      {% if page.next_page %}
        <a href="{{ page.next_page.url | url }}"
           class="md-footer__link md-footer__link--next">
          <div class="md-footer__title">
            <span class="md-footer__direction">Next</span>
            {{ page.next_page.title }}
          </div>
          <div class="md-footer__button md-icon">
            {% include ".icons/material/arrow-right.svg" %}
          </div>
        </a>
      {% endif %}
    </nav>
  {% endif %}

  <!-- Corporate Footer -->
  <div class="md-footer-meta md-typeset">
    <div class="md-footer-meta__inner md-grid">
      <div style="flex: 1;">
        <div style="font-weight: 600; margin-bottom: 0.3rem;">
          Your Company Name
        </div>
        <div style="font-size: 0.75rem; opacity: 0.7;">
          &copy; {{ build_date_utc.strftime('%Y') }} Your Company.
          All rights reserved. 
          Confidential and proprietary.
        </div>
      </div>
      <div style="text-align: right; font-size: 0.8rem;">
        <a href="https://your-intranet.com/legal">Legal</a> · 
        <a href="https://your-intranet.com/privacy">Privacy</a> · 
        <a href="https://your-intranet.com/support">Support</a>
      </div>
    </div>
  </div>
</footer>
```

### 6.3 Custom 404 Page

Create `docs/404.md`:

```markdown
---
template: 404.html
title: Page Not Found
---

# Page Not Found

The page you're looking for doesn't exist or has been moved.

[Return to Home](/)
```

---

## Step 7 — Wire Everything in mkdocs.yml

Bring all the pieces together:

```yaml
# mkdocs.yml — Theme & Branding Section

theme:
  name: material
  custom_dir: overrides
  language: en
  font: false                                # Disable Google Fonts (self-hosted)
  logo: assets/images/logo.svg
  favicon: assets/images/favicon.png
  
  features:
    - navigation.instant
    - navigation.instant.progress
    - navigation.tracking
    - navigation.tabs
    - navigation.tabs.sticky
    - navigation.sections
    - navigation.indexes
    - navigation.top
    - search.suggest
    - search.highlight
    - search.share
    - content.code.copy
    - content.code.annotate
    - content.tabs.link
    - content.tooltips
    - content.action.edit
    - header.autohide
    - announce.dismiss
  
  palette:
    - media: "(prefers-color-scheme: light)"
      scheme: default
      toggle:
        icon: material/brightness-7
        name: Switch to dark mode
    - media: "(prefers-color-scheme: dark)"
      scheme: slate
      toggle:
        icon: material/brightness-4
        name: Switch to light mode

  # Note: primary/accent are NOT set here because we control them
  # entirely via CSS custom properties in overrides.css.
  # Setting them in YAML would inject Material's built-in colour
  # classes which would conflict with our tokens.

# ── CSS Loading Order (ORDER MATTERS) ──
extra_css:
  - assets/stylesheets/corporate.css          # Your existing corporate CSS
  - assets/stylesheets/overrides.css          # Material token overrides
  - assets/stylesheets/components.css         # Component-level styles
```

> **Loading order is critical.** CSS files are injected in array order. `corporate.css` loads first as the base, `overrides.css` maps corporate values to Material tokens, and `components.css` applies targeted component styles last.

---

## Step 8 — Integrating Your Existing Corporate CSS

Your existing `corporate.css` likely defines variables, classes, and rules that don't directly align with Material's tokens. Here is the bridging strategy:

### 8.1 Map Corporate Variables to Material Tokens

If your corporate CSS uses its own custom properties:

```css
/* Your existing corporate.css might define: */
:root {
  --corp-primary:      #1B3A6B;
  --corp-secondary:    #E8A317;
  --corp-bg:           #FFFFFF;
  --corp-text:         #1A1A2E;
  --corp-text-muted:   #555570;
  --corp-border:       #DDDDE5;
  --corp-font-family:  "Corporate Sans", sans-serif;
  --corp-font-mono:    "Corporate Mono", monospace;
}
```

Then in `overrides.css`, bridge them:

```css
/* overrides.css — bridge corporate tokens to Material tokens */

:root {
  --md-primary-fg-color:          var(--corp-primary);
  --md-primary-fg-color--light:   color-mix(in srgb, var(--corp-primary) 70%, white);
  --md-primary-fg-color--dark:    color-mix(in srgb, var(--corp-primary) 70%, black);
  --md-accent-fg-color:           var(--corp-secondary);
  --md-default-fg-color:          var(--corp-text);
  --md-default-fg-color--light:   var(--corp-text-muted);
  --md-default-fg-color--lightest:var(--corp-border);
  --md-default-bg-color:          var(--corp-bg);
  --md-text-font:                 var(--corp-font-family);
  --md-code-font:                 var(--corp-font-mono);
  --md-footer-bg-color:           var(--corp-primary);
}
```

This approach means you maintain a single source of truth in `corporate.css` and never duplicate colour values.

### 8.2 Handle Conflicts

Your corporate CSS may include global rules that clash with Material's styles. Common issues and fixes:

| Conflict | Symptom | Fix |
|---|---|---|
| Global `* { box-sizing }` | Layout breaks | Material already sets this; remove from corporate CSS or scope it |
| Global `a { color }` | Links don't match theme | Scope to `.md-typeset a` or remove the global rule |
| Global `body { font-family }` | Font flickers | Remove; use `--md-text-font` token instead |
| Global `h1-h6` styles | Heading sizes wrong | Scope to `.md-typeset h1` or let Material's tokens handle it |
| Reset stylesheets | Everything breaks | Remove the reset; Material includes its own |

If you cannot modify `corporate.css` (it is shared with other projects), wrap conflicting rules with a scope:

```css
/* Prevent corporate global rules from affecting Material */
.corporate-app h1 { /* ... */ }          /* Scoped — won't affect docs */
.md-typeset h1 { /* Material's rules */ } /* Only affects docs content */
```

---

## Step 9 — Custom Admonition Types (Branded Callouts)

Define organisation-specific callout types that match your brand:

```css
/* docs/assets/stylesheets/components.css — add these */

/* Corporate Policy callout */
:root {
  --md-admonition-icon--policy:
    url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4z"/></svg>');
}

.md-typeset .admonition.policy,
.md-typeset details.policy {
  border-color: var(--md-primary-fg-color);
}

.md-typeset .policy > .admonition-title,
.md-typeset .policy > summary {
  background-color: rgba(27, 58, 107, 0.1);
}

.md-typeset .policy > .admonition-title::before,
.md-typeset .policy > summary::before {
  -webkit-mask-image: var(--md-admonition-icon--policy);
  mask-image: var(--md-admonition-icon--policy);
  background-color: var(--md-primary-fg-color);
}

/* Decision Record callout */
:root {
  --md-admonition-icon--decision:
    url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M18 16v-5c0-3.07-1.64-5.64-4.5-6.32V4c0-.83-.67-1.5-1.5-1.5s-1.5.67-1.5 1.5v.68C7.63 5.36 6 7.92 6 11v5l-2 2v1h16v-1l-2-2zm-6 6c1.1 0 2-.9 2-2h-4c0 1.1.89 2 2 2z"/></svg>');
}

.md-typeset .admonition.decision,
.md-typeset details.decision {
  border-color: var(--md-accent-fg-color);
}

.md-typeset .decision > .admonition-title,
.md-typeset .decision > summary {
  background-color: rgba(232, 163, 23, 0.1);
}

.md-typeset .decision > .admonition-title::before,
.md-typeset .decision > summary::before {
  -webkit-mask-image: var(--md-admonition-icon--decision);
  mask-image: var(--md-admonition-icon--decision);
  background-color: var(--md-accent-fg-color);
}
```

Usage in markdown:

```markdown
!!! policy "Data Retention Policy"
    All customer data must be retained for a minimum of 7 years.

??? decision "ADR-042: Chose PostgreSQL over DynamoDB"
    We selected PostgreSQL for its relational query capabilities
    and our team's existing expertise.
```

---

## Step 10 — Verification Checklist

After applying all customisations, verify every surface:

```
□  Header bar uses corporate primary colour
□  Logo renders correctly in light and dark modes
□  Favicon appears in browser tab
□  Navigation tabs use corporate styling
□  Sidebar active state shows accent colour
□  Search bar is styled and functional
□  Body text uses corporate font (inspect element → computed style)
□  Code blocks use corporate mono font
□  Headings h1–h4 use correct weights and colours
□  Links use accent colour with hover effect
□  Tables have branded header row
□  Admonitions (note, tip, warning, danger) are branded
□  Custom admonitions (policy, decision) render correctly
□  Dark mode toggle works and all tokens switch
□  Footer shows corporate copyright and links
□  Back-to-top button uses brand colours
□  Announcement banner appears at top
□  Buttons use corporate styling
□  Cookie consent banner (if enabled) is branded
□  404 page is branded
□  Print view is clean (Ctrl+P)
□  Mobile responsive — test at 375px, 768px, 1024px
□  Google Fonts are NOT loaded (check Network tab)
□  No FOUC (Flash of Unstyled Content) on page load
```

Run these commands to verify technical aspects:

```bash
# Build with strict mode to catch warnings
mkdocs build --strict

# Check for 404s and broken links
pip install linkchecker
linkchecker site/index.html

# Check that Google Fonts are not loaded
grep -r "fonts.googleapis" site/ && echo "WARNING: Google Fonts detected" || echo "OK: No Google Fonts"

# Check CSS load order in output
grep -n "stylesheet" site/index.html | head -20
```

---

## Step 11 — File Inventory Summary

Here is every file you need to create or modify, with its purpose:

| File | Purpose | Required? |
|---|---|---|
| `mkdocs.yml` | Central config — theme, plugins, CSS loading order | Yes |
| `docs/assets/stylesheets/corporate.css` | Your existing corporate CSS (source of truth) | Yes |
| `docs/assets/stylesheets/overrides.css` | Bridge corporate tokens → Material tokens | Yes |
| `docs/assets/stylesheets/components.css` | Targeted UI component branding | Recommended |
| `docs/assets/images/logo.svg` | Header logo | Yes |
| `docs/assets/images/logo-dark.svg` | Dark-mode logo variant | Optional |
| `docs/assets/images/favicon.png` | Browser tab icon | Yes |
| `docs/assets/fonts/*.woff2` | Self-hosted corporate fonts | If using custom fonts |
| `overrides/main.html` | Master template (banner, layout changes) | Optional |
| `overrides/partials/logo.html` | Dark/light logo switcher | Optional |
| `overrides/partials/footer.html` | Custom branded footer | Recommended |
| `docs/404.md` | Custom 404 page | Recommended |

---

*This guide assumes Material for MkDocs 9.5+. Token names and override paths are stable across minor versions but should be re-verified on major upgrades.*

# SEO Checklist — AIUtilities

Utility tool sites win on long-tail search volume. Each individual tool page is a landing page.
This checklist covers everything from technical SEO to per-page on-page work.

---

## 1. Technical SEO

### Crawlability & Indexing
- [ ] `robots.txt` live at `/robots.txt` — Disallow admin, allow everything else
- [ ] XML sitemap live at `/sitemap.xml` — auto-generated, submitted to Google Search Console
- [ ] Sitemap submitted to Bing Webmaster Tools
- [ ] All tool URLs use clean slugs: `/tools/<category>/<tool-slug>/`
- [ ] No `noindex` on tool pages (only on admin, auth, profile pages)
- [ ] Canonical tags on every page (`<link rel="canonical" href="...">`)
- [ ] No duplicate content — each tool page has unique title + description
- [ ] Pagination handled with `?page=` params only (no duplicate category pages)

### Site Speed (Core Web Vitals)
- [ ] Largest Contentful Paint (LCP) < 2.5s
- [ ] First Input Delay (FID) / Interaction to Next Paint (INP) < 200ms
- [ ] Cumulative Layout Shift (CLS) < 0.1
- [ ] No render-blocking JavaScript — HTMX and scripts loaded `defer`
- [ ] Tailwind loaded via CDN (acceptable for v1; switch to PurgeCSS build for v2)
- [ ] Images served in WebP format with explicit `width` + `height`
- [ ] Whitenoise compressed static files enabled (`CompressedManifestStaticFilesStorage`)
- [ ] Gzip / Brotli compression enabled on Nginx
- [ ] HTTP/2 enabled on Nginx

### Mobile & Accessibility
- [ ] `<meta name="viewport" content="width=device-width, initial-scale=1.0">` on all pages
- [ ] All tool forms usable on mobile (no horizontal scroll)
- [ ] Minimum touch target size 44×44px for buttons
- [ ] Colour contrast ratio ≥ 4.5:1 for body text
- [ ] All images have descriptive `alt` attributes
- [ ] Form inputs have associated `<label>` elements

### Structured Data (Schema.org)
- [ ] `SoftwareApplication` schema on every tool page
- [ ] `HowTo` schema on tools with step-by-step instructions
- [ ] `FAQPage` schema on tool pages with FAQ sections
- [ ] `BreadcrumbList` schema on category and tool pages
- [ ] `WebSite` schema with `SearchAction` on homepage (enables Google Sitelinks Search Box)
- [ ] `Organization` schema on homepage
- [ ] Validate all schema at https://validator.schema.org/

### HTTPS & Security Headers
- [ ] HTTPS enforced (HTTP redirects to HTTPS)
- [ ] `Strict-Transport-Security` header set
- [ ] `X-Content-Type-Options: nosniff`
- [ ] `X-Frame-Options: SAMEORIGIN`
- [ ] `Content-Security-Policy` header configured
- [ ] Django `SECURE_SSL_REDIRECT = True` in production

---

## 2. On-Page SEO — Per Tool Page

Every tool page at `/tools/<category>/<slug>/` must have all of the following:

### Title Tag
- [ ] Format: `{Tool Name} — Free Online {Tool Name} | AIUtilities`
- [ ] Length: 50–60 characters
- [ ] Contains primary keyword (the tool name) near the front
- [ ] Unique across all pages

### Meta Description
- [ ] 120–160 characters
- [ ] Contains primary keyword
- [ ] Includes a benefit/CTA ("Free, no signup required")
- [ ] Unique across all pages
- [ ] Written for click-through, not just keyword density

### H1
- [ ] Exactly one `<h1>` per page
- [ ] Matches (or closely matches) the title tag keyword
- [ ] Example: "Free Online Age Calculator"

### Heading Hierarchy
- [ ] `<h2>` used for main sections (How to Use, FAQ, Related Tools)
- [ ] `<h3>` used for sub-sections
- [ ] No skipped heading levels

### Content
- [ ] 150–300 words of body text describing what the tool does and how to use it
- [ ] "How to use" section with numbered steps
- [ ] FAQ section (3–5 questions) — drives `FAQPage` schema + featured snippets
- [ ] Related tools section linking to 3–5 similar tools (internal linking)

### URL
- [ ] Clean slug: `/tools/age-calculator/` or `/tools/calculators/age-calculator/`
- [ ] Lowercase, hyphen-separated, no underscores
- [ ] Primary keyword in URL
- [ ] Stable — never change a tool URL once indexed

### Images
- [ ] Screenshot or illustration of the tool output where relevant
- [ ] Descriptive file name: `age-calculator-result.webp`
- [ ] Descriptive `alt` text

### Open Graph + Twitter Card
- [ ] `og:title`, `og:description`, `og:image`, `og:url` on every page
- [ ] `twitter:card`, `twitter:title`, `twitter:description`
- [ ] OG image: 1200×630px, shows tool name and category

---

## 3. Category Pages (`/tools/<category>/`)

- [ ] H1: "Free Online {Category Name}" (e.g. "Free Online Calculators")
- [ ] 100–200 words describing the category
- [ ] List of all tools in the category with descriptions (for internal PageRank flow)
- [ ] Breadcrumb: Home › Tools › {Category}
- [ ] `BreadcrumbList` structured data
- [ ] Pagination if category has > 30 tools (`rel="next"` / `rel="prev"`)

---

## 4. Homepage

- [ ] H1: "Free Online Tools — Calculators, Converters, PDF, Image & More"
- [ ] Brief (50–100 word) intro paragraph with target keywords
- [ ] Category grid visible above the fold
- [ ] `SearchAction` schema enabling Google search box in SERPs
- [ ] Internal links to all category pages
- [ ] Internal links to top 10 most popular tool pages
- [ ] `WebSite` + `Organization` structured data

---

## 5. Internal Linking Strategy

- [ ] Every tool page links to 3–5 related tools ("You might also like")
- [ ] Every tool page links back to its category page (breadcrumb)
- [ ] Every category page links to all tools in that category
- [ ] Homepage links to all category pages
- [ ] Footer contains links to top 12 categories
- [ ] Anchor text uses descriptive keywords, not "click here"
- [ ] No orphaned pages (every tool reachable within 3 clicks from homepage)

---

## 6. Content Marketing (Long-Tail Traffic)

Each tool category can support blog content:

- [ ] "How to calculate X" articles targeting informational queries
- [ ] "X vs Y" comparison articles
- [ ] "Best free X tools" listicles (own the SERP for your own category)
- [ ] Tutorial videos embedded on tool pages

Priority topics (by search volume):
1. How to compress a PDF
2. How to calculate BMI
3. How to convert HEIC to JPG
4. How to generate a QR code
5. Free JSON formatter online

---

## 7. Google Search Console

- [ ] Property verified (HTML tag or DNS method)
- [ ] Sitemap submitted
- [ ] Core Web Vitals report reviewed
- [ ] Coverage report checked for crawl errors
- [ ] Rich Results Test run on all schema types
- [ ] Performance report set up to track per-tool impressions and clicks
- [ ] URL Inspection used to request indexing for new tool pages

---

## 8. Bing & Other Search Engines

- [ ] Bing Webmaster Tools property verified
- [ ] Sitemap submitted to Bing
- [ ] IndexNow integration enabled (Django plugin or manual pings on new tools)

---

## 9. Per-Launch Checklist (When Adding a New Tool)

Before marking a tool as live:

- [ ] Unique `<title>` (50–60 chars)
- [ ] Unique meta description (120–160 chars)
- [ ] H1 set
- [ ] How to use section written
- [ ] FAQ section (3+ questions)
- [ ] Related tools linked
- [ ] `SoftwareApplication` schema added
- [ ] Breadcrumb links work
- [ ] URL added to sitemap (auto via registry)
- [ ] OG image present
- [ ] Mobile tested (Chrome DevTools)
- [ ] Page speed checked (Lighthouse score ≥ 90)
- [ ] URL Inspection → Request Indexing in GSC

---

## 10. Tracking & Analytics

- [ ] Google Analytics 4 installed (via `{% block extra_head %}`)
- [ ] GSC + GA4 linked
- [ ] Conversion event: tool_used (fire on tool form submit)
- [ ] Custom dimension: tool_name, category_name
- [ ] Search Console data imported into GA4
- [ ] Heatmap tool (e.g. Microsoft Clarity — free) on top 10 tool pages

---

## Priority Order for Maximum Impact

1. Fix all technical issues (canonicals, robots.txt, sitemap) — day 1
2. Add structured data to all existing tool pages — week 1
3. Write unique meta descriptions for all tool pages — week 1-2
4. Add FAQ + How To sections to top 50 tools — month 1
5. Internal linking audit — month 1
6. Core Web Vitals optimisation — month 2
7. Content marketing (blog) — month 2+

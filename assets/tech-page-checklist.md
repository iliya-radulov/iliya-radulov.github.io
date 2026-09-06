# Tech page checklist

Quick reference for writing a new detail page. Full template with inline
comments: `tech-page-template.html`.

## Non-negotiable
- [ ] `abstract-box` right after the subtitle, before the first `<h2>` — Goal/Result, or Key Takeaway if there's no clear before/after
- [ ] Footer cross-link line — "Continues from... / Continued in..." for session logs, "Part of... / Referenced by..." for reference pages
- [ ] Uses `assets/style.css` only — no page-specific `<style>` blocks (that's a Tier-1 hub decision, made deliberately, not a default)
- [ ] Photos use `class="site-photo"` directly on `<img>` — no custom wrapper classes

## Strongly recommended
- [ ] Real numbers in tables, not prose paraphrases ("fast" → the actual ms/Hz/% figure)
- [ ] Actual commands run go in `<pre><code>`, verbatim — not reconstructed from memory
- [ ] At least one honest "what didn't work" note if anything didn't — a page with only successes reads as incomplete, not impressive
- [ ] Eyebrow uses an existing convention (see template) rather than a new one-off label

## When to reach for a table instead of a bullet list
- Comparing the same metric across multiple things (Pi 4 vs Mac, arm 1 vs arm 2)
- A limitations/status list with more than ~3 items
- Anything with a natural ✅/⚠️/☐ status per row

## When a page should NOT use this template
If the page is a **hub page** (project landing page, `index.html`-level) rather
than a detail/log page, it's a candidate for its own bespoke design instead —
see the GoExplore wrap-up or alloy-lab Stage 2 pages for that pattern. This
template is for the tech-detail pages underneath a hub, where consistency is
the point.

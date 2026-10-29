#!/usr/bin/env python3
"""
Build script for timurrakhmatullin.com
Reads data/*.json files and regenerates index.html from template.
"""

import json
import re
from pathlib import Path
from html import escape

SITE_DIR = Path(__file__).parent
DATA_DIR = SITE_DIR / "data"
INDEX_PATH = SITE_DIR / "index.html"


def load_json(name: str):
    path = DATA_DIR / name
    if not path.exists():
        return [] if name != "metrics.json" else {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_metrics_html(metrics: dict) -> str:
    items = [
        (metrics.get("users_served", "22M+"), "Users Served"),
        (metrics.get("citations", "31+"), "Citations"),
        (metrics.get("merged_prs", "20"), "Merged PRs"),
        (metrics.get("publications", "10+"), "Publications"),
        (metrics.get("oss_projects", "5"), "OSS Projects"),
    ]
    parts = []
    for val, label in items:
        parts.append(
            f'  <div class="metric" role="listitem">\n'
            f'    <div class="metric__value">{escape(str(val))}</div>\n'
            f'    <div class="metric__label">{escape(label)}</div>\n'
            f'  </div>'
        )
    return (
        '<div class="metrics" role="list" aria-label="Key metrics">\n'
        + "\n".join(parts)
        + "\n</div>"
    )


def build_projects_html(projects: list) -> str:
    parts = []
    for p in projects:
        tags_html = ""
        if p.get("accent_tag"):
            tags_html += f'      <span class="tag tag--accent">{escape(p["accent_tag"])}</span>\n'
        for t in p.get("tags", []):
            tags_html += f'      <span class="tag">{escape(t)}</span>\n'

        parts.append(
            f'  <div class="project">\n'
            f'    <div class="project__header">\n'
            f'      <h3 class="project__name"><a href="{escape(p["url"])}" target="_blank" rel="noopener">{escape(p["name"])}</a></h3>\n'
            f'      <span class="project__lang">{escape(p["lang"])}</span>\n'
            f'    </div>\n'
            f'    <p class="project__desc">\n'
            f'      {escape(p["desc"])}\n'
            f'    </p>\n'
            f'    <div class="project__stats">\n'
            f'{tags_html}'
            f'    </div>\n'
            f'  </div>'
        )
    return "\n\n".join(parts)


def build_contributions_html(contribs: list) -> str:
    total = sum(c.get("merged_prs", 0) for c in contribs)
    rows = []
    for c in sorted(contribs, key=lambda x: x.get("merged_prs", 0), reverse=True):
        rows.append(
            f'        <tr>\n'
            f'          <td><a href="{escape(c["url"])}" target="_blank" rel="noopener">{escape(c["project"])}</a></td>\n'
            f'          <td>{escape(c["area"])}</td>\n'
            f'          <td style="text-align:right" class="contrib-count">{c["merged_prs"]}</td>\n'
            f'        </tr>'
        )
    pending_note = ""
    return (
        f'  <div class="section__label">Open-Source Contributions</div>\n'
        f'  <h2 class="section__heading">{total} Merged Pull Requests to Major Projects</h2>\n'
        f'\n'
        f'  <div class="overflow-x">\n'
        f'    <table class="contrib-table">\n'
        f'      <thead>\n'
        f'        <tr>\n'
        f'          <th>Project</th>\n'
        f'          <th>Area</th>\n'
        f'          <th style="text-align:right">Merged PRs</th>\n'
        f'        </tr>\n'
        f'      </thead>\n'
        f'      <tbody>\n'
        + "\n".join(rows)
        + "\n"
        f'      </tbody>\n'
        f'    </table>\n'
        f'  </div>'
    )


def build_publications_html(pubs: list) -> str:
    total_cites = sum(p.get("citations", 0) for p in pubs)
    parts = []
    for p in sorted(pubs, key=lambda x: (-x.get("citations", 0), x.get("year", ""))):
        cite_span = ""
        if p.get("citations", 0) > 0:
            cite_span = f'<span class="pub__cite">{p["citations"]} citations</span>'

        title_html = escape(p["title"])
        if p.get("url"):
            title_html = f'<a href="{escape(p["url"])}" target="_blank" rel="noopener">{title_html}</a>'

        venue_parts = [p.get("year", "")]
        if p.get("venue"):
            venue_parts.append(f' · {escape(p["venue"])}')

        parts.append(
            f'  <div class="pub">\n'
            f'    <div class="pub__title">{title_html}{cite_span}</div>\n'
            f'    <div class="pub__venue">{"".join(venue_parts)}</div>\n'
            f'  </div>'
        )
    scholar_link = (
        '  <p style="font-size: 0.85rem; margin-top: 1rem;">\n'
        '    <a href="https://scholar.google.com/citations?user=d0nzx0oAAAAJ" target="_blank" rel="noopener" '
        'style="color: var(--accent); text-decoration: none; font-weight: 500;">'
        "View full publication list on Google Scholar →</a>\n"
        "  </p>"
    )
    return (
        f'  <div class="section__label">Research & Publications</div>\n'
        f'  <h2 class="section__heading">Peer-Reviewed Papers — {total_cites}+ Citations</h2>\n\n'
        + "\n\n".join(parts)
        + "\n\n"
        + scholar_link
    )


def build_award_list(items: list, label: str, heading: str) -> str:
    parts = []
    for item in items:
        title = escape(item["title"])
        if item.get("url"):
            title = f'<a href="{escape(item["url"])}" target="_blank" rel="noopener" class="inline-link">{title}</a>'
        note_html = ""
        if item.get("note"):
            note_html = f'\n      <div class="award__note">{escape(item["note"])}</div>'
        parts.append(
            f'  <div class="award">\n'
            f'    <span class="award__year">{escape(str(item["year"]))}</span>\n'
            f'    <div>\n'
            f'      <div class="award__text"><strong>{title}</strong></div>'
            f'{note_html}\n'
            f'    </div>\n'
            f'  </div>'
        )
    return (
        f'  <div class="section__label">{escape(label)}</div>\n'
        f'  <h2 class="section__heading">{escape(heading)}</h2>\n\n'
        + "\n".join(parts)
    )


def build_media_html(media: list) -> str:
    interviews = [m for m in media if m.get("type") in ("interview", "expert_quote", "mention")]
    award_cov = [m for m in media if m.get("type") == "award_coverage"]

    parts = [
        '  <div class="section__label">Media Coverage</div>\n'
        '  <h2 class="section__heading">Published Material About Timur Rakhmatullin</h2>\n'
        '  <p style="margin-bottom: 1rem;">\n'
        "    Interviews and articles by third-party journalists in professional and major media outlets.\n"
        "  </p>\n"
    ]

    for m in interviews:
        title_html = escape(m["title"])
        if m.get("url"):
            title_html = f'<a href="{escape(m["url"])}" target="_blank" rel="noopener">{title_html}</a>'
        venue = escape(m.get("venue", ""))
        date = escape(m.get("date", ""))
        author = f" · Author: {escape(m['author'])}" if m.get("author") else ""
        parts.append(
            f'  <div class="pub">\n'
            f'    <div class="pub__title">{title_html}</div>\n'
            f'    <div class="pub__venue">{venue} · {date}{author}</div>\n'
            f'  </div>\n'
        )

    if award_cov:
        parts.append('  <h3 class="media-sub">Award Coverage</h3>\n')
        parts.append(
            '  <p style="margin-bottom: 0.75rem;">\n'
            "    Articles about award recognition in major media outlets.\n"
            "  </p>\n"
        )
        for m in award_cov:
            title_html = escape(m["title"])
            if m.get("url"):
                title_html = f'<a href="{escape(m["url"])}" target="_blank" rel="noopener">{title_html}</a>'
            if m.get("coverage_links"):
                links = " · ".join(
                    f'<a href="{escape(cl["url"])}" target="_blank" rel="noopener">{escape(cl["name"])}</a>'
                    for cl in m["coverage_links"]
                )
                venue_text = f"Covered by: {links}"
                if m.get("date"):
                    venue_text += f" · {escape(m['date'])}"
            else:
                venue_text = escape(m.get("venue", ""))
            parts.append(
                f'  <div class="pub">\n'
                f'    <div class="pub__title">{title_html}</div>\n'
                f'    <div class="pub__venue">{venue_text}</div>\n'
                f'  </div>\n'
            )

    return "\n".join(parts)


def rebuild():
    html = INDEX_PATH.read_text(encoding="utf-8")

    metrics = load_json("metrics.json")
    judging = load_json("judging.json")
    media = load_json("media.json")
    publications = load_json("publications.json")
    contributions = load_json("contributions.json")
    projects = load_json("projects.json")
    awards = load_json("awards.json")
    memberships = load_json("memberships.json")

    # Replace KEY METRICS section
    metrics_html = build_metrics_html(metrics)
    html = re.sub(
        r'<div class="metrics".*?</div>\s*</div>\s*</div>\s*</div>\s*</div>\s*</div>',
        metrics_html,
        html,
        flags=re.DOTALL,
    )

    # Replace OPEN-SOURCE PROJECTS section content
    projects_html = build_projects_html(projects)
    html = re.sub(
        r'(<!-- OPEN-SOURCE PROJECTS -->\s*<section class="section">\s*<div class="section__label">Open-Source Projects</div>\s*<h2 class="section__heading">.*?</h2>)\s*(.*?)(</section>\s*\n\s*<!-- OPEN-SOURCE CONTRIBUTIONS -->)',
        lambda m: m.group(1) + "\n\n" + projects_html + "\n" + m.group(3),
        html,
        flags=re.DOTALL,
    )

    # Replace CONTRIBUTIONS section content
    contribs_html = build_contributions_html(contributions)
    html = re.sub(
        r'(<!-- OPEN-SOURCE CONTRIBUTIONS -->\s*<section class="section">)\s*.*?(</section>\s*\n\s*<!-- PUBLICATIONS -->)',
        lambda m: m.group(1) + "\n" + contribs_html + "\n" + m.group(2),
        html,
        flags=re.DOTALL,
    )

    # Replace PUBLICATIONS section content
    pubs_html = build_publications_html(publications)
    html = re.sub(
        r'(<!-- PUBLICATIONS -->\s*<section class="section">)\s*.*?(</section>\s*\n\s*<!-- AWARDS)',
        lambda m: m.group(1) + "\n" + pubs_html + "\n" + m.group(2),
        html,
        flags=re.DOTALL,
    )

    # Replace AWARDS section content
    awards_html = build_award_list(awards, "Awards", "Industry Awards")
    html = re.sub(
        r'(<!-- AWARDS & RECOGNITION -->\s*<section class="section">)\s*.*?(</section>\s*\n\s*<!-- JUDGING)',
        lambda m: m.group(1) + "\n" + awards_html + "\n" + m.group(2),
        html,
        flags=re.DOTALL,
    )

    # Replace JUDGING section content
    judging_html = build_award_list(judging, "Judging", "Judge & Expert Council Member")
    html = re.sub(
        r'(<!-- JUDGING -->\s*<section class="section">)\s*.*?(</section>\s*\n\s*<!-- MEMBERSHIPS)',
        lambda m: m.group(1) + "\n" + judging_html + "\n" + m.group(2),
        html,
        flags=re.DOTALL,
    )

    # Replace MEMBERSHIPS section content
    memb_html = build_award_list(
        memberships, "Professional Memberships", "Associations Requiring Outstanding Achievements"
    )
    html = re.sub(
        r'(<!-- MEMBERSHIPS -->\s*<section class="section">)\s*.*?(</section>\s*\n\s*<!-- SPEAKING)',
        lambda m: m.group(1) + "\n" + memb_html + "\n" + m.group(2),
        html,
        flags=re.DOTALL,
    )

    # Replace MEDIA section content
    media_html = build_media_html(media)
    html = re.sub(
        r'(<!-- MEDIA COVERAGE -->\s*<section class="section">)\s*.*?(</section>\s*\n\s*<!-- FOOTER)',
        lambda m: m.group(1) + "\n" + media_html + "\n" + m.group(2),
        html,
        flags=re.DOTALL,
    )

    INDEX_PATH.write_text(html, encoding="utf-8")
    print(f"Rebuilt {INDEX_PATH}")
    print(f"  Metrics: {metrics.get('merged_prs', '?')} PRs, {metrics.get('citations', '?')} citations")
    print(f"  {len(projects)} projects, {len(contributions)} contrib targets, {sum(c['merged_prs'] for c in contributions)} total merged")
    print(f"  {len(publications)} publications, {len(judging)} judging instances")
    print(f"  {len(media)} media entries, {len(awards)} awards, {len(memberships)} memberships")


if __name__ == "__main__":
    rebuild()

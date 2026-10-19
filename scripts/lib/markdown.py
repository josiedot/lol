"""Render blog-post markdown bodies to HTML.

Output is consumed via `{{ post.body_html | safe }}` in the post template,
which bypasses jinja autoescape. Inputs are author-controlled markdown
files under blog/ (no user-submitted content), so raw HTML in posts is
intentional. Do not feed untrusted markdown through this renderer without
adding a sanitizer (e.g. bleach).
"""
from __future__ import annotations

from xml.etree import ElementTree

import markdown as md
from markdown.treeprocessors import Treeprocessor


class ScrollableTables(Treeprocessor):
    def run(self, root):
        for parent in list(root.iter()):
            for index, child in enumerate(list(parent)):
                if child.tag != "table":
                    continue
                wrapper = ElementTree.Element("div", {
                    "class": "table-scroll",
                    "role": "region",
                    "aria-label": "Scrollable table",
                    "tabindex": "0",
                })
                parent.remove(child)
                parent.insert(index, wrapper)
                wrapper.append(child)
                for header in child.findall("./thead/tr/th"):
                    header.set("scope", "col")


def render_post_body(text: str) -> str:
    """Render a blog post body. Returns an HTML fragment, no <html>/<body>."""
    converter = md.Markdown(
        extensions=["fenced_code", "tables", "footnotes", "attr_list", "sane_lists"],
        output_format="html5",
    )
    converter.treeprocessors.register(ScrollableTables(converter), "scrollable_tables", 15)
    return converter.convert(text)

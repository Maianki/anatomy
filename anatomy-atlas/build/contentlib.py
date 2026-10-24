"""Verbatim sentence extraction from OpenStax CNXML modules, matched by sentence prefix."""
import re, xml.etree.ElementTree as ET
NS = "{http://cnx.rice.edu/cnxml}"


def slug(number, title):
    """OpenStax page slug, e.g. 22.1 + "Organs and Structures of the Respiratory System"."""
    t = re.sub(r"[^a-z0-9 ]+", "", title.lower().replace("’", ""))
    return "https://openstax.org/books/anatomy-and-physiology-2e/pages/" + number.replace(".", "-") + "-" + "-".join(t.split())


class Module:
    def __init__(self, path, number, url, title=""):
        self.paras, self.section, self.number, self.url, self.title = {}, {}, number, url, title
        root = ET.parse(path).getroot()
        self._walk(root.find(NS + "content"), "")

    def _walk(self, el, sec):
        for ch in el:
            tag = ch.tag.replace(NS, "")
            if tag == "section":
                t = ch.find(NS + "title")
                self._walk(ch, re.sub(r"\s+", " ", "".join(t.itertext())).strip() if t is not None else sec)
            elif tag == "para":
                self.paras[ch.get("id")] = re.sub(r"\s+", " ", "".join(ch.itertext())).strip()
                self.section[ch.get("id")] = sec
            else:
                self._walk(ch, sec)

    def sent(self, pid, prefix):
        p = self.paras[pid]
        i = p.index(prefix)  # fails loudly if the words are not in the source
        m = re.search(r"\.[\u201d\"\u2019]?(?=\s|$)", p[i:])
        s = p[i:i + m.end()]
        assert not re.search(r"\(\s*\)|\(see [a-z]?\s*\)|\([a-z]\)| shows | shown in ,| in \.$| in ,", s), s  # sentence points at a figure we don't show
        sec = self.section[pid]
        if sec == "Chapter Review":  # on openstax.org these paragraphs live on the chapter's review page
            ch = self.number.split(".")[0]
            return {"text": s, "pid": pid, "label": f"Ch. {ch} Chapter Review",
                    "url": f"https://openstax.org/books/anatomy-and-physiology-2e/pages/{ch}-chapter-review"}
        return {"text": s, "pid": pid, "label": self.number + " " + (sec or self.title), "url": self.url}

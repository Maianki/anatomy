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
        self.path = {}  # pid -> list of enclosing section titles, outermost first
        self.boxed = set()  # paragraphs inside notes, figures or exercises (not running text)
        root = ET.parse(path).getroot()
        self._walk(root.find(NS + "content"), "", [], False)

    def _walk(self, el, sec, path, boxed):
        for ch in el:
            tag = ch.tag.replace(NS, "")
            if tag == "section":
                t = ch.find(NS + "title")
                title = re.sub(r"\s+", " ", "".join(t.itertext())).strip() if t is not None else sec
                self._walk(ch, title, path + [title], boxed)
            elif tag == "para":
                self.paras[ch.get("id")] = re.sub(r"\s+", " ", "".join(ch.itertext())).strip()
                self.section[ch.get("id")] = sec
                self.path[ch.get("id")] = path
                if boxed:
                    self.boxed.add(ch.get("id"))
            else:
                self._walk(ch, sec, path, boxed or tag in ("note", "figure", "table", "exercise", "glossary"))

    # sentence helpers used by the bone content: every sentence still goes through sent(), so it is checked
    def sentences(self, pid):
        return re.findall(r".+?\.[\u201d\"\u2019]?(?=\s+[A-Z\u201c(]|$)", self.paras[pid])

    def ok(self, s):
        return not re.search(r"\(\s*\)|\(\s*(?:(?:and|or|see|also|,|;)\s*)+\)|\(see [a-z]?\s*\)|\([a-z]\)| shows | shown in ,| in \.$| in ,|\. (?:provides|shows|lists|summarizes) | of and ,", s)

    def section_pids(self, title, under=None):
        return [p for p in self.paras if self.section[p] == title and p not in self.boxed and (under is None or under in self.path[p])]

    def first(self, title, n=2, under=None):
        out = []
        for pid in self.section_pids(title, under):
            for s in self.sentences(pid):
                s = s.strip()
                if self.ok(s) and len(out) < n:
                    out.append(self.sent(pid, s[:60]))
            if len(out) >= n:
                break
        assert out, ("no usable sentence in section", self.number, title)
        return out

    def mention(self, title, word, under=None):
        for pid in self.section_pids(title, under):  # prefer a sentence that starts with the bone's name
            for s in self.sentences(pid):
                s = s.strip()
                if self.ok(s) and re.match(r"(The|Each)\s+(\w+\s+){0,2}%s\b" % re.escape(word), s, re.I):
                    return self.sent(pid, s[:60])
        for pid in self.section_pids(title, under):
            for s in self.sentences(pid):
                s = s.strip()
                if self.ok(s) and re.search(r"\b%s\b" % re.escape(word), s, re.I):
                    return self.sent(pid, s[:60])
        return None

    def intro(self, n=3):
        out = []
        for pid in self.paras:
            if self.path[pid]:
                break
            if pid in self.boxed:
                continue
            for s in self.sentences(pid):
                s = s.strip()
                if self.ok(s) and len(out) < n:
                    out.append(self.sent(pid, s[:60]))
        return out

    def sent(self, pid, prefix):
        p = self.paras[pid]
        i = p.index(prefix)  # fails loudly if the words are not in the source
        m = re.search(r"\.[\u201d\"\u2019]?(?=\s|$)", p[i:])
        s = p[i:i + m.end()]
        assert not re.search(r"\(\s*\)|\(\s*(?:(?:and|or|see|also|,|;)\s*)+\)|\(see [a-z]?\s*\)|\([a-z]\)| shows | shown in ,| in \.$| in ,|\. (?:provides|shows|lists|summarizes) | of and ,", s), s  # sentence points at a figure we don't show
        sec = self.section[pid]
        if sec == "Chapter Review":  # on openstax.org these paragraphs live on the chapter's review page
            ch = self.number.split(".")[0]
            return {"text": s, "pid": pid, "label": f"Ch. {ch} Chapter Review",
                    "url": f"https://openstax.org/books/anatomy-and-physiology-2e/pages/{ch}-chapter-review"}
        return {"text": s, "pid": pid, "label": self.number + " " + (sec or self.title), "url": self.url}

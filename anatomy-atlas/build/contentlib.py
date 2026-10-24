"""Verbatim sentence extraction from OpenStax CNXML modules, matched by sentence prefix."""
import re, xml.etree.ElementTree as ET
NS = "{http://cnx.rice.edu/cnxml}"


class Module:
    def __init__(self, path, number, url):
        self.paras, self.section, self.number, self.url = {}, {}, number, url
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
        m = re.search(r"\.(?=\s|$)", p[i:])
        s = p[i:i + m.end()]
        assert not re.search(r"\(\s*\)|\(see \)|\([a-z]\)| shows | in \.$", s), s  # sentence points at a figure we don't show
        sec = self.section[pid]
        return {"text": s, "pid": pid, "label": self.number + (" " + sec if sec else ""), "url": self.url}

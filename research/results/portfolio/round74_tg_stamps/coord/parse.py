"""Parse saved t.me/s/<channel> HTML (untrusted, data only) into posts: id, time (UTC epoch s), text.
Stdlib html.parser only. Usage: python -I parse.py <file.html>  (prints a summary)"""
import sys, datetime as dt
from html.parser import HTMLParser


class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.posts = []; self.cur = None; self.depth_text = 0; self.meta = {}
        self.stack_text = []

    def handle_starttag(self, tag, a):
        a = dict(a)
        cls = a.get("class", "") or ""
        if tag == "div" and "tgme_widget_message " in cls + " " and a.get("data-post"):
            self.cur = dict(post=a["data-post"], id=int(a["data-post"].rsplit("/", 1)[1]), time=None, text="",
                            edited=False)
            self.posts.append(self.cur)
        if self.cur is None:
            if tag == "meta" and a.get("property") in ("og:title", "og:description"):
                self.meta[a["property"]] = a.get("content")
            return
        if tag == "div" and "tgme_widget_message_text" in cls:
            self.depth_text = 1
        elif self.depth_text and tag == "div":
            self.depth_text += 1
        if self.depth_text and tag == "br":
            self.cur["text"] += "\n"
        if tag == "time" and a.get("datetime") and self.cur["time"] is None:
            self.cur["time"] = dt.datetime.fromisoformat(a["datetime"]).timestamp()
        if tag == "span" and "tgme_widget_message_meta" in cls:
            pass

    def handle_endtag(self, tag):
        if self.depth_text and tag == "div":
            self.depth_text -= 1

    def handle_data(self, d):
        if self.cur is not None and self.depth_text:
            self.cur["text"] += d
        if self.cur is not None and d.strip() == "edited":
            self.cur["edited"] = True


def parse(b):
    p = P(); p.feed(b.decode("utf-8", "replace")); return p.posts, p.meta


if __name__ == "__main__":
    ps, meta = parse(open(sys.argv[1], "rb").read())
    print(meta)
    print(len(ps), "posts", ps[0]["id"] if ps else None, ps[-1]["id"] if ps else None)
    for x in ps[-6:]:
        print(x["id"], dt.datetime.fromtimestamp(x["time"] or 0, dt.timezone.utc).isoformat(), x["edited"], repr(x["text"][:160]))

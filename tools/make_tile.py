#!/usr/bin/env python3
"""Turn this tree into a single-purpose tile build: own title id, name, port and icon, and a
fixed payload ELF (tiles/<tile>/tile.json). Run once in a clean checkout before `make`."""
import json, os, re, shutil, sys

root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
cfg = json.load(open(os.path.join(root, "tiles", sys.argv[1], "tile.json")))
tid, name, port = cfg["id"], cfg["name"], int(cfg["port"])
assert re.fullmatch(r"[A-Z]{4}\d{5}", tid), tid

def sub(path, pairs):
    p = os.path.join(root, path); s = open(p, encoding="utf-8").read()
    for old, new in pairs:
        n = s.count(old)
        assert n >= 1, (path, old)
        s = s.replace(old, new)
    open(p, "w", encoding="utf-8").write(s)

sub("include/wkali.h", [('#define WKALI_PORT 18181', '#define WKALI_PORT %d' % port),
                         ('#define WKAL_TITLE_ID "WKAL00001"', '#define WKAL_TITLE_ID "%s"' % tid)])
sub("include/installer_config.h", [('#define INSTALLER_APP_NAME "WebKit Autoloader"', '#define INSTALLER_APP_NAME "%s"' % name)])
sub("assets/param.json.template", [('"titleId": "WKAL00001"', '"titleId": "%s"' % tid),
                                    ('127.0.0.1:18181/', '127.0.0.1:%d/' % port),
                                    ('"titleName": "WebKit Autoloader v[[VERSION_PLACEHOLDER]]"', '"titleName": "%s"' % name)])
for f in ("frontend/autoloader/app.js", "frontend/installer-page/index.html", "frontend/pointer/index.html", "tools/gen_version.py"):
    sub(f, [("WebKit Autoloader", name)])
shutil.copy(os.path.join(root, cfg["icon"]), os.path.join(root, "assets", "icon.svg"))
print("tile %s: %s, port %d, payload %s" % (tid, name, port, cfg["loader"]))

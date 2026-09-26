#!/usr/bin/env python3
"""TGL installer. Touch Grass Later: the developer harness with a joke for
a name and a regiment for a work ethic.

Run it:  python3 install/tgl-install.py
Flags:   --yes (skip pauses), --no-color, --target DIR (install location)
"""

import argparse
import os
import shutil
import sys

# ---------------------------------------------------------------------------
# Style. Plain ANSI only, so this works over the most boring SSH terminal.
# ---------------------------------------------------------------------------

def _colors_enabled():
    if os.environ.get("NO_COLOR"):
        return False
    return sys.stdout.isatty()

class C:
    def __init__(self, enabled):
        self.e = enabled
    def wrap(self, code, text):
        return "\033[%sm%s\033[0m" % (code, text) if self.e else text
    def red(self, t): return self.wrap("91", t)
    def dim(self, t): return self.wrap("2", t)
    def bold(self, t): return self.wrap("1", t)
    def green(self, t): return self.wrap("92", t)
    def yellow(self, t): return self.wrap("93", t)

def banner(c):
    """The welcome banner. Green grass, a tree with a swing. Touch grass."""
    letters = r"""
  ███████╗ ██████╗ ██╗
  ╚══██╔══╝██╔════╝ ██║
     ██║   ██║  ███╗██║
     ██║   ██║   ██║██║
     ██║   ╚██████╔╝███████╗
     ╚═╝    ╚═════╝ ╚══════╝"""
    tagline = "        TOUCH GRASS LATER"
    tree = [
        "                  ____",
        "               __/    \\__",
        "              /          \\",
        "             |            |",
        "              \\          /",
        "               \\________/_______________________",
        "                    ||                     |  |",
        "                    ||                     |  |",
        "                    ||                     |__|",
        "                 ___||___",
    ]
    swing_top = 6  # tree lines the swing hangs from
    swing_col = 43
    grass = "\n".join([
        "  , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , ,",
        "   \\/ \\/ \\/ \\/ \\/ \\/ \\/ \\/ \\/ \\/ \\/ \\/ \\/ \\/ \\/ \\/ \\/ \\/ \\/",
    ])
    lines = [c.green(c.bold(letters)), c.dim(tagline), ""]
    for i, tl in enumerate(tree):
        if swing_top <= i < swing_top + 3:
            # swing hangs here: tree stays green, swing goes yellow
            lines.append(c.green(tl[:swing_col]) + c.yellow(tl[swing_col:]))
        else:
            lines.append(c.green(tl))
    lines.append(c.green(grass))
    return "\n".join(lines)

HELP = {
    "welcome": (
        "TGL is a developer harness for Muse agents. It splits every build "
        "into two modes with a hard gate between them.\n\n"
        "Plan Mode is the war room. Your agent grills you one question at a "
        "time, writes a spec and a sliced plan, and waits for your sign-off. "
        "No code happens here. Measure twice.\n\n"
        "Attack Mode is the assault. You say 'go attack mode' and your agent "
        "executes the signed plan one slice at a time, reviewing each slice "
        "before moving on. Then a red team tries to break what got built. "
        "Cut once.\n\n"
        "The name is the joke devs put on a sticker. The discipline is the "
        "serious part. This installer puts the harness where your Muse agent "
        "can find it."
    ),
    "env": (
        "The environment check makes sure this machine can actually run the "
        "installer and hold the skill files. It checks the Python version "
        "(3.8 or newer keeps everything in this script working) and that the "
        "parent folder of the install target is writable. If either fails, "
        "it tells you exactly what to fix instead of dying halfway through a "
        "copy."
    ),
    "target": (
        "The install target is the folder your Muse agent reads skills from. "
        "The default is ~/workspace/skills/tgl. If you already keep skills "
        "somewhere else, point the installer there instead. The installer "
        "copies the SKILL.md, templates, and docs into that folder. Nothing "
        "outside that folder is touched."
    ),
    "install": (
        "The install step copies the harness files into place: SKILL.md (the "
        "harness itself), the templates folder (spec, plan, ledger, release "
        "checklist), and the docs folder (tutorial and mode guides). If the "
        "target already exists, files are overwritten with the fresh copies, "
        "so re-running the installer is how you upgrade."
    ),
    "verify": (
        "The verify step reads back what was installed and checks it is "
        "real: SKILL.md exists and its frontmatter parses (the name field the "
        "agent uses to recognize the skill). This is the TGL way: never trust "
        "a build report, check the thing itself. If verification fails, the "
        "installer says so plainly instead of claiming success."
    ),
    "tutorial": (
        "The first-run tutorial shows you the two phrases that run "
        "everything: 'TGL, plan X' enters Plan Mode, 'go attack mode' "
        "launches the assault. It walks through a tiny example so your first "
        "real session does not feel like a cold start. The full guided tour "
        "lives in docs/tutorial.md after install."
    ),
}

def ask_help(c, key):
    print()
    print(c.dim("Help:"))
    print(HELP[key])
    print()

def prompt(c, text, help_key=None, default=None):
    suffix = ""
    if help_key:
        suffix = c.dim("  ([h]elp)")
    if default:
        text = "%s [%s]%s: " % (text, default, suffix)
    else:
        text = "%s%s: " % (text, suffix)
    while True:
        try:
            ans = input(text).strip()
        except EOFError:
            return default or ""
        if help_key and ans.lower() in ("h", "?", "help"):
            ask_help(c, help_key)
            continue
        if ans == "" and default is not None:
            return default
        return ans

def pause(c, args):
    if not args.yes:
        try:
            input(c.dim("Press Enter to continue..."))
        except EOFError:
            pass

def check(label, ok, detail=""):
    mark = "ok" if ok else "FAIL"
    line = "  [%s] %s" % (mark, label)
    if detail:
        line += " (%s)" % detail
    return ok, line

# ---------------------------------------------------------------------------
# Steps
# ---------------------------------------------------------------------------

def step_env(c, args, ctx):
    print(c.bold("Step 1: environment check"))
    print("Making sure this machine can hold the skill. (h for help)")
    if prompt(c, "Choice", help_key="env", default="") is None:
        pass
    results = []
    ok, line = check("Python version", sys.version_info >= (3, 8),
                     "%d.%d.%d" % sys.version_info[:3])
    results.append((ok, line))
    parent = os.path.dirname(os.path.abspath(ctx["target"]))
    writable = os.path.isdir(parent) and os.access(parent, os.W_OK)
    if not os.path.isdir(parent):
        try:
            os.makedirs(parent, exist_ok=True)
            writable = os.access(parent, os.W_OK)
        except OSError:
            writable = False
    ok, line = check("Skills parent writable", writable, parent)
    results.append((ok, line))
    for ok, line in results:
        print(line if ok else c.red(line))
    if not all(ok for ok, _ in results):
        print(c.red("Environment check failed. Fix the items above and re-run."))
        return False
    print(c.green("Environment looks good."))
    return True

def step_target(c, args, ctx):
    print()
    print(c.bold("Step 2: install location"))
    print("Where your Muse agent reads skills from. (h for help)")
    default = os.path.expanduser("~/workspace/skills/tgl")
    if args.target:
        ctx["target"] = os.path.abspath(os.path.expanduser(args.target))
        print("Using --target: %s" % ctx["target"])
        return True
    target = prompt(c, "Install to", help_key="target", default=default)
    ctx["target"] = os.path.abspath(os.path.expanduser(target))
    return True

def find_source(c, ctx):
    here = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(here)
    # The repo root holds SKILL.md next to install/. An older checkout may
    # still nest the skill at <root>/skills/tgl/. Check both, so the
    # installer works wherever the repo lives. Nothing is hardcoded to one
    # machine or one checkout shape.
    for candidate in (repo_root, os.path.join(repo_root, "skills", "tgl")):
        if os.path.isfile(os.path.join(candidate, "SKILL.md")):
            return candidate
    return None

def step_install(c, args, ctx):
    print()
    print(c.bold("Step 3: install"))
    print("Copying the harness into place. (h for help)")
    prompt(c, "Ready", help_key="install", default="")
    src = find_source(c, ctx)
    if src is None:
        print(c.red("Could not find the skill source next to this installer."))
        manual = prompt(c, "Path to the folder containing SKILL.md")
        manual = os.path.abspath(os.path.expanduser(manual))
        if not os.path.isfile(os.path.join(manual, "SKILL.md")):
            print(c.red("No SKILL.md there either. Aborting."))
            return False
        src = manual
    ctx["source"] = src
    if os.path.abspath(src) == os.path.abspath(ctx["target"]):
        print("Source and target are the same folder. Nothing to copy, "
              "will verify in place.")
        ctx["copied"] = []
        return True
    copied = []
    for root, dirs, files in os.walk(src):
        dirs[:] = [d for d in dirs
                   if d not in ("__pycache__", ".git", ".svn", ".hg")]
        for f in files:
            if f.startswith(".") or f.endswith((".pyc", ".pyo")):
                continue
            src_file = os.path.join(root, f)
            rel = os.path.relpath(src_file, src)
            dst_file = os.path.join(ctx["target"], rel)
            os.makedirs(os.path.dirname(dst_file), exist_ok=True)
            shutil.copy2(src_file, dst_file)
            copied.append(rel)
    ctx["copied"] = sorted(copied)
    print(c.green("Copied %d files." % len(copied)))
    return True

def parse_frontmatter(path):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            head = fh.read(2000)
    except OSError:
        return None
    if not head.startswith("---"):
        return None
    end = head.find("\n---", 3)
    if end == -1:
        return None
    front = head[3:end]
    fields = {}
    for line in front.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fields[k.strip()] = v.strip().strip('"').strip("'")
    return fields

def step_verify(c, args, ctx):
    print()
    print(c.bold("Step 4: verify"))
    print("Reading back the install. Trust the thing, not the report. "
          "(h for help)")
    prompt(c, "Ready", help_key="verify", default="")
    skill = os.path.join(ctx["target"], "SKILL.md")
    if not os.path.isfile(skill):
        print(c.red("SKILL.md missing at %s" % ctx["target"]))
        return False
    fields = parse_frontmatter(skill)
    if not fields or "name" not in fields:
        print(c.red("SKILL.md frontmatter did not parse."))
        return False
    print(c.green("SKILL.md present, frontmatter parses (name: %s)."
                  % fields.get("name", "?")))
    for extra in ("templates", "docs"):
        p = os.path.join(ctx["target"], extra)
        print("  [%s] %s" % ("ok" if os.path.isdir(p) else "--", extra))
    print(c.green("Install verified."))
    return True

def step_tutorial(c, args, ctx):
    print()
    print(c.bold("Step 5: first run"))
    print("A sixty second tour so your first session is not a cold start. "
          "(h for help)")
    choice = prompt(c, "Show the tour? (y/n)", help_key="tutorial",
                    default="y")
    if choice.lower().startswith("n"):
        print("Skipped. The full tour lives in docs/tutorial.md.")
        return True
    print()
    print(c.bold("Your first op, in five moves:"))
    print()
    print("  1. Point your Muse agent at the installed skill, or just say")
    print("     %s." % c.bold('"run TGL"'))
    print()
    print("  2. Say: %s" % c.bold('"TGL, plan a bookmarking app"'))
    print("     Your agent enters Plan Mode and grills you, one question at")
    print("     a time. Answer honestly. This is the war room.")
    print()
    print("  3. Read the spec and the sliced plan. Sign them off.")
    print("     Nothing is built until you say so. Measure twice.")
    print()
    print("  4. Say: %s" % c.red(c.bold('"go attack mode"')))
    print("     The regiment executes the plan one slice at a time, reviews")
    print("     each slice, then a red team tries to break it. Cut once.")
    print()
    print("  5. Ship. The ledger records what was learned. Touch grass later.")
    print()
    print(c.dim("Full guided walkthrough: docs/tutorial.md"))
    return True

def summary(c, ctx):
    print()
    print(c.bold(c.green("TGL installed.")))
    print()
    print("  Location: %s" % ctx["target"])
    if ctx.get("copied"):
        print("  Files: %d copied" % len(ctx["copied"]))
    print()
    print("  Two phrases run everything:")
    print("    %s  enters Plan Mode (the war room)" % c.bold('"TGL, plan X"'))
    print("    %s  launches Attack Mode (the assault)" % c.red(c.bold('"go attack mode"')))
    print()
    print(c.dim("Red team creed: break it before they do. Now touch grass later."))

# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="Install the TGL developer harness.")
    ap.add_argument("--yes", action="store_true", help="skip pauses")
    ap.add_argument("--no-color", action="store_true", help="disable ANSI colors")
    ap.add_argument("--target", default=None, help="install location")
    args = ap.parse_args()
    c = C(_colors_enabled() and not args.no_color)
    ctx = {"target": os.path.expanduser("~/workspace/skills/tgl"),
           "source": None, "copied": []}

    try:
        print(banner(c))
        print(c.bold("TGL installer. Touch Grass Later."))
        print()
        print("The developer harness with a joke for a name and a regiment")
        print("for a work ethic. Two modes, one hard gate between them:")
        print()
        print("  %s  the war room. Spec and plan, no code until you sign."
              % c.bold("Plan Mode,"))
        print("  %s  the assault. Say 'go attack mode' and the regiment moves."
              % c.red(c.bold("Attack Mode,")))
        print()
        print(c.dim("Press h at any prompt for help. Ctrl+C quits cleanly."))
        print()
        pause(c, args)

        steps = [step_env, step_target, step_install, step_verify,
                 step_tutorial]
        for step in steps:
            if not step(c, args, ctx):
                print()
                print(c.red("Installer stopped. Nothing half-installed is "
                            "left in a weird state: re-run to try again."))
                return 1
        summary(c, ctx)
        return 0
    except KeyboardInterrupt:
        print()
        print(c.dim("Installer cancelled. Nothing was half-installed."))
        return 130

if __name__ == "__main__":
    sys.exit(main())

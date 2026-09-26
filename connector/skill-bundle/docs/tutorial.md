# TGL tutorial: your first op

*Plan Mode measures twice. Attack Mode cuts once.*

This is a guided first run. The mission is tiny on purpose: a bookmarking
app. Somewhere to save links with a title and a tag, nothing more. You will
say two phrases, answer some questions, sign a plan, and watch the regiment
work. Total time: about ten minutes of your attention, most of it reading.

## Before you start

TGL needs to be installed where your Muse agent can see it. Either:

- Point your agent at the TGL repo and say **"install TGL"**, and it walks
  you through, or
- Run `python3 install/tgl-install.py` in a terminal.

Then just talk to your agent. That is the whole UI.

## Move 1: enter Plan Mode

You type:

> TGL, plan a bookmarking app

Your agent reads the project memory and ledger first (so it never re-asks a
settled question), then enters Plan Mode and starts recon. Recon is a grill:
one question at a time, and every bounded decision arrives as tappable
choices, always.

It looks like this:

> **Agent:** What should saving a bookmark feel like? I'd go with the quick
> popup, it keeps the flow fast without losing the tag.
> 1. One click, no questions asked
> 2. Quick popup for title and tag
> 3. Full editor with notes

You tap one. The agent names its recommendation every time, so you always
know where it stands. It asks the next thing. Maybe five or six questions
total: where do bookmarks live, do tags autocomplete, is there search, does
it work offline. Each answer reshapes what gets asked next, until nothing is
left silently assumed. Nothing is being built yet. This is the war room, and
the war room is patient.

**Why it works this way:** the cheapest bug is the one you never build.
Five minutes of questions now saves an hour of rework later. Measure twice.

## Move 2: read the spec

When recon is done, your agent writes SPEC.md and shows it to you. For our
toy app it reads something like:

> **Bookmarking app.** Save a link with a title and one tag. List
> bookmarks, filter by tag, search titles. One click to save from anywhere.
> No accounts, data lives on the device.

Read it. If something is wrong, say so now. Changing a sentence here costs
nothing. Changing it after the build costs a slice.

## Move 3: read the plan, then sign it

Next comes PLAN.md: the spec broken into numbered slices, each naming exact
files, interfaces, tests, commands, and expected output, plus a Review Focus
(how a real user would break this slice). Ours might be:

> **Slice 1:** data model and storage. Files: bookmarks.py. Expected: save,
> list, and filter round-trip in a test.
> Review Focus: what happens with a duplicate URL?
>
> **Slice 2:** the save flow. Expected: one click saves with the picked
> defaults.
> Review Focus: what if the title is empty?
>
> **Slice 3:** list, tag filter, search.
> Review Focus: what does search do with zero results?

You read it, and then you sign it. Say **"approved"** or similar. The agent
records the approval with a date. Until you do, no code exists. That is not
a suggestion. That is the chain of command.

## Move 4: go attack mode

You type:

> go attack mode

That is the battle cry, and the regiment moves. Your agent (now the
commanding agent) hands slice 1 to a fresh subagent with the spec and only
that slice. When slice 1 lands, the commanding agent reviews it against the
spec, quoting the spec lines it implements, before slice 2 begins. You do
not need to watch every step, but you can. Each slice is small enough to
verify in one pass.

**What you will notice:** it feels slower than one-shotting at first, and
then it feels faster, because nothing comes back broken in a surprising way.
Cut once.

**What you will also notice:** your agent checks in. Never a silent build,
never a status dump. At each slice boundary you get a 5-line SITREP:

> **SITREP**
> BUILDING: slice 2, the save flow
> BLOCKED: clear
> NEXT: slice 3, list and search
> ETA: about ten minutes
> NEED: nothing

Short, human, bottom line up front. If it ever goes quiet, something is
wrong.

## Move 5: the red team attacks

After the last slice, a fresh agent plays red team. It did not build this,
so it has no attachment to it. Its job is to break the bookmarking app the
way a real user would. Watch what it finds:

> **Red team:** Saved the same URL twice. Got two identical bookmarks. The
> spec said "save a link," it never said what a duplicate is. Also: deleted
> a bookmark, no undo, no confirmation. One misclick and it is gone.

The builder missed both. The spec was silent on duplicates, and nobody
thought about the misclick. That is exactly what the red team is for: it
hunts the failure the builder missed. Red team creed: break it before they
do.

The fixes go in as new slices, reviewed the same way. Nothing ships until it
survives its own red team.

## Move 6: ship

The release checklist runs: every slice reviewed, red-team record written,
tests green, no hardcoded identity, ledger updated. The ledger gets one
honest paragraph about what was learned. Maybe:

> Duplicates and delete-undo were red-team catches, not spec catches. Next
> time, recon asks about duplicates and destructive actions explicitly.

Then it is live. Touch grass later.

## What you just learned

Two phrases run everything: **"TGL, plan X"** and **"go attack mode."**
Between them sits a hard gate (no signed plan, no assault), a ledger that
remembers, and a red team that breaks things before your users do.

Now point it at something real.

# Plan Mode vs Attack Mode

*Plan Mode measures twice. Attack Mode cuts once.*

TGL has two modes and a hard gate between them. This page is the deep dive:
what each mode is for, when to use it, and what happens at the gate.

## At a glance

| | Plan Mode | Attack Mode |
|---|---|---|
| Nickname | the war room | the assault |
| Energy | deliberate, patient | relentless |
| You do | answer questions, read, sign | say the battle cry, watch |
| Agent does | grills, specs, plans | executes, reviews, red-teams, ships |
| Code written | zero, always | everything, in slices |
| Ends with | signed SPEC.md + PLAN.md | shipped version + ledger entry |
| Trigger | "TGL, plan X" | "go attack mode" |

Blue team draws the battle plan in the war room. Red team runs the assault,
then turns around and attacks what blue built. Nothing ships until it
survives its own red team.

## Plan Mode in detail

Plan Mode covers two phases: Discuss (recon) and Plan (spec + sliced plan).

**Recon.** Your agent reads the project memory and LEDGER.md first, then
grills you one question at a time. Bounded decisions get tappable choices.
It ends with a written goal both sides agree on. If you already know exactly
what you want, recon is short. If you do not, recon is where you figure it
out, which is much cheaper than figuring it out mid-build.

**SPEC.md.** What and why, no code. Tight enough that a stranger could build
from it. Includes non-goals, because what you are not building is half the
spec.

**PLAN.md.** The spec broken into numbered slices. Each slice names exact
files, interfaces, tests, commands, and expected output, plus a Review Focus:
the ways a real user would break this slice. Slices stay small enough to
verify in one pass.

**Sign-off.** You read both files and approve. The agent records the
approval with a date and version. No code exists until this happens.

**When to use it:** at the start of anything, and any time the plan needs to
change mid-build. A changed plan goes back through sign-off. That is not
bureaucracy, that is how the regiment stays honest.

## Attack Mode in detail

Attack Mode covers three phases: Execute, Verify, Ship.

**Execute.** One subagent per slice. Each gets fresh context, the spec, and
only its slice. Fresh context matters: it is how TGL fights context rot
without any git machinery. The commanding agent reviews each slice against
the spec before the next begins, and every implementation quotes the spec
lines it implements. If a slice cannot quote its lines, it did not follow
orders.

**Verify: the red team.** A fresh agent plays adversary. It tries to break
the build the way a real user would, hunts the failure the builder missed,
and attacks the plan's own assumptions. Verification happens in the real
surface at real size with real data. Build reports are not evidence. The red
team writes down what it actually saw and what it broke.

**Ship.** The release checklist runs, the ledger gets its after-action
entry, and the version goes live.

**When to use it:** when there is a signed plan. That is the only condition,
and it is absolute.

## The gate: a worked example

This is the chain of command, and it is the only enforcement mechanism TGL
has. Watch what happens when someone skips Plan Mode:

> **You:** go attack mode. Build me a habit tracker.
>
> **Agent:** I cannot march without orders. There is no signed SPEC.md and
> PLAN.md for a habit tracker, so there is nothing to execute. Want to enter
> Plan Mode? Say "TGL, plan a habit tracker" and we will draw up the battle
> plan first.

No override flag, no "attack anyway." A regiment without orders is just a
mob. If the plan needs to change mid-assault, the commanding agent halts,
the change goes through Plan Mode sign-off, and the assault resumes. Slow is
smooth, smooth is fast.

## Red-team Verify: a concrete catch

Back to the bookmarking app from the tutorial. The spec said "save a link
with a title and one tag." The plan had three slices. Everything passed
review. Then the red team got it for ten minutes and found two things:

1. **Duplicates.** Saving the same URL twice created two identical
   bookmarks. The spec never defined what a duplicate is, so the builder
   never handled it. The red team tried it because real users double-click.
2. **No undo on delete.** One misclick, bookmark gone, no confirmation. The
   builder tested that delete works. The red team tested that delete hurts.

Both fixes went in as new slices, reviewed the same way. The ledger recorded
the lesson: recon now asks about duplicates and destructive actions
explicitly. That is the dogfood loop. The red team finds it, the ledger
remembers it, the harness gets better.

## Which mode am I in?

If you are answering questions, you are in Plan Mode. If slices are landing
for review, you are in Attack Mode. If you are unsure, ask. Your agent always
knows which mode it is in, and it will tell you straight.

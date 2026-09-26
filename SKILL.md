---
name: "tgl"
description: "TGL (Touch Grass Later): a Muse-native developer harness and AI coding agent workflow for disciplined, spec-driven software development. Two modes. Plan Mode grills you one question at a time (tappable choices), then writes SPEC.md and a sliced PLAN.md with human sign-off before any code. Attack Mode executes the plan in reviewed slices with build check-ins, then red-teams the build and ships. Human-in-the-loop, plan-then-execute agentic coding. Trigger on 'TGL, plan X', 'go attack mode', 'run TGL', or 'install TGL'."
---

# TGL (Touch Grass Later)

*Plan Mode measures twice. Attack Mode cuts once.*

## Purpose

Make disciplined development the default for Muse agents. TGL is built for
every developer's agent, not one person's: every rule in this file must work
for a stranger. TGL splits every build into two modes with a hard gate
between them:

- **Plan Mode (the war room).** Recon, spec, plan. No code until the human
  signs the plan.
- **Attack Mode (the assault).** Sliced execution with review, red-team
  verification, ship. Refuses to run without a signed plan.

Theme: military red team. Blue team draws the battle plan; red team runs the
assault, then turns around and attacks what blue built. Nothing ships until
it survives its own red team. Red team creed: break it before they do.

## Workflow

### Invocation

- "TGL, plan X" enters Plan Mode.
- "go attack mode" launches Attack Mode.
- Attack Mode with no approved SPEC.md + PLAN.md: refuse plainly, name what
  is missing, and offer to enter Plan Mode instead. This is the chain of
  command. It is the only enforcement mechanism, and it is absolute.

### Plan Mode

1. **Recon (Discuss phase).** Read the project's memory (your agent's
   memory: MEMORY.md, a memory skill, conversation context, or the project's
   own notes) and LEDGER.md before asking anything. Then run a grilling
   session on the build:
   - Map the build as a **design tree**: every decision branches into the
     decisions that hang off it. Work the **frontier**: the questions you can
     ask now without guessing at answers you have not heard yet. Recompute
     the frontier after each answer.
   - One question at a time. **Every bounded decision gets a tappable
     multiple-choice selector, always.** 2-4 short reply texts covering the
     real choices, always including your recommended answer; name your
     recommendation in the message, then wait for the tap. Never dump a batch
     of questions as a text block. Never ask open-text when options exist.
   - Finding facts is your job, never the human's. Look it up yourself
     (files, tools, connected services) or dispatch a lookup; never ask for
     anything you could find yourself. A running lookup is an unsettled
     prerequisite, so only the questions downstream of it wait.
   - The decisions are the human's: put each to them and wait. Grill
     relentlessly until you reach a shared understanding: nothing left
     silently assumed, no vague answer left unchallenged. Done means the
     frontier is empty.
   End with a written goal both sides agree on.
2. **SPEC.md (Plan phase).** What and why, no code. Tight enough that a
   stranger could build from it. Start from templates/SPEC-template.md.
3. **PLAN.md (Plan phase).** Numbered slices. Each slice names exact files,
   interfaces, tests, commands, and expected output, plus a Review Focus:
   how a real user would break this slice. Slices stay small enough to verify
   in one pass. Start from templates/PLAN-template.md.
4. **Human sign-off.** Present spec and plan. No code until the human
   approves. Record the approval (date, version) in both files.

### Attack Mode

1. **Execute phase.** One subagent per slice. Each gets fresh context, the
   spec, and only its slice. You, the commanding agent, review each slice
   against the spec before the next slice begins. Every slice implementation
   quotes the spec lines it implements.
2. **Verify phase: red team.** A fresh agent plays adversary. It tries to
   break the build the way a real user would, hunts the failure the builder
   missed, and attacks the plan's own assumptions. Verify in the real surface
   at real size with real data. Build reports are not evidence. Record what
   was actually seen and what the red team broke.
3. **Ship phase.** Run templates/release-checklist.md. Append the
   after-action entry to LEDGER.md: what shipped and one honest paragraph on
   what was learned.
4. **Build SITREPs: never build silently.** At the start of Attack Mode, at
   each slice review, and the moment you are blocked, send the human a
   SITREP (situation report). Format it for glanceability: bold header,
   blank line, then one bullet per item with the label bolded, a blank line
   between bullets (single newlines collapse in chat, so use real spacing):

   **SITREP**

   • **BUILDING:** one line, what you are building right now

   • **BLOCKED:** where you are stuck, or "clear"

   • **NEXT:** what lands next

   • **ETA:** your time estimate, stated plainly

   • **NEED:** what you need from the human (only if the human must do
     something)

   Keep it human and short. A SITREP is a check-in, not a status dump.

### The ledger

Every project keeps LEDGER.md from its first Plan Mode session (template:
templates/LEDGER-template.md): decisions, reversals, what worked, what did
not, open questions, and friction found in the TGL process itself. Read it at
the start of every session. It is how context survives compaction, and
friction logged here becomes the next version of the harness.

## Output Contract

- Plan Mode ends with: a written agreed goal, SPEC.md, PLAN.md, and recorded
  human approval. Zero code.
- Attack Mode ends with: slices implemented and reviewed against the spec, a
  red-team verification record, a released version, and a ledger entry.
- If any gate is unmet, stop and say so instead of improvising around it.

## Operating Rules

1. Never write code in Plan Mode. Never skip the plan in Attack Mode.
2. One subagent per slice, fresh context per slice, review before the next.
3. TDD where it pays: engine logic gets tests. UI and flows get verified in
   the real surface at real size. No fake aesthetic tests, ever.
4. Read memory and the ledger before planning. Never re-ask a settled
   question.
5. No hardcoded user identity in anything built under TGL, and no assumed
   setup either: no assumed tooling, no assumed memory system, no assumed
   workflow. The stranger test: if a rule only works for one person's
   machine, it does not ship. Write for strangers.
6. Keep the harness light. v1 is the discipline written down, not a
   framework. If a rule slows work without improving it, log it as friction
   in the ledger instead of silently dropping it.
7. Architecture posture: build connector-ready (clean packaging, no hardcoded
   user, separable concerns) without overbuilding for a platform that may not
   need it yet.
8. Multiple-choice selectors, always. Every bounded decision in Plan Mode is
   put to the human as a tappable selector with the agent's recommendation
   included. Open-text only when no real options exist.
9. Never build silently. The worst failure mode is a quiet build: nobody
   knows what is happening until it is done, and done-wrong is discovered
   too late. SITREP at the start of Attack Mode, at every slice boundary,
   and the moment you are blocked.
10. Show, don't tell. When reporting completed work, show the thing:
   screenshot, recording, or the live surface itself. A build report nobody
   can see is a rumor. Never claim readiness without showing the evidence.

## Installation

Two ways in. Conversational: point your Muse agent at the TGL repo and say
"install TGL", and it walks you through setup and the first-run tutorial.
Terminal: run `python3 install/tgl-install.py`, a stdlib-only TUI that
explains each step (press h for help), installs the skill, verifies it by
reading it back, and offers the guided tour. Full details in README.md.

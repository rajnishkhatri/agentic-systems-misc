# Four Questions That Changed How I Think About Agent Explainability

Last year, I was deep in a post-incident review. A multi-agent invoice processing system had approved a payment it shouldn't have. I had logs—plenty of them. I could see *what* happened.

But the finance director kept asking questions I couldn't answer: *Which agent approved it? What version was running? Did the validation checks pass or were they skipped? Why did the system choose auto-approval instead of routing for review?*

I realized I'd been thinking about explainability all wrong. Recording events wasn't enough. I needed to answer fundamentally different questions.

---

## The Four Questions That Keep Coming Up

After that incident, I started paying closer attention to the questions stakeholders actually ask. Developers want different things than compliance officers. Operations teams have different needs than auditors.

But I noticed a pattern. Regardless of who was asking, the questions fell into four categories:

1. **What happened?**
2. **Who did it?**
3. **What was checked?**
4. **Why was it done?**

These became what I now think of as the four pillars of agent explainability. Each addresses a distinct aspect of transparency, and together they provide surprisingly comprehensive coverage.

---

## Pillar 1: Recording — "What Happened?"

This is where I usually start, and for good reason. I've found I need a complete record of everything that occurred during agent execution—the steps that were planned versus what actually ran, the inputs and outputs at each stage, timing information, and any parameter changes along the way.

Think of it like an aviation black box. After a flight, investigators can reconstruct exactly what happened, in what order, and where things started to go wrong.

In practice, this means capturing task plans, execution traces, which agents collaborated, and checkpoints you can roll back to. When a cascade failure happens, this pillar lets you trace it back to the originating event.

I've found this is necessary but not sufficient. Knowing *what* happened doesn't tell you *who* was responsible or *why* decisions were made.

---

## Pillar 2: Identity — "Who Did It?"

This one took me longer to appreciate. In a multi-agent system, I realized that simply knowing "the approval agent" handled something wasn't specific enough. I needed to know which version, what configuration it was running, who owns it, and whether anyone tampered with it.

It's like combining a passport with a professional license—proving not just who the agent is, but what it's qualified to do and what rules govern its behavior.

In practice, this means tracking agent identity (ID, version, owner), declared capabilities, operational policies, and some form of signature verification to detect tampering. For compliance-heavy environments, this is often the pillar auditors care most about.

I initially underestimated how often "which agent version processed this?" becomes a critical question during incident review.

---

## Pillar 3: Validation — "What Was Checked?"

This pillar answers what constraints were applied and whether outputs passed them. Did the response meet length requirements? Was PII detected and handled? Were required fields present? Did confidence scores fall within acceptable ranges?

Think of it like a customs inspection form—you declare what's expected, check what's actual, and document every inspection result.

The key insight for me was that validation isn't just about catching problems. It's about *proving* that checks happened. When a compliance officer asks whether customer data was properly handled, having validation traces allows me to show exactly what was checked and what actions were taken.

Different failures might warrant different responses: reject and stop, attempt automatic correction, escalate to human review, or just log and continue. Tracking these decisions creates audit evidence.

---

## Pillar 4: Reasoning — "Why Was It Done?"

This is the pillar I'm still grappling with the most. It attempts to track the decision-making process—not just what choice was made, but why that approach was selected over alternatives.

Think of it like a research lab notebook. Scientists don't just record results; they document their reasoning, the hypotheses they considered, and why they chose one experimental design over another.

In my experiments, this means logging decisions with explicit reasoning, the alternatives that were considered and rejected, what artifacts were produced, and how confident the agent was. For the regulated workflows I've seen, this kind of documentation seems to be the difference between a defensible methodology and an unexplainable black box.

---

## How They Work Together

I've come to see these not as competing approaches, but as complementary pieces of a puzzle. A robust production system likely needs all four simultaneously.

Consider a healthcare AI reviewing medical scans:
- **Recording** captures the full processing sequence for each case
- **Identity** verifies which agent version (with FDA-cleared configuration) handled the analysis
- **Validation** ensures no patient PHI leaks into logs
- **Reasoning** documents why the AI flagged specific regions for radiologist review

Each pillar answers different questions for different stakeholders. The radiologist wants to understand the reasoning. The compliance officer wants identity verification and validation traces. The operations team needs recording for incident investigation.

---

## What I'm Still Learning

I won't pretend this framework is complete. Some open questions I'm working through:

How much recording is enough without creating performance overhead or storage costs that become unmanageable? How do you balance transparency with security when traces might contain sensitive information? What's the right level of abstraction for different stakeholders?

But framing explainability around these four questions has given me a clearer way to think about what I'm actually trying to capture—and to identify gaps before they become problems in production.

---

## A Question for You

I'm curious how others structure their thinking about agent explainability. Do these four pillars resonate with the questions you're getting from stakeholders? Are there categories I'm missing?

If you're building agentic systems and have found different frameworks useful, I'd genuinely like to hear about them.

---

*This is part of a series on making AI agent systems more transparent and auditable. If there's a specific pillar you'd like me to dig into more deeply, let me know in the comments.*


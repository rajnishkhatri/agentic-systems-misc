# What I Learned About Explaining AI Agents (It's Not What I Expected)

A few months ago, a compliance officer asked me a question about a multi-agent system I'd been working on: "Why did the system escalate this particular case to a human reviewer?"

I thought I was prepared. I had SHAP values ready. I could show her exactly which words in the customer complaint pushed our sentiment classifier toward "high urgency." I'd done my homework on model interpretability.

But she looked at my explanation and said, "That's not what I'm asking."

She didn't want to know why the *model* made a prediction. She wanted to know why the *system* made a decision—which agents were involved, what information passed between them, why one agent handed off to another instead of resolving directly, and what policy triggered the escalation.

I didn't have good answers. And that gap in my understanding sent me down a learning path I want to share.

---

## A Distinction I Wish I'd Understood Earlier

It turns out there's a meaningful difference between two things I had been mentally lumping together.

**Model interpretability** focuses on individual predictions. Tools like LIME and SHAP are genuinely excellent at this. They can tell you that in a sentiment classification, the word "disappointing" pushed the score toward negative while "fast shipping" pulled it back toward positive. For understanding model behavior, detecting bias, and debugging training issues, these tools are invaluable. I still use them regularly.

**Agent explainability** operates at a different level entirely. When you have multiple agents coordinating—one classifying inputs, another gathering evidence, a third making decisions based on what the others found—the system's behavior emerges from their interaction. No single model prediction explains the outcome.

I suspect many practitioners have encountered this distinction without having clear language for it. I certainly had. The compliance officer's question forced me to recognize that I'd been treating model-level tools as if they provided system-level transparency. They don't, and that's not a criticism of those tools—it's just a recognition of what they're designed for.

---

## Why I Think This Confusion Is Common

The AI industry developed model interpretability tools first, which makes sense—standalone models were how most of us deployed ML for years. A fraud detection model made a prediction, you explained the prediction, and that was sufficient.

Agentic systems change the picture. Consider what happens in a dispute resolution workflow (something I've spent a lot of time thinking about lately). An intake agent classifies the dispute. An evidence-gathering agent retrieves transaction history. An analysis agent evaluates the evidence. A resolution agent determines the outcome.

Each agent might use ML models internally, but the system's behavior emerges from their orchestration. When something goes wrong—or when an auditor asks why something happened—you need to trace through the entire sequence, not just examine one model's feature importance.

I'm not sure I fully appreciated this until I found myself unable to answer that compliance officer's question. Sometimes the most useful learning comes from realizing what you don't know.

---

## What I've Found Actually Helps

Through trial and error (heavy on the error), I've started thinking about agent explainability in terms of four types of information you need to capture. I'm still refining this framework, but it's been useful so far.

**Execution traces** help answer "what happened." This means recording the steps the system took, decision points encountered, parameters that changed during execution, and handoffs between agents. When something goes wrong, you need to reconstruct the sequence of events. I learned this the hard way during incident investigations where I had the final output but no visibility into how we got there.

**Identity and accountability** help answer "who did it." In multi-agent systems, knowing which specific agent—including its version and configuration—handled each action matters more than I initially realized. "The approval agent did it" isn't sufficient when an auditor asks questions. You need version numbers and policy configurations.

**Validation records** help answer "what was checked." Logging validation results—PII detection, confidence thresholds, required fields—creates audit evidence. This feels obvious in retrospect, but I wasn't systematic about it until compliance requirements forced the issue.

**Decision reasoning** helps answer "why this approach." When an agent chose option A over options B and C, capturing that reasoning becomes valuable later. This is perhaps the closest to traditional interpretability, but at the workflow level rather than the model level.

I'm curious whether others have arrived at similar categories or think about this differently.

---

## An Example That Made It Concrete for Me

Invoice processing helped clarify the distinction in my mind.

With model interpretability alone, I could explain why the extraction model identified "Acme Corp" as the vendor name—the text pattern matched, the location on the page was typical, confidence was high. That's useful information for debugging the extraction model.

But when someone asked why a particular invoice was routed for manual review when similar invoices were auto-approved, model interpretability couldn't help. That question required understanding which agent processed the invoice, what version it was running, what threshold triggered the review, and whether any recent parameter changes affected the routing logic.

The first type of explanation satisfies data scientists working on model improvements. The second satisfies compliance officers, operations teams, and incident responders. Both are legitimate needs, and I'd been focused primarily on the first while assuming it covered the second.

---

## What I'm Still Figuring Out

I want to be honest that I don't have this fully solved. Some open questions I'm working through:

How much tracing is enough without creating performance overhead or storage costs that become unmanageable? I've seen teams log everything and drown in data they never use, and teams log too little and regret it during incidents.

How do you balance transparency with security when traces might contain sensitive information? The same detailed logs that help with debugging could be problematic if exposed.

What's the right level of abstraction for different stakeholders? A developer debugging a failure needs different detail than an auditor reviewing compliance.

If you're working on agentic systems and have thoughts on any of this, I'd genuinely appreciate hearing your perspective.

---

## The Takeaway I Keep Coming Back To

Model interpretability and agent explainability answer different questions for different people. Both matter. I spent too long thinking the first was sufficient, and that gap showed up at exactly the wrong moment.

If you're building agentic systems, it might be worth asking what questions your stakeholders actually need answered and whether your current tooling can answer them. That compliance officer's question taught me mine couldn't.

---

*I'm planning to write more about the specific approaches I've found useful for each type of explainability. If there's a particular aspect you'd like me to dig into first, let me know in the comments.*

*And if you've encountered this model-vs-agent explainability gap in your own work, I'd be curious to hear how you've addressed it.*

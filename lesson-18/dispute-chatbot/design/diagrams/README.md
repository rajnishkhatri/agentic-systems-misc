# Dispute Chatbot Design Diagrams

This folder contains Mermaid diagram source files (`.mmd`) for the Merchant Dispute Resolution Chatbot.

## Diagrams Index

| File | Description | Type |
|------|-------------|------|
| `01_main_sequence.mmd` | End-to-end happy path flow | Sequence |
| `02_state_machine.mmd` | 5-phase workflow state transitions | State |
| `03_evidence_gatherer.mmd` | Hierarchical evidence gathering architecture | Flowchart |
| `04_judge_panel.mmd` | LLM Judge Panel validation flow | Flowchart |
| `05_explainability_layer.mmd` | Four pillars of explainability | Flowchart |
| `06_data_flow.mmd` | Complete data flow across system | Flowchart |
| `07_security_flow.mmd` | Request flow through security layers | Flowchart |
| `08_escalation_flow.mmd` | Escalation decision tree | Flowchart |
| `09_evidence_sequence.mmd` | Evidence gathering sequence | Sequence |
| `10_vrol_submission.mmd` | VROL submission with retry | Sequence |

## Viewing Diagrams

### Option 1: VS Code Extensions
- Install **Mermaid Preview** or **Markdown Preview Mermaid Support**
- Open any `.mmd` file and use preview

### Option 2: Mermaid Live Editor
- Visit [mermaid.live](https://mermaid.live)
- Paste diagram content

### Option 3: Generate SVGs with mermaid-cli

```bash
# Install mermaid-cli
npm install -g @mermaid-js/mermaid-cli

# Generate all SVGs
for f in *.mmd; do
    mmdc -i "$f" -o "${f%.mmd}.svg" -t dark
done
```

### Option 4: GitHub/GitLab Rendering
Both GitHub and GitLab render Mermaid diagrams in markdown files natively.

## Diagram Conventions

### Colors
- **Blue** (`#e1f5fe`, `#e3f2fd`): Planning/coordination components
- **Orange** (`#fff3e0`): Specialist agents
- **Green** (`#c8e6c9`, `#e8f5e9`): Success states, aggregators
- **Yellow** (`#fff9c4`): Warning states
- **Red** (`#ffcdd2`): Error/block states, security components
- **Pink** (`#fce4ec`): Logging components

### Naming
- Participants use abbreviated names with full descriptions
- States use UPPERCASE (CLASSIFY, GATHER, etc.)
- Actions use Title Case

## Related Documents

- [System Context](../00_system_context.md)
- [Flow Diagrams (consolidated)](../01_flow_diagrams.md)
- Domain Model (coming soon)


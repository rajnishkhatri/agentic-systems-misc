# Address Fraud Detection: First Principles Guide - Documentation

This directory contains the comprehensive documentation for the Address Fraud Detection First Principles Guide React application.

## Files

### `address-fraud-first-principles-companion.md`
The complete companion reference document (918 lines) providing:

- **Part I: The Seven Rivers of Theft** - Detailed analysis of fraud attack vectors
- **Part II: The Six Axioms** - Fundamental principles underlying detection
- **Part III: From Axiom to Architecture** - Technical implementation guides
- **Part IV: Boundaries and Failures** - When and why detection strategies fail
- **Part V: The Analyst's Role** - Human-in-the-loop considerations
- **Part VI: Metrics That Matter** - Evaluation frameworks
- **Part VII: Regulatory Context** - Compliance requirements

## Integration

The React application (`src/components/AddressFraudFirstPrinciplesGuide.jsx`) seamlessly integrates with this documentation through:

1. **Contextual Reference Links**: Each phase of the interactive guide links to relevant sections
2. **Progressive Disclosure**: Links appear as users advance through the learning phases
3. **Comprehensive Footer**: Complete reference panel with organized navigation
4. **Rich Tooltips**: Immediate context without leaving the application

## Usage

The interactive React app provides:
- 6 learning phases (Baseline → Assumptions → Axioms → Mechanisms → Application → Synthesis)
- Interactive elements and animations
- Contextual deep-dive links to this documentation
- Self-contained experience with external reference capability

## Technical Notes

- All reference links point to GitHub-hosted markdown with proper anchor navigation
- Links open in new tabs with appropriate security attributes
- Responsive design works across desktop and mobile devices
- Component is self-contained with no external dependencies beyond React

## Development

To run the application:
```bash
npm install
npm run dev
```

The development server will start on http://localhost:5174 (or next available port).
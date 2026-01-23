import React, { useState, useEffect } from 'react';

// ============================================================================
// FIRST PRINCIPLES DEEP DIVE: ADDRESS MANIPULATION & SHIPPING FRAUD DETECTION
// A recursive exploration from surface knowledge to irreducible axioms
// For AI Architects and Fraud Analysts
// ============================================================================
//
// "The drop that enters the sea does not vanish—it becomes the sea."
// Here we trace the hidden rivers that carry stolen goods to distant shores.
// Not the transaction alone, but the *address*—that quiet coordinate
// where intention meets geography, where the fraudster must finally surface.
//
// ============================================================================

// GitHub URL for companion markdown document (now in app docs directory)
const COMPANION_MD_BASE_URL = 'https://github.com/rajnishkhatri/ml-fraud-react/blob/main/docs/address-fraud-first-principles-companion.md';

// Reference Link Component for consistent styling and linking
const ReferenceLink = ({ section, anchor, children, tooltip, className = "" }) => {
  const url = `${COMPANION_MD_BASE_URL}${anchor ? `#${anchor}` : ''}`;

  return (
    <div className="group relative inline-block">
      <a
        href={url}
        target="_blank"
        rel="noopener noreferrer"
        className={`inline-flex items-center gap-2 px-3 py-1.5 text-sm rounded-lg border border-slate-600/50 bg-slate-800/30 text-slate-300 hover:text-slate-100 hover:border-slate-500 transition-all duration-200 hover:bg-slate-700/50 ${className}`}
        title={tooltip || `Deep dive: ${section}`}
      >
        <span className="text-xs">📖</span>
        {children}
        <span className="text-xs opacity-70">↗</span>
      </a>
      {tooltip && (
        <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 text-xs text-slate-200 bg-slate-900 border border-slate-700 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none whitespace-nowrap z-10">
          {tooltip}
        </div>
      )}
    </div>
  );
};

const AddressFraudFirstPrinciplesGuide = ({ onBack }) => {
  const [activePhase, setActivePhase] = useState(0);
  const [expandedAxioms, setExpandedAxioms] = useState({});
  const [expandedWhyChains, setExpandedWhyChains] = useState({});
  const [quizAnswers, setQuizAnswers] = useState({});
  const [showResults, setShowResults] = useState(false);
  const [animatedItems, setAnimatedItems] = useState([]);
  
  // Staggered animation effect
  useEffect(() => {
    setAnimatedItems([]);
    for (let i = 0; i < 20; i++) {
      setTimeout(() => {
        setAnimatedItems(prev => [...prev, i]);
      }, i * 80);
    }
  }, [activePhase]);

  const phases = [
    { id: 0, name: 'BASELINE', label: 'What Is It?', icon: '◯', color: 'amber' },
    { id: 1, name: 'ASSUMPTIONS', label: 'Challenge Beliefs', icon: '◇', color: 'cyan' },
    { id: 2, name: 'AXIOMS', label: 'Drill to Truth', icon: '△', color: 'violet' },
    { id: 3, name: 'MECHANISMS', label: 'How It Works', icon: '□', color: 'emerald' },
    { id: 4, name: 'APPLICATION', label: 'Where It Applies', icon: '⬡', color: 'pink' },
    { id: 5, name: 'SYNTHESIS', label: 'Test Understanding', icon: '◎', color: 'indigo' },
  ];

  const toggleAxiom = (id) => {
    setExpandedAxioms(prev => ({ ...prev, [id]: !prev[id] }));
  };

  const toggleWhyChain = (id) => {
    setExpandedWhyChains(prev => ({ ...prev, [id]: !prev[id] }));
  };

  // ============================================================================
  // PHASE 0: ESTABLISH BASELINE (WHAT)
  // ============================================================================
  const BaselinePhase = () => (
    <div className="space-y-8">
      <div className="border-l-4 border-amber-500 pl-6 py-2">
        <p className="text-amber-400 font-mono text-sm tracking-widest">PHASE 1: ESTABLISH BASELINE</p>
        <h2 className="text-3xl font-serif text-slate-100 mt-2">What is Address Manipulation Fraud at its most literal level?</h2>
        <p className="text-slate-400 mt-2 italic">
          "The thief cannot remain a ghost forever. Somewhere, the stolen thing must land."
        </p>
      </div>

      {/* Core Definition */}
      <div className={`bg-slate-800/50 rounded-xl p-8 border border-slate-700/50 transition-all duration-500 ${animatedItems.includes(0) ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
        <h3 className="text-xl font-semibold text-slate-100 mb-6 flex items-center gap-3">
          <span className="w-8 h-8 rounded-full bg-amber-500/20 flex items-center justify-center text-amber-400 text-sm">1</span>
          Observable Phenomenon
        </h3>
        
        <div className="grid md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <div className="bg-slate-900/50 rounded-lg p-5">
              <h4 className="text-amber-400 font-medium mb-3">What Is Address Manipulation Fraud?</h4>
              <p className="text-slate-300 leading-relaxed">
                <span className="text-amber-300">Address manipulation fraud</span> encompasses techniques 
                fraudsters use to circumvent billing/shipping address verification, enabling them to 
                receive stolen goods without revealing their true identity or location.
              </p>
              <div className="mt-4 p-4 bg-slate-800/50 rounded-lg font-mono text-sm">
                <p className="text-slate-400">// The fundamental problem:</p>
                <p className="text-amber-300">FRAUDSTER GOAL: Receive physical goods</p>
                <p className="text-emerald-300">CONSTRAINT: Cannot use own address directly</p>
                <p className="text-violet-300">SOLUTION: Manipulate the address chain</p>
              </div>
            </div>
            
            <div className="bg-slate-900/50 rounded-lg p-5">
              <h4 className="text-amber-400 font-medium mb-3 flex items-center justify-between">
                The Seven Fraud Vectors (What We Observe)
                <ReferenceLink
                  section="Part I: The Seven Rivers of Theft"
                  anchor="part-i-the-seven-rivers-of-theft"
                  tooltip="Detailed analysis of each fraud vector with real-world examples and detection strategies"
                >
                  Complete Analysis
                </ReferenceLink>
              </h4>
              <ul className="text-slate-300 space-y-3">
                <li className="flex items-start justify-between gap-3">
                  <div className="flex items-start gap-2">
                    <span className="text-amber-500">→</span>
                    <div>
                      <strong>Porch Piracy:</strong> Physical interception at cardholder's address
                      <p className="text-xs text-slate-400 mt-1">43% of Americans affected, often targeting high-value households</p>
                    </div>
                  </div>
                  <ReferenceLink
                    section="Porch Piracy"
                    anchor="1-porch-piracy-the-lurker-at-the-threshold"
                    tooltip="The simplest attack: waiting at doorsteps for package delivery"
                    className="text-xs"
                  >
                    Details
                  </ReferenceLink>
                </li>
                <li className="flex items-start justify-between gap-3">
                  <div className="flex items-start gap-2">
                    <span className="text-amber-500">→</span>
                    <div>
                      <strong>Mule Networks:</strong> Recruited intermediaries receiving/reshipping goods
                      <p className="text-xs text-slate-400 mt-1">High betweenness centrality reveals network bridges</p>
                    </div>
                  </div>
                  <ReferenceLink
                    section="Mule Networks"
                    anchor="2-mule-networks-the-recruited-river"
                    tooltip="Graph analysis techniques for detecting recruitment patterns"
                    className="text-xs"
                  >
                    Details
                  </ReferenceLink>
                </li>
                <li className="flex items-start justify-between gap-3">
                  <div className="flex items-start gap-2">
                    <span className="text-amber-500">→</span>
                    <div>
                      <strong>Reshipper Abuse:</strong> Legitimate services exploited for anonymity
                      <p className="text-xs text-slate-400 mt-1">Velocity and destination analysis for detection</p>
                    </div>
                  </div>
                  <ReferenceLink
                    section="Reshippers"
                    anchor="3-reshippers-the-legitimate-cloak"
                    tooltip="How fraudsters hide behind legitimate freight forwarders"
                    className="text-xs"
                  >
                    Details
                  </ReferenceLink>
                </li>
                <li className="flex items-start justify-between gap-3">
                  <div className="flex items-start gap-2">
                    <span className="text-amber-500">→</span>
                    <div>
                      <strong>AVS Manipulation:</strong> Gaming address verification systems
                      <p className="text-xs text-slate-400 mt-1">Exploiting partial matches in verification logic</p>
                    </div>
                  </div>
                  <ReferenceLink
                    section="AVS Manipulation"
                    anchor="4-avs-manipulation-gaming-the-partial-match"
                    tooltip="Technical details of address verification system vulnerabilities"
                    className="text-xs"
                  >
                    Details
                  </ReferenceLink>
                </li>
                <li className="flex items-start justify-between gap-3">
                  <div className="flex items-start gap-2">
                    <span className="text-amber-500">→</span>
                    <div>
                      <strong>Triangulation:</strong> Fake storefronts fulfilling with stolen cards
                      <p className="text-xs text-slate-400 mt-1">Detecting price arbitrage and timing patterns</p>
                    </div>
                  </div>
                  <ReferenceLink
                    section="Triangulation"
                    anchor="5-triangulation-the-invisible-storefront"
                    tooltip="The sophisticated fraud that exploits ecosystem gaps"
                    className="text-xs"
                  >
                    Details
                  </ReferenceLink>
                </li>
                <li className="flex items-start justify-between gap-3">
                  <div className="flex items-start gap-2">
                    <span className="text-amber-500">→</span>
                    <div>
                      <strong>Open House Fraud:</strong> Using temporary-access locations
                      <p className="text-xs text-slate-400 mt-1">Cross-referencing with property and booking databases</p>
                    </div>
                  </div>
                  <ReferenceLink
                    section="Open House Fraud"
                    anchor="6-open-house-fraud-the-temporary-address"
                    tooltip="Exploiting Airbnb and real estate listings for package delivery"
                    className="text-xs"
                  >
                    Details
                  </ReferenceLink>
                </li>
                <li className="flex items-start justify-between gap-3">
                  <div className="flex items-start gap-2">
                    <span className="text-amber-500">→</span>
                    <div>
                      <strong>Post-Approval Changes:</strong> Social engineering address modifications
                      <p className="text-xs text-slate-400 mt-1">NLP analysis of support conversations for detection</p>
                    </div>
                  </div>
                  <ReferenceLink
                    section="Post-Approval Manipulation"
                    anchor="7-post-approval-manipulation-the-voice-on-the-phone"
                    tooltip="How fraudsters exploit customer support processes"
                    className="text-xs"
                  >
                    Details
                  </ReferenceLink>
                </li>
              </ul>

              {/* Key Insight Box */}
              <div className="mt-6 p-4 bg-amber-900/20 border border-amber-700/30 rounded-lg">
                <h5 className="text-amber-300 font-medium mb-2 flex items-center gap-2">
                  <span className="text-xs">💡</span>
                  Key Insight: The Address Chain
                </h5>
                <p className="text-slate-300 text-sm leading-relaxed">
                  Every fraud vector manipulates the <strong>address chain</strong>: billing → shipping → reshipper → mule → final destination.
                  Detection requires monitoring the entire chain, not just the initial transaction.
                </p>
                <div className="mt-3">
                  <ReferenceLink
                    section="Physical Materialization Axiom"
                    anchor="axiom-1-physical-materialization"
                    tooltip="The fundamental constraint that makes address fraud detectable"
                    className="text-xs"
                  >
                    Understanding the Axiom
                  </ReferenceLink>
                </div>
              </div>
            </div>
          </div>

          <div className="space-y-4">
            <div className="bg-slate-900/50 rounded-lg p-5">
              <h4 className="text-amber-400 font-medium mb-3">Industry State (2025)</h4>
              <div className="grid grid-cols-2 gap-4 text-center">
                <div className="bg-slate-800 rounded-lg p-4">
                  <div className="text-2xl font-bold text-amber-400">43%</div>
                  <div className="text-xs text-slate-400 mt-1">Package theft victims (2020 study)</div>
                </div>
                <div className="bg-slate-800 rounded-lg p-4">
                  <div className="text-2xl font-bold text-amber-400">&lt;100ms</div>
                  <div className="text-xs text-slate-400 mt-1">Latency requirement for scoring</div>
                </div>
                <div className="bg-slate-800 rounded-lg p-4">
                  <div className="text-2xl font-bold text-amber-400">18%</div>
                  <div className="text-xs text-slate-400 mt-1">AUC gain with temporal GNNs</div>
                </div>
                <div className="bg-slate-800 rounded-lg p-4">
                  <div className="text-2xl font-bold text-amber-400">74.51%</div>
                  <div className="text-xs text-slate-400 mt-1">F1 for MuleTrace detection</div>
                </div>
              </div>
            </div>
            
            <div className="bg-slate-900/50 rounded-lg p-5">
              <h4 className="text-amber-400 font-medium mb-3">Evolution of Detection</h4>
              <div className="relative pl-4 border-l-2 border-slate-600 space-y-3">
                <div className="relative"><span className="absolute -left-[21px] w-3 h-3 rounded-full bg-slate-600"></span><span className="text-slate-400 text-sm">Pre-2015:</span> <span className="text-slate-300">AVS matching only (numbers check)</span></div>
                <div className="relative"><span className="absolute -left-[21px] w-3 h-3 rounded-full bg-slate-500"></span><span className="text-slate-400 text-sm">2016-19:</span> <span className="text-slate-300">Velocity rules + manual review</span></div>
                <div className="relative"><span className="absolute -left-[21px] w-3 h-3 rounded-full bg-amber-600"></span><span className="text-slate-400 text-sm">2020-22:</span> <span className="text-slate-300">ML ensembles (XGBoost, Random Forest)</span></div>
                <div className="relative"><span className="absolute -left-[21px] w-3 h-3 rounded-full bg-amber-500"></span><span className="text-slate-400 text-sm">2023-24:</span> <span className="text-slate-300">Graph Neural Networks for ring detection</span></div>
                <div className="relative"><span className="absolute -left-[21px] w-3 h-3 rounded-full bg-amber-400"></span><span className="text-slate-400 text-sm">2025:</span> <span className="text-slate-300">Temporal GNNs + Entity Resolution + Weak Supervision</span></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Key Definitions */}
      <div className={`bg-slate-800/50 rounded-xl p-8 border border-slate-700/50 transition-all duration-500 delay-100 ${animatedItems.includes(1) ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
        <h3 className="text-xl font-semibold text-slate-100 mb-6 flex items-center gap-3">
          <span className="w-8 h-8 rounded-full bg-amber-500/20 flex items-center justify-center text-amber-400 text-sm">2</span>
          Precise Definitions Required
        </h3>
        
        <div className="grid md:grid-cols-3 gap-4">
          {[
            { term: 'AVS (Address Verification Service)', def: 'System checking if billing address numbers match card issuer records. Only validates building number + ZIP—ignores street name.' },
            { term: 'Mule', def: 'Person recruited (often unknowingly) to receive packages and reship to fraudster. Key intermediary obscuring the chain.' },
            { term: 'Reshipper', def: 'Legitimate freight forwarding service enabling cross-border package consolidation. Often exploited for anonymity.' },
            { term: 'Entity Resolution', def: 'Process of linking fragmented identities across transactions. Uses fuzzy matching and graph analysis to expose hidden connections.' },
            { term: 'Betweenness Centrality', def: 'Graph metric measuring how often a node lies on shortest paths between others. High betweenness = likely mule intermediary.' },
            { term: 'Triangulation Fraud', def: 'Fake storefront operation: accepts real payment, fulfills with stolen card, profits the difference. Shipping address is the "customer."' },
          ].map((item, idx) => (
            <div key={idx} className="bg-slate-900/50 rounded-lg p-4">
              <h4 className="text-amber-400 font-medium text-sm">{item.term}</h4>
              <p className="text-slate-400 text-sm mt-2">{item.def}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Component Diagram */}
      <div className={`bg-slate-800/50 rounded-xl p-8 border border-slate-700/50 transition-all duration-500 delay-200 ${animatedItems.includes(2) ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
        <h3 className="text-xl font-semibold text-slate-100 mb-6 flex items-center gap-3">
          <span className="w-8 h-8 rounded-full bg-amber-500/20 flex items-center justify-center text-amber-400 text-sm">3</span>
          System Architecture Overview (Component Diagram)
        </h3>
        
        <div className="bg-slate-900 rounded-lg p-6 font-mono text-sm">
          <pre className="text-slate-300 overflow-x-auto">
{`┌─────────────────────────────────────────────────────────────────────┐
│                     ADDRESS FRAUD DETECTION SYSTEM                   │
├─────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐     ┌─────────────────┐     ┌───────────────┐  │
│  │  Event Ingestion │     │  Feature Store   │     │  Graph DB     │  │
│  │  (Kafka)         │────▶│  (Feast/Tecton)  │────▶│  (Neo4j)      │  │
│  └─────────────────┘     └─────────────────┘     └───────────────┘  │
│           │                       │                      │          │
│           ▼                       ▼                      ▼          │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │              REAL-TIME SCORING ENGINE (Flink)               │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌───────────────────┐   │    │
│  │  │ Rule Engine │  │ ML Ensemble │  │ GNN Embeddings    │   │    │
│  │  │ (Velocity)  │  │ (XGBoost)   │  │ (GraphSAGE+RGCN)  │   │    │
│  │  └─────────────┘  └─────────────┘  └───────────────────┘   │    │
│  └─────────────────────────────────────────────────────────────┘    │
│           │                                                         │
│           ▼                                                         │
│  ┌─────────────────┐     ┌─────────────────┐     ┌───────────────┐  │
│  │ Decision Engine │────▶│ Analyst Queue   │────▶│ Feedback Loop │  │
│  │ (Allow/Review/  │     │ (HITL Dashboard)│     │ (Active Learn)│  │
│  │  Decline)       │     └─────────────────┘     └───────────────┘  │
│  └─────────────────┘                                                │
└─────────────────────────────────────────────────────────────────────┘

Entity Types in Graph:
  ○ Account    ○ Device    ○ Address    ○ IP    ○ Card    ○ Phone/Email

Edge Types:
  ─── TRANSACTS_WITH    ─── SHARES_DEVICE    ─── USES_ADDRESS
  ─── LINKED_CARD       ─── SAME_NETWORK     ─── RECEIVES_SHIPMENT`}
          </pre>
        </div>
        
        <p className="text-slate-400 text-sm mt-4 italic">
          "Each layer strips away another mask. The rule engine catches the careless. 
          The ML ensemble catches the clever. The graph catches the organized."
        </p>
      </div>

      {/* Known vs Assumed */}
      <div className={`bg-gradient-to-r from-amber-900/20 to-orange-900/20 rounded-xl p-8 border border-amber-500/30 transition-all duration-500 delay-300 ${animatedItems.includes(3) ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
        <h3 className="text-xl font-semibold text-amber-400 mb-4">Known vs. Assumed</h3>
        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <h4 className="text-slate-100 font-medium mb-3">What We KNOW</h4>
            <ul className="text-slate-300 text-sm space-y-2">
              <li>• Physical goods must be delivered somewhere</li>
              <li>• AVS only checks numbers, not street names</li>
              <li>• Mule networks create graph structures</li>
              <li>• Reshippers add legitimate-looking intermediate hops</li>
              <li>• Ground truth labels arrive 30-90 days delayed</li>
              <li>• Fraud rate is highly imbalanced (~0.1-1%)</li>
            </ul>
          </div>
          <div>
            <h4 className="text-slate-100 font-medium mb-3">What We ASSUME</h4>
            <ul className="text-slate-300 text-sm space-y-2">
              <li>• Address patterns meaningfully differ fraud vs. legitimate</li>
              <li>• Fraudsters can't perfectly mimic local behavior</li>
              <li>• Graph structure reveals coordination</li>
              <li>• Historical patterns predict future attacks</li>
              <li>• Feature engineering captures relevant signals</li>
              <li>• ← These become our targets in Phase 2</li>
            </ul>
          </div>
        </div>
      </div>

      <div className="flex justify-end pt-4">
        <button 
          onClick={() => setActivePhase(1)}
          className="bg-amber-500 hover:bg-amber-400 text-slate-900 font-semibold px-8 py-3 rounded-lg transition-all hover:scale-105"
        >
          Challenge Assumptions →
        </button>
      </div>
    </div>
  );

  // ============================================================================
  // PHASE 1: CHALLENGE ASSUMPTIONS (WHY)
  // ============================================================================
  const AssumptionsPhase = () => (
    <div className="space-y-8">
      <div className="border-l-4 border-cyan-500 pl-6 py-2">
        <p className="text-cyan-400 font-mono text-sm tracking-widest">PHASE 2: CHALLENGE ASSUMPTIONS</p>
        <h2 className="text-3xl font-serif text-slate-100 mt-2">Why do we believe these detection approaches work?</h2>
        <p className="text-slate-400 mt-2 italic">
          "To find what is solid, first name what is sand."
        </p>
        <div className="mt-4">
          <ReferenceLink
            section="Prelude: Why First Principles?"
            anchor="prelude-why-first-principles"
            tooltip="The fundamental question: What must be true for detection to work?"
            className="text-sm"
          >
            The First Principles Approach
          </ReferenceLink>
        </div>
      </div>

      {/* Conventional Wisdom */}
      <div className={`bg-slate-800/50 rounded-xl p-8 border border-slate-700/50 transition-all duration-500 ${animatedItems.includes(0) ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
        <h3 className="text-xl font-semibold text-slate-100 mb-6 flex items-center gap-3">
          <span className="w-8 h-8 rounded-full bg-cyan-500/20 flex items-center justify-center text-cyan-400 text-sm">1</span>
          The Conventional Wisdom
        </h3>
        
        <div className="space-y-4">
          {[
            {
              belief: "Graph neural networks detect fraud rings because fraudsters share infrastructure",
              challenge: "But sophisticated rings deliberately avoid shared signals. Are we detecting only amateur operations?",
              question: "What if perfect operational security becomes achievable?"
            },
            {
              belief: "Mules can be identified by betweenness centrality in transaction graphs",
              challenge: "High-volume legitimate businesses also have high betweenness. We're flagging hubs, not necessarily mules.",
              question: "Can structural position alone distinguish malicious from legitimate intermediaries?"
            },
            {
              belief: "Address entry patterns reveal non-locals (typos, formatting)",
              challenge: "This assumes fraudsters type their own addresses. What about copy-paste? Autofill? Mule-provided details?",
              question: "How robust is the signal as fraudster tooling improves?"
            },
            {
              belief: "Velocity anomalies (many orders to one address) indicate fraud",
              challenge: "Gift registries, corporate shipping, events all create legitimate velocity spikes.",
              question: "Can we distinguish coordination from legitimate aggregation?"
            },
            {
              belief: "Reshippers are inherently suspicious",
              challenge: "Reshippers serve legitimate expats, travelers, and cross-border shoppers. Blanket suspicion creates massive false positives.",
              question: "What signals distinguish abuse from legitimate use?"
            }
          ].map((item, idx) => (
            <div key={idx} className="bg-slate-900/50 rounded-lg p-5">
              <div className="flex items-start gap-4">
                <span className="text-cyan-400 font-bold text-lg">?</span>
                <div>
                  <p className="text-cyan-300 font-medium">{item.belief}</p>
                  <p className="text-slate-400 text-sm mt-2">{item.challenge}</p>
                  <p className="text-amber-400 text-sm mt-2 italic">→ {item.question}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Ladder of Inference */}
      <div className={`bg-slate-800/50 rounded-xl p-8 border border-slate-700/50 transition-all duration-500 delay-100 ${animatedItems.includes(1) ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
        <h3 className="text-xl font-semibold text-slate-100 mb-6 flex items-center gap-3">
          <span className="w-8 h-8 rounded-full bg-cyan-500/20 flex items-center justify-center text-cyan-400 text-sm">2</span>
          Ladder of Inference: How Did We Get Here?
        </h3>
        
        <div className="bg-slate-900 rounded-lg p-6">
          <div className="flex flex-col items-center space-y-2">
            {[
              { level: "CONCLUSIONS", content: "GNNs are the best approach for address fraud", color: "red" },
              { level: "BELIEFS", content: "Network structure encodes fraud patterns", color: "orange" },
              { level: "ASSUMPTIONS", content: "Fraudsters must share some infrastructure", color: "yellow" },
              { level: "INTERPRETATIONS", content: "Connected accounts are suspicious", color: "green" },
              { level: "SELECTED DATA", content: "Focus on shared devices, IPs, addresses", color: "teal" },
              { level: "OBSERVABLE DATA", content: "Transaction logs, address records, chargebacks", color: "cyan" },
            ].map((item, idx) => (
              <div key={idx} className="w-full max-w-lg">
                <div className={`bg-${item.color}-900/30 border border-${item.color}-500/30 rounded-lg p-3 text-center`}>
                  <p className={`text-${item.color}-400 text-xs font-mono`}>{item.level}</p>
                  <p className="text-slate-200 text-sm mt-1">{item.content}</p>
                </div>
                {idx < 5 && <div className="text-center text-slate-600 py-1">↑</div>}
              </div>
            ))}
          </div>
          <p className="text-slate-400 text-sm mt-4 text-center italic">
            "At each rung, we added interpretation. The question: which rungs are solid?"
          </p>
        </div>
      </div>

      {/* Hidden Assumptions Grid */}
      <div className={`bg-slate-800/50 rounded-xl p-8 border border-slate-700/50 transition-all duration-500 delay-200 ${animatedItems.includes(2) ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
        <h3 className="text-xl font-semibold text-slate-100 mb-6 flex items-center gap-3">
          <span className="w-8 h-8 rounded-full bg-cyan-500/20 flex items-center justify-center text-cyan-400 text-sm">3</span>
          Hidden Assumptions Surfaced
        </h3>
        
        <div className="grid md:grid-cols-2 gap-4">
          <div className="bg-cyan-900/20 border border-cyan-500/30 rounded-lg p-4">
            <h4 className="text-cyan-400 font-medium">Physical Constraint Assumptions</h4>
            <ul className="text-slate-300 text-sm mt-2 space-y-1">
              <li>• Goods must be received at a physical location</li>
              <li>• Location correlates with fraud risk</li>
              <li>• Geographic distance implies relationship distance</li>
              <li className="text-amber-400">⚠ Weakened by: digital goods, VPNs, remote work</li>
            </ul>
          </div>
          
          <div className="bg-cyan-900/20 border border-cyan-500/30 rounded-lg p-4">
            <h4 className="text-cyan-400 font-medium">Behavioral Signal Assumptions</h4>
            <ul className="text-slate-300 text-sm mt-2 space-y-1">
              <li>• Typing patterns reveal identity/origin</li>
              <li>• Address formatting indicates local knowledge</li>
              <li>• Historical behavior predicts future behavior</li>
              <li className="text-amber-400">⚠ Weakened by: copy-paste, automation, GenAI</li>
            </ul>
          </div>
          
          <div className="bg-cyan-900/20 border border-cyan-500/30 rounded-lg p-4">
            <h4 className="text-cyan-400 font-medium">Network Structure Assumptions</h4>
            <ul className="text-slate-300 text-sm mt-2 space-y-1">
              <li>• Fraud rings share infrastructure</li>
              <li>• Mules have distinctive graph positions</li>
              <li>• Community detection finds fraud clusters</li>
              <li className="text-amber-400">⚠ Weakened by: operational security, burner infrastructure</li>
            </ul>
          </div>
          
          <div className="bg-cyan-900/20 border border-cyan-500/30 rounded-lg p-4">
            <h4 className="text-cyan-400 font-medium">Label Quality Assumptions</h4>
            <ul className="text-slate-300 text-sm mt-2 space-y-1">
              <li>• Chargebacks indicate true fraud</li>
              <li>• Friendly fraud is distinguishable</li>
              <li>• Ground truth eventually arrives</li>
              <li className="text-amber-400">⚠ Weakened by: label noise, 90-day delay, selection bias</li>
            </ul>
          </div>
        </div>
      </div>

      {/* First Principles vs Analogy */}
      <div className={`bg-gradient-to-r from-cyan-900/20 to-teal-900/20 rounded-xl p-8 border border-cyan-500/30 transition-all duration-500 delay-300 ${animatedItems.includes(3) ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
        <h3 className="text-xl font-semibold text-cyan-400 mb-4">Are We Reasoning From First Principles or Analogy?</h3>
        
        <div className="grid md:grid-cols-2 gap-6">
          <div className="bg-slate-900/50 rounded-lg p-4">
            <h4 className="text-red-400 font-medium mb-2">❌ Reasoning by Analogy</h4>
            <ul className="text-slate-300 text-sm space-y-2">
              <li>"PayPal uses GNNs, so we should too"</li>
              <li>"Stripe blocks reshippers, so we should too"</li>
              <li>"Industry standard is XGBoost + rules"</li>
              <li>"Everyone checks AVS match"</li>
            </ul>
          </div>
          
          <div className="bg-slate-900/50 rounded-lg p-4">
            <h4 className="text-emerald-400 font-medium mb-2">✓ Reasoning From Fundamentals</h4>
            <ul className="text-slate-300 text-sm space-y-2">
              <li>"Physical goods require physical receipt"</li>
              <li>"Information asymmetry creates detectable signals"</li>
              <li>"Coordinated behavior creates network structure"</li>
              <li>"Different goals produce different distributions"</li>
            </ul>
          </div>
        </div>
        
        <p className="text-slate-400 text-sm mt-4 italic">
          "The question is not 'What do others do?' but 'What must be true for detection to work?'"
        </p>
      </div>

      <div className="flex justify-between pt-4">
        <button 
          onClick={() => setActivePhase(0)}
          className="text-slate-400 hover:text-slate-200 font-medium px-6 py-3 transition-colors"
        >
          ← Back to Baseline
        </button>
        <button 
          onClick={() => setActivePhase(2)}
          className="bg-cyan-500 hover:bg-cyan-400 text-slate-900 font-semibold px-8 py-3 rounded-lg transition-all hover:scale-105"
        >
          Drill to Axioms →
        </button>
      </div>
    </div>
  );

  // ============================================================================
  // PHASE 2: DRILL TO AXIOMS (RECURSIVE WHYS)
  // ============================================================================
  const AxiomsPhase = () => {
    const axioms = [
      {
        id: 1,
        title: "AXIOM 1: Physical Materialization Requirement",
        statement: "Stolen physical goods must eventually exist at a location controlled by or accessible to the fraudster.",
        stoppingCriterion: "Physical Law (conservation of matter, locality)",
        confidence: "High",
        evidence: "Fundamental physics—objects cannot teleport. This is the irreducible constraint that forces address fraud to exist.",
        whyChain: [
          { q: "Why do fraudsters manipulate addresses?", a: "To receive stolen physical goods" },
          { q: "Why must they receive the goods?", a: "Physical goods have value only when possessed" },
          { q: "Why must goods be possessed to have value?", a: "They cannot be resold, used, or monetized without physical control" },
          { q: "Why can't goods be controlled without physical presence?", a: "Physical matter is localized—it exists in one place at a time" },
          { q: "Why is matter localized?", a: "FUNDAMENTAL PHYSICS → STOP (First Principle reached)" }
        ],
        implications: [
          "Every physical fraud has an 'endpoint'—the address where goods land",
          "Detection strategies can target this endpoint",
          "The address chain is the attack surface",
          "Digital goods bypass this axiom entirely"
        ]
      },
      {
        id: 2,
        title: "AXIOM 2: Information Asymmetry",
        statement: "Fraudsters operate with incomplete information about the cardholder, while systems can observe signals the fraudster cannot fully anticipate or control.",
        stoppingCriterion: "Information Theory (knowledge gaps)",
        confidence: "High",
        evidence: "Stolen credentials are a subset of identity. Fraudsters cannot know device history, behavioral patterns, typical addresses, relationship networks.",
        whyChain: [
          { q: "Why can address fraud be detected?", a: "Because fraudster behavior differs from legitimate behavior" },
          { q: "Why does fraudster behavior differ?", a: "They lack complete information about who they're impersonating" },
          { q: "Why do they lack complete information?", a: "Stolen credentials capture only explicit data, not implicit patterns" },
          { q: "Why can't they obtain implicit patterns?", a: "Behavioral history exists across systems they can't access; some signals are generated in real-time" },
          { q: "Why can't they access all systems?", a: "INFORMATION IS BOUNDED AND DISTRIBUTED → STOP (First Principle reached)" }
        ],
        implications: [
          "Features that capture 'what the fraudster can't know' are most valuable",
          "Device fingerprints, behavioral biometrics, relationship graphs exploit this",
          "As data breaches expand, this asymmetry shrinks",
          "The adversarial game is fundamentally about information"
        ]
      },
      {
        id: 3,
        title: "AXIOM 3: Goal Divergence",
        statement: "Fraudsters optimize for different objectives (speed, anonymity, value extraction) than legitimate customers (convenience, trust, relationship).",
        stoppingCriterion: "Economic/Game Theory (utility maximization)",
        confidence: "High",
        evidence: "Rational actors optimize for their utility function. Different utilities produce different observable behaviors.",
        whyChain: [
          { q: "Why do fraud patterns differ from legitimate patterns?", a: "Fraudsters have different goals" },
          { q: "Why do different goals matter?", a: "Goals shape behavior—optimization targets differ" },
          { q: "Why does optimization differ?", a: "Fraudsters maximize: speed (before detection), value (high-ticket items), anonymity (identity protection)" },
          { q: "Why these specific optimizations?", a: "Their utility function includes avoiding capture; legitimate users don't have this constraint" },
          { q: "Why do utility functions determine behavior?", a: "RATIONAL AGENT THEORY → STOP (First Principle reached)" }
        ],
        implications: [
          "High-value items with fast shipping are disproportionately targeted",
          "Anonymity-seeking behavior (reshippers, burner info) is a signal",
          "Rush orders combined with new addresses are suspicious",
          "The 'effort budget' of a fraudster constrains their attack surface"
        ]
      },
      {
        id: 4,
        title: "AXIOM 4: Network Effects of Coordination",
        statement: "Coordinated fraud creates structural patterns in relationship graphs that individual fraud does not—multiple actors sharing infrastructure leave network traces.",
        stoppingCriterion: "Graph Theory (emergent structure)",
        confidence: "High",
        evidence: "When multiple actors share devices, addresses, or payment methods, edges form in the relationship graph. These edges are absent in uncoordinated legitimate activity.",
        whyChain: [
          { q: "Why do GNNs detect fraud rings?", a: "Fraud rings create distinctive graph structures" },
          { q: "Why do they create distinctive structures?", a: "Coordination requires shared infrastructure" },
          { q: "Why does shared infrastructure create structure?", a: "Every shared element (device, address, IP) creates an edge in the relationship graph" },
          { q: "Why do edges reveal coordination?", a: "Unrelated legitimate actors don't share private infrastructure" },
          { q: "Why don't legitimate actors share infrastructure?", a: "SOCIAL NETWORK TOPOLOGY IS DETERMINED BY ACTUAL RELATIONSHIPS → STOP (First Principle reached)" }
        ],
        implications: [
          "Mule networks have characteristic betweenness centrality",
          "Community detection algorithms identify fraud clusters",
          "The more sophisticated the ring, the more operational security needed",
          "Counter-intuition: some fraud rings deliberately inject noise to break structure"
        ]
      },
      {
        id: 5,
        title: "AXIOM 5: Local Knowledge Encoding",
        statement: "Genuine local knowledge produces patterns (address formatting, terminology, timing) that are difficult to authentically replicate without actual local experience.",
        stoppingCriterion: "Cognitive Science (tacit knowledge)",
        confidence: "Medium",
        evidence: "Writing 'Tel Aviv' vs 'Telaviv' vs 'TLV' reveals local familiarity. Timing of orders reflects timezone. Abbreviation patterns are culturally specific.",
        whyChain: [
          { q: "Why can non-locals be detected from address entry?", a: "They make different errors than locals" },
          { q: "Why do non-locals make different errors?", a: "They lack tacit knowledge of local conventions" },
          { q: "Why is tacit knowledge location-specific?", a: "It's acquired through lived experience, not explicit learning" },
          { q: "Why can't tacit knowledge be perfectly simulated?", a: "The space of possible conventions is too large to research exhaustively" },
          { q: "Why is the space too large?", a: "CULTURAL KNOWLEDGE IS DISTRIBUTED AND IMPLICIT → STOP (First Principle reached)" }
        ],
        implications: [
          "Zip/city name frequency analysis detects outliers",
          "Keystroke timing and correction patterns reveal familiarity",
          "This axiom weakens as fraudsters use local mules",
          "Copy-paste and autofill can bypass this signal"
        ]
      },
      {
        id: 6,
        title: "AXIOM 6: Statistical Separability",
        statement: "Two populations with different underlying processes generate different probability distributions that can, in principle, be distinguished given sufficient data.",
        stoppingCriterion: "Statistical Theory (distribution divergence)",
        confidence: "High",
        evidence: "This is the mathematical foundation of all classification. If P(features|fraud) ≠ P(features|legitimate), a classifier can learn the boundary.",
        whyChain: [
          { q: "Why can ML detect address fraud?", a: "Fraud and legitimate transactions have different feature distributions" },
          { q: "Why are the distributions different?", a: "They're generated by actors with different information, goals, and constraints" },
          { q: "Why can different distributions be separated?", a: "Statistical theory: divergent distributions have non-overlapping regions" },
          { q: "Why does divergence enable classification?", a: "Classification finds decision boundaries that maximize separation" },
          { q: "Why do decision boundaries work?", a: "FUNDAMENTAL MATHEMATICS → STOP (First Principle reached)" }
        ],
        implications: [
          "Feature engineering should maximize distribution divergence",
          "Class imbalance affects where we can find boundary",
          "Adversarial attacks try to shift fraud distribution toward legitimate",
          "Perfect mimicry would make this axiom fail—but perfect mimicry is expensive"
        ]
      }
    ];

    return (
      <div className="space-y-8">
        <div className="border-l-4 border-violet-500 pl-6 py-2">
          <p className="text-violet-400 font-mono text-sm tracking-widest">PHASE 3: DRILL TO AXIOMS</p>
          <h2 className="text-3xl font-serif text-slate-100 mt-2">What are the irreducible foundations of address fraud detection?</h2>
          <p className="text-slate-400 mt-2 italic">
            "Ask 'why' until you hit bedrock. Then build upward with certainty."
          </p>
          <div className="mt-4">
            <ReferenceLink
              section="Part II: The Six Axioms"
              anchor="part-ii-the-six-axioms"
              tooltip="Comprehensive analysis of each axiom with proofs and failure modes"
              className="text-sm"
            >
              Complete Axiom Analysis
            </ReferenceLink>
          </div>
        </div>

        {/* Axiom Cards */}
        {axioms.map((axiom, idx) => (
          <div 
            key={axiom.id}
            className={`bg-slate-800/50 rounded-xl border border-slate-700/50 transition-all duration-500 ${animatedItems.includes(idx) ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}
          >
            <button 
              onClick={() => toggleAxiom(axiom.id)}
              className="w-full p-6 text-left flex items-center justify-between hover:bg-slate-700/20 transition-colors rounded-xl"
            >
              <div className="flex items-center gap-4 flex-1">
                <span className="w-10 h-10 rounded-full bg-violet-500/20 flex items-center justify-center text-violet-400 font-bold">
                  {axiom.id}
                </span>
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-semibold text-slate-100">{axiom.title}</h3>
                    <div className="ml-4">
                      <ReferenceLink
                        section={`Axiom ${axiom.id}`}
                        anchor={`axiom-${axiom.id}-${axiom.title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')}`}
                        tooltip={`Detailed analysis of ${axiom.title.split(': ')[1]}`}
                        className="text-xs"
                      >
                        Deep Dive
                      </ReferenceLink>
                    </div>
                  </div>
                  <p className="text-violet-400 text-sm mt-1">{axiom.stoppingCriterion} • Confidence: {axiom.confidence}</p>
                </div>
              </div>
              <span className={`text-2xl text-slate-400 transition-transform ${expandedAxioms[axiom.id] ? 'rotate-180' : ''}`}>
                ⌄
              </span>
            </button>
            
            {expandedAxioms[axiom.id] && (
              <div className="px-6 pb-6 space-y-4">
                {/* Statement */}
                <div className="bg-violet-900/20 border border-violet-500/30 rounded-lg p-4">
                  <p className="text-slate-200 font-medium">{axiom.statement}</p>
                </div>
                
                {/* Why Chain */}
                <div className="bg-slate-900/50 rounded-lg p-4">
                  <button 
                    onClick={() => toggleWhyChain(axiom.id)}
                    className="flex items-center gap-2 text-cyan-400 font-medium hover:text-cyan-300 transition-colors"
                  >
                    <span className={`transition-transform ${expandedWhyChains[axiom.id] ? 'rotate-90' : ''}`}>▶</span>
                    Show Recursive Why Chain (5 Whys)
                  </button>
                  
                  {expandedWhyChains[axiom.id] && (
                    <div className="mt-4 pl-4 border-l-2 border-violet-500/30 space-y-3">
                      {axiom.whyChain.map((step, i) => (
                        <div key={i} className="relative">
                          <span className="absolute -left-[9px] w-4 h-4 rounded-full bg-violet-500/50 text-xs flex items-center justify-center text-white">
                            {i + 1}
                          </span>
                          <div className="pl-4">
                            <p className="text-cyan-300 text-sm">{step.q}</p>
                            <p className="text-slate-300 text-sm mt-1">→ {step.a}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
                
                {/* Evidence */}
                <div className="bg-slate-900/50 rounded-lg p-4">
                  <h4 className="text-emerald-400 font-medium text-sm">Supporting Evidence</h4>
                  <p className="text-slate-400 text-sm mt-2">{axiom.evidence}</p>
                </div>
                
                {/* Implications */}
                <div className="bg-slate-900/50 rounded-lg p-4">
                  <h4 className="text-amber-400 font-medium text-sm">Implications for System Design</h4>
                  <ul className="text-slate-300 text-sm mt-2 space-y-1">
                    {axiom.implications.map((imp, i) => (
                      <li key={i}>• {imp}</li>
                    ))}
                  </ul>
                </div>
              </div>
            )}
          </div>
        ))}

        {/* Axiom Relationship Diagram */}
        <div className={`bg-slate-800/50 rounded-xl p-8 border border-slate-700/50 transition-all duration-500 ${animatedItems.includes(6) ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
          <h3 className="text-xl font-semibold text-slate-100 mb-6">How Axioms Combine: Dependency Graph</h3>
          
          <div className="bg-slate-900 rounded-lg p-6 font-mono text-sm">
            <pre className="text-slate-300 overflow-x-auto">
{`                    ┌─────────────────────────────────────┐
                    │  A6: STATISTICAL SEPARABILITY       │
                    │  (Mathematical foundation for ML)   │
                    └──────────────────┬──────────────────┘
                                       │
              ┌────────────────────────┼────────────────────────┐
              │                        │                        │
              ▼                        ▼                        ▼
┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐
│ A2: INFORMATION     │  │ A3: GOAL           │  │ A5: LOCAL          │
│ ASYMMETRY           │  │ DIVERGENCE          │  │ KNOWLEDGE          │
│ (What fraudster     │  │ (Different          │  │ (Tacit signals     │
│  can't know)        │  │  optimization)      │  │  reveal origin)    │
└─────────┬───────────┘  └─────────┬───────────┘  └─────────┬───────────┘
          │                        │                        │
          └────────────────────────┼────────────────────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    │                             │
                    ▼                             ▼
      ┌─────────────────────────┐  ┌─────────────────────────┐
      │ A1: PHYSICAL            │  │ A4: NETWORK             │
      │ MATERIALIZATION         │  │ EFFECTS                 │
      │ (Goods must land)       │  │ (Coordination creates   │
      │                         │  │  graph structure)       │
      └─────────────────────────┘  └─────────────────────────┘
                    │                             │
                    └──────────────┬──────────────┘
                                   │
                                   ▼
                    ┌─────────────────────────────┐
                    │   ADDRESS FRAUD DETECTION   │
                    │   BECOMES POSSIBLE          │
                    └─────────────────────────────┘`}
            </pre>
          </div>
          
          <p className="text-slate-400 text-sm mt-4 italic">
            "Remove any axiom, and a category of attack becomes undetectable."
          </p>
        </div>

        <div className="flex justify-between pt-4">
          <button 
            onClick={() => setActivePhase(1)}
            className="text-slate-400 hover:text-slate-200 font-medium px-6 py-3 transition-colors"
          >
            ← Back to Assumptions
          </button>
          <button 
            onClick={() => setActivePhase(3)}
            className="bg-violet-500 hover:bg-violet-400 text-slate-900 font-semibold px-8 py-3 rounded-lg transition-all hover:scale-105"
          >
            Understand Mechanisms →
          </button>
        </div>
      </div>
    );
  };

  // ============================================================================
  // PHASE 3: UNDERSTAND MECHANISMS (HOW)
  // ============================================================================
  const MechanismsPhase = () => (
    <div className="space-y-8">
      <div className="border-l-4 border-emerald-500 pl-6 py-2">
        <p className="text-emerald-400 font-mono text-sm tracking-widest">PHASE 4: UNDERSTAND MECHANISMS</p>
        <h2 className="text-3xl font-serif text-slate-100 mt-2">How do these axioms combine to enable detection?</h2>
        <p className="text-slate-400 mt-2 italic">
          "Now we rebuild from bedrock. Every layer justified by what lies beneath."
        </p>
        <div className="mt-4">
          <ReferenceLink
            section="Part III: From Axiom to Architecture"
            anchor="part-iii-from-axiom-to-architecture"
            tooltip="Complete technical implementation guide: GNNs, Entity Resolution, Real-time Scoring"
            className="text-sm"
          >
            Technical Implementation Guide
          </ReferenceLink>
        </div>
      </div>

      {/* Mechanism 1: Graph-Based Detection */}
      <div className={`bg-slate-800/50 rounded-xl p-8 border border-slate-700/50 transition-all duration-500 ${animatedItems.includes(0) ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
        <h3 className="text-xl font-semibold text-slate-100 mb-6 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="w-8 h-8 rounded-full bg-emerald-500/20 flex items-center justify-center text-emerald-400 text-sm">1</span>
            Graph Neural Networks for Fraud Ring Detection
          </div>
          <ReferenceLink
            section="The Graph Neural Network Pipeline"
            anchor="the-graph-neural-network-pipeline"
            tooltip="Detailed GNN architecture: GraphSAGE, RGCN, Temporal GNNs, and production considerations"
            className="text-xs"
          >
            Implementation Details
          </ReferenceLink>
        </h3>

        <p className="text-slate-300 mb-4">
          <strong className="text-emerald-300">Axioms Applied:</strong> A4 (Network Effects) + A6 (Statistical Separability)
          <span className="ml-4">
            <ReferenceLink
              section="Axiom 4: Network Effects of Coordination"
              anchor="axiom-4-network-effects-of-coordination"
              tooltip="Why coordinated fraud creates detectable graph patterns"
              className="text-xs"
            >
              A4 Details
            </ReferenceLink>
          </span>
        </p>
        
        <div className="grid md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <div className="bg-slate-900/50 rounded-lg p-4">
              <h4 className="text-emerald-400 font-medium mb-2">Why It Works (From First Principles)</h4>
              <ol className="text-slate-300 text-sm space-y-2">
                <li>1. Coordinated fraud requires shared infrastructure (A4)</li>
                <li>2. Shared infrastructure creates edges in relationship graph</li>
                <li>3. Edges encode information beyond single-transaction features</li>
                <li>4. GNNs aggregate neighbor information through message passing</li>
                <li>5. Node embeddings capture structural position + local features</li>
                <li>6. Different structures → different embeddings → separable (A6)</li>
              </ol>
            </div>
            
            <div className="bg-slate-900/50 rounded-lg p-4">
              <h4 className="text-emerald-400 font-medium mb-2">Architecture Choice Reasoning</h4>
              <div className="space-y-2 text-sm">
                <p className="text-slate-300"><strong className="text-cyan-300">GraphSAGE:</strong> Inductive learning—new nodes without retraining. Best for production where new accounts arrive constantly.</p>
                <p className="text-slate-300"><strong className="text-cyan-300">RGCN:</strong> Heterogeneous edges—models SHARED_DEVICE differently from SAME_ADDRESS. Essential for rich fraud graphs.</p>
                <p className="text-slate-300"><strong className="text-cyan-300">Temporal GNN:</strong> Time-aware—fraud patterns evolve. Captures "this connection is new" signal.</p>
              </div>
            </div>
          </div>
          
          <div className="bg-slate-900 rounded-lg p-4 font-mono text-xs">
            <p className="text-slate-500 mb-2"># Sequence Diagram: GNN Inference Pipeline</p>
            <pre className="text-slate-300 overflow-x-auto">
{`┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│ Event    │     │ Graph    │     │ GNN      │     │ Ensemble │
│ Ingestion│     │ DB       │     │ Engine   │     │ Model    │
└────┬─────┘     └────┬─────┘     └────┬─────┘     └────┬─────┘
     │                │                │                │
     │ Transaction    │                │                │
     ├───────────────▶│                │                │
     │                │                │                │
     │                │ Subgraph Query │                │
     │                ├───────────────▶│                │
     │                │                │                │
     │                │   2-hop        │                │
     │                │◀──────────────┤│                │
     │                │   Neighbors    │                │
     │                │                │                │
     │                │                │ Message Pass   │
     │                │                ├───────────────▶│
     │                │                │                │
     │                │                │   Embedding    │
     │                │                │◀──────────────┤│
     │                │                │   + Score      │
     │                │                │                │
     │◀───────────────┴────────────────┴────────────────│
     │              Risk Score (0-1)                    │
     ▼                                                  ▼`}
            </pre>
          </div>
        </div>
        
        <div className="mt-4 bg-amber-900/20 border border-amber-500/30 rounded-lg p-4">
          <h4 className="text-amber-400 font-medium mb-2">Feynman Test: Can You Explain This Simply?</h4>
          <p className="text-slate-300 text-sm">
            "Fraud rings are like friend groups—if person A shares a device with B, and B shares an address with C, 
            and C shares a card with D... they're probably working together. The GNN sees this 'friendship chain' 
            and says: 'You four are connected in ways strangers wouldn't be. That's suspicious.'"
          </p>
        </div>
      </div>

      {/* Mechanism 2: Entity Resolution */}
      <div className={`bg-slate-800/50 rounded-xl p-8 border border-slate-700/50 transition-all duration-500 delay-100 ${animatedItems.includes(1) ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
        <h3 className="text-xl font-semibold text-slate-100 mb-6 flex items-center gap-3">
          <span className="w-8 h-8 rounded-full bg-emerald-500/20 flex items-center justify-center text-emerald-400 text-sm">2</span>
          Entity Resolution for Identity Linking
        </h3>
        
        <p className="text-slate-300 mb-4">
          <strong className="text-emerald-300">Axioms Applied:</strong> A2 (Information Asymmetry) + A5 (Local Knowledge)
        </p>
        
        <div className="grid md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <div className="bg-slate-900/50 rounded-lg p-4">
              <h4 className="text-emerald-400 font-medium mb-2">Why It Works (From First Principles)</h4>
              <ol className="text-slate-300 text-sm space-y-2">
                <li>1. Fraudsters create multiple "identities" to avoid detection (A3)</li>
                <li>2. But they can't know all the subtle signals they leave (A2)</li>
                <li>3. Typos, formatting, timing patterns leak through (A5)</li>
                <li>4. Entity resolution links "John Smith" ≈ "J. Smith" ≈ "jsmith"</li>
                <li>5. Fuzzy matching catches deliberate variations</li>
                <li>6. Connected components reveal the true identity count</li>
              </ol>
            </div>
            
            <div className="bg-slate-900/50 rounded-lg p-4">
              <h4 className="text-emerald-400 font-medium mb-2">Algorithm Components</h4>
              <div className="space-y-2 text-sm">
                <p className="text-slate-300"><strong className="text-cyan-300">Levenshtein Distance:</strong> "123 Main St" ↔ "123 Main Street" = 4 edits</p>
                <p className="text-slate-300"><strong className="text-cyan-300">Soundex:</strong> "Smith" ↔ "Smyth" = S530 (phonetic match)</p>
                <p className="text-slate-300"><strong className="text-cyan-300">N-gram Similarity:</strong> "Acme Corp" ↔ "ACME Corporation" = high overlap</p>
                <p className="text-slate-300"><strong className="text-cyan-300">Graph Clustering:</strong> Connected components after fuzzy matching</p>
              </div>
            </div>
          </div>
          
          <div className="bg-slate-900 rounded-lg p-4 font-mono text-xs">
            <p className="text-slate-500 mb-2"># Activity Diagram: Entity Resolution Flow</p>
            <pre className="text-slate-300 overflow-x-auto">
{`                ┌─────────────────┐
                │  Raw Records    │
                │  (Addresses)    │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │  Normalize      │
                │  (Case, Abbrev) │
                └────────┬────────┘
                         │
            ┌────────────┼────────────┐
            │            │            │
            ▼            ▼            ▼
    ┌───────────┐ ┌───────────┐ ┌───────────┐
    │ Blocking  │ │ Blocking  │ │ Blocking  │
    │ (ZIP)     │ │ (City)    │ │ (Phone)   │
    └─────┬─────┘ └─────┬─────┘ └─────┬─────┘
          │             │             │
          └──────────┬──┴─────────────┘
                     │
                     ▼
           ┌─────────────────┐
           │  Pairwise       │
           │  Comparison     │
           │  (Fuzzy Match)  │
           └────────┬────────┘
                    │
                    ▼
           ┌─────────────────┐
           │  Threshold      │
           │  (sim > 0.85)   │
           └────────┬────────┘
                    │
                    ▼
           ┌─────────────────┐
           │  Connected      │
           │  Components     │
           └────────┬────────┘
                    │
                    ▼
           ┌─────────────────┐
           │  Entity IDs     │
           │  (Merged)       │
           └─────────────────┘`}
            </pre>
          </div>
        </div>
      </div>

      {/* Mechanism 3: Real-Time Streaming */}
      <div className={`bg-slate-800/50 rounded-xl p-8 border border-slate-700/50 transition-all duration-500 delay-200 ${animatedItems.includes(2) ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
        <h3 className="text-xl font-semibold text-slate-100 mb-6 flex items-center gap-3">
          <span className="w-8 h-8 rounded-full bg-emerald-500/20 flex items-center justify-center text-emerald-400 text-sm">3</span>
          Real-Time Streaming Architecture
        </h3>
        
        <p className="text-slate-300 mb-4">
          <strong className="text-emerald-300">Axioms Applied:</strong> A3 (Goal Divergence—speed) + A6 (Separability requires fresh data)
        </p>
        
        <div className="bg-slate-900 rounded-lg p-6 font-mono text-xs">
          <p className="text-slate-500 mb-2"># Component Diagram: Streaming Pipeline</p>
          <pre className="text-slate-300 overflow-x-auto">
{`┌────────────────────────────────────────────────────────────────────────────┐
│                        REAL-TIME FRAUD SCORING PIPELINE                     │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                  │
│  │   KAFKA      │───▶│   FLINK      │───▶│   REDIS      │                  │
│  │   Topics     │    │   Streaming  │    │   Feature    │                  │
│  │              │    │   Engine     │    │   Store      │                  │
│  │ • orders     │    │              │    │              │                  │
│  │ • addresses  │    │ • Window     │    │ • Address    │                  │
│  │ • devices    │    │   aggregates │    │   velocity   │                  │
│  └──────────────┘    │ • Joins      │    │ • Device     │                  │
│                      │ • Filters    │    │   history    │                  │
│                      └──────┬───────┘    └──────┬───────┘                  │
│                             │                   │                          │
│                             ▼                   ▼                          │
│                      ┌──────────────────────────────────┐                  │
│                      │      MODEL SERVING (Triton)      │                  │
│                      │                                   │                  │
│                      │  ┌─────────┐  ┌─────────┐        │                  │
│                      │  │ XGBoost │  │ GNN     │        │                  │
│                      │  │ Ensemble│  │ Embed   │        │                  │
│                      │  └────┬────┘  └────┬────┘        │                  │
│                      │       │            │             │                  │
│                      │       └─────┬──────┘             │                  │
│                      │             │                    │                  │
│                      │       ┌─────▼─────┐              │                  │
│                      │       │ Meta-Model│              │                  │
│                      │       │ (Stacking)│              │                  │
│                      │       └─────┬─────┘              │                  │
│                      └─────────────┼────────────────────┘                  │
│                                    │                                       │
│                                    ▼                                       │
│                      ┌──────────────────────────┐                          │
│                      │   DECISION ENGINE        │                          │
│                      │   • score < 0.3 → ALLOW  │                          │
│                      │   • score 0.3-0.7 → REVIEW│                         │
│                      │   • score > 0.7 → DECLINE│                          │
│                      └──────────────────────────┘                          │
│                                                                            │
│  LATENCY BUDGET:  Kafka(5ms) + Flink(20ms) + Redis(2ms) + Model(50ms)     │
│                   + Decision(3ms) = ~80ms total (target: <100ms)          │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘`}
          </pre>
        </div>
        
        <div className="mt-4 grid md:grid-cols-2 gap-4">
          <div className="bg-slate-900/50 rounded-lg p-4">
            <h4 className="text-emerald-400 font-medium mb-2">Why Streaming Matters (First Principles)</h4>
            <p className="text-slate-300 text-sm">
              Fraudsters optimize for speed (A3)—they want to extract value before detection. 
              Streaming enables fresh features: "This address had 0 orders yesterday, now 5 in 2 hours."
              Batch processing misses the velocity signal that makes detection possible.
            </p>
          </div>
          <div className="bg-slate-900/50 rounded-lg p-4">
            <h4 className="text-emerald-400 font-medium mb-2">Feature Freshness Trade-offs</h4>
            <div className="text-slate-300 text-sm space-y-1">
              <p>• <strong>Real-time (ms):</strong> Velocity, session patterns</p>
              <p>• <strong>Near-real-time (min):</strong> Graph embeddings, entity resolution</p>
              <p>• <strong>Batch (hours):</strong> Community detection, model retraining</p>
            </div>
          </div>
        </div>
      </div>

      {/* Mechanism 4: Feedback Loops */}
      <div className={`bg-slate-800/50 rounded-xl p-8 border border-slate-700/50 transition-all duration-500 delay-300 ${animatedItems.includes(3) ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
        <h3 className="text-xl font-semibold text-slate-100 mb-6 flex items-center gap-3">
          <span className="w-8 h-8 rounded-full bg-emerald-500/20 flex items-center justify-center text-emerald-400 text-sm">4</span>
          Human-in-the-Loop Feedback Mechanisms
        </h3>
        
        <p className="text-slate-300 mb-4">
          <strong className="text-emerald-300">Axioms Applied:</strong> A2 (Information Asymmetry) + Addressing Label Delay
        </p>
        
        <div className="grid md:grid-cols-2 gap-6">
          <div className="bg-slate-900/50 rounded-lg p-4">
            <h4 className="text-emerald-400 font-medium mb-2">The Delayed Feedback Problem</h4>
            <div className="text-slate-300 text-sm space-y-2">
              <p>Ground truth (chargebacks) arrives 30-90 days after transaction.</p>
              <p>During this "blind period," models can silently degrade.</p>
              <p><strong>First Principles Solution:</strong></p>
              <ul className="ml-4 space-y-1">
                <li>• Analyst labels provide immediate feedback signal</li>
                <li>• Active learning prioritizes most informative cases</li>
                <li>• Weak supervision generates pseudo-labels at scale</li>
              </ul>
            </div>
          </div>
          
          <div className="bg-slate-900/50 rounded-lg p-4">
            <h4 className="text-emerald-400 font-medium mb-2">Analyst Workflow Integration</h4>
            <div className="text-slate-300 text-sm space-y-2">
              <p><strong>Queue Prioritization:</strong></p>
              <ul className="ml-4 space-y-1">
                <li>• Uncertainty sampling: cases where model is least confident</li>
                <li>• Value-weighted: high-dollar uncertain cases first</li>
                <li>• Diversity sampling: cover feature space broadly</li>
              </ul>
              <p className="mt-2"><strong>Result:</strong> 75% reduction in labeling cost (Feedzai benchmark)</p>
            </div>
          </div>
        </div>
        
        <div className="mt-4 bg-slate-900 rounded-lg p-4 font-mono text-xs">
          <pre className="text-slate-300 overflow-x-auto">
{`┌────────────────────────────────────────────────────────────────┐
│              STATE MACHINE: FEEDBACK LOOP                       │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│   ┌─────────┐     ┌─────────────┐     ┌─────────────┐          │
│   │ SCORING │────▶│ UNCERTAINTY │────▶│ ANALYST     │          │
│   │         │     │ CHECK       │     │ QUEUE       │          │
│   └─────────┘     └──────┬──────┘     └──────┬──────┘          │
│        ▲                 │                   │                 │
│        │                 │ High Confidence   │ Label           │
│        │                 ▼                   ▼                 │
│        │          ┌─────────────┐     ┌─────────────┐          │
│        │          │ AUTO        │     │ FEEDBACK    │          │
│        │          │ DECISION    │     │ COLLECTION  │          │
│        │          └─────────────┘     └──────┬──────┘          │
│        │                                     │                 │
│        │                                     ▼                 │
│        │                              ┌─────────────┐          │
│        │                              │ RETRAIN     │          │
│        └──────────────────────────────│ PIPELINE    │          │
│                                       └─────────────┘          │
│                                                                │
│   Transition Rules:                                            │
│   • score ∈ [0.3, 0.7] → ANALYST_QUEUE                        │
│   • score < 0.3 → AUTO_ALLOW                                   │
│   • score > 0.7 → AUTO_DECLINE                                 │
│   • analyst_label → FEEDBACK_COLLECTION                        │
│   • accumulated_labels > threshold → RETRAIN                   │
│                                                                │
└────────────────────────────────────────────────────────────────┘`}
          </pre>
        </div>
      </div>

      {/* Causal Flow Diagram */}
      <div className={`bg-gradient-to-r from-emerald-900/20 to-teal-900/20 rounded-xl p-8 border border-emerald-500/30 transition-all duration-500 delay-400 ${animatedItems.includes(4) ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
        <h3 className="text-xl font-semibold text-emerald-400 mb-4">Complete Causal Flow: Axioms → Detection</h3>
        
        <div className="bg-slate-900 rounded-lg p-6 font-mono text-xs">
          <pre className="text-slate-300 overflow-x-auto">
{`AXIOM LAYER                    FEATURE LAYER                    MODEL LAYER
─────────────                   ─────────────                    ───────────

A1: Physical      ───────────▶  • Address exists                 ┐
    Materialization             • Delivery possible              │
                                • Commercial/Residential type    │
                                                                 │
A2: Information   ───────────▶  • Device fingerprint mismatch   │
    Asymmetry                   • Behavioral pattern deviation   │───▶ XGBoost
                                • Typing pattern anomalies       │     Ensemble
                                                                 │
A3: Goal          ───────────▶  • High-value items               │
    Divergence                  • Rush shipping                  │
                                • New address for existing user  ┘
                                
A4: Network       ───────────▶  • Shared device edges           ┐
    Effects                     • Address clustering             │───▶ GNN
                                • Betweenness centrality         │     Embeddings
                                                                 ┘
A5: Local         ───────────▶  • ZIP/City rarity score         ┐
    Knowledge                   • Abbreviation patterns          │───▶ Anomaly
                                • Timing consistency             │     Detection
                                                                 ┘
A6: Statistical   ───────────▶  [Enables all ML—provides mathematical foundation]
    Separability

                                                    │
                                                    ▼
                                           ┌───────────────┐
                                           │   META-MODEL  │
                                           │   (Stacking)  │
                                           └───────┬───────┘
                                                   │
                                                   ▼
                                           ┌───────────────┐
                                           │  RISK SCORE   │
                                           │   P(fraud)    │
                                           └───────────────┘`}
          </pre>
        </div>
      </div>

      <div className="flex justify-between pt-4">
        <button 
          onClick={() => setActivePhase(2)}
          className="text-slate-400 hover:text-slate-200 font-medium px-6 py-3 transition-colors"
        >
          ← Back to Axioms
        </button>
        <button 
          onClick={() => setActivePhase(4)}
          className="bg-emerald-500 hover:bg-emerald-400 text-slate-900 font-semibold px-8 py-3 rounded-lg transition-all hover:scale-105"
        >
          Explore Applications →
        </button>
      </div>
    </div>
  );

  // ============================================================================
  // PHASE 4: APPLICATION (WHERE/WHEN)
  // ============================================================================
  const ApplicationPhase = () => (
    <div className="space-y-8">
      <div className="border-l-4 border-pink-500 pl-6 py-2">
        <p className="text-pink-400 font-mono text-sm tracking-widest">PHASE 5: CONTEXTUALIZE & APPLY</p>
        <h2 className="text-3xl font-serif text-slate-100 mt-2">Where does this understanding apply—and where does it break?</h2>
        <p className="text-slate-400 mt-2 italic">
          "Every truth has its territory. Know the borders."
        </p>
        <div className="mt-4">
          <ReferenceLink
            section="Part IV: Boundaries and Failures"
            anchor="part-iv-boundaries-and-failures"
            tooltip="Comprehensive analysis of when axioms fail and how to adapt detection strategies"
            className="text-sm"
          >
            Failure Mode Analysis
          </ReferenceLink>
        </div>
      </div>

      {/* Boundary Conditions by Fraud Vector */}
      <div className={`bg-slate-800/50 rounded-xl p-8 border border-slate-700/50 transition-all duration-500 ${animatedItems.includes(0) ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
        <h3 className="text-xl font-semibold text-slate-100 mb-6 flex items-center gap-3">
          <span className="w-8 h-8 rounded-full bg-pink-500/20 flex items-center justify-center text-pink-400 text-sm">1</span>
          Detection Applicability by Fraud Vector
        </h3>
        
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-700">
                <th className="text-left py-3 px-4 text-pink-400">Fraud Vector</th>
                <th className="text-left py-3 px-4 text-pink-400">Primary Axioms</th>
                <th className="text-left py-3 px-4 text-pink-400">Detection Approach</th>
                <th className="text-left py-3 px-4 text-pink-400">Limitations</th>
              </tr>
            </thead>
            <tbody className="text-slate-300">
              <tr className="border-b border-slate-800">
                <td className="py-3 px-4 font-medium">Porch Piracy</td>
                <td className="py-3 px-4 text-slate-400">A1, A2</td>
                <td className="py-3 px-4">Address-level theft history, delivery timing optimization</td>
                <td className="py-3 px-4 text-amber-400">Post-transaction only; limited pre-auth signals</td>
              </tr>
              <tr className="border-b border-slate-800">
                <td className="py-3 px-4 font-medium">Mule Networks</td>
                <td className="py-3 px-4 text-slate-400">A4, A6</td>
                <td className="py-3 px-4">GNN embeddings, betweenness centrality, community detection</td>
                <td className="py-3 px-4 text-amber-400">Operational security can break graph signals</td>
              </tr>
              <tr className="border-b border-slate-800">
                <td className="py-3 px-4 font-medium">Reshipper Abuse</td>
                <td className="py-3 px-4 text-slate-400">A3, A4</td>
                <td className="py-3 px-4">Velocity analysis, cross-merchant patterns</td>
                <td className="py-3 px-4 text-amber-400">Legitimate reshippers create false positives</td>
              </tr>
              <tr className="border-b border-slate-800">
                <td className="py-3 px-4 font-medium">AVS Manipulation</td>
                <td className="py-3 px-4 text-slate-400">A2, A5</td>
                <td className="py-3 px-4">Address normalization, fuzzy matching, post-change tracking</td>
                <td className="py-3 px-4 text-amber-400">Only checks numbers; street names ignored</td>
              </tr>
              <tr className="border-b border-slate-800">
                <td className="py-3 px-4 font-medium">Triangulation</td>
                <td className="py-3 px-4 text-slate-400">A3, A6</td>
                <td className="py-3 px-4">Checkout timing, price arbitrage signals, seller patterns</td>
                <td className="py-3 px-4 text-amber-400">Customer is legitimate; hard to distinguish</td>
              </tr>
              <tr className="border-b border-slate-800">
                <td className="py-3 px-4 font-medium">Open House Fraud</td>
                <td className="py-3 px-4 text-slate-400">A1, A4</td>
                <td className="py-3 px-4">Address reuse clustering, property database cross-reference</td>
                <td className="py-3 px-4 text-amber-400">Requires external data (Airbnb, MLS)</td>
              </tr>
              <tr>
                <td className="py-3 px-4 font-medium">Post-Approval Changes</td>
                <td className="py-3 px-4 text-slate-400">A2, A3</td>
                <td className="py-3 px-4">Sequence models, NLP on support conversations</td>
                <td className="py-3 px-4 text-amber-400">Social engineering is hard to detect at scale</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* When Axioms Fail */}
      <div className={`bg-slate-800/50 rounded-xl p-8 border border-slate-700/50 transition-all duration-500 delay-100 ${animatedItems.includes(1) ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
        <h3 className="text-xl font-semibold text-slate-100 mb-6 flex items-center gap-3">
          <span className="w-8 h-8 rounded-full bg-pink-500/20 flex items-center justify-center text-pink-400 text-sm">2</span>
          Edge Cases: When Axioms Weaken or Fail
        </h3>
        
        <div className="grid md:grid-cols-2 gap-4">
          {[
            {
              axiom: "A1: Physical Materialization",
              weakness: "Digital Goods",
              explanation: "No physical address needed. Gift cards, software licenses, streaming subscriptions bypass this entirely.",
              mitigation: "Different feature set: email domain, IP geolocation, account age"
            },
            {
              axiom: "A2: Information Asymmetry",
              weakness: "Data Breaches at Scale",
              explanation: "Fullz packages include device IDs, behavioral patterns, social connections. The asymmetry shrinks.",
              mitigation: "Shift to real-time behavioral biometrics (harder to steal)"
            },
            {
              axiom: "A4: Network Effects",
              weakness: "Perfect OpSec",
              explanation: "Sophisticated rings use unique devices, addresses, IPs per transaction. No shared edges.",
              mitigation: "Higher-order patterns: timing correlation, transaction graph topology"
            },
            {
              axiom: "A5: Local Knowledge",
              weakness: "Copy-Paste & Automation",
              explanation: "Mules provide addresses; fraudsters copy-paste. No typing pattern signal.",
              mitigation: "Focus on content patterns, not entry patterns"
            },
            {
              axiom: "A6: Statistical Separability",
              weakness: "Perfect Mimicry",
              explanation: "GenAI can generate realistic behavioral sequences. Distributions converge.",
              mitigation: "Adversarial training, dynamic feature generation"
            }
          ].map((item, idx) => (
            <div key={idx} className="bg-slate-900/50 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <span className="text-red-400 text-lg">⚠</span>
                <div>
                  <h4 className="text-pink-400 font-medium">{item.axiom}</h4>
                  <p className="text-red-300 text-sm mt-1"><strong>Weakened by:</strong> {item.weakness}</p>
                  <p className="text-slate-400 text-sm mt-1">{item.explanation}</p>
                  <p className="text-emerald-400 text-sm mt-2"><strong>Mitigation:</strong> {item.mitigation}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Novel Applications */}
      <div className={`bg-slate-800/50 rounded-xl p-8 border border-slate-700/50 transition-all duration-500 delay-200 ${animatedItems.includes(2) ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
        <h3 className="text-xl font-semibold text-slate-100 mb-6 flex items-center gap-3">
          <span className="w-8 h-8 rounded-full bg-pink-500/20 flex items-center justify-center text-pink-400 text-sm">3</span>
          Novel Applications: Where Else Do These Axioms Apply?
        </h3>
        
        <div className="grid md:grid-cols-3 gap-4">
          <div className="bg-gradient-to-br from-violet-900/30 to-purple-900/30 rounded-lg p-4 border border-violet-500/30">
            <h4 className="text-violet-400 font-medium mb-2">Money Mule Detection</h4>
            <p className="text-slate-300 text-sm">Same A4 (Network Effects) + A3 (Goal Divergence). Money flows have graph structure; mules optimize for throughput, not relationship building.</p>
            <p className="text-violet-300 text-sm mt-2 italic">Key transfer: betweenness centrality identifies fund intermediaries</p>
          </div>
          
          <div className="bg-gradient-to-br from-cyan-900/30 to-blue-900/30 rounded-lg p-4 border border-cyan-500/30">
            <h4 className="text-cyan-400 font-medium mb-2">Account Takeover Prevention</h4>
            <p className="text-slate-300 text-sm">A2 (Information Asymmetry) + A5 (Local Knowledge). Attackers don't know victim's typical device, location, or timing patterns.</p>
            <p className="text-cyan-300 text-sm mt-2 italic">Key transfer: behavioral biometrics, session fingerprinting</p>
          </div>
          
          <div className="bg-gradient-to-br from-emerald-900/30 to-green-900/30 rounded-lg p-4 border border-emerald-500/30">
            <h4 className="text-emerald-400 font-medium mb-2">Synthetic Identity Detection</h4>
            <p className="text-slate-300 text-sm">A4 (Network Effects) + A6 (Separability). Synthetic identities share PII elements; graphs reveal impossible combinations.</p>
            <p className="text-emerald-300 text-sm mt-2 italic">Key transfer: entity resolution exposes synthetic clusters</p>
          </div>
        </div>
      </div>

      {/* Regulatory Considerations */}
      <div className={`bg-gradient-to-r from-pink-900/20 to-rose-900/20 rounded-xl p-8 border border-pink-500/30 transition-all duration-500 delay-300 ${animatedItems.includes(3) ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
        <h3 className="text-xl font-semibold text-pink-400 mb-4">Regulatory Boundaries</h3>
        
        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <h4 className="text-slate-100 font-medium mb-3">BSA/AML Requirements (Mule Detection)</h4>
            <ul className="text-slate-300 text-sm space-y-2">
              <li>• <strong>SAR filing deadlines:</strong> 30 days (60 with extension)</li>
              <li>• <strong>Mule triggers:</strong> ACH from unrelated sources + rapid withdrawal</li>
              <li>• <strong>FinCEN 2024 rule:</strong> "Effective" AML programs need demonstrable ML performance</li>
              <li>• <strong>Audit trail:</strong> All decisions must be logged for examination</li>
            </ul>
          </div>
          <div>
            <h4 className="text-slate-100 font-medium mb-3">GDPR Constraints (EU Operations)</h4>
            <ul className="text-slate-300 text-sm space-y-2">
              <li>• <strong>Article 6(1)(f):</strong> Fraud prevention as legitimate interest</li>
              <li>• <strong>Article 22:</strong> Right to explanation for automated decisions</li>
              <li>• <strong>Data minimization:</strong> Collect only what's necessary</li>
              <li>• <strong>EU AI Act (2026):</strong> Mandatory explainability for high-risk systems</li>
            </ul>
          </div>
        </div>
        
        <p className="text-slate-400 text-sm mt-4 italic">
          "Explainability is not optional. SHAP provides both analyst insight and regulatory compliance."
        </p>
      </div>

      <div className="flex justify-between pt-4">
        <button 
          onClick={() => setActivePhase(3)}
          className="text-slate-400 hover:text-slate-200 font-medium px-6 py-3 transition-colors"
        >
          ← Back to Mechanisms
        </button>
        <button 
          onClick={() => setActivePhase(5)}
          className="bg-pink-500 hover:bg-pink-400 text-slate-900 font-semibold px-8 py-3 rounded-lg transition-all hover:scale-105"
        >
          Test Understanding →
        </button>
      </div>
    </div>
  );

  // ============================================================================
  // PHASE 5: SYNTHESIS (TEST UNDERSTANDING)
  // ============================================================================
  const SynthesisPhase = () => {
    const quizQuestions = [
      {
        id: 1,
        question: "Which axiom is MOST directly violated when a fraud ring uses perfect operational security (unique device, IP, address per transaction)?",
        options: [
          "A1: Physical Materialization",
          "A4: Network Effects",
          "A5: Local Knowledge",
          "A6: Statistical Separability"
        ],
        correct: 1,
        explanation: "A4 (Network Effects) depends on shared infrastructure creating graph edges. Perfect OpSec eliminates these edges, making the ring invisible to graph analysis."
      },
      {
        id: 2,
        question: "A fraudster uses a legitimate reshipper to forward packages. Which detection approach is MOST effective?",
        options: [
          "AVS matching (numbers only)",
          "Velocity analysis across reshippers",
          "Device fingerprint matching",
          "Keystroke pattern analysis"
        ],
        correct: 1,
        explanation: "Velocity analysis (many orders to same reshipper) leverages A4 (coordination creates patterns) while distinguishing abuse from legitimate use through volume anomalies."
      },
      {
        id: 3,
        question: "Why does the ZIP/city frequency analysis detect mules (e.g., 'Telaviv' vs 'Tel Aviv')?",
        options: [
          "Because mules always misspell addresses",
          "Because non-locals lack tacit knowledge of local conventions (A5)",
          "Because graph structure reveals the mule",
          "Because AVS fails on non-standard formatting"
        ],
        correct: 1,
        explanation: "This exploits A5 (Local Knowledge). Non-locals don't know the common spelling variations locals use, producing statistically rare combinations."
      },
      {
        id: 4,
        question: "What is the FUNDAMENTAL reason GNNs outperform transaction-level ML for fraud ring detection?",
        options: [
          "GNNs are newer and more advanced",
          "GNNs can process more features",
          "GNNs capture relational information invisible to row-based models (A4)",
          "GNNs are faster at inference"
        ],
        correct: 2,
        explanation: "GNNs aggregate neighbor information through message passing, capturing the network structure that A4 tells us fraud rings create. This information doesn't exist in individual transaction features."
      },
      {
        id: 5,
        question: "A bank's fraud model has high AUC-ROC (0.98) but low AUC-PR (0.10). What does this indicate?",
        options: [
          "The model is excellent and ready for production",
          "The model catches fraud well but has too many false positives",
          "The model is overfitting to the training data",
          "The dataset has extreme class imbalance, and ROC is misleading"
        ],
        correct: 3,
        explanation: "With ~0.1% fraud rate, ROC-AUC can look great even for weak models. PR-AUC focuses on minority class performance. Low PR-AUC means the model struggles to find fraud without excessive false alarms."
      }
    ];

    const handleQuizAnswer = (questionId, answerIdx) => {
      setQuizAnswers(prev => ({ ...prev, [questionId]: answerIdx }));
    };

    const calculateScore = () => {
      let correct = 0;
      quizQuestions.forEach(q => {
        if (quizAnswers[q.id] === q.correct) correct++;
      });
      return correct;
    };

    return (
      <div className="space-y-8">
        <div className="border-l-4 border-indigo-500 pl-6 py-2">
          <p className="text-indigo-400 font-mono text-sm tracking-widest">PHASE 6: SYNTHESIS</p>
          <h2 className="text-3xl font-serif text-slate-100 mt-2">Test Your First Principles Understanding</h2>
          <p className="text-slate-400 mt-2 italic">
            "Understanding is not memory. It is the ability to rebuild."
          </p>
          <div className="mt-4 flex gap-3">
            <ReferenceLink
              section="Part V: The Analyst's Role"
              anchor="part-v-the-analysts-role"
              tooltip="How analysts work with automated detection systems"
              className="text-sm"
            >
              Analyst Guide
            </ReferenceLink>
            <ReferenceLink
              section="Part VI: Metrics That Matter"
              anchor="part-vi-metrics-that-matter"
              tooltip="Evaluation metrics for fraud detection: AUC-PR, cost-sensitive evaluation, drift detection"
              className="text-sm"
            >
              Metrics Guide
            </ReferenceLink>
            <ReferenceLink
              section="Part VII: Regulatory Context"
              anchor="part-vii-regulatory-context"
              tooltip="BSA/AML, GDPR, and EU AI Act compliance considerations"
              className="text-sm"
            >
              Regulatory Guide
            </ReferenceLink>
          </div>
        </div>

        {/* Quiz Section */}
        <div className={`bg-slate-800/50 rounded-xl p-8 border border-slate-700/50 transition-all duration-500 ${animatedItems.includes(0) ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
          <h3 className="text-xl font-semibold text-slate-100 mb-6">Comprehension Check</h3>
          
          <div className="space-y-6">
            {quizQuestions.map((q, idx) => (
              <div key={q.id} className="bg-slate-900/50 rounded-lg p-5">
                <p className="text-slate-200 font-medium mb-4">{idx + 1}. {q.question}</p>
                <div className="space-y-2">
                  {q.options.map((option, optIdx) => (
                    <button
                      key={optIdx}
                      onClick={() => handleQuizAnswer(q.id, optIdx)}
                      className={`w-full text-left p-3 rounded-lg border transition-all ${
                        quizAnswers[q.id] === optIdx
                          ? showResults
                            ? optIdx === q.correct
                              ? 'bg-emerald-900/30 border-emerald-500 text-emerald-300'
                              : 'bg-red-900/30 border-red-500 text-red-300'
                            : 'bg-indigo-900/30 border-indigo-500 text-indigo-300'
                          : showResults && optIdx === q.correct
                            ? 'bg-emerald-900/20 border-emerald-500/50 text-emerald-400'
                            : 'border-slate-700 text-slate-400 hover:border-slate-500 hover:text-slate-300'
                      }`}
                    >
                      {String.fromCharCode(65 + optIdx)}. {option}
                    </button>
                  ))}
                </div>
                {showResults && (
                  <div className={`mt-4 p-3 rounded-lg ${quizAnswers[q.id] === q.correct ? 'bg-emerald-900/20 border border-emerald-500/30' : 'bg-amber-900/20 border border-amber-500/30'}`}>
                    <p className={`text-sm ${quizAnswers[q.id] === q.correct ? 'text-emerald-300' : 'text-amber-300'}`}>
                      <strong>Explanation:</strong> {q.explanation}
                    </p>
                  </div>
                )}
              </div>
            ))}
          </div>
          
          <div className="mt-6 flex items-center justify-between">
            <button
              onClick={() => setShowResults(true)}
              className="bg-indigo-500 hover:bg-indigo-400 text-slate-900 font-semibold px-6 py-2 rounded-lg transition-all"
            >
              Check Answers
            </button>
            {showResults && (
              <div className="text-slate-200">
                Score: <span className="text-indigo-400 font-bold">{calculateScore()}/{quizQuestions.length}</span>
              </div>
            )}
          </div>
        </div>

        {/* Uncertainty Register */}
        <div className={`bg-slate-800/50 rounded-xl p-8 border border-slate-700/50 transition-all duration-500 delay-100 ${animatedItems.includes(1) ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
          <h3 className="text-xl font-semibold text-slate-100 mb-6">Uncertainty Register: What Remains Unknown</h3>
          
          <div className="grid md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <h4 className="text-slate-100 font-medium">Axioms That Might Be Assumptions</h4>
              <div className="text-slate-300 text-sm space-y-2">
                <p>• <strong>A4 (Network Effects):</strong> As GenAI generates synthetic identities with believable patterns, will graph signals remain reliable?</p>
                <p>• <strong>A5 (Local Knowledge):</strong> Large language models can now generate culturally appropriate address formats. Is this signal dying?</p>
                <p>• <strong>A6 (Separability):</strong> If adversarial ML becomes accessible, can fraudsters train against our models?</p>
              </div>
            </div>
            
            <div className="space-y-4">
              <h4 className="text-slate-100 font-medium">Recommended Areas for Investigation</h4>
              <div className="text-slate-300 text-sm space-y-2">
                <p>• <strong>Causal inference:</strong> Do our features CAUSE fraud flags, or just correlate with true indicators?</p>
                <p>• <strong>Adversarial robustness:</strong> How do models degrade under targeted attacks? What's the security margin?</p>
                <p>• <strong>Fairness audits:</strong> Do address-based models exhibit disparate impact across demographic groups?</p>
                <p>• <strong>Temporal stability:</strong> How fast do fraud tactics evolve? What's the model half-life?</p>
              </div>
            </div>
          </div>
        </div>

        {/* The Irreducible Core */}
        <div className={`bg-gradient-to-r from-violet-900/30 to-indigo-900/30 rounded-xl p-8 border border-violet-500/30 transition-all duration-500 ${animatedItems.includes(2) ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
          <h3 className="text-xl font-semibold text-violet-400 mb-4">The Irreducible Core</h3>
          <p className="text-slate-300 leading-relaxed">
            Address manipulation fraud detection, at its foundation, exploits a small set of bedrock truths:
          </p>
          <div className="grid md:grid-cols-2 gap-4 mt-4">
            <div className="text-slate-300 text-sm space-y-1">
              <p>1. Physical goods must materialize somewhere</p>
              <p>2. Fraudsters operate with incomplete information</p>
              <p>3. Different goals produce different behaviors</p>
            </div>
            <div className="text-slate-300 text-sm space-y-1">
              <p>4. Coordination creates network structure</p>
              <p>5. Local knowledge is hard to fake perfectly</p>
              <p>6. Different distributions can be separated</p>
            </div>
          </div>
          <p className="text-violet-300 text-sm mt-6 italic">
            "The art of fraud detection is not in choosing algorithms. It is in identifying which axioms apply to your context, 
            designing features that probe those axioms, and building systems that adapt as fraudsters evolve. 
            Everything else is implementation detail."
          </p>
        </div>

        <div className="flex justify-between pt-4">
          <button 
            onClick={() => setActivePhase(4)}
            className="text-slate-400 hover:text-slate-200 font-medium px-6 py-3 transition-colors"
          >
            ← Back to Application
          </button>
          <button 
            onClick={() => setActivePhase(0)}
            className="bg-indigo-500 hover:bg-indigo-400 text-slate-900 font-semibold px-8 py-3 rounded-lg transition-all hover:scale-105"
          >
            Start Over →
          </button>
        </div>
      </div>
    );
  };

  // ============================================================================
  // MAIN RENDER
  // ============================================================================
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-slate-100">
      {/* Background texture */}
      <div className="fixed inset-0 opacity-30">
        <div className="absolute inset-0" style={{
          backgroundImage: `radial-gradient(circle at 25% 25%, rgba(251, 191, 36, 0.03) 0%, transparent 50%),
                           radial-gradient(circle at 75% 75%, rgba(139, 92, 246, 0.03) 0%, transparent 50%)`
        }}></div>
      </div>

      <div className="relative z-10">
        {/* Header */}
        <header className="border-b border-slate-800/50 bg-slate-900/80 backdrop-blur-sm sticky top-0 z-50">
          <div className="max-w-6xl mx-auto px-6 py-6">
            <div className="flex items-center justify-between gap-4 mb-4">
              <div className="flex items-center gap-4">
                {onBack && (
                  <button
                    onClick={onBack}
                    className="text-slate-400 hover:text-slate-200 transition-colors mr-2"
                    title="Back to Home"
                  >
                    ←
                  </button>
                )}
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-amber-500 to-violet-600 flex items-center justify-center">
                  <span className="text-2xl">📦</span>
                </div>
                <div>
                  <h1 className="text-2xl font-serif text-slate-100">Address Manipulation & Shipping Fraud: From Axioms to Detection</h1>
                </div>
              </div>
              {onBack && (
                <button
                  onClick={onBack}
                  className="bg-amber-500 hover:bg-amber-400 text-slate-900 font-semibold px-4 py-2 rounded-lg transition-all hover:scale-105"
                  title="Go to Home"
                >
                  Home
                </button>
              )}
            </div>
            
            {/* Phase Navigation */}
            <div className="flex gap-1 overflow-x-auto pb-2">
              {phases.map((phase) => (
                <button
                  key={phase.id}
                  onClick={() => setActivePhase(phase.id)}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg whitespace-nowrap transition-all ${
                    activePhase === phase.id
                      ? 'bg-gradient-to-r from-amber-500/20 to-violet-500/20 text-slate-100 border border-amber-500/30'
                      : 'text-slate-500 hover:text-slate-300 hover:bg-slate-800/50'
                  }`}
                >
                  <span className="text-lg">{phase.icon}</span>
                  <div className="text-left">
                    <p className="text-xs font-mono">{phase.name}</p>
                    <p className="text-sm">{phase.label}</p>
                  </div>
                </button>
              ))}
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-6xl mx-auto px-6 py-8">
          {activePhase === 0 && <BaselinePhase />}
          {activePhase === 1 && <AssumptionsPhase />}
          {activePhase === 2 && <AxiomsPhase />}
          {activePhase === 3 && <MechanismsPhase />}
          {activePhase === 4 && <ApplicationPhase />}
          {activePhase === 5 && <SynthesisPhase />}
        </main>

        {/* Comprehensive Reference Panel */}
        <footer className="max-w-6xl mx-auto px-6 pb-8">
          <div className="bg-slate-800/30 border border-slate-700/50 rounded-xl p-6">
            <h3 className="text-xl font-semibold text-slate-100 mb-6 text-center flex items-center justify-center gap-3">
              <span className="text-2xl">📚</span>
              Complete Reference Guide
              <span className="text-2xl">📚</span>
            </h3>

            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {/* Fundamentals */}
              <div className="space-y-3">
                <h4 className="text-lg font-medium text-amber-400 border-b border-amber-500/30 pb-2">🎯 Fundamentals</h4>
                <div className="space-y-2">
                  <ReferenceLink
                    section="Prelude: Why First Principles?"
                    anchor="prelude-why-first-principles"
                    tooltip="The philosophical foundation: asking 'why' until you hit bedrock"
                    className="block w-full text-sm"
                  >
                    First Principles Approach
                  </ReferenceLink>
                  <ReferenceLink
                    section="Part I: The Seven Rivers of Theft"
                    anchor="part-i-the-seven-rivers-of-theft"
                    tooltip="Complete analysis of all seven fraud attack vectors"
                    className="block w-full text-sm"
                  >
                    Seven Fraud Vectors
                  </ReferenceLink>
                  <ReferenceLink
                    section="Part II: The Six Axioms"
                    anchor="part-ii-the-six-axioms"
                    tooltip="The irreducible foundations that make address fraud detectable"
                    className="block w-full text-sm"
                  >
                    Core Axioms
                  </ReferenceLink>
                </div>
              </div>

              {/* Technical Implementation */}
              <div className="space-y-3">
                <h4 className="text-lg font-medium text-emerald-400 border-b border-emerald-500/30 pb-2">⚙️ Implementation</h4>
                <div className="space-y-2">
                  <ReferenceLink
                    section="The Graph Neural Network Pipeline"
                    anchor="the-graph-neural-network-pipeline"
                    tooltip="Complete GNN implementation: GraphSAGE, RGCN, Temporal GNNs"
                    className="block w-full text-sm"
                  >
                    Graph Neural Networks
                  </ReferenceLink>
                  <ReferenceLink
                    section="Entity Resolution: Linking the Fragments"
                    anchor="entity-resolution-linking-the-fragments"
                    tooltip="Machine learning techniques for linking fragmented identities"
                    className="block w-full text-sm"
                  >
                    Entity Resolution
                  </ReferenceLink>
                  <ReferenceLink
                    section="Real-Time Scoring: The Streaming Architecture"
                    anchor="real-time-scoring-the-streaming-architecture"
                    tooltip="Production architecture: Kafka, Flink, Redis, Model Serving"
                    className="block w-full text-sm"
                  >
                    Real-time Systems
                  </ReferenceLink>
                  <ReferenceLink
                    section="Appendix B: Technology Stack Recommendations"
                    anchor="appendix-b-technology-stack-recommendations"
                    tooltip="Recommended tools and technologies for each component"
                    className="block w-full text-sm"
                  >
                    Technology Stack
                  </ReferenceLink>
                </div>
              </div>

              {/* Advanced Topics */}
              <div className="space-y-3">
                <h4 className="text-lg font-medium text-violet-400 border-b border-violet-500/30 pb-2">🧠 Advanced</h4>
                <div className="space-y-2">
                  <ReferenceLink
                    section="Part IV: Boundaries and Failures"
                    anchor="part-iv-boundaries-and-failures"
                    tooltip="When axioms fail: digital goods, fullz economy, operational security"
                    className="block w-full text-sm"
                  >
                    Failure Modes
                  </ReferenceLink>
                  <ReferenceLink
                    section="Part V: The Analyst's Role"
                    anchor="part-v-the-analysts-role"
                    tooltip="Human-in-the-loop: active learning, feedback, collaboration"
                    className="block w-full text-sm"
                  >
                    Analyst Integration
                  </ReferenceLink>
                  <ReferenceLink
                    section="Part VI: Metrics That Matter"
                    anchor="part-vi-metrics-that-matter"
                    tooltip="Evaluation metrics: AUC-PR, cost-sensitive evaluation, drift detection"
                    className="block w-full text-sm"
                  >
                    Evaluation Metrics
                  </ReferenceLink>
                  <ReferenceLink
                    section="Part VII: Regulatory Context"
                    anchor="part-vii-regulatory-context"
                    tooltip="BSA/AML compliance, GDPR considerations, EU AI Act requirements"
                    className="block w-full text-sm"
                  >
                    Regulatory Compliance
                  </ReferenceLink>
                </div>
              </div>

              {/* Quick Reference */}
              <div className="space-y-3 md:col-span-2 lg:col-span-3">
                <h4 className="text-lg font-medium text-cyan-400 border-b border-cyan-500/30 pb-2 text-center">🔍 Quick Reference</h4>
                <div className="grid md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <ReferenceLink
                      section="Appendix A: Key Formulas and Queries"
                      anchor="appendix-a-key-formulas-and-queries"
                      tooltip="SQL queries, mathematical formulas, and implementation snippets"
                      className="block w-full text-sm"
                    >
                      📐 Formulas & Queries
                    </ReferenceLink>
                    <ReferenceLink
                      section="Appendix C: Further Reading"
                      anchor="appendix-c-further-reading"
                      tooltip="Academic papers, industry resources, and recommended books"
                      className="block w-full text-sm"
                    >
                      📚 Further Reading
                    </ReferenceLink>
                  </div>
                  <div className="space-y-2">
                    <ReferenceLink
                      section="Coda: The Irreducible Core"
                      anchor="coda-the-irreducible-core"
                      tooltip="Summary of the six fundamental truths of address fraud detection"
                      className="block w-full text-sm"
                    >
                      💎 Core Principles Summary
                    </ReferenceLink>
                  </div>
                </div>
              </div>
            </div>

            <div className="mt-6 pt-4 border-t border-slate-700/30 text-center">
              <p className="text-slate-400 text-sm italic">
                "The drop that enters the sea does not vanish. It becomes the sea."
              </p>
              <p className="text-slate-500 text-xs mt-2">
                Complete companion documentation: {COMPANION_MD_BASE_URL.split('/').pop()}
              </p>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
};

export default AddressFraudFirstPrinciplesGuide;

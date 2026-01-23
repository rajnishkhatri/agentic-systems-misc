import React, { useState, useEffect } from 'react';

// ============================================================================
// FIRST PRINCIPLES DEEP DIVE: STOLEN CREDIT CARD FRAUD DETECTION
// A recursive exploration from surface knowledge to irreducible axioms
// For AI Architects and Fraud Analysts
// ============================================================================

const StolenCardFraudFirstPrinciplesGuide = ({ onBack }) => {
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
        <h2 className="text-3xl font-serif text-slate-100 mt-2">What is Stolen Credit Card Fraud Detection at its most literal level?</h2>
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
              <h4 className="text-amber-400 font-medium mb-3">What Is Stolen Card Fraud?</h4>
              <p className="text-slate-300 leading-relaxed">
                <span className="text-amber-300">Stolen credit card fraud</span> is the unauthorized use of credit card credentials 
                (card number, expiration date, CVV, cardholder name) by someone other than the legitimate cardholder to purchase goods or services.
              </p>
              <div className="mt-4 p-4 bg-slate-800/50 rounded-lg font-mono text-sm">
                <p className="text-slate-400">// At its most literal:</p>
                <p className="text-amber-300">INPUT:  Transaction features</p>
                <p className="text-emerald-300">PROCESS: Mathematical transformation</p>
                <p className="text-violet-300">OUTPUT: P(fraud) ∈ [0, 1]</p>
              </div>
            </div>
            
            <div className="bg-slate-900/50 rounded-lg p-5">
              <h4 className="text-amber-400 font-medium mb-3">The Transaction Event (What We Observe)</h4>
              <ul className="text-slate-300 space-y-2">
                <li className="flex items-start gap-2"><span className="text-amber-500">→</span> Card credentials (PAN, expiry, CVV, BIN)</li>
                <li className="flex items-start gap-2"><span className="text-amber-500">→</span> Transaction details (amount, MCC, merchant ID)</li>
                <li className="flex items-start gap-2"><span className="text-amber-500">→</span> Device fingerprint (browser hash, device ID)</li>
                <li className="flex items-start gap-2"><span className="text-amber-500">→</span> Network identity (IP, ASN, geolocation)</li>
                <li className="flex items-start gap-2"><span className="text-amber-500">→</span> Behavioral signals (keystroke, session patterns)</li>
                <li className="flex items-start gap-2"><span className="text-amber-500">→</span> Historical context (velocity, typical merchants)</li>
              </ul>
            </div>
          </div>

          <div className="space-y-4">
            <div className="bg-slate-900/50 rounded-lg p-5">
              <h4 className="text-amber-400 font-medium mb-3">Industry State (2025)</h4>
              <div className="grid grid-cols-2 gap-4 text-center">
                <div className="bg-slate-800 rounded-lg p-4">
                  <div className="text-2xl font-bold text-amber-400">0.1-1%</div>
                  <div className="text-xs text-slate-400 mt-1">Transaction fraud rate</div>
                </div>
                <div className="bg-slate-800 rounded-lg p-4">
                  <div className="text-2xl font-bold text-amber-400">&lt;100ms</div>
                  <div className="text-xs text-slate-400 mt-1">Latency requirement</div>
                </div>
                <div className="bg-slate-800 rounded-lg p-4">
                  <div className="text-2xl font-bold text-amber-400">0.94-0.96</div>
                  <div className="text-xs text-slate-400 mt-1">AUC (XGBoost on IEEE-CIS)</div>
                </div>
                <div className="bg-slate-800 rounded-lg p-4">
                  <div className="text-2xl font-bold text-amber-400">13×</div>
                  <div className="text-xs text-slate-400 mt-1">False positive cost vs fraud</div>
                </div>
              </div>
            </div>
            
            <div className="bg-slate-900/50 rounded-lg p-5">
              <h4 className="text-amber-400 font-medium mb-3">Evolution of Detection</h4>
              <div className="relative pl-4 border-l-2 border-slate-600 space-y-3">
                <div className="relative"><span className="absolute -left-[21px] w-3 h-3 rounded-full bg-slate-600"></span><span className="text-slate-400 text-sm">2016:</span> <span className="text-slate-300">Logistic Regression (Stripe Radar v1)</span></div>
                <div className="relative"><span className="absolute -left-[21px] w-3 h-3 rounded-full bg-slate-500"></span><span className="text-slate-400 text-sm">2020:</span> <span className="text-slate-300">Wide & Deep (XGBoost + DNN)</span></div>
                <div className="relative"><span className="absolute -left-[21px] w-3 h-3 rounded-full bg-amber-600"></span><span className="text-slate-400 text-sm">2022:</span> <span className="text-slate-300">DNN-only (ResNeXt-inspired)</span></div>
                <div className="relative"><span className="absolute -left-[21px] w-3 h-3 rounded-full bg-amber-400"></span><span className="text-slate-400 text-sm">2024-25:</span> <span className="text-slate-300">Foundation Models (Stripe PFM, TallierLTM)</span></div>
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
            { term: 'CNP (Card-Not-Present)', def: 'Transaction where physical card is not swiped/inserted—e-commerce, phone orders. Our primary attack surface.' },
            { term: 'Chargeback', def: 'Dispute where cardholder claims transaction was unauthorized. Triggers investigation. Our primary label source (30-90 day delay).' },
            { term: 'BIN (Bank ID Number)', def: 'First 6-8 digits identifying issuing bank. Encodes card type, geography, risk profile.' },
            { term: 'MCC (Merchant Category)', def: '4-digit code classifying merchant type. 5411=grocery, 7995=gambling. High-risk MCCs indicate fraud targets.' },
            { term: 'Feature Drift', def: 'Change in input data distribution degrading model. Fraud patterns evolve; models become stale.' },
            { term: 'Velocity Features', def: 'Aggregated counts/sums over time windows: txns/hour, amount/day. Core signals for pattern deviation.' },
          ].map((item, i) => (
            <div key={i} className="bg-slate-900/50 rounded-lg p-4 border border-slate-700/30 hover:border-amber-500/30 transition-colors">
              <h4 className="text-amber-400 font-mono text-sm mb-2">{item.term}</h4>
              <p className="text-slate-300 text-sm leading-relaxed">{item.def}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Known vs Assumed */}
      <div className={`bg-slate-800/50 rounded-xl p-8 border border-slate-700/50 transition-all duration-500 delay-200 ${animatedItems.includes(2) ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
        <h3 className="text-xl font-semibold text-slate-100 mb-6 flex items-center gap-3">
          <span className="w-8 h-8 rounded-full bg-amber-500/20 flex items-center justify-center text-amber-400 text-sm">3</span>
          Distinguishing KNOWN from ASSUMED
        </h3>
        
        <div className="grid md:grid-cols-2 gap-6">
          <div className="bg-emerald-900/20 rounded-lg p-5 border border-emerald-500/30">
            <h4 className="text-emerald-400 font-medium mb-3 flex items-center gap-2">
              <span>✓</span> Empirically KNOWN
            </h4>
            <ul className="text-slate-300 space-y-2 text-sm">
              <li>• XGBoost achieves AUC 0.94-0.96 on fraud benchmarks</li>
              <li>• Fraud comprises 0.1-1% of transactions (extreme imbalance)</li>
              <li>• Chargeback windows extend 30-90 days (delayed labels)</li>
              <li>• False declines cost $118B annually—13× actual fraud</li>
              <li>• Stripe PFM improved card-testing detection 59%→97%</li>
              <li>• Graph features improve detection by up to 20%</li>
            </ul>
          </div>
          
          <div className="bg-rose-900/20 rounded-lg p-5 border border-rose-500/30">
            <h4 className="text-rose-400 font-medium mb-3 flex items-center gap-2">
              <span>?</span> Commonly ASSUMED
            </h4>
            <ul className="text-slate-300 space-y-2 text-sm">
              <li>• "Fraud is anomalous behavior" (fraudsters can mimic)</li>
              <li>• "More data improves detection" (poisoned data hurts)</li>
              <li>• "Past patterns predict future fraud" (adversarial adaptation)</li>
              <li>• "Lower fraud rate = better system" (ignores false positives)</li>
              <li>• "Real-time detection is necessary" (auth holds exist)</li>
              <li>• "IP geolocation is reliable" (VPNs, mobile NAT)</li>
            </ul>
          </div>
        </div>
      </div>

      <div className="text-center pt-4">
        <button 
          onClick={() => setActivePhase(1)}
          className="bg-amber-500 hover:bg-amber-400 text-slate-900 font-semibold px-8 py-3 rounded-lg transition-all hover:scale-105"
        >
          Proceed to Challenge Assumptions →
        </button>
      </div>
    </div>
  );

  // ============================================================================
  // PHASE 1: CHALLENGE ASSUMPTIONS (FIRST WHY)
  // ============================================================================
  const AssumptionsPhase = () => {
    const assumptions = [
      {
        id: 'fraud-anomaly',
        assumption: 'Fraud is anomalous behavior that can be detected',
        challenge: 'Why do we believe fraud appears as anomaly?',
        analysis: 'This assumes normal behavior is well-defined and stable. But new customers have no baseline. Legitimate behavior changes (travel, life events). And sophisticated fraudsters increasingly mimic normal patterns using stolen behavioral data.',
        hidden: 'We assume fraudsters CAN\'T perfectly mimic legitimate behavior. But what if they can?'
      },
      {
        id: 'more-data',
        assumption: 'More data improves fraud detection',
        challenge: 'Why would more data help?',
        analysis: 'If fraud patterns from 2020 no longer appear in 2025 (concept drift), old data hurts. If fraudsters have poisoned historical data with successful attacks, more poisoned data amplifies errors. Data quantity only helps if relevance and quality remain stable.',
        hidden: 'We assume the past predicts the future—fraudsters deliberately break this assumption.'
      },
      {
        id: 'past-predicts',
        assumption: 'Past patterns predict future fraud',
        challenge: 'Why should past fraud look like future fraud?',
        analysis: 'This is fundamentally an adversarial game, not a prediction problem. Fraudsters LEARN from detection. They observe what gets blocked and adapt. Static patterns become exploitable. The fraud distribution is non-stationary BY DESIGN.',
        hidden: 'We assume fraud detection is a prediction problem. It\'s actually an adversarial game.'
      },
      {
        id: 'lower-better',
        assumption: 'Lower fraud rate equals better system',
        challenge: 'Why is minimizing fraud rate the goal?',
        analysis: 'A system that declines EVERY transaction achieves 0% fraud rate. But it also has 0% revenue. False declines cost 13× more than fraud losses. Customer lifetime value destroyed by false declines far exceeds fraud savings.',
        hidden: 'We assume fraud rate is the metric. The real metric is profit = revenue - fraud - false_positive_cost.'
      },
      {
        id: 'real-time',
        assumption: 'Real-time decisions are necessary',
        challenge: 'Why must we decide in <100ms?',
        analysis: 'Payment networks expect immediate response. But this is a DESIGN CHOICE, not physics. Authorization holds exist (7-day review windows). Many high-value transactions could tolerate delayed confirmation. Speed is a constraint imposed by system design.',
        hidden: 'We assume the payment system\'s current design is fixed. It could be redesigned.'
      }
    ];

    return (
      <div className="space-y-8">
        <div className="border-l-4 border-cyan-500 pl-6 py-2">
          <p className="text-cyan-400 font-mono text-sm tracking-widest">PHASE 2: CHALLENGE ASSUMPTIONS</p>
          <h2 className="text-3xl font-serif text-slate-100 mt-2">Why do we believe these things are true?</h2>
        </div>

        <div className={`bg-slate-800/50 rounded-xl p-8 border border-slate-700/50 transition-all duration-500 ${animatedItems.includes(0) ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
          <h3 className="text-xl font-semibold text-slate-100 mb-2">The Ladder of Inference</h3>
          <p className="text-slate-400 mb-6">Every belief rests on layers of interpretation. Click each assumption to expose hidden beliefs.</p>
          
          {/* Ladder visualization */}
          <div className="flex items-center justify-center mb-8">
            <div className="relative">
              <svg viewBox="0 0 400 200" className="w-full max-w-md">
                <defs>
                  <linearGradient id="ladderGradCyan" x1="0%" y1="100%" x2="0%" y2="0%">
                    <stop offset="0%" stopColor="#22d3ee" stopOpacity="0.2"/>
                    <stop offset="100%" stopColor="#22d3ee" stopOpacity="0.8"/>
                  </linearGradient>
                </defs>
                <rect x="100" y="170" width="200" height="20" rx="3" fill="url(#ladderGradCyan)" opacity="0.3"/>
                <text x="200" y="183" textAnchor="middle" fill="#94a3b8" fontSize="10">Observable: Transaction Data</text>
                
                <rect x="100" y="135" width="200" height="20" rx="3" fill="url(#ladderGradCyan)" opacity="0.4"/>
                <text x="200" y="148" textAnchor="middle" fill="#94a3b8" fontSize="10">Selected: IP on Tor list</text>
                
                <rect x="100" y="100" width="200" height="20" rx="3" fill="url(#ladderGradCyan)" opacity="0.5"/>
                <text x="200" y="113" textAnchor="middle" fill="#94a3b8" fontSize="10">Interpreted: User hiding identity</text>
                
                <rect x="100" y="65" width="200" height="20" rx="3" fill="url(#ladderGradCyan)" opacity="0.7"/>
                <text x="200" y="78" textAnchor="middle" fill="#94a3b8" fontSize="10">Assumed: Legitimate users don't hide</text>
                
                <rect x="100" y="30" width="200" height="20" rx="3" fill="url(#ladderGradCyan)" opacity="0.9"/>
                <text x="200" y="43" textAnchor="middle" fill="#cbd5e1" fontSize="10" fontWeight="bold">Conclusion: This is fraud</text>
                
                <path d="M 320 170 L 340 100 L 320 30" stroke="#22d3ee" strokeWidth="2" fill="none" strokeDasharray="4"/>
                <polygon points="320,25 325,35 315,35" fill="#22d3ee"/>
              </svg>
            </div>
          </div>
          
          <div className="space-y-4">
            {assumptions.map((item, i) => (
              <div 
                key={item.id}
                className="bg-slate-900/50 rounded-lg border border-slate-700/30 overflow-hidden"
              >
                <button
                  onClick={() => toggleAxiom(item.id)}
                  className="w-full p-5 text-left flex items-center justify-between hover:bg-slate-800/50 transition-colors"
                >
                  <div>
                    <p className="text-cyan-400 font-mono text-xs mb-1">ASSUMPTION</p>
                    <p className="text-slate-100 font-medium">{item.assumption}</p>
                  </div>
                  <span className={`text-xl text-cyan-400 transition-transform ${expandedAxioms[item.id] ? 'rotate-90' : ''}`}>→</span>
                </button>
                
                {expandedAxioms[item.id] && (
                  <div className="px-5 pb-5 border-t border-slate-700/30 pt-4 space-y-4">
                    <div>
                      <p className="text-cyan-400 font-medium text-sm mb-2">{item.challenge}</p>
                      <p className="text-slate-300 text-sm">{item.analysis}</p>
                    </div>
                    <div className="bg-rose-900/20 rounded-lg p-4 border border-rose-500/30">
                      <p className="text-rose-400 font-medium text-sm mb-1">Hidden Assumption Exposed:</p>
                      <p className="text-slate-300 text-sm">{item.hidden}</p>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Analogy vs First Principles */}
        <div className={`bg-slate-800/50 rounded-xl p-8 border border-slate-700/50 transition-all duration-500 ${animatedItems.includes(1) ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
          <h3 className="text-xl font-semibold text-slate-100 mb-6">Reasoning by Analogy vs. First Principles</h3>
          
          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-rose-900/20 rounded-lg p-5 border border-rose-500/30">
              <h4 className="text-rose-400 font-medium mb-3">Analogy-Based (Common)</h4>
              <ul className="text-slate-300 text-sm space-y-2">
                <li>• "Stripe uses XGBoost, so we should too"</li>
                <li>• "IEEE-CIS winners used 500 features, so more is better"</li>
                <li>• "Banks require explainability, so we need SHAP"</li>
                <li>• "Industry uses velocity features, so we need them"</li>
              </ul>
            </div>
            
            <div className="bg-emerald-900/20 rounded-lg p-5 border border-emerald-500/30">
              <h4 className="text-emerald-400 font-medium mb-3">First Principles (Required)</h4>
              <ul className="text-slate-300 text-sm space-y-2">
                <li>• "WHY does gradient boosting work on fraud data?"</li>
                <li>• "WHAT is the information-theoretic limit of detection?"</li>
                <li>• "WHY can fraud be detected at all?"</li>
                <li>• "WHAT minimum information distinguishes fraud?"</li>
              </ul>
            </div>
          </div>
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
            Proceed to Drill to Axioms →
          </button>
        </div>
      </div>
    );
  };

  // ============================================================================
  // PHASE 2: DRILL TO AXIOMS (RECURSIVE WHYS)
  // ============================================================================
  const AxiomsPhase = () => {
    const whyChains = [
      {
        id: 'why-detectable',
        claim: 'We can detect stolen credit card fraud with ML models',
        chain: [
          { why: 'Why can we detect it?', answer: 'Fraudsters behave differently than legitimate cardholders.' },
          { why: 'Why do they behave differently?', answer: 'They lack information that legitimate users possess.' },
          { why: 'Why do they lack this information?', answer: 'They only have stolen credentials, not full identity context.' },
          { why: 'Why can\'t they obtain full identity?', answer: 'Identity is distributed across multiple systems; cost exceeds expected fraud proceeds.' },
          { why: 'Why is identity distributed and costly to obtain?', answer: 'AXIOM: Information asymmetry exists. Data exists in specific locations with access controls. Fraudsters have incomplete knowledge by definition.', isAxiom: true },
        ]
      },
      {
        id: 'why-patterns',
        claim: 'Historical features (velocity, typical amounts) have strong predictive signal',
        chain: [
          { why: 'Why do historical features predict fraud?', answer: 'Legitimate users have established behavioral patterns; fraudsters deviate.' },
          { why: 'Why do legitimate users have patterns?', answer: 'Humans have habits, routines, and constraints (work schedules, home locations).' },
          { why: 'Why do humans have consistent patterns?', answer: 'Behavior is constrained by physical reality and optimized for efficiency.' },
          { why: 'Why does past behavior constrain present?', answer: 'AXIOM: Temporal consistency—past constrains present. Abrupt departures from established patterns are statistically rare for legitimate users.', isAxiom: true },
        ]
      },
      {
        id: 'why-location',
        claim: 'Geolocation features (IP mismatch, impossible travel) detect fraud',
        chain: [
          { why: 'Why does location mismatch indicate fraud?', answer: 'Fraudster is physically elsewhere than the claimed billing address.' },
          { why: 'Why can\'t fraudsters be at the billing address?', answer: 'They acquired credentials remotely, not through physical theft at the location.' },
          { why: 'Why can\'t they teleport or spoof location perfectly?', answer: 'Physical reality constrains presence. VPNs help but leave traces. Impossible travel is impossible.' },
          { why: 'Why is being in two places impossible?', answer: 'AXIOM: Physical laws constrain behavior. A person can only be in one location at a time and travel at finite speeds. This is bedrock reality.', isAxiom: true },
        ]
      },
      {
        id: 'why-goals',
        claim: 'Fraudsters purchase different products than legitimate users',
        chain: [
          { why: 'Why do purchase patterns differ?', answer: 'Fraudsters prefer easily monetizable items (gift cards, electronics).' },
          { why: 'Why prefer monetizable items?', answer: 'They need to convert stolen value to cash before detection.' },
          { why: 'Why optimize for monetization speed?', answer: 'They\'re rational economic actors maximizing expected return.' },
          { why: 'Why do different goals produce different behavior?', answer: 'AXIOM: Goal divergence. Legitimate users optimize for utility; fraudsters optimize for monetization. Different objective functions produce different optima.', isAxiom: true },
        ]
      },
      {
        id: 'why-ml-works',
        claim: 'ML classification can separate fraud from legitimate transactions',
        chain: [
          { why: 'Why can ML separate them?', answer: 'The distributions P(features|fraud) and P(features|legitimate) are different.' },
          { why: 'Why are distributions different?', answer: 'Axioms 1-4: Information asymmetry, temporal consistency, physical constraints, goal divergence all create measurable differences.' },
          { why: 'Why do measurable differences enable classification?', answer: 'AXIOM: Classification is possible when feature distributions differ. This is mathematical truth—the foundation of statistical learning theory.', isAxiom: true },
        ]
      },
    ];

    const axioms = [
      {
        id: 'axiom-1',
        statement: 'Information Asymmetry Exists',
        test: 'Regress Termination / Information Theory',
        confidence: 'High',
        evidence: 'Fullz packages cost $15-65 vs $1-5 for basic cards precisely because more information is valuable. Stripe\'s network effect exploits this.',
        domain: 'Applies to all fraud types, authentication systems, and deception generally.'
      },
      {
        id: 'axiom-2',
        statement: 'Economic Actors Optimize Expected Value',
        test: 'Definitional Truth (Economics)',
        confidence: 'High',
        evidence: 'Fraud shifts toward lower-friction targets (e-commerce vs. EMV). Attack volume correlates with expected transaction value.',
        domain: 'Applies to all rational adversaries. Implies raising attack cost reduces fraud.'
      },
      {
        id: 'axiom-3',
        statement: 'Past Behavior Constrains Present (Temporal Consistency)',
        test: 'Physical/Behavioral Law',
        confidence: 'Medium-High',
        evidence: 'Velocity features consistently top performers. Featurespace\'s "Adaptive Behavioral Analytics" is built on this principle.',
        domain: 'Applies to behavioral modeling broadly. Weakens for new accounts, life events.'
      },
      {
        id: 'axiom-4',
        statement: 'Physical Laws Constrain Behavior (Spatiotemporal)',
        test: 'Physical Law (Indemonstrable)',
        confidence: 'High',
        evidence: 'Impossible travel detection works. Commercial flight max ~900 km/h sets hard constraint. A person cannot be in two places.',
        domain: 'Universal physical constraint. Weakens for VPNs, corporate proxies.'
      },
      {
        id: 'axiom-5',
        statement: 'Different Objectives Produce Different Behavior (Goal Divergence)',
        test: 'Logical Law (Optimization Theory)',
        confidence: 'High',
        evidence: 'Fraudsters prefer gift cards, electronics, digital goods. Merchant category distribution differs systematically.',
        domain: 'Applies to all adversarial detection. Foundation of adversarial ML.'
      },
      {
        id: 'axiom-6',
        statement: 'Classification Is Possible When Distributions Differ',
        test: 'Mathematical Law (Statistics)',
        confidence: 'High (Mathematical Truth)',
        evidence: 'All ML fraud models achieve AUC > 0.5 (better than random). Follows from probability theory.',
        domain: 'Universal constraint on statistical learning. Sets theoretical detection limit.'
      },
    ];

    return (
      <div className="space-y-8">
        <div className="border-l-4 border-violet-500 pl-6 py-2">
          <p className="text-violet-400 font-mono text-sm tracking-widest">PHASE 3: DRILL TO AXIOMS</p>
          <h2 className="text-3xl font-serif text-slate-100 mt-2">What truths cannot be derived from anything more fundamental?</h2>
        </div>

        {/* Recursive Why Chains */}
        <div className={`bg-slate-800/50 rounded-xl p-8 border border-slate-700/50 transition-all duration-500 ${animatedItems.includes(0) ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
          <h3 className="text-xl font-semibold text-slate-100 mb-2">The 5 Whys Applied Recursively</h3>
          <p className="text-slate-400 mb-6">Click each chain to follow the reasoning to its irreducible foundation.</p>
          
          <div className="space-y-4">
            {whyChains.map((chain) => (
              <div 
                key={chain.id}
                className="bg-slate-900/50 rounded-lg border border-slate-700/30 overflow-hidden"
              >
                <button
                  onClick={() => toggleWhyChain(chain.id)}
                  className="w-full p-5 text-left flex items-center justify-between hover:bg-slate-800/50 transition-colors"
                >
                  <div>
                    <p className="text-violet-400 font-mono text-xs mb-1">CLAIM</p>
                    <p className="text-slate-100">{chain.claim}</p>
                  </div>
                  <span className={`text-xl text-violet-400 transition-transform ${expandedWhyChains[chain.id] ? 'rotate-90' : ''}`}>→</span>
                </button>
                
                {expandedWhyChains[chain.id] && (
                  <div className="px-5 pb-5 border-t border-slate-700/30 pt-4">
                    <div className="relative pl-6 border-l-2 border-violet-500/50 space-y-4">
                      {chain.chain.map((step, j) => (
                        <div key={j} className={`relative ${step.isAxiom ? 'bg-violet-900/30 -ml-6 pl-6 py-3 pr-4 rounded-r-lg border-l-2 border-violet-500' : ''}`}>
                          <span className={`absolute -left-[9px] w-4 h-4 rounded-full ${step.isAxiom ? 'bg-violet-500' : 'bg-slate-600'} flex items-center justify-center text-xs text-slate-900 font-bold`}>
                            {j + 1}
                          </span>
                          <p className="text-violet-300 font-medium text-sm mb-1">{step.why}</p>
                          <p className={`text-sm ${step.isAxiom ? 'text-violet-100 font-medium' : 'text-slate-300'}`}>{step.answer}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* First Principles Map */}
        <div className={`bg-slate-800/50 rounded-xl p-8 border border-violet-500/30 transition-all duration-500 ${animatedItems.includes(1) ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
          <h3 className="text-xl font-semibold text-violet-400 mb-6">First Principles Map: The 6 Axioms</h3>
          
          <div className="space-y-4">
            {axioms.map((axiom, i) => (
              <div key={axiom.id} className="bg-slate-900/50 rounded-lg p-5 border border-violet-500/20">
                <div className="flex items-start justify-between gap-4 mb-3">
                  <div>
                    <p className="text-violet-400 font-mono text-xs mb-1">AXIOM #{i + 1}</p>
                    <p className="text-slate-100 font-medium">{axiom.statement}</p>
                  </div>
                  <span className={`px-2 py-1 rounded text-xs font-medium ${axiom.confidence === 'High' || axiom.confidence === 'High (Mathematical Truth)' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-amber-500/20 text-amber-400'}`}>
                    {axiom.confidence}
                  </span>
                </div>
                
                <div className="grid md:grid-cols-3 gap-3 text-sm">
                  <div>
                    <p className="text-slate-500 text-xs mb-1">Stopping Criterion Met</p>
                    <p className="text-slate-300">{axiom.test}</p>
                  </div>
                  <div>
                    <p className="text-slate-500 text-xs mb-1">Supporting Evidence</p>
                    <p className="text-slate-300">{axiom.evidence}</p>
                  </div>
                  <div>
                    <p className="text-slate-500 text-xs mb-1">Domain Independence</p>
                    <p className="text-slate-300">{axiom.domain}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Axiom Architecture Diagram */}
        <div className={`bg-slate-800/50 rounded-xl p-8 border border-slate-700/50 transition-all duration-500 ${animatedItems.includes(2) ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
          <h3 className="text-xl font-semibold text-slate-100 mb-4">How Axioms Map to Detection Capabilities</h3>
          <div className="bg-slate-900/50 rounded-lg p-6">
            <div className="grid md:grid-cols-3 gap-4 text-center text-sm">
              <div className="space-y-3">
                <div className="bg-violet-900/30 rounded-lg p-3 border border-violet-500/30">
                  <p className="text-violet-400 font-mono text-xs">AXIOM 1</p>
                  <p className="text-slate-200">Information Asymmetry</p>
                </div>
                <div className="text-violet-400">↓</div>
                <div className="bg-slate-800 rounded-lg p-3">
                  <p className="text-slate-300">Device fingerprint features</p>
                  <p className="text-slate-300">Historical linkage counts</p>
                </div>
              </div>
              <div className="space-y-3">
                <div className="bg-violet-900/30 rounded-lg p-3 border border-violet-500/30">
                  <p className="text-violet-400 font-mono text-xs">AXIOM 3</p>
                  <p className="text-slate-200">Temporal Consistency</p>
                </div>
                <div className="text-violet-400">↓</div>
                <div className="bg-slate-800 rounded-lg p-3">
                  <p className="text-slate-300">Velocity features</p>
                  <p className="text-slate-300">Amount z-scores</p>
                </div>
              </div>
              <div className="space-y-3">
                <div className="bg-violet-900/30 rounded-lg p-3 border border-violet-500/30">
                  <p className="text-violet-400 font-mono text-xs">AXIOM 4</p>
                  <p className="text-slate-200">Physical Constraints</p>
                </div>
                <div className="text-violet-400">↓</div>
                <div className="bg-slate-800 rounded-lg p-3">
                  <p className="text-slate-300">IP-billing distance</p>
                  <p className="text-slate-300">Impossible travel flags</p>
                </div>
              </div>
            </div>
          </div>
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
            Proceed to Mechanisms →
          </button>
        </div>
      </div>
    );
  };

  // ============================================================================
  // PHASE 3: UNDERSTAND MECHANISMS (HOW)
  // ============================================================================
  const MechanismsPhase = () => {
    const [activeTab, setActiveTab] = useState('flow');

    return (
      <div className="space-y-8">
        <div className="border-l-4 border-emerald-500 pl-6 py-2">
          <p className="text-emerald-400 font-mono text-sm tracking-widest">PHASE 4: UNDERSTAND MECHANISMS</p>
          <h2 className="text-3xl font-serif text-slate-100 mt-2">How do axioms combine to produce detection systems?</h2>
        </div>

        {/* Tab Navigation */}
        <div className="flex gap-2 flex-wrap">
          {[
            { id: 'flow', label: 'Causal Flow' },
            { id: 'features', label: 'Feature Engineering' },
            { id: 'models', label: 'Why Models Work' },
            { id: 'leverage', label: 'Leverage Points' },
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 rounded-lg font-medium transition-all ${activeTab === tab.id ? 'bg-emerald-500 text-slate-900' : 'bg-slate-800 text-slate-400 hover:text-slate-200'}`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Causal Flow */}
        {activeTab === 'flow' && (
          <div className={`bg-slate-800/50 rounded-xl p-8 border border-slate-700/50 transition-all duration-500 ${animatedItems.includes(0) ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
            <h3 className="text-xl font-semibold text-slate-100 mb-6">From Axioms to Fraud Score</h3>
            
            <div className="space-y-6">
              <div className="bg-slate-900/50 rounded-lg p-6">
                <div className="grid grid-cols-1 md:grid-cols-5 gap-4 items-center text-center">
                  <div className="bg-violet-900/30 rounded-lg p-4 border border-violet-500/30">
                    <p className="text-violet-400 font-mono text-xs mb-1">AXIOM</p>
                    <p className="text-sm text-slate-200">Information Asymmetry</p>
                  </div>
                  <div className="text-emerald-400 text-2xl hidden md:block">→</div>
                  <div className="bg-cyan-900/20 rounded-lg p-4 border border-cyan-500/30">
                    <p className="text-cyan-400 font-mono text-xs mb-1">OBSERVABLE</p>
                    <p className="text-sm text-slate-200">Fraudster lacks device history</p>
                  </div>
                  <div className="text-emerald-400 text-2xl hidden md:block">→</div>
                  <div className="bg-emerald-900/20 rounded-lg p-4 border border-emerald-500/30">
                    <p className="text-emerald-400 font-mono text-xs mb-1">FEATURE</p>
                    <p className="text-sm text-slate-200">device_first_seen_days = 0</p>
                  </div>
                </div>
              </div>

              <div className="grid md:grid-cols-2 gap-6">
                <div className="bg-slate-900/50 rounded-lg p-5">
                  <h4 className="text-emerald-400 font-medium mb-3">The Information-Theoretic View</h4>
                  <div className="text-slate-300 text-sm space-y-3">
                    <p><strong className="text-slate-200">Legitimate cardholder possesses:</strong></p>
                    <ul className="list-disc pl-5 space-y-1">
                      <li>Full identity (name, address, history)</li>
                      <li>Physical device with persistent fingerprint</li>
                      <li>Habitual patterns (timing, merchants)</li>
                      <li>Geographic presence matching claimed location</li>
                    </ul>
                    <p className="mt-3"><strong className="text-slate-200">Fraudster possesses:</strong></p>
                    <ul className="list-disc pl-5 space-y-1">
                      <li>Stolen credentials only</li>
                      <li>Fresh/spoofed device with no history</li>
                      <li>Network location not matching claimed</li>
                    </ul>
                  </div>
                </div>

                <div className="bg-slate-900/50 rounded-lg p-5">
                  <h4 className="text-emerald-400 font-medium mb-3">Detection Mechanism</h4>
                  <div className="text-slate-300 text-sm space-y-2">
                    <p><strong className="text-slate-200">Features probe for information asymmetry:</strong></p>
                    <p>Each feature asks: "Does this user have information only the legitimate cardholder would have?"</p>
                    <div className="bg-slate-800/50 rounded p-3 font-mono text-xs mt-3">
                      <p className="text-slate-400">// Core mechanism</p>
                      <p>feature_signal = probe(cardholder_info)</p>
                      <p>model_aggregate = Σ weighted_signals</p>
                      <p>P(fraud) = σ(model_aggregate)</p>
                      <p>decision = threshold(P(fraud))</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Feature Engineering */}
        {activeTab === 'features' && (
          <div className={`bg-slate-800/50 rounded-xl p-8 border border-slate-700/50 transition-all duration-500 ${animatedItems.includes(0) ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
            <h3 className="text-xl font-semibold text-slate-100 mb-6">Features Derived from Each Axiom</h3>
            
            <div className="space-y-6">
              {[
                {
                  axiom: 'A1: Information Asymmetry',
                  color: 'violet',
                  features: [
                    { name: 'device_first_seen_days', purpose: 'Has this device been linked to this identity?' },
                    { name: 'card_device_count', purpose: 'How many devices used this card? (Legit: 1-2)' },
                    { name: 'email_card_count', purpose: 'How many cards linked to this email?' },
                    { name: 'historical_txn_count', purpose: 'How much history does this identity have?' },
                  ]
                },
                {
                  axiom: 'A3: Temporal Consistency',
                  color: 'cyan',
                  features: [
                    { name: 'amount_zscore_7d', purpose: 'Is this amount normal for this user?' },
                    { name: 'velocity_1h_count', purpose: 'Transaction count in last hour' },
                    { name: 'time_since_last_txn', purpose: 'Is the transaction cadence normal?' },
                    { name: 'merchant_category_entropy', purpose: 'Does user shop at diverse merchants?' },
                  ]
                },
                {
                  axiom: 'A4: Physical Constraints',
                  color: 'amber',
                  features: [
                    { name: 'ip_billing_distance_km', purpose: 'Distance between IP and billing address' },
                    { name: 'impossible_travel_flag', purpose: 'Could user physically have traveled from last location?' },
                    { name: 'timezone_mismatch', purpose: 'Does browser timezone match billing address?' },
                    { name: 'vpn_proxy_flag', purpose: 'Is IP on known proxy/VPN list?' },
                  ]
                },
                {
                  axiom: 'A5: Goal Divergence',
                  color: 'pink',
                  features: [
                    { name: 'is_digital_goods', purpose: 'Is the product easily monetizable?' },
                    { name: 'is_gift_card', purpose: 'Is this a high-value, untraceable product?' },
                    { name: 'shipping_billing_mismatch', purpose: 'Does shipping go somewhere else?' },
                    { name: 'high_risk_mcc', purpose: 'Is merchant category fraud-prone?' },
                  ]
                },
              ].map((group, i) => (
                <div key={i} className="bg-slate-900/50 rounded-lg p-5">
                  <h4 className={`text-${group.color}-400 font-medium mb-4`}>{group.axiom}</h4>
                  <div className="grid md:grid-cols-2 gap-3">
                    {group.features.map((f, j) => (
                      <div key={j} className="bg-slate-800/50 rounded p-3">
                        <code className="text-emerald-300 text-sm">{f.name}</code>
                        <p className="text-slate-400 text-xs mt-1">{f.purpose}</p>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Why Models Work */}
        {activeTab === 'models' && (
          <div className={`bg-slate-800/50 rounded-xl p-8 border border-slate-700/50 transition-all duration-500 ${animatedItems.includes(0) ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
            <h3 className="text-xl font-semibold text-slate-100 mb-6">Why Each Model Architecture Works</h3>
            
            <div className="space-y-6">
              <div className="bg-slate-900/50 rounded-lg p-5">
                <h4 className="text-emerald-400 font-medium mb-3">XGBoost/LightGBM (Gradient Boosting)</h4>
                <div className="grid md:grid-cols-2 gap-4">
                  <div className="text-slate-300 text-sm space-y-2">
                    <p><strong className="text-slate-200">Grounded in Axiom A5 (Goal Divergence):</strong></p>
                    <p>Fraud signals are often threshold-based:</p>
                    <ul className="list-disc pl-5">
                      <li>Legitimate: amount &lt; typical × 2</li>
                      <li>Fraudulent: amount &gt; typical × 5</li>
                    </ul>
                    <p className="mt-2">Decision trees naturally find these thresholds without explicit encoding.</p>
                  </div>
                  <div className="bg-slate-800/50 rounded p-3 font-mono text-xs">
                    <p className="text-slate-400"># Why boosting works for fraud</p>
                    <p className="text-slate-300">for tree in range(n_trees):</p>
                    <p className="text-slate-300 pl-4">tree_pred = fit_tree(X, residual)</p>
                    <p className="text-slate-300 pl-4">residual = y_true - prediction</p>
                    <p className="text-emerald-300 pl-4"># Each tree specializes in boundary cases</p>
                    <p className="text-emerald-300 pl-4"># Fraud is in the tails → boosting helps</p>
                  </div>
                </div>
              </div>

              <div className="bg-slate-900/50 rounded-lg p-5">
                <h4 className="text-emerald-400 font-medium mb-3">LSTM/GRU (Sequence Models)</h4>
                <div className="grid md:grid-cols-2 gap-4">
                  <div className="text-slate-300 text-sm space-y-2">
                    <p><strong className="text-slate-200">Grounded in Axiom A3 (Temporal Consistency):</strong></p>
                    <p>Transaction ORDER contains information beyond aggregates:</p>
                    <p className="font-mono bg-slate-800/50 rounded p-2 text-xs mt-2">
                      Sequence: [low, low, low, HUGE]
                      <br/>→ Test-then-exploit pattern
                    </p>
                    <p className="mt-2">XGBoost sees aggregates. LSTM sees the sequence.</p>
                  </div>
                  <div className="text-slate-300 text-sm">
                    <p><strong className="text-slate-200">Performance:</strong></p>
                    <ul className="list-disc pl-5 mt-2">
                      <li>LSTM with attention: 99.9% accuracy</li>
                      <li>Outperforms RF on offline transactions</li>
                      <li>Variable-length via pack_padded_sequence</li>
                    </ul>
                  </div>
                </div>
              </div>

              <div className="bg-slate-900/50 rounded-lg p-5">
                <h4 className="text-emerald-400 font-medium mb-3">Graph Neural Networks (GNN)</h4>
                <div className="grid md:grid-cols-2 gap-4">
                  <div className="text-slate-300 text-sm space-y-2">
                    <p><strong className="text-slate-200">Grounded in Axiom A2 (Economic Optimization):</strong></p>
                    <p>Fraudsters share infrastructure to reduce costs:</p>
                    <ul className="list-disc pl-5 mt-2">
                      <li>Same device for multiple cards</li>
                      <li>Same email domain across accounts</li>
                      <li>Same IP block for many attacks</li>
                    </ul>
                    <p className="mt-2">These create hidden graph connections invisible to tabular models.</p>
                  </div>
                  <div className="text-slate-300 text-sm">
                    <p><strong className="text-slate-200">What GNN sees that XGBoost can't:</strong></p>
                    <div className="bg-slate-800/50 rounded p-2 text-xs font-mono mt-2">
                      Account A ←→ shares_device ←→ Account B (fraud)<br/>
                      Account A ←→ 2_hop ←→ Fraud ring cluster<br/>
                      <span className="text-rose-400">Verdict: High risk (guilt by association)</span>
                    </div>
                    <p className="mt-2">Performance: 91% accuracy, 0.961 AUC with Neo4j + XGBoost</p>
                  </div>
                </div>
              </div>

              <div className="bg-slate-900/50 rounded-lg p-5">
                <h4 className="text-emerald-400 font-medium mb-3">Foundation Models (Stripe PFM, TallierLTM)</h4>
                <div className="grid md:grid-cols-2 gap-4">
                  <div className="text-slate-300 text-sm space-y-2">
                    <p><strong className="text-slate-200">Grounded in Axiom A1 (Information Asymmetry):</strong></p>
                    <p>Self-supervised learning on transaction "grammar":</p>
                    <ul className="list-disc pl-5 mt-2">
                      <li>No fraud labels needed for pre-training</li>
                      <li>Learns what "fluent" transaction behavior looks like</li>
                      <li>Fraud has "ungrammatical" patterns</li>
                    </ul>
                  </div>
                  <div className="text-slate-300 text-sm">
                    <p><strong className="text-slate-200">Results:</strong></p>
                    <ul className="list-disc pl-5 mt-2">
                      <li>Stripe PFM: 59% → 97% card-testing detection</li>
                      <li>TallierLTM: 71% improvement in fraud value detection</li>
                      <li>$6B+ falsely declined transactions recovered</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Leverage Points */}
        {activeTab === 'leverage' && (
          <div className={`bg-slate-800/50 rounded-xl p-8 border border-slate-700/50 transition-all duration-500 ${animatedItems.includes(0) ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
            <h3 className="text-xl font-semibold text-slate-100 mb-6">Maximum Leverage Intervention Points</h3>
            <p className="text-slate-400 mb-6">From mechanistic understanding, where does intervention have maximum impact?</p>
            
            <div className="space-y-4">
              {[
                { rank: 1, point: 'Feature Store Latency', example: 'Slow features → stale signals. Redis with <10ms p99', impact: 'High', effort: 'Medium' },
                { rank: 2, point: 'Historical Depth', example: 'Shallow history → weak temporal signal. 90+ day lookback', impact: 'High', effort: 'Low' },
                { rank: 3, point: 'Graph Connectivity', example: 'Sparse graph → missed fraud rings. Consortium data sharing', impact: 'Very High', effort: 'High' },
                { rank: 4, point: 'Label Quality', example: 'Noisy labels → noisy model. Multi-source labeling infrastructure', impact: 'Very High', effort: 'High' },
                { rank: 5, point: 'Feedback Loop Speed', example: 'Slow retraining → concept drift. Daily model updates', impact: 'High', effort: 'Medium' },
                { rank: 6, point: 'Threshold Optimization', example: 'Static threshold → suboptimal. Dynamic, cost-weighted thresholds', impact: 'Medium', effort: 'Low' },
              ].map((item, i) => (
                <div key={i} className="flex items-center gap-4 bg-slate-900/50 rounded-lg p-4">
                  <div className="w-10 h-10 rounded-full bg-emerald-500/20 flex items-center justify-center text-emerald-400 font-bold flex-shrink-0">
                    {item.rank}
                  </div>
                  <div className="flex-1">
                    <p className="text-slate-100 font-medium">{item.point}</p>
                    <p className="text-slate-400 text-sm">{item.example}</p>
                  </div>
                  <div className="text-right flex-shrink-0">
                    <p className={`text-sm font-medium ${item.impact === 'Very High' ? 'text-emerald-400' : item.impact === 'High' ? 'text-amber-400' : 'text-slate-400'}`}>
                      {item.impact} Impact
                    </p>
                    <p className="text-slate-500 text-xs">{item.effort} Effort</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

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
            Proceed to Application →
          </button>
        </div>
      </div>
    );
  };

  // ============================================================================
  // PHASE 4: APPLICATION (WHEN/WHERE/WHAT IF)
  // ============================================================================
  const ApplicationPhase = () => {
    return (
      <div className="space-y-8">
        <div className="border-l-4 border-pink-500 pl-6 py-2">
          <p className="text-pink-400 font-mono text-sm tracking-widest">PHASE 5: CONTEXTUALIZE & APPLY</p>
          <h2 className="text-3xl font-serif text-slate-100 mt-2">Where does this understanding apply and where does it break down?</h2>
        </div>

        {/* Boundary Conditions */}
        <div className={`bg-slate-800/50 rounded-xl p-8 border border-slate-700/50 transition-all duration-500 ${animatedItems.includes(0) ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
          <h3 className="text-xl font-semibold text-slate-100 mb-6">Boundary Conditions: When Do Axioms Hold?</h3>
          
          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-emerald-900/20 rounded-lg p-5 border border-emerald-500/30">
              <h4 className="text-emerald-400 font-medium mb-3">✓ Axioms Apply When:</h4>
              <ul className="text-slate-300 text-sm space-y-2">
                <li>• Credentials stolen remotely (not insider theft)</li>
                <li>• Fraudster is economically motivated (not vandalism)</li>
                <li>• User has established behavioral history</li>
                <li>• Transaction has digital footprint to analyze</li>
                <li>• Physical presence matters (goods shipped)</li>
                <li>• Fraud patterns are distinct from legitimate</li>
              </ul>
            </div>
            
            <div className="bg-rose-900/20 rounded-lg p-5 border border-rose-500/30">
              <h4 className="text-rose-400 font-medium mb-3">✗ Axioms Break Down When:</h4>
              <ul className="text-slate-300 text-sm space-y-2">
                <li>• Insider threat with full identity access</li>
                <li>• Full identity theft (fraudster lives as victim)</li>
                <li>• New account (no behavioral baseline)</li>
                <li>• VPNs/proxies hide true location</li>
                <li>• Digital goods (no shipping address)</li>
                <li>• Perfect mimicry achieved (future risk)</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Axiom Breakdown Table */}
        <div className={`bg-slate-800/50 rounded-xl p-8 border border-slate-700/50 transition-all duration-500 ${animatedItems.includes(1) ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
          <h3 className="text-xl font-semibold text-slate-100 mb-6">Axiom Failure Scenarios</h3>
          
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-700">
                  <th className="text-left text-slate-400 font-medium py-3 px-4">Axiom</th>
                  <th className="text-left text-emerald-400 font-medium py-3 px-4">Holds When</th>
                  <th className="text-left text-rose-400 font-medium py-3 px-4">Fails When</th>
                </tr>
              </thead>
              <tbody className="text-slate-300">
                <tr className="border-b border-slate-800">
                  <td className="py-3 px-4 font-medium">A1: Information Asymmetry</td>
                  <td className="py-3 px-4">Remote credential theft</td>
                  <td className="py-3 px-4">Insider threat, full identity theft</td>
                </tr>
                <tr className="border-b border-slate-800">
                  <td className="py-3 px-4 font-medium">A2: Economic Optimization</td>
                  <td className="py-3 px-4">Profit-motivated fraudsters</td>
                  <td className="py-3 px-4">Vandalism, hacktivism, state actors</td>
                </tr>
                <tr className="border-b border-slate-800">
                  <td className="py-3 px-4 font-medium">A3: Temporal Consistency</td>
                  <td className="py-3 px-4">Stable user behavior</td>
                  <td className="py-3 px-4">Life changes, market events, new accounts</td>
                </tr>
                <tr className="border-b border-slate-800">
                  <td className="py-3 px-4 font-medium">A4: Physical Constraints</td>
                  <td className="py-3 px-4">Physical goods transactions</td>
                  <td className="py-3 px-4">VPNs, corporate proxies, digital goods</td>
                </tr>
                <tr className="border-b border-slate-800">
                  <td className="py-3 px-4 font-medium">A5: Goal Divergence</td>
                  <td className="py-3 px-4">Monetization fraud</td>
                  <td className="py-3 px-4">Account destruction, data theft</td>
                </tr>
                <tr>
                  <td className="py-3 px-4 font-medium">A6: Distribution Difference</td>
                  <td className="py-3 px-4">Distinct fraud patterns</td>
                  <td className="py-3 px-4">Perfect mimicry achieved</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        {/* Transfer Opportunities */}
        <div className={`bg-slate-800/50 rounded-xl p-8 border border-slate-700/50 transition-all duration-500 ${animatedItems.includes(2) ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
          <h3 className="text-xl font-semibold text-slate-100 mb-6">Transfer: Analogous Domains Sharing These Axioms</h3>
          
          <div className="grid md:grid-cols-3 gap-4">
            {[
              { domain: 'Account Takeover (ATO)', shared: ['Information asymmetry', 'Device mismatch', 'Behavior change'], unique: 'Same account, different actor' },
              { domain: 'Anti-Money Laundering', shared: ['All 6 axioms', 'Network analysis', 'Economic actors'], unique: 'Longer time horizons, graph focus' },
              { domain: 'Insurance Fraud', shared: ['Economic optimization', 'Goal divergence'], unique: 'Different claim patterns' },
              { domain: 'Healthcare Fraud', shared: ['Temporal patterns', 'Goal divergence'], unique: 'Billing anomalies focus' },
              { domain: 'Synthetic Identity', shared: ['No history (A3 weak)', 'Economic actors'], unique: 'Fabricated identity from scratch' },
              { domain: 'Bot Detection', shared: ['Non-human patterns', 'Distributed IPs'], unique: 'Behavioral biometrics focus' },
            ].map((item, i) => (
              <div key={i} className="bg-slate-900/50 rounded-lg p-4 border border-slate-700/30">
                <h4 className="text-pink-400 font-medium mb-2">{item.domain}</h4>
                <div className="space-y-2 text-sm">
                  <div>
                    <p className="text-slate-500 text-xs">Shared Axioms:</p>
                    <p className="text-slate-300">{item.shared.join(', ')}</p>
                  </div>
                  <div>
                    <p className="text-slate-500 text-xs">Key Difference:</p>
                    <p className="text-slate-400">{item.unique}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Novel Insights */}
        <div className={`bg-slate-800/50 rounded-xl p-8 border border-pink-500/30 transition-all duration-500 ${animatedItems.includes(3) ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
          <h3 className="text-xl font-semibold text-pink-400 mb-6">Novel Insights from First Principles</h3>
          
          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-slate-900/50 rounded-lg p-5">
              <h4 className="text-slate-100 font-medium mb-3">Insight 1: Detection-Arms-Race is Economically Bounded</h4>
              <p className="text-slate-300 text-sm mb-3">
                From A2 (Economic Optimization): Fraudsters only invest in evasion up to expected profit &gt; evasion cost.
              </p>
              <p className="text-pink-400 text-sm">Implication: You don't need perfect detection. Make expected attack value negative.</p>
            </div>
            
            <div className="bg-slate-900/50 rounded-lg p-5">
              <h4 className="text-slate-100 font-medium mb-3">Insight 2: Friction IS Detection</h4>
              <p className="text-slate-300 text-sm mb-3">
                From A1 + A2: Every verification step both provides signal AND raises attack cost.
              </p>
              <p className="text-pink-400 text-sm">Implication: Implement risk-based step-up authentication. Dynamic friction beats uniform friction.</p>
            </div>
            
            <div className="bg-slate-900/50 rounded-lg p-5">
              <h4 className="text-slate-100 font-medium mb-3">Insight 3: Labeling is the Real Bottleneck</h4>
              <p className="text-slate-300 text-sm mb-3">
                From A6: Theoretical limit is distributional separation. Practical limit is label quality/availability.
              </p>
              <p className="text-pink-400 text-sm">Implication: Invest in labeling infrastructure before model architecture.</p>
            </div>
            
            <div className="bg-slate-900/50 rounded-lg p-5">
              <h4 className="text-slate-100 font-medium mb-3">Insight 4: Foundation Models Are Natural Evolution</h4>
              <p className="text-slate-300 text-sm mb-3">
                Self-supervised learning: No labels needed, learns "transaction grammar," transfers across merchants.
              </p>
              <p className="text-pink-400 text-sm">Implication: Industry will converge on pre-trained transaction models, like NLP converged on LLMs.</p>
            </div>
          </div>
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
            Test Your Understanding →
          </button>
        </div>
      </div>
    );
  };

  // ============================================================================
  // PHASE 5: SYNTHESIS (QUIZ + UNCERTAINTY)
  // ============================================================================
  const SynthesisPhase = () => {
    const questions = [
      {
        id: 'q1',
        question: 'What fundamental axiom explains WHY fraud can be detected at all?',
        options: [
          'Fraudsters are less intelligent than fraud analysts',
          'Information asymmetry—fraudsters lack context only legitimate cardholders possess',
          'Machine learning algorithms are sufficiently powerful',
          'Payment networks collect enough data'
        ],
        correct: 1,
        explanation: 'Axiom 1 (Information Asymmetry) is foundational. Fraudsters possess stolen credentials but lack behavioral history, device relationships, and full identity context. This asymmetry creates detectable patterns.'
      },
      {
        id: 'q2',
        question: 'Why do velocity features (transactions/hour, amount/day) work so well for fraud detection?',
        options: [
          'They are easy to compute in real-time',
          'Fraudsters always transact faster than legitimate users',
          'They probe Axiom 3 (Temporal Consistency)—fraudsters cannot mimic historical patterns they don\'t know',
          'Industry benchmarks have proven their effectiveness'
        ],
        correct: 2,
        explanation: 'Velocity features derive their power from Axiom 3: Past constrains present. Legitimate users have established patterns. Fraudsters, lacking this history, produce anomalous velocity signatures.'
      },
      {
        id: 'q3',
        question: 'What makes "impossible travel" detection theoretically sound from first principles?',
        options: [
          'IP geolocation databases are highly accurate',
          'It exploits Axiom 4 (Physical Laws)—a person cannot be in two places at once',
          'Airlines share passenger data with payment networks',
          'VPNs are detectable by latency analysis'
        ],
        correct: 1,
        explanation: 'Axiom 4 (Physical Laws Constrain Behavior) is bedrock reality. A human can only be in one location and travel at finite speeds. This is indemonstrable truth—the foundation of spatiotemporal detection.'
      },
      {
        id: 'q4',
        question: 'Why do GNNs (Graph Neural Networks) add value beyond tabular models like XGBoost?',
        options: [
          'GNNs have more parameters and can learn more complex patterns',
          'GNNs exploit Axiom 2—fraudsters share infrastructure to reduce costs, creating hidden network connections',
          'GNNs are faster at inference time',
          'GNNs handle missing data better'
        ],
        correct: 1,
        explanation: 'Axiom 2 (Economic Optimization) explains fraud ring formation. Fraudsters share devices, IPs, and infrastructure to reduce per-attack costs. GNNs detect these hidden connections that tabular models cannot see.'
      },
      {
        id: 'q5',
        question: 'What is the first-principles explanation for why foundation models (Stripe PFM, TallierLTM) represent a paradigm shift?',
        options: [
          'They have more training data than previous models',
          'They use GPT-4 architecture which is proven to work',
          'They learn "transaction grammar" through self-supervised learning, exploiting Axiom 1 without requiring fraud labels',
          'They are faster at inference'
        ],
        correct: 2,
        explanation: 'Foundation models exploit Axiom 1 (Information Asymmetry) at scale. By learning what "fluent" transaction behavior looks like without labels, they detect fraud as "ungrammatical" patterns—breaking the label delay constraint.'
      },
      {
        id: 'q6',
        question: 'When would ALL six axioms fail, making fraud detection theoretically impossible?',
        options: [
          'When fraud rate drops below 0.01%',
          'When payment networks implement stronger encryption',
          'When a fraudster achieves perfect mimicry—full identity access, same goals, same behavior',
          'When regulations prohibit ML-based decisions'
        ],
        correct: 2,
        explanation: 'If a fraudster achieves perfect mimicry—complete information (breaks A1), same optimization goal (breaks A5), identical behavior (breaks A3), same location (breaks A4)—detection becomes theoretically impossible. This is the ultimate boundary of all fraud detection.'
      }
    ];

    const handleAnswer = (qId, optionIndex) => {
      setQuizAnswers(prev => ({ ...prev, [qId]: optionIndex }));
    };

    const score = Object.entries(quizAnswers).reduce((acc, [qId, answer]) => {
      const q = questions.find(q => q.id === qId);
      return acc + (q && answer === q.correct ? 1 : 0);
    }, 0);

    return (
      <div className="space-y-8">
        <div className="border-l-4 border-indigo-500 pl-6 py-2">
          <p className="text-indigo-400 font-mono text-sm tracking-widest">PHASE 6: SYNTHESIS</p>
          <h2 className="text-3xl font-serif text-slate-100 mt-2">Test Your First-Principles Understanding</h2>
        </div>

        <div className={`bg-slate-800/50 rounded-xl p-8 border border-slate-700/50 transition-all duration-500 ${animatedItems.includes(0) ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-semibold text-slate-100">Knowledge Validation</h3>
            {showResults && (
              <div className={`px-4 py-2 rounded-lg ${score >= 5 ? 'bg-emerald-500/20 text-emerald-400' : score >= 3 ? 'bg-amber-500/20 text-amber-400' : 'bg-rose-500/20 text-rose-400'}`}>
                Score: {score}/{questions.length}
              </div>
            )}
          </div>

          <div className="space-y-6">
            {questions.map((q, i) => (
              <div key={q.id} className="bg-slate-900/50 rounded-lg p-5 border border-slate-700/30">
                <p className="text-slate-100 font-medium mb-4">{i + 1}. {q.question}</p>
                
                <div className="space-y-2">
                  {q.options.map((option, j) => {
                    const isSelected = quizAnswers[q.id] === j;
                    const isCorrect = j === q.correct;
                    
                    return (
                      <button
                        key={j}
                        onClick={() => !showResults && handleAnswer(q.id, j)}
                        disabled={showResults}
                        className={`w-full text-left p-3 rounded-lg transition-all ${
                          showResults
                            ? isCorrect
                              ? 'bg-emerald-500/20 border border-emerald-500/50 text-emerald-300'
                              : isSelected
                                ? 'bg-rose-500/20 border border-rose-500/50 text-rose-300'
                                : 'bg-slate-800/50 text-slate-500'
                            : isSelected
                              ? 'bg-indigo-500/20 border border-indigo-500/50 text-indigo-300'
                              : 'bg-slate-800/50 hover:bg-slate-700/50 text-slate-300'
                        }`}
                      >
                        <span className="mr-2">{String.fromCharCode(65 + j)}.</span>
                        {option}
                      </button>
                    );
                  })}
                </div>

                {showResults && (
                  <div className="mt-4 p-4 bg-indigo-900/20 rounded-lg border border-indigo-500/30">
                    <p className="text-indigo-400 font-medium text-sm mb-1">First-Principles Explanation:</p>
                    <p className="text-slate-300 text-sm">{q.explanation}</p>
                  </div>
                )}
              </div>
            ))}
          </div>

          <div className="mt-6 text-center">
            {!showResults ? (
              <button 
                onClick={() => setShowResults(true)}
                disabled={Object.keys(quizAnswers).length < questions.length}
                className={`px-8 py-3 rounded-lg font-semibold transition-all ${
                  Object.keys(quizAnswers).length < questions.length
                    ? 'bg-slate-700 text-slate-500 cursor-not-allowed'
                    : 'bg-indigo-500 hover:bg-indigo-400 text-slate-900 hover:scale-105'
                }`}
              >
                Submit & See Explanations
              </button>
            ) : (
              <button 
                onClick={() => { setShowResults(false); setQuizAnswers({}); }}
                className="bg-slate-700 hover:bg-slate-600 text-slate-200 font-semibold px-8 py-3 rounded-lg transition-all"
              >
                Reset Quiz
              </button>
            )}
          </div>
        </div>

        {/* Uncertainty Register */}
        <div className={`bg-slate-800/50 rounded-xl p-8 border border-indigo-500/30 transition-all duration-500 ${animatedItems.includes(1) ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
          <h3 className="text-xl font-semibold text-indigo-400 mb-6">Uncertainty Register: What Remains Unknown</h3>
          
          <div className="grid md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <h4 className="text-slate-100 font-medium">Axioms That Might Be Assumptions</h4>
              <div className="text-slate-300 text-sm space-y-2">
                <p>• <strong>A3 (Temporal Consistency):</strong> How stable is behavior really? Gen Z patterns differ from Boomers. Gig workers have irregular patterns.</p>
                <p>• <strong>A4 (Physical Constraints):</strong> Is location still meaningful? Remote work, VPN adoption, digital goods all weaken this.</p>
                <p>• <strong>A6 (Distribution Difference):</strong> Is perfect mimicry achievable? GenAI can generate realistic behavioral sequences. Deepfakes spoof biometrics.</p>
              </div>
            </div>
            
            <div className="space-y-4">
              <h4 className="text-slate-100 font-medium">Recommended Areas for Investigation</h4>
              <div className="text-slate-300 text-sm space-y-2">
                <p>• <strong>Causal inference:</strong> Do velocity features CAUSE fraud flags, or are they correlated with true indicators?</p>
                <p>• <strong>Adversarial robustness:</strong> How do models degrade under targeted attacks? What's the security margin?</p>
                <p>• <strong>Foundation model interpretability:</strong> What "transaction grammar" do pre-trained models actually learn?</p>
                <p>• <strong>Fairness audits:</strong> Do models exhibit disparate impact across demographic groups?</p>
              </div>
            </div>
          </div>
        </div>

        {/* The Irreducible Core */}
        <div className={`bg-gradient-to-r from-violet-900/30 to-indigo-900/30 rounded-xl p-8 border border-violet-500/30 transition-all duration-500 ${animatedItems.includes(2) ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
          <h3 className="text-xl font-semibold text-violet-400 mb-4">The Irreducible Core</h3>
          <p className="text-slate-300 leading-relaxed">
            Stolen credit card fraud detection, at its foundation, exploits a small set of bedrock truths:
          </p>
          <div className="grid md:grid-cols-2 gap-4 mt-4">
            <div className="text-slate-300 text-sm space-y-1">
              <p>1. Fraudsters don't have complete information</p>
              <p>2. Fraudsters optimize for different goals</p>
              <p>3. Past behavior predicts future behavior</p>
            </div>
            <div className="text-slate-300 text-sm space-y-1">
              <p>4. Physical reality constrains behavior</p>
              <p>5. Different distributions can be separated</p>
              <p>6. Everything else is implementation detail</p>
            </div>
          </div>
          <p className="text-violet-300 text-sm mt-4 italic">
            "The art of fraud detection is not in choosing algorithms. It is in identifying which axioms apply to your context, designing features that probe those axioms, and building systems that adapt as fraudsters evolve."
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
                  <span className="text-2xl">🔐</span>
                </div>
                <div>
                  <h1 className="text-2xl font-serif text-slate-100">Stolen Credit Card Fraud Detection: From Axioms to Application</h1>
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
      </div>
    </div>
  );
};

export default StolenCardFraudFirstPrinciplesGuide;

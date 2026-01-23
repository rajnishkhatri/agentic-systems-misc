import React, { useState, useEffect, useRef } from 'react';

// ============================================================================
// FIRST PRINCIPLES DEEP DIVE: ML FRAUD DETECTION
// A recursive exploration from surface knowledge to irreducible axioms
// ============================================================================

const MLFraudFirstPrinciplesGuide = ({ onBack }) => {
  const [activePhase, setActivePhase] = useState(0);
  const [expandedAxioms, setExpandedAxioms] = useState({});
  const [expandedWhyChains, setExpandedWhyChains] = useState({});
  const [quizAnswers, setQuizAnswers] = useState({});
  const [showResults, setShowResults] = useState(false);
  const [animatedItems, setAnimatedItems] = useState([]);
  
  // Staggered animation effect
  useEffect(() => {
    setAnimatedItems([]);
    const items = [];
    for (let i = 0; i < 20; i++) {
      setTimeout(() => {
        setAnimatedItems(prev => [...prev, i]);
      }, i * 80);
    }
  }, [activePhase]);

  const phases = [
    { id: 0, name: 'BASELINE', label: 'What Is It?', icon: '◯' },
    { id: 1, name: 'ASSUMPTIONS', label: 'Challenge Beliefs', icon: '◇' },
    { id: 2, name: 'AXIOMS', label: 'Drill to Truth', icon: '△' },
    { id: 3, name: 'MECHANISMS', label: 'How It Works', icon: '□' },
    { id: 4, name: 'APPLICATION', label: 'Where It Applies', icon: '⬡' },
    { id: 5, name: 'SYNTHESIS', label: 'Test Understanding', icon: '◎' },
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
        <h2 className="text-3xl font-serif text-slate-100 mt-2">What is ML Fraud Detection at its most literal, observable level?</h2>
      </div>

      {/* Factual Inventory */}
      <div className={`bg-slate-800/50 rounded-xl p-8 border border-slate-700/50 transition-all duration-500 ${animatedItems.includes(0) ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
        <h3 className="text-xl font-semibold text-slate-100 mb-6 flex items-center gap-3">
          <span className="w-8 h-8 rounded-full bg-amber-500/20 flex items-center justify-center text-amber-400 text-sm">1</span>
          Factual Inventory
        </h3>
        
        <div className="grid md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <div className="bg-slate-900/50 rounded-lg p-5">
              <h4 className="text-amber-400 font-medium mb-3">Observable Phenomenon</h4>
              <p className="text-slate-300 leading-relaxed">
                ML fraud detection is a <span className="text-amber-300">binary classification system</span> that receives transaction data as input and outputs a probability score indicating likelihood of fraud. At its most literal level, it transforms a vector of numerical features into a single scalar value between 0 and 1.
              </p>
            </div>
            
            <div className="bg-slate-900/50 rounded-lg p-5">
              <h4 className="text-amber-400 font-medium mb-3">Constituent Parts</h4>
              <ul className="text-slate-300 space-y-2">
                <li className="flex items-start gap-2"><span className="text-amber-500">→</span> Feature vectors (500+ attributes per transaction)</li>
                <li className="flex items-start gap-2"><span className="text-amber-500">→</span> Mathematical models (decision trees, neural networks)</li>
                <li className="flex items-start gap-2"><span className="text-amber-500">→</span> Historical labeled data (fraud/not-fraud outcomes)</li>
                <li className="flex items-start gap-2"><span className="text-amber-500">→</span> Scoring thresholds (business-determined cutoffs)</li>
                <li className="flex items-start gap-2"><span className="text-amber-500">→</span> Human review queues (medium-confidence cases)</li>
              </ul>
            </div>
          </div>

          <div className="space-y-4">
            <div className="bg-slate-900/50 rounded-lg p-5">
              <h4 className="text-amber-400 font-medium mb-3">Current State (2025)</h4>
              <div className="grid grid-cols-2 gap-4 text-center">
                <div className="bg-slate-800 rounded-lg p-4">
                  <div className="text-2xl font-bold text-amber-400">87%</div>
                  <div className="text-xs text-slate-400 mt-1">Financial institutions using AI fraud detection</div>
                </div>
                <div className="bg-slate-800 rounded-lg p-4">
                  <div className="text-2xl font-bold text-amber-400">&lt;100ms</div>
                  <div className="text-xs text-slate-400 mt-1">Decision latency target</div>
                </div>
                <div className="bg-slate-800 rounded-lg p-4">
                  <div className="text-2xl font-bold text-amber-400">97-98%</div>
                  <div className="text-xs text-slate-400 mt-1">Accuracy achieved</div>
                </div>
                <div className="bg-slate-800 rounded-lg p-4">
                  <div className="text-2xl font-bold text-amber-400">$25B</div>
                  <div className="text-xs text-slate-400 mt-1">Annual fraud prevented (Visa alone)</div>
                </div>
              </div>
            </div>
            
            <div className="bg-slate-900/50 rounded-lg p-5">
              <h4 className="text-amber-400 font-medium mb-3">Timeline of Development</h4>
              <div className="relative pl-4 border-l-2 border-slate-600 space-y-3">
                <div className="relative"><span className="absolute -left-[21px] w-3 h-3 rounded-full bg-slate-600"></span><span className="text-slate-400 text-sm">1990s-2005:</span> <span className="text-slate-300">Manual rules & thresholds</span></div>
                <div className="relative"><span className="absolute -left-[21px] w-3 h-3 rounded-full bg-slate-500"></span><span className="text-slate-400 text-sm">2005-2015:</span> <span className="text-slate-300">Risk-based approaches</span></div>
                <div className="relative"><span className="absolute -left-[21px] w-3 h-3 rounded-full bg-amber-600"></span><span className="text-slate-400 text-sm">2015-2020:</span> <span className="text-slate-300">Hybrid ML systems</span></div>
                <div className="relative"><span className="absolute -left-[21px] w-3 h-3 rounded-full bg-amber-400"></span><span className="text-slate-400 text-sm">2020-2025:</span> <span className="text-slate-300">AI-native deep learning</span></div>
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
            { term: 'Fraud', def: 'Intentional deception for unauthorized financial gain. NOT the same as error, mistake, or policy violation.' },
            { term: 'Classification', def: 'Mathematical function mapping inputs to discrete categories. In fraud: mapping transaction features → {fraud, legitimate}.' },
            { term: 'Precision', def: 'Of all transactions flagged as fraud, what % were actually fraud? High precision = fewer false alarms.' },
            { term: 'Recall', def: 'Of all actual fraud, what % did we catch? High recall = fewer missed frauds.' },
            { term: 'Feature', def: 'A measurable property of a transaction: amount, time, location, velocity, device fingerprint, etc.' },
            { term: 'Concept Drift', def: 'When the statistical relationship between inputs and outputs changes over time—fraud patterns evolve.' },
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
              <li>• XGBoost achieves 97-98% accuracy on fraud datasets</li>
              <li>• Fraud comprises 0.1-0.2% of transactions (extreme imbalance)</li>
              <li>• Chargeback windows extend 120-540 days (delayed labels)</li>
              <li>• False declines cost $81B annually to merchants</li>
              <li>• Production systems require &lt;100ms latency</li>
              <li>• 41% of customers never return after false decline</li>
            </ul>
          </div>
          
          <div className="bg-rose-900/20 rounded-lg p-5 border border-rose-500/30">
            <h4 className="text-rose-400 font-medium mb-3 flex items-center gap-2">
              <span>?</span> Commonly ASSUMED
            </h4>
            <ul className="text-slate-300 space-y-2 text-sm">
              <li>• "More data always improves models" (not if poisoned)</li>
              <li>• "Deep learning beats tree models" (not on tabular data)</li>
              <li>• "Higher accuracy is always better" (at what precision cost?)</li>
              <li>• "Rules are obsolete" (they provide compliance baseline)</li>
              <li>• "Explainability sacrifices accuracy" (myth on structured data)</li>
              <li>• "Removing protected attributes removes bias" (proxy variables persist)</li>
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
        id: 'ml-works',
        assumption: 'ML is the best approach to fraud detection',
        challenge: 'Why do we believe ML works better than rules?',
        analysis: 'Rules can only encode patterns humans already recognize. ML discovers patterns humans miss—but only if those patterns exist in historical data. The assumption that "patterns exist in data" is itself an assumption about fraud behavior being systematic rather than purely random.',
        hidden: 'We assume fraudsters behave systematically enough to be predictable.'
      },
      {
        id: 'accuracy-matters',
        assumption: 'High accuracy is the goal',
        challenge: 'Why do we optimize for accuracy?',
        analysis: 'In 99.9% legitimate transaction base, a model that predicts "not fraud" for everything achieves 99.9% accuracy but catches zero fraud. Accuracy hides the real tradeoff: precision vs recall. The business question is "how much customer friction will we accept to catch more fraud?"',
        hidden: 'We assume accuracy metrics reflect business value—they often don\'t.'
      },
      {
        id: 'more-data',
        assumption: 'More historical data improves models',
        challenge: 'Why would more data help?',
        analysis: 'If fraud patterns from 2020 no longer appear in 2025 (concept drift), old data may hurt rather than help. If fraudsters have poisoned historical data, more poisoned data amplifies the problem. Data quantity only helps if data quality and relevance remain stable.',
        hidden: 'We assume the past predicts the future—fraudsters deliberately break this.'
      },
      {
        id: 'tree-dominance',
        assumption: 'Tree models dominate because they\'re best',
        challenge: 'Why do XGBoost/LightGBM lead production?',
        analysis: 'Trees dominate not because they\'re mathematically optimal, but because: (1) regulations require explainability, (2) domain experts can incorporate features easily, (3) they handle tabular data well, (4) inference is fast. These are socio-technical constraints, not ML optimality.',
        hidden: 'We assume "what works in production" reflects theoretical best—it reflects constraints.'
      },
      {
        id: 'real-time',
        assumption: 'Real-time decisions are necessary',
        challenge: 'Why must we decide in &lt;100ms?',
        analysis: 'Payment authorization expects immediate response—customers won\'t wait. But this is a constraint imposed by payment network design, not a fundamental truth. Authorization holds (7-day review windows) exist specifically because some decisions need more time.',
        hidden: 'We assume the payment system\'s current design is fixed and optimal.'
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
          
          <div className="flex items-center justify-center mb-8">
            <div className="relative">
              <svg viewBox="0 0 400 200" className="w-full max-w-md">
                <defs>
                  <linearGradient id="ladderGrad" x1="0%" y1="100%" x2="0%" y2="0%">
                    <stop offset="0%" stopColor="#22d3ee" stopOpacity="0.2"/>
                    <stop offset="100%" stopColor="#22d3ee" stopOpacity="0.8"/>
                  </linearGradient>
                </defs>
                {/* Ladder rungs */}
                <rect x="100" y="170" width="200" height="20" rx="3" fill="url(#ladderGrad)" opacity="0.3"/>
                <text x="200" y="183" textAnchor="middle" fill="#94a3b8" fontSize="10">Observable Data</text>
                
                <rect x="100" y="135" width="200" height="20" rx="3" fill="url(#ladderGrad)" opacity="0.4"/>
                <text x="200" y="148" textAnchor="middle" fill="#94a3b8" fontSize="10">Selected Data</text>
                
                <rect x="100" y="100" width="200" height="20" rx="3" fill="url(#ladderGrad)" opacity="0.5"/>
                <text x="200" y="113" textAnchor="middle" fill="#94a3b8" fontSize="10">Interpreted Meaning</text>
                
                <rect x="100" y="65" width="200" height="20" rx="3" fill="url(#ladderGrad)" opacity="0.7"/>
                <text x="200" y="78" textAnchor="middle" fill="#94a3b8" fontSize="10">Assumptions Made</text>
                
                <rect x="100" y="30" width="200" height="20" rx="3" fill="url(#ladderGrad)" opacity="0.9"/>
                <text x="200" y="43" textAnchor="middle" fill="#cbd5e1" fontSize="10" fontWeight="bold">Conclusions & Actions</text>
                
                {/* Arrow */}
                <path d="M 320 170 L 320 40 L 330 50 M 320 40 L 310 50" stroke="#22d3ee" strokeWidth="2" fill="none"/>
                <text x="350" y="105" fill="#22d3ee" fontSize="9" transform="rotate(90, 350, 105)">Abstraction Increases</text>
              </svg>
            </div>
          </div>
        </div>

        <div className="space-y-4">
          {assumptions.map((item, i) => (
            <div 
              key={item.id}
              className={`bg-slate-800/50 rounded-xl border border-slate-700/50 overflow-hidden transition-all duration-500 ${animatedItems.includes(i + 1) ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}
            >
              <button
                onClick={() => toggleAxiom(item.id)}
                className="w-full p-6 text-left flex items-center justify-between hover:bg-slate-700/30 transition-colors"
              >
                <div>
                  <p className="text-cyan-400 font-mono text-xs mb-1">ASSUMPTION #{i + 1}</p>
                  <p className="text-lg text-slate-100">"{item.assumption}"</p>
                </div>
                <span className={`text-2xl text-cyan-400 transition-transform ${expandedAxioms[item.id] ? 'rotate-45' : ''}`}>+</span>
              </button>
              
              {expandedAxioms[item.id] && (
                <div className="px-6 pb-6 space-y-4 border-t border-slate-700/50 pt-4">
                  <div className="bg-cyan-900/20 rounded-lg p-4 border border-cyan-500/30">
                    <p className="text-cyan-400 font-medium mb-2">Challenge Question:</p>
                    <p className="text-slate-200 italic" dangerouslySetInnerHTML={{ __html: item.challenge }} />
                  </div>
                  
                  <div className="bg-slate-900/50 rounded-lg p-4">
                    <p className="text-slate-400 font-medium mb-2">Analysis:</p>
                    <p className="text-slate-300 leading-relaxed">{item.analysis}</p>
                  </div>
                  
                  <div className="bg-rose-900/20 rounded-lg p-4 border border-rose-500/30">
                    <p className="text-rose-400 font-medium mb-2">Hidden Assumption Exposed:</p>
                    <p className="text-slate-200">{item.hidden}</p>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>

        <div className={`bg-slate-800/50 rounded-xl p-8 border border-cyan-500/30 transition-all duration-500 ${animatedItems.includes(7) ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
          <h3 className="text-xl font-semibold text-cyan-400 mb-4">Reasoning by Analogy vs. First Principles</h3>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-slate-900/50 rounded-lg p-5">
              <h4 className="text-rose-400 font-medium mb-3">Reasoning by Analogy (Common)</h4>
              <p className="text-slate-300 text-sm mb-3">"Other companies use XGBoost for fraud, so we should too."</p>
              <p className="text-slate-400 text-sm">This imports others' constraints without examining if they apply to us.</p>
            </div>
            <div className="bg-slate-900/50 rounded-lg p-5">
              <h4 className="text-emerald-400 font-medium mb-3">First Principles (Better)</h4>
              <p className="text-slate-300 text-sm mb-3">"What mathematical properties does our fraud problem require? What constraints do our regulations impose?"</p>
              <p className="text-slate-400 text-sm">This derives solutions from fundamental truths about our specific context.</p>
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
        id: 'why-ml',
        claim: 'ML is effective for fraud detection',
        chain: [
          { why: 'Why is ML effective?', answer: 'ML finds patterns in high-dimensional data that humans cannot perceive.' },
          { why: 'Why can\'t humans perceive these patterns?', answer: 'Human cognition cannot process 500+ features simultaneously or detect nonlinear interactions.' },
          { why: 'Why do these patterns exist in fraud data?', answer: 'Fraudsters exhibit behavioral signatures—timing, velocity, device—that differ from legitimate users.' },
          { why: 'Why do fraudsters exhibit detectable signatures?', answer: 'Fraud requires specific operational constraints (monetization paths, attack tools, time pressure) that constrain behavior.' },
          { why: 'Why do operational constraints create patterns?', answer: 'AXIOM: Purposeful action toward goals creates statistical regularity. This is a fundamental truth about intentional behavior—it cannot be completely random or it would not achieve its purpose.', isAxiom: true },
        ]
      },
      {
        id: 'why-adversarial',
        claim: 'Fraud detection faces the "intelligent adversary" problem',
        chain: [
          { why: 'Why do adversaries matter?', answer: 'Fraudsters actively probe and adapt to detection systems, unlike static classification targets.' },
          { why: 'Why do they adapt?', answer: 'Economic incentive: successful fraud = profit. Failed fraud = lost investment. Adaptation is rational.' },
          { why: 'Why does their adaptation break models?', answer: 'Models learn P(fraud|features) from historical data. Adversaries shift the distribution so historical P ≠ future P.' },
          { why: 'Why does this distribution shift persist?', answer: 'It\'s an arms race: any stable detection method becomes a known obstacle to route around.' },
          { why: 'Why is this an arms race?', answer: 'AXIOM: In zero-sum games with feedback, any exploitable strategy will be exploited, forcing counter-adaptation. This is Nash equilibrium dynamics—a mathematical truth about strategic interaction.', isAxiom: true },
        ]
      },
      {
        id: 'why-imbalance',
        claim: 'Class imbalance (0.1-0.2% fraud) is a fundamental challenge',
        chain: [
          { why: 'Why is imbalance a problem?', answer: 'Standard ML objectives optimize overall accuracy, which ignores rare classes.' },
          { why: 'Why do objectives ignore rare classes?', answer: 'Loss functions sum errors equally—1000 correct majorities outweigh 1 missed minority.' },
          { why: 'Why not just reweight?', answer: 'Reweighting helps but doesn\'t solve the fundamental: rare events have less statistical signal to learn from.' },
          { why: 'Why does rarity reduce signal?', answer: 'Statistical estimation variance scales with 1/n. Fewer examples = higher variance = unstable patterns.' },
          { why: 'Why does variance scale with 1/n?', answer: 'AXIOM: Law of Large Numbers—sample statistics converge to true parameters only as n→∞. Small samples have irreducible uncertainty. This is mathematical truth about statistical inference.', isAxiom: true },
        ]
      },
      {
        id: 'why-explainability',
        claim: 'Explainability is legally required',
        chain: [
          { why: 'Why do regulations require explainability?', answer: 'GDPR Article 22, FCRA, ECOA mandate that decisions affecting individuals be explainable.' },
          { why: 'Why do laws mandate explainability?', answer: 'Democratic principle: power exercised over individuals requires accountability and contestability.' },
          { why: 'Why is accountability fundamental?', answer: 'Power without accountability enables arbitrary harm—a core threat to human autonomy and dignity.' },
          { why: 'Why does autonomy matter?', answer: 'AXIOM: In liberal democratic societies, individuals possess inherent dignity and right to understand decisions affecting them. This is a foundational ethical axiom—derived from Kantian ethics and democratic theory.', isAxiom: true },
        ]
      },
    ];

    const axioms = [
      {
        id: 'axiom-1',
        statement: 'Purposeful action creates statistical regularity',
        test: 'Regress Termination',
        confidence: 'High',
        evidence: 'Any goal-directed behavior constrained by physics, economics, or logistics will exhibit patterns. Completely random behavior cannot achieve goals reliably.',
        domain: 'Applies to all fraud types, all adversaries, all time periods'
      },
      {
        id: 'axiom-2',
        statement: 'Zero-sum games with feedback converge to strategic equilibrium',
        test: 'Physical/Logical Law (Game Theory)',
        confidence: 'High',
        evidence: 'Nash equilibrium proof: in repeated games, rational actors will find and exploit any static strategy, forcing perpetual adaptation.',
        domain: 'Applies wherever attackers receive feedback (approvals/declines)'
      },
      {
        id: 'axiom-3',
        statement: 'Statistical estimation requires sufficient samples',
        test: 'Physical/Logical Law (Statistics)',
        confidence: 'High',
        evidence: 'Law of Large Numbers, Central Limit Theorem. Variance of sample mean = σ²/n. Mathematically proven.',
        domain: 'Applies to all ML, not just fraud. Universal constraint.'
      },
      {
        id: 'axiom-4',
        statement: 'Power over individuals requires accountability',
        test: 'Definitional Truth (Democratic Ethics)',
        confidence: 'Medium-High',
        evidence: 'Foundational to democratic governance, enshrined in law globally. Not universal across all political systems.',
        domain: 'Applies in regulated jurisdictions with rule of law'
      },
      {
        id: 'axiom-5',
        statement: 'Information degrades through time without refresh',
        test: 'Physical/Logical Law (Entropy)',
        confidence: 'High',
        evidence: 'Second Law of Thermodynamics extended to information theory. Patterns learned from past data decay as world changes.',
        domain: 'Applies to all predictive systems. Drives concept drift.'
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
            {whyChains.map((chain, i) => (
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
          <h3 className="text-xl font-semibold text-violet-400 mb-6">First Principles Map</h3>
          
          <div className="space-y-4">
            {axioms.map((axiom, i) => (
              <div key={axiom.id} className="bg-slate-900/50 rounded-lg p-5 border border-violet-500/20">
                <div className="flex items-start justify-between gap-4 mb-3">
                  <div>
                    <p className="text-violet-400 font-mono text-xs mb-1">AXIOM #{i + 1}</p>
                    <p className="text-slate-100 font-medium">{axiom.statement}</p>
                  </div>
                  <span className={`px-2 py-1 rounded text-xs font-medium ${axiom.confidence === 'High' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-amber-500/20 text-amber-400'}`}>
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

        {/* Aristotle's Criteria */}
        <div className={`bg-slate-800/50 rounded-xl p-8 border border-slate-700/50 transition-all duration-500 ${animatedItems.includes(2) ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
          <h3 className="text-xl font-semibold text-slate-100 mb-4">Aristotle's Criteria for True First Principles (archai)</h3>
          <div className="grid md:grid-cols-5 gap-4">
            {[
              { name: 'TRUE', desc: 'Corresponds to observable reality' },
              { name: 'PRIMARY', desc: 'Cannot be derived from anything more fundamental' },
              { name: 'INDEMONSTRABLE', desc: 'Proving it requires assuming it' },
              { name: 'BETTER KNOWN', desc: 'More certain than what follows from it' },
              { name: 'PRIOR', desc: 'Logically and epistemically foundational' },
            ].map((c, i) => (
              <div key={i} className="bg-slate-900/50 rounded-lg p-4 text-center">
                <p className="text-violet-400 font-bold mb-2">{c.name}</p>
                <p className="text-slate-400 text-xs">{c.desc}</p>
              </div>
            ))}
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
          <h2 className="text-3xl font-serif text-slate-100 mt-2">How do axioms combine to produce observed phenomena?</h2>
        </div>

        {/* Tab Navigation */}
        <div className="flex gap-2 flex-wrap">
          {[
            { id: 'flow', label: 'Causal Flow' },
            { id: 'feedback', label: 'Feedback Loops' },
            { id: 'leverage', label: 'Leverage Points' },
            { id: 'rebuild', label: 'Rebuild from Axioms' },
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
            <h3 className="text-xl font-semibold text-slate-100 mb-6">From Axioms to Observable System</h3>
            
            <div className="space-y-6">
              {/* Visual flow diagram */}
              <div className="bg-slate-900/50 rounded-lg p-6">
                <div className="grid grid-cols-1 md:grid-cols-5 gap-4 items-center text-center">
                  <div className="bg-violet-900/30 rounded-lg p-4 border border-violet-500/30">
                    <p className="text-violet-400 font-mono text-xs mb-1">AXIOM</p>
                    <p className="text-sm text-slate-200">Purposeful action creates regularity</p>
                  </div>
                  <div className="text-emerald-400 text-2xl hidden md:block">→</div>
                  <div className="bg-emerald-900/20 rounded-lg p-4 border border-emerald-500/30">
                    <p className="text-emerald-400 font-mono text-xs mb-1">MECHANISM</p>
                    <p className="text-sm text-slate-200">Fraud behavior generates statistical signal</p>
                  </div>
                  <div className="text-emerald-400 text-2xl hidden md:block">→</div>
                  <div className="bg-amber-900/20 rounded-lg p-4 border border-amber-500/30">
                    <p className="text-amber-400 font-mono text-xs mb-1">OBSERVABLE</p>
                    <p className="text-sm text-slate-200">ML models can learn to classify</p>
                  </div>
                </div>
              </div>

              <div className="grid md:grid-cols-2 gap-6">
                <div className="bg-slate-900/50 rounded-lg p-5">
                  <h4 className="text-emerald-400 font-medium mb-3">Mechanism 1: Pattern Learning</h4>
                  <div className="text-slate-300 text-sm space-y-2">
                    <p><strong className="text-slate-200">Axiom:</strong> Statistical estimation requires sufficient samples</p>
                    <p><strong className="text-slate-200">+ Axiom:</strong> Purposeful action creates regularity</p>
                    <p><strong className="text-slate-200">= Mechanism:</strong> Given enough fraud examples with consistent patterns, models can approximate P(fraud|features)</p>
                    <p><strong className="text-slate-200">Constraint:</strong> Rare events (0.1%) limit sample size, increasing variance in learned patterns</p>
                  </div>
                </div>

                <div className="bg-slate-900/50 rounded-lg p-5">
                  <h4 className="text-emerald-400 font-medium mb-3">Mechanism 2: Model Decay</h4>
                  <div className="text-slate-300 text-sm space-y-2">
                    <p><strong className="text-slate-200">Axiom:</strong> Information degrades through time</p>
                    <p><strong className="text-slate-200">+ Axiom:</strong> Zero-sum games converge to equilibrium</p>
                    <p><strong className="text-slate-200">= Mechanism:</strong> Historical patterns become obsolete as adversaries adapt, requiring continuous retraining</p>
                    <p><strong className="text-slate-200">Constraint:</strong> Delayed feedback (120+ days) means models can silently degrade before detection</p>
                  </div>
                </div>

                <div className="bg-slate-900/50 rounded-lg p-5">
                  <h4 className="text-emerald-400 font-medium mb-3">Mechanism 3: Regulatory Constraint</h4>
                  <div className="text-slate-300 text-sm space-y-2">
                    <p><strong className="text-slate-200">Axiom:</strong> Power requires accountability</p>
                    <p><strong className="text-slate-200">= Mechanism:</strong> Models must be explainable to comply with law</p>
                    <p><strong className="text-slate-200">Consequence:</strong> Tree-based models dominate despite potentially lower raw accuracy because they satisfy this constraint</p>
                    <p><strong className="text-slate-200">Trade-off:</strong> Explainability requirements may reduce detection rates by 5-10%</p>
                  </div>
                </div>

                <div className="bg-slate-900/50 rounded-lg p-5">
                  <h4 className="text-emerald-400 font-medium mb-3">Mechanism 4: Arms Race Dynamics</h4>
                  <div className="text-slate-300 text-sm space-y-2">
                    <p><strong className="text-slate-200">Axiom:</strong> Zero-sum games force counter-adaptation</p>
                    <p><strong className="text-slate-200">= Mechanism:</strong> Any effective detection method is probed, learned, and evaded by adversaries</p>
                    <p><strong className="text-slate-200">Implication:</strong> No static model can remain effective—perpetual evolution required</p>
                    <p><strong className="text-slate-200">Evidence:</strong> TaoBao study: precision dropped from 90% → 20% under adversarial attack</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Feedback Loops */}
        {activeTab === 'feedback' && (
          <div className={`bg-slate-800/50 rounded-xl p-8 border border-slate-700/50 transition-all duration-500 ${animatedItems.includes(0) ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
            <h3 className="text-xl font-semibold text-slate-100 mb-6">Critical Feedback Loops</h3>
            
            <div className="space-y-6">
              {[
                {
                  name: 'Adversarial Learning Loop',
                  type: 'Reinforcing (Negative)',
                  description: 'Model blocks fraud → Fraudster observes decline → Fraudster modifies approach → Modified fraud evades model → Model accuracy drops',
                  color: 'rose'
                },
                {
                  name: 'Price of Success Paradox',
                  type: 'Balancing (Negative)',
                  description: 'Model catches fraud → Less fraud succeeds → Fewer fraud examples in training data → Model has less signal to learn from → Model quality degrades',
                  color: 'amber'
                },
                {
                  name: 'Analyst Feedback Loop',
                  type: 'Reinforcing (Positive)',
                  description: 'Model flags uncertain cases → Analyst reviews and labels → Labels improve training data → Model uncertainty decreases → Better predictions',
                  color: 'emerald'
                },
                {
                  name: 'Customer Trust Loop',
                  type: 'Reinforcing (Can be +/-)',
                  description: 'False decline → Customer abandons cart → Lost revenue → Pressure to reduce false positives → Threshold lowered → More fraud gets through OR better model deployed',
                  color: 'cyan'
                }
              ].map((loop, i) => (
                <div key={i} className={`bg-slate-900/50 rounded-lg p-5 border-l-4 border-${loop.color}-500`}>
                  <div className="flex items-start justify-between gap-4 mb-3">
                    <h4 className={`text-${loop.color}-400 font-medium`}>{loop.name}</h4>
                    <span className={`text-xs px-2 py-1 rounded bg-${loop.color}-500/20 text-${loop.color}-300`}>{loop.type}</span>
                  </div>
                  <div className="flex items-center gap-2 text-slate-300 text-sm flex-wrap">
                    {loop.description.split(' → ').map((step, j, arr) => (
                      <React.Fragment key={j}>
                        <span className="bg-slate-800 px-2 py-1 rounded">{step}</span>
                        {j < arr.length - 1 && <span className={`text-${loop.color}-400`}>→</span>}
                      </React.Fragment>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Leverage Points */}
        {activeTab === 'leverage' && (
          <div className={`bg-slate-800/50 rounded-xl p-8 border border-slate-700/50 transition-all duration-500 ${animatedItems.includes(0) ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
            <h3 className="text-xl font-semibold text-slate-100 mb-6">Maximum Leverage Intervention Points</h3>
            <p className="text-slate-400 mb-6">Ranked by impact per unit of investment (Meadows hierarchy)</p>
            
            <div className="space-y-4">
              {[
                { rank: 1, point: 'Paradigm Shift', example: 'From "catch fraud" to "make fraud economically unviable"', impact: 'Transformational', effort: 'Very High' },
                { rank: 2, point: 'System Goals', example: 'Optimize for customer LTV, not just fraud rate', impact: 'Very High', effort: 'High' },
                { rank: 3, point: 'Feedback Loop Structure', example: 'Real-time analyst feedback vs. batch retraining', impact: 'High', effort: 'Medium' },
                { rank: 4, point: 'Information Flow', example: 'Cross-institutional data sharing (federated learning)', impact: 'High', effort: 'High' },
                { rank: 5, point: 'Rules of the System', example: 'Regulatory requirements for explainability', impact: 'Medium', effort: 'External' },
                { rank: 6, point: 'Parameters', example: 'Threshold tuning, feature weights', impact: 'Low', effort: 'Low' },
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
                    <p className={`text-sm font-medium ${item.impact === 'Transformational' || item.impact === 'Very High' ? 'text-emerald-400' : item.impact === 'High' ? 'text-amber-400' : 'text-slate-400'}`}>
                      {item.impact} Impact
                    </p>
                    <p className="text-slate-500 text-xs">{item.effort} Effort</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Rebuild from Axioms */}
        {activeTab === 'rebuild' && (
          <div className={`bg-slate-800/50 rounded-xl p-8 border border-slate-700/50 transition-all duration-500 ${animatedItems.includes(0) ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
            <h3 className="text-xl font-semibold text-slate-100 mb-6">Rebuilding ML Fraud Detection from First Principles</h3>
            <p className="text-slate-400 mb-6">If we knew only the axioms, what system would we design?</p>
            
            <div className="space-y-6">
              <div className="bg-emerald-900/20 rounded-lg p-5 border border-emerald-500/30">
                <h4 className="text-emerald-400 font-medium mb-3">The Feynman Test</h4>
                <p className="text-slate-300 text-sm">
                  "What I cannot create, I do not understand." Can we derive the modern ML fraud system purely from axioms?
                </p>
              </div>

              <div className="relative pl-8 border-l-2 border-emerald-500/50 space-y-6">
                {[
                  { axiom: 'Purposeful action creates regularity', derivation: 'Therefore: fraud behavior will exhibit learnable patterns. Build a pattern-learning system (ML classifier).' },
                  { axiom: 'Statistical estimation requires samples', derivation: 'Therefore: we need labeled fraud examples. Build feedback loops to capture chargebacks and analyst labels.' },
                  { axiom: 'Zero-sum games force adaptation', derivation: 'Therefore: patterns will shift. Build continuous retraining and drift detection. No static model.' },
                  { axiom: 'Information degrades through time', derivation: 'Therefore: recent data matters more. Weight recent examples higher. Implement time-decay.' },
                  { axiom: 'Power requires accountability', derivation: 'Therefore: decisions must be explainable. Choose interpretable models (trees) or add explanation layers (SHAP).' },
                ].map((step, i) => (
                  <div key={i} className="relative">
                    <span className="absolute -left-[13px] w-6 h-6 rounded-full bg-emerald-500 flex items-center justify-center text-xs text-slate-900 font-bold">
                      {i + 1}
                    </span>
                    <div className="bg-slate-900/50 rounded-lg p-4">
                      <p className="text-violet-400 text-sm font-medium mb-2">From: "{step.axiom}"</p>
                      <p className="text-slate-300">{step.derivation}</p>
                    </div>
                  </div>
                ))}
              </div>

              <div className="bg-slate-900/50 rounded-lg p-5 border border-slate-700/30">
                <h4 className="text-slate-100 font-medium mb-3">Result: Derived System Architecture</h4>
                <p className="text-slate-300 text-sm">
                  From five axioms alone, we derive: (1) ML-based classification, (2) labeled data collection via feedback, 
                  (3) continuous retraining with drift detection, (4) time-weighted features, and (5) explainable model selection.
                  This matches exactly what industry leaders like Stripe, PayPal, and Mastercard have built—validating that 
                  the axioms are correct and sufficient.
                </p>
              </div>
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
                <li>• Fraud is goal-directed (not random errors)</li>
                <li>• Historical data contains representative fraud examples</li>
                <li>• Feedback loops exist (chargebacks, reports)</li>
                <li>• Jurisdiction has accountability requirements</li>
                <li>• Attack surface is digital (produces data)</li>
                <li>• Economic incentives drive fraudster behavior</li>
              </ul>
            </div>
            
            <div className="bg-rose-900/20 rounded-lg p-5 border border-rose-500/30">
              <h4 className="text-rose-400 font-medium mb-3">✗ Axioms Break Down When:</h4>
              <ul className="text-slate-300 text-sm space-y-2">
                <li>• Fraud is truly novel (no historical examples)</li>
                <li>• Insider threats with legitimate access patterns</li>
                <li>• Jurisdiction without explainability requirements</li>
                <li>• Attacks don't require repeated transactions</li>
                <li>• Social engineering without digital footprint</li>
                <li>• State-sponsored attacks (infinite resources)</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Transfer Opportunities */}
        <div className={`bg-slate-800/50 rounded-xl p-8 border border-slate-700/50 transition-all duration-500 ${animatedItems.includes(1) ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
          <h3 className="text-xl font-semibold text-slate-100 mb-6">Transfer: Analogous Domains Sharing These Axioms</h3>
          
          <div className="grid md:grid-cols-3 gap-4">
            {[
              { domain: 'Cybersecurity', shared: ['Intelligent adversary', 'Arms race', 'Pattern detection'], unique: 'Network topology focus' },
              { domain: 'Spam Detection', shared: ['Adversarial adaptation', 'Class imbalance', 'Concept drift'], unique: 'Text/content focus' },
              { domain: 'Medical Diagnosis', shared: ['Class imbalance', 'Explainability need', 'High stakes'], unique: 'No adversary (disease doesn\'t adapt)' },
              { domain: 'Credit Scoring', shared: ['Regulatory requirements', 'Fairness concerns', 'Explainability'], unique: 'Not adversarial (mostly)' },
              { domain: 'Autonomous Vehicles', shared: ['Real-time latency', 'High stakes', 'Explainability'], unique: 'Physics-based patterns' },
              { domain: 'Anti-Money Laundering', shared: ['All fraud axioms', 'Longer time horizons', 'Graph analysis'], unique: 'Network-level focus' },
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

        {/* What-If Scenarios */}
        <div className={`bg-slate-800/50 rounded-xl p-8 border border-slate-700/50 transition-all duration-500 ${animatedItems.includes(2) ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
          <h3 className="text-xl font-semibold text-slate-100 mb-6">What If: Novel Applications from First Principles</h3>
          
          <div className="space-y-4">
            {[
              {
                scenario: 'What if we had real-time ground truth (no delayed feedback)?',
                analysis: 'The "information degrades" constraint would loosen. Models could adapt instantly. Adversarial adaptation would still occur but we\'d detect it faster. Active learning would become even more powerful.',
                implication: 'Invest in faster label collection (real-time 3D Secure challenges, instant merchant confirmation).'
              },
              {
                scenario: 'What if we could share data across all institutions?',
                analysis: 'The "sample size" constraint would ease dramatically. Rare fraud types would have 1000x more examples. But privacy axioms and competitive dynamics create new constraints.',
                implication: 'Federated learning and privacy-preserving computation become critical enabling technologies.'
              },
              {
                scenario: 'What if adversaries had access to our model?',
                analysis: 'Assume they already do (black-box probing). The adversarial axiom tells us this doesn\'t fundamentally change the game—it just accelerates it. Defense must assume compromised models.',
                implication: 'Ensemble diversity, randomized thresholds, and continuous model rotation become essential.'
              },
              {
                scenario: 'What if explainability requirements were removed?',
                analysis: 'Black-box models (deep learning) could be deployed. Accuracy might increase 5-10% on complex patterns. But fairness violations would go undetected, creating legal and ethical risk.',
                implication: 'Explainability constraints exist for good reasons. Work within them rather than hoping they disappear.'
              },
            ].map((item, i) => (
              <div key={i} className="bg-slate-900/50 rounded-lg p-5 border border-slate-700/30">
                <h4 className="text-pink-400 font-medium mb-2">{item.scenario}</h4>
                <div className="grid md:grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-slate-500 text-xs mb-1">Analysis:</p>
                    <p className="text-slate-300">{item.analysis}</p>
                  </div>
                  <div>
                    <p className="text-slate-500 text-xs mb-1">Strategic Implication:</p>
                    <p className="text-emerald-300">{item.implication}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Emerging Frontiers */}
        <div className={`bg-slate-800/50 rounded-xl p-8 border border-pink-500/30 transition-all duration-500 ${animatedItems.includes(3) ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
          <h3 className="text-xl font-semibold text-pink-400 mb-6">Emerging Frontiers: Where Axioms Meet New Technology</h3>
          
          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-slate-900/50 rounded-lg p-5">
              <h4 className="text-slate-100 font-medium mb-3">Large Language Models</h4>
              <p className="text-slate-300 text-sm mb-3">
                LLMs achieve 97.98% accuracy on phone call fraud detection. They satisfy the "purposeful action creates regularity" axiom by detecting semantic patterns in conversation.
              </p>
              <p className="text-pink-400 text-sm">First principles question: Does the "explainability" axiom permit LLM deployment? Current answer: marginally, with careful SHAP/attention analysis.</p>
            </div>
            
            <div className="bg-slate-900/50 rounded-lg p-5">
              <h4 className="text-slate-100 font-medium mb-3">Graph Neural Networks</h4>
              <p className="text-slate-300 text-sm mb-3">
                GNNs achieve 0.991 AUC by detecting fraud rings—coordinated attacks invisible to individual transaction analysis.
              </p>
              <p className="text-pink-400 text-sm">First principles insight: Fraudsters collaborate (purposeful action), creating relational patterns. GNNs exploit the axiom at the network level.</p>
            </div>
            
            <div className="bg-slate-900/50 rounded-lg p-5">
              <h4 className="text-slate-100 font-medium mb-3">Multi-Agent Systems</h4>
              <p className="text-slate-300 text-sm mb-3">
                Oracle, FraudShield deploy specialized agents for investigation. Reduces investigation time by 60%.
              </p>
              <p className="text-pink-400 text-sm">First principles insight: Human analysts have bounded attention (cognitive axiom). Agent specialization matches human cognitive architecture.</p>
            </div>
            
            <div className="bg-slate-900/50 rounded-lg p-5">
              <h4 className="text-slate-100 font-medium mb-3">Synthetic Data Generation</h4>
              <p className="text-slate-300 text-sm mb-3">
                Diffusion models and GANs create synthetic fraud examples, addressing the class imbalance axiom constraint.
              </p>
              <p className="text-pink-400 text-sm">First principles risk: Synthetic data assumes we know the fraud distribution. If we're wrong, we amplify our blindspots.</p>
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
  // PHASE 5: SYNTHESIS (KNOWLEDGE CHECK)
  // ============================================================================
  const SynthesisPhase = () => {
    const questions = [
      {
        id: 'q1',
        question: 'Why do tree-based models (XGBoost, LightGBM) dominate production fraud systems?',
        options: [
          'They have the highest mathematical accuracy',
          'They satisfy regulatory explainability requirements while maintaining strong performance',
          'They were invented first and became industry standard',
          'Deep learning requires too much compute'
        ],
        correct: 1,
        explanation: 'From our axioms: "Power requires accountability" creates regulatory explainability requirements. Tree models satisfy this constraint while providing competitive accuracy on tabular data. This is a socio-technical constraint, not pure ML optimality.'
      },
      {
        id: 'q2',
        question: 'What first principle explains why fraud detection models degrade over time?',
        options: [
          'Software entropy causes code to become buggy',
          'Training data expires after a certain period',
          'Adversarial equilibrium forces fraudsters to adapt, invalidating learned patterns',
          'Regulatory changes require model updates'
        ],
        correct: 2,
        explanation: 'The axiom "Zero-sum games with feedback converge to strategic equilibrium" explains this. Fraudsters receive feedback (approvals/declines) and rationally adapt to evade detection. Static models become exploitable targets.'
      },
      {
        id: 'q3',
        question: 'Why is 98% accuracy potentially misleading for fraud detection?',
        options: [
          'It\'s too high to be realistic',
          'With 0.1% fraud rate, a model predicting "not fraud" achieves 99.9% accuracy while catching zero fraud',
          'Accuracy is measured incorrectly in fraud systems',
          'Fraud definitions vary by country'
        ],
        correct: 1,
        explanation: 'From the axiom "Statistical estimation requires sufficient samples": extreme class imbalance (0.1-0.2% fraud) means accuracy rewards majority-class prediction. The real metrics are precision (false alarm rate) and recall (catch rate).'
      },
      {
        id: 'q4',
        question: 'What makes the "intelligent adversary" problem unique to fraud detection?',
        options: [
          'Fraudsters are smarter than other criminals',
          'Unlike image recognition, the target distribution actively evolves to evade detection',
          'Fraud data is more complex than other ML domains',
          'Financial transactions have more features'
        ],
        correct: 1,
        explanation: 'The axiom "Purposeful action creates regularity" applies to both legitimate users AND fraudsters—but fraudsters purposefully adapt to make their actions NOT regular. This creates an arms race absent from static classification tasks.'
      },
      {
        id: 'q5',
        question: 'If you could only implement one improvement to a fraud system, which would have the highest leverage?',
        options: [
          'Tune the classification threshold more precisely',
          'Add more features to the model',
          'Implement real-time analyst feedback loops',
          'Switch from XGBoost to deep learning'
        ],
        correct: 2,
        explanation: 'From Meadows\' leverage hierarchy: feedback loop structure changes have much higher impact than parameter tuning. Analyst feedback provides real-time labels, combats concept drift, and addresses the delayed feedback axiom constraint.'
      },
      {
        id: 'q6',
        question: 'Why does "fairness through unawareness" (removing protected attributes) NOT work?',
        options: [
          'It\'s illegal to remove protected attributes',
          'Proxy variables (ZIP codes, transaction patterns) correlate with protected attributes and carry the bias',
          'The model needs those features for accuracy',
          'Regulators require all features to be present'
        ],
        correct: 1,
        explanation: 'This is an empirical finding, not derivable from our axioms alone—it\'s a boundary of our first-principles framework. The hidden structure of data correlation requires empirical investigation beyond axiom-level reasoning.'
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
                    const showFeedback = showResults && isSelected;
                    
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
                <p>• "Accountability requires explainability" — some argue outcome fairness matters more than process transparency</p>
                <p>• "Purposeful action is always detectable" — quantum/zero-knowledge fraud might break this</p>
                <p>• "More data improves estimation" — at what point does adversarial poisoning dominate?</p>
              </div>
            </div>
            
            <div className="space-y-4">
              <h4 className="text-slate-100 font-medium">Recommended Areas for Further Investigation</h4>
              <div className="text-slate-300 text-sm space-y-2">
                <p>• Causal inference for fraud: can we identify causal fraud mechanisms vs. correlations?</p>
                <p>• Adversarial robustness guarantees: can we mathematically bound model degradation?</p>
                <p>• Multi-agent fraud ecosystems: how do fraud rings coordinate and can we model this?</p>
                <p>• LLM-based fraud: how do axioms apply when fraudsters use generative AI?</p>
              </div>
            </div>
          </div>
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
                  <span className="text-2xl">△</span>
                </div>
                <div>
                  <h1 className="text-2xl font-serif text-slate-100">ML Fraud Detection: From Axioms to Application</h1>
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

export default MLFraudFirstPrinciplesGuide;

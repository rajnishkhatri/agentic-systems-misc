import React, { useState, useMemo } from 'react';

// Components
import FallacyCard from './components/FallacyCard';
import PatternAntiPatternCard from './components/PatternAntiPatternCard';
import PolyaPhaseFlow from './components/PolyaPhaseFlow';
import WorkedExampleBreakdown from './components/WorkedExampleBreakdown';
import QuizMode from './components/QuizMode';

// Data
import fallaciesData from './data/fallacies-data.json';
import patternsData from './data/patterns-anti-patterns.json';
import phasesData from './data/polya-phases.json';
import disputeData from './data/dispute-grounding.json';
import hwMethodsData from './data/hw-counter-methods.json';

const LogicalFallaciesExplorer = () => {
  const [activeFallacyId, setActiveFallacyId] = useState(null);
  const [activePhase, setActivePhase] = useState("UNDERSTAND");
  const [completedPhases, setCompletedPhases] = useState([]);

  // Memoized data lookups
  const activeFallacy = useMemo(() => 
    fallaciesData.find(f => f.id === activeFallacyId), 
    [activeFallacyId]
  );

  const activePattern = useMemo(() => 
    patternsData.find(p => p.fallacy_id === activeFallacyId), 
    [activeFallacyId]
  );

  const activeExample = useMemo(() => 
    disputeData.find(d => d.fallacy_id === activeFallacyId), 
    [activeFallacyId]
  );

  const activeCounter = useMemo(() => 
    hwMethodsData.find(h => h.fallacy_id === activeFallacyId), 
    [activeFallacyId]
  );

  // Handlers
  const handlePhaseSelect = (phase) => {
    setActivePhase(phase);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleReturn = () => {
    setActiveFallacyId(null);
    setActivePhase("UNDERSTAND");
    setCompletedPhases([]);
  };

  // Render Content based on Phase
  const renderPhaseContent = () => {
    switch (activePhase) {
      case "UNDERSTAND":
        return (
          <div className="animate-fadeIn space-y-6">
            <FallacyCard 
              fallacy={activeFallacy} 
              isActive={true} 
              onClick={() => {}} 
            />
            
            <div className="bg-rose-50 border border-rose-200 rounded-xl p-6">
              <h3 className="text-lg font-bold text-rose-800 mb-4 flex items-center gap-2">
                <span>🚩</span> Red Flags to Watch For
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {activePattern?.anti_pattern?.red_flags?.map((flag, idx) => (
                  <div key={idx} className="bg-white p-3 rounded-lg border border-rose-100 shadow-sm flex items-start gap-3">
                    <span className="text-rose-500 font-bold">•</span>
                    <span className="text-slate-700 text-sm">{flag}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        );

      case "PLAN":
        return (
          <div className="animate-fadeIn">
            <div className="bg-indigo-50 border border-indigo-100 rounded-xl p-6 mb-6">
               <h3 className="text-lg font-bold text-indigo-900 mb-2">Detection Strategy</h3>
               <p className="text-indigo-800">
                 To detect this fallacy, we need to compare the "Pitch" against the "Reality" by examining the data distribution and testing methodology.
               </p>
            </div>
            <PatternAntiPatternCard 
              data={activePattern} 
              // counterMethod passed here if we want it, but maybe better in COUNTER phase
            />
          </div>
        );

      case "TASKS":
        return (
          <div className="animate-fadeIn space-y-4">
            <h3 className="text-xl font-bold text-slate-800 mb-4">Verification Checklist</h3>
            {[
              "Request the full confusion matrix (not just accuracy)",
              "Verify test set distribution matches production traffic",
              "Check for 'Seed Hacking' (best of N runs)",
              "Identify any excluded 'edge cases' or 'outliers'"
            ].map((task, idx) => (
              <label key={idx} className="flex items-center gap-4 p-4 bg-white border border-slate-200 rounded-xl cursor-pointer hover:bg-slate-50 transition-colors">
                <input type="checkbox" className="w-5 h-5 text-indigo-600 rounded focus:ring-indigo-500" />
                <span className="text-slate-700 font-medium">{task}</span>
              </label>
            ))}
            
            <div className="mt-8 p-6 bg-slate-900 rounded-xl text-slate-300 font-mono text-sm overflow-x-auto">
              <p className="text-xs text-slate-500 uppercase mb-2">SQL Verification Query</p>
              <pre>{`SELECT 
  network, 
  reason_code, 
  COUNT(*) as volume,
  SUM(CASE WHEN prediction = label THEN 1 ELSE 0 END) / COUNT(*) as accuracy
FROM model_eval_results
GROUP BY 1, 2
ORDER BY volume DESC;`}</pre>
            </div>
          </div>
        );

      case "EXECUTE":
        return (
          <div className="animate-fadeIn">
            <WorkedExampleBreakdown example={activeExample} />
          </div>
        );

      case "REFLECT":
        // Hardcoded quiz for demo purposes as it's not in JSON yet
        const demoQuestions = [
          {
            question: "Why is '99% Accuracy' often a red flag in fraud detection?",
            options: [
              "It's too low for financial systems",
              "It suggests the test set might be unbalanced (e.g., 99% non-fraud)",
              "It means the model is overfitting to noise",
              "It's actually a good sign, no red flag"
            ],
            correctAnswer: 1,
            explanation: "In imbalanced datasets (like fraud), a model can achieve 99% accuracy by simply predicting 'Legit' for everything. You need Precision/Recall or Confusion Matrices."
          }
        ];
        return (
          <div className="animate-fadeIn">
            <QuizMode 
              questions={demoQuestions} 
              onComplete={(score) => console.log("Quiz completed", score)}
              onClose={() => handlePhaseSelect("COUNTER")}
            />
          </div>
        );

      case "COUNTER":
        return (
          <div className="animate-fadeIn space-y-6">
            <div className="bg-indigo-50 border border-indigo-100 rounded-xl p-8 text-center">
              <span className="text-4xl mb-4 block">🛡️</span>
              <h3 className="text-2xl font-bold text-indigo-900 mb-2">Counter-Measure Applied</h3>
              <p className="text-indigo-700 max-w-2xl mx-auto">
                You have successfully identified the fallacy and have the tools to refute it.
              </p>
            </div>

            {activeCounter && (
              <div className="bg-white border border-slate-200 rounded-xl p-6">
                <h4 className="text-sm font-bold text-slate-500 uppercase tracking-wide mb-4">
                  Recommended HW Method
                </h4>
                <div className="flex items-start gap-4">
                  <div className="bg-indigo-100 p-3 rounded-lg text-indigo-600 font-bold">
                    {activeCounter.hw_method}
                  </div>
                  <div>
                    <h5 className="font-bold text-slate-800">{activeCounter.technique}</h5>
                    <p className="text-slate-600 mt-1">{activeCounter.description}</p>
                    <div className="mt-4 bg-slate-50 p-3 rounded font-mono text-xs text-slate-600 border border-slate-200">
                      from {activeCounter.code_reference} import ...
                    </div>
                  </div>
                </div>
              </div>
            )}
            
            <button 
              onClick={handleReturn}
              className="w-full py-4 bg-slate-800 text-white rounded-xl font-bold hover:bg-slate-700 transition-all shadow-lg"
            >
              Complete & Return to Overview
            </button>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 font-sans text-slate-900">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-50">
        <div className="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-2xl">🦉</span>
            <h1 className="font-bold text-xl text-slate-800 tracking-tight">
              AI Logical Fallacies <span className="text-indigo-600 text-sm font-normal ml-2 bg-indigo-50 px-2 py-1 rounded-full">Interactive Tutor</span>
            </h1>
          </div>
          {activeFallacyId && (
            <button 
              onClick={handleReturn}
              className="text-sm font-medium text-slate-500 hover:text-slate-800 transition-colors"
            >
              ← Back to List
            </button>
          )}
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-6 py-8">
        {!activeFallacyId ? (
          /* Dashboard View */
          <div className="animate-fadeIn">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold text-slate-800 mb-4">Master the Art of AI Skepticism</h2>
              <p className="text-slate-600 max-w-2xl mx-auto text-lg">
                Identify, analyze, and counter common logical fallacies found in AI product pitches, research papers, and technical debates.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {fallaciesData.map((fallacy) => (
                <FallacyCard 
                  key={fallacy.id} 
                  fallacy={fallacy} 
                  isActive={false}
                  onClick={() => setActiveFallacyId(fallacy.id)} 
                />
              ))}
              
              {/* Placeholders for future fallacies to fill the grid visually */}
              {[1, 2, 3].map((i) => (
                <div key={i} className="border border-dashed border-slate-200 rounded-xl p-6 flex flex-col items-center justify-center text-center opacity-60">
                  <span className="text-3xl mb-2 grayscale">🔒</span>
                  <p className="font-bold text-slate-400">Coming Soon</p>
                  <p className="text-xs text-slate-400 mt-1">More fallacies in development</p>
                </div>
              ))}
            </div>
          </div>
        ) : (
          /* Detail View */
          <div className="animate-fadeIn">
             <div className="mb-6">
                <h2 className="text-3xl font-bold text-slate-900 mb-2">{activeFallacy.name}</h2>
                <p className="text-slate-600 text-lg">{activeFallacy.description}</p>
             </div>

             <PolyaPhaseFlow 
               phases={phasesData} 
               activePhase={activePhase} 
               onPhaseSelect={handlePhaseSelect} 
             />

             {renderPhaseContent()}
          </div>
        )}
      </main>
    </div>
  );
};

export default LogicalFallaciesExplorer;

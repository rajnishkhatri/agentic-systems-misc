import React, { useState } from 'react';

const WorkedExampleBreakdown = ({ example }) => {
  const [activeAnnotation, setActiveAnnotation] = useState(null);

  if (!example) return null;

  return (
    <div className="bg-white rounded-xl shadow-lg border border-slate-200 overflow-hidden my-6">
      <div className="bg-slate-800 p-4 flex items-center justify-between">
        <div className="flex items-center gap-2 text-white">
          <span>📝</span>
          <h3 className="font-bold">Worked Example: {example.title}</h3>
        </div>
        <span className="text-xs bg-slate-700 text-slate-300 px-2 py-1 rounded">EXECUTE Phase</span>
      </div>

      <div className="p-6">
        {/* Scenario Context */}
        <div className="mb-6">
          <p className="text-sm font-bold text-slate-500 uppercase tracking-wide mb-2">Scenario</p>
          <p className="text-slate-700">{example.scenario}</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* The Claim (Left) */}
          <div className="bg-amber-50 rounded-lg p-6 border border-amber-200 relative">
            <div className="absolute top-0 right-0 bg-amber-200 text-amber-800 text-xs font-bold px-2 py-1 rounded-bl-lg">
              VENDOR CLAIM
            </div>
            <p className="font-serif text-lg text-slate-800 italic leading-relaxed">
              "{example.scenario}" 
              {/* Note: In a real implementation, we'd parse the claim to be highlightable text segments */}
            </p>
            
            <div className="mt-4 pt-4 border-t border-amber-200/50">
               <p className="text-sm text-slate-600">
                 <strong className="text-amber-800">The Pitch:</strong> High accuracy, production ready.
               </p>
            </div>
          </div>

          {/* The Reality Check (Right) */}
          <div className="space-y-4">
            <div 
              className={`
                p-4 rounded-lg border cursor-pointer transition-all
                ${activeAnnotation === 'truth' ? 'bg-indigo-50 border-indigo-300 shadow-md' : 'bg-white border-slate-200 hover:bg-slate-50'}
              `}
              onMouseEnter={() => setActiveAnnotation('truth')}
              onMouseLeave={() => setActiveAnnotation(null)}
            >
              <div className="flex items-start gap-3">
                <span className="text-xl">🔍</span>
                <div>
                  <h4 className="font-bold text-slate-800 text-sm mb-1">The Ground Truth</h4>
                  <p className="text-sm text-slate-600">{example.ground_truth}</p>
                </div>
              </div>
            </div>

            <div 
              className={`
                p-4 rounded-lg border cursor-pointer transition-all
                ${activeAnnotation === 'reality' ? 'bg-rose-50 border-rose-300 shadow-md' : 'bg-white border-slate-200 hover:bg-slate-50'}
              `}
              onMouseEnter={() => setActiveAnnotation('reality')}
              onMouseLeave={() => setActiveAnnotation(null)}
            >
              <div className="flex items-start gap-3">
                <span className="text-xl">💥</span>
                <div>
                  <h4 className="font-bold text-slate-800 text-sm mb-1">Production Reality</h4>
                  <p className="text-sm text-slate-600">{example.reality}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* References Footer */}
        {example.dataset_references && (
          <div className="mt-6 pt-4 border-t border-slate-100">
             <p className="text-xs font-semibold text-slate-400 uppercase mb-2">Verified Against Data Sources</p>
             <div className="flex flex-wrap gap-2">
               {example.dataset_references.map((ref, idx) => (
                 <span key={idx} className="text-xs bg-slate-100 text-slate-500 px-2 py-1 rounded font-mono truncate max-w-xs" title={ref}>
                   📄 {ref.split('/').pop()}
                 </span>
               ))}
             </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default WorkedExampleBreakdown;

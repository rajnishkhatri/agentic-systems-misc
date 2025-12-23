import React from 'react';

const PatternAntiPatternCard = ({ data, counterMethod }) => {
  if (!data) return null;

  const { anti_pattern, pattern } = data;

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden my-6">
      {/* Header handled by parent or omitted if redundant */}
      
      <div className="grid grid-cols-1 md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-slate-200">
        
        {/* Anti-Pattern Side */}
        <div className="p-6 bg-rose-50/30">
          <div className="flex items-center gap-2 mb-3 text-rose-600">
            <span className="text-xl">❌</span>
            <h4 className="font-bold text-sm tracking-wide uppercase">Anti-Pattern</h4>
          </div>
          
          <h3 className="text-lg font-bold text-slate-800 mb-2">{anti_pattern.title}</h3>
          <p className="text-slate-600 mb-4 min-h-[3rem]">{anti_pattern.description}</p>
          
          <div className="mb-4">
            <p className="text-xs font-semibold text-rose-700 uppercase mb-2">🚩 Red Flags</p>
            <ul className="space-y-1">
              {anti_pattern.red_flags.map((flag, idx) => (
                <li key={idx} className="flex items-start gap-2 text-sm text-slate-700">
                  <span className="text-rose-400 mt-0.5">•</span>
                  {flag}
                </li>
              ))}
            </ul>
          </div>

          <div className="mt-4">
            <p className="text-xs font-semibold text-slate-500 uppercase mb-2">Code Smell</p>
            <pre className="bg-slate-900 text-rose-300 p-3 rounded-lg text-xs font-mono overflow-x-auto">
              <code>{anti_pattern.code_smell}</code>
            </pre>
          </div>
        </div>

        {/* Pattern Side */}
        <div className="p-6 bg-emerald-50/30">
          <div className="flex items-center gap-2 mb-3 text-emerald-600">
            <span className="text-xl">✅</span>
            <h4 className="font-bold text-sm tracking-wide uppercase">Best Practice</h4>
          </div>

          <h3 className="text-lg font-bold text-slate-800 mb-2">{pattern.title}</h3>
          <p className="text-slate-600 mb-4 min-h-[3rem]">{pattern.description}</p>
          
          <div className="mb-4">
            <p className="text-xs font-semibold text-emerald-700 uppercase mb-2">✨ Best Practices</p>
            <ul className="space-y-1">
              {pattern.best_practices.map((practice, idx) => (
                <li key={idx} className="flex items-start gap-2 text-sm text-slate-700">
                  <span className="text-emerald-400 mt-0.5">•</span>
                  {practice}
                </li>
              ))}
            </ul>
          </div>

          <div className="mt-4">
            <p className="text-xs font-semibold text-slate-500 uppercase mb-2">Recommended Template</p>
            <pre className="bg-slate-900 text-emerald-300 p-3 rounded-lg text-xs font-mono overflow-x-auto">
              <code>{pattern.code_template}</code>
            </pre>
          </div>
        </div>
      </div>

      {/* HW Method Footer */}
      {counterMethod && (
        <div className="bg-indigo-50 border-t border-indigo-100 p-4 flex items-start sm:items-center gap-3">
          <span className="text-2xl shrink-0">🔬</span>
          <div>
            <span className="text-xs font-bold text-indigo-600 uppercase tracking-wide">
              Counter with {counterMethod.hw_method}
            </span>
            <p className="text-sm text-slate-700 mt-0.5">
              {counterMethod.description} <span className="font-mono text-indigo-700 text-xs bg-indigo-100 px-1 py-0.5 rounded ml-1">{counterMethod.technique}</span>
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default PatternAntiPatternCard;

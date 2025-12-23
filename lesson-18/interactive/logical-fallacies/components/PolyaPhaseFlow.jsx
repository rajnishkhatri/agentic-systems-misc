import React from 'react';

const PolyaPhaseFlow = ({ phases, activePhase, onPhaseSelect }) => {
  if (!phases) return null;

  return (
    <div className="my-8">
      {/* Mobile: Dropdown/Slider */}
      <div className="md:hidden mb-4">
        <label className="block text-xs font-bold text-slate-500 uppercase mb-2">Current Phase</label>
        <select 
          value={activePhase} 
          onChange={(e) => onPhaseSelect(e.target.value)}
          className="w-full p-3 bg-white border border-slate-200 rounded-lg text-slate-800 font-medium shadow-sm focus:ring-2 focus:ring-indigo-500 outline-none"
        >
          {phases.map((p) => (
            <option key={p.phase} value={p.phase}>
              {p.icon} {p.phase}
            </option>
          ))}
        </select>
      </div>

      {/* Desktop: Horizontal Stepper */}
      <div className="hidden md:flex justify-between items-center relative mb-8">
        {/* Connection Line */}
        <div className="absolute top-1/2 left-0 w-full h-1 bg-slate-200 -z-10 transform -translate-y-1/2 rounded-full" />
        
        {phases.map((p, idx) => {
          const isActive = activePhase === p.phase;
          const isPast = phases.findIndex(ph => ph.phase === activePhase) > idx;
          
          return (
            <button
              key={p.phase}
              onClick={() => onPhaseSelect(p.phase)}
              className="group relative flex flex-col items-center focus:outline-none"
            >
              <div 
                className={`
                  w-12 h-12 rounded-full flex items-center justify-center text-xl shadow-sm border-4 transition-all duration-300 z-10
                  ${isActive 
                    ? 'bg-indigo-600 border-indigo-100 text-white scale-110 shadow-indigo-200' 
                    : isPast
                      ? 'bg-indigo-50 border-indigo-200 text-indigo-400'
                      : 'bg-white border-slate-200 text-slate-300 group-hover:border-indigo-200 group-hover:text-indigo-300'
                  }
                `}
              >
                {p.icon}
              </div>
              <span 
                className={`
                  absolute top-14 text-xs font-bold tracking-wider transition-colors
                  ${isActive ? 'text-indigo-700' : 'text-slate-400'}
                `}
              >
                {p.phase}
              </span>
            </button>
          );
        })}
      </div>

      {/* Content Area */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 md:p-8 min-h-[200px] transition-all duration-300">
        {phases.map((p) => (
          activePhase === p.phase && (
            <div key={p.phase} className="animate-fadeIn">
              <div className="flex items-center gap-3 mb-4 border-b border-slate-100 pb-4">
                <span className="text-3xl">{p.icon}</span>
                <div>
                  <h2 className="text-2xl font-bold text-slate-800">{p.phase}</h2>
                  <p className="text-slate-500 text-sm">{p.description}</p>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {p.key_elements.map((element, i) => (
                  <div key={i} className="bg-slate-50 rounded-lg p-3 border border-slate-100 flex items-center gap-2">
                    <div className="w-1.5 h-1.5 rounded-full bg-indigo-400" />
                    <span className="text-sm font-medium text-slate-700">{element}</span>
                  </div>
                ))}
              </div>
            </div>
          )
        ))}
      </div>
    </div>
  );
};

export default PolyaPhaseFlow;

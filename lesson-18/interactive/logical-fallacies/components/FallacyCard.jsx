import React from 'react';

const FallacyCard = ({ fallacy, onClick, isActive }) => {
  return (
    <div 
      onClick={onClick}
      className={`
        cursor-pointer rounded-xl border transition-all duration-300 overflow-hidden
        ${isActive 
          ? 'bg-white border-indigo-500 shadow-lg ring-2 ring-indigo-100' 
          : 'bg-white border-slate-200 hover:border-indigo-300 hover:shadow-md'
        }
      `}
    >
      <div className="p-5">
        <div className="flex justify-between items-start mb-3">
          <div>
            <span className="inline-block px-2 py-1 text-xs font-semibold tracking-wide text-indigo-600 bg-indigo-50 rounded-full mb-2">
              {fallacy.category}
            </span>
            <h3 className="text-xl font-bold text-slate-800">{fallacy.name}</h3>
          </div>
          {isActive && (
            <span className="text-2xl animate-fadeIn">🎯</span>
          )}
        </div>
        
        <p className="text-slate-600 mb-4 leading-relaxed">
          {fallacy.description}
        </p>
        
        <div className="bg-slate-50 rounded-lg p-3 border border-slate-100">
          <p className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-1">
            CONTEXT
          </p>
          <p className="text-sm text-slate-700 italic">
            {fallacy.ai_context}
          </p>
        </div>
      </div>
      
      {/* Visual footer indicator */}
      <div className={`h-1 w-full ${isActive ? 'bg-indigo-500' : 'bg-slate-100'}`} />
    </div>
  );
};

export default FallacyCard;

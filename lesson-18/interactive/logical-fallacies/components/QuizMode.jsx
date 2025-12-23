import React, { useState } from 'react';

const QuizMode = ({ questions, onComplete, onClose }) => {
  const [currentIdx, setCurrentIdx] = useState(0);
  const [score, setScore] = useState(0);
  const [showResult, setShowResult] = useState(false);
  const [selectedOption, setSelectedOption] = useState(null);
  const [isAnswered, setIsAnswered] = useState(false);

  // Fallback if no questions provided
  if (!questions || questions.length === 0) {
    return (
      <div className="p-8 text-center">
        <p className="text-slate-500">No quiz questions available for this module yet.</p>
        <button onClick={onClose} className="mt-4 text-indigo-600 font-medium">Return to Tutorial</button>
      </div>
    );
  }

  const currentQ = questions[currentIdx];

  const handleOptionSelect = (optionIdx) => {
    if (isAnswered) return;
    setSelectedOption(optionIdx);
    setIsAnswered(true);
    
    if (optionIdx === currentQ.correctAnswer) {
      setScore(s => s + 1);
    }
  };

  const nextQuestion = () => {
    if (currentIdx < questions.length - 1) {
      setCurrentIdx(c => c + 1);
      setSelectedOption(null);
      setIsAnswered(false);
    } else {
      setShowResult(true);
      if (onComplete) onComplete(score);
    }
  };

  if (showResult) {
    return (
      <div className="bg-white rounded-xl shadow-lg border border-slate-200 p-8 text-center animate-fadeIn">
        <div className="mb-6">
          <span className="text-6xl mb-4 block">🏆</span>
          <h2 className="text-2xl font-bold text-slate-800 mb-2">Quiz Complete!</h2>
          <p className="text-slate-600">You scored <strong className="text-indigo-600 text-xl">{score}/{questions.length}</strong></p>
        </div>
        
        <div className="w-full bg-slate-100 rounded-full h-4 mb-8 overflow-hidden">
          <div 
            className="bg-indigo-500 h-full transition-all duration-1000 ease-out"
            style={{ width: `${(score / questions.length) * 100}%` }}
          />
        </div>

        <button 
          onClick={onClose}
          className="bg-indigo-600 text-white px-8 py-3 rounded-lg font-bold hover:bg-indigo-700 transition-colors shadow-lg shadow-indigo-200"
        >
          Return to Learning
        </button>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-lg border border-slate-200 overflow-hidden max-w-2xl mx-auto my-8">
      {/* Header */}
      <div className="bg-slate-50 px-6 py-4 border-b border-slate-200 flex justify-between items-center">
        <span className="text-sm font-bold text-slate-500 uppercase tracking-wide">
          Question {currentIdx + 1} of {questions.length}
        </span>
        <span className="text-sm font-medium text-indigo-600">
          Score: {score}
        </span>
      </div>

      <div className="p-6 md:p-8">
        <h3 className="text-xl font-bold text-slate-800 mb-6 leading-relaxed">
          {currentQ.question}
        </h3>

        <div className="space-y-3">
          {currentQ.options.map((opt, idx) => {
            let statusClass = "border-slate-200 hover:border-indigo-300 hover:bg-slate-50";
            
            if (isAnswered) {
              if (idx === currentQ.correctAnswer) {
                statusClass = "border-emerald-500 bg-emerald-50 text-emerald-800 ring-1 ring-emerald-500";
              } else if (idx === selectedOption) {
                statusClass = "border-rose-500 bg-rose-50 text-rose-800";
              } else {
                statusClass = "border-slate-100 opacity-50";
              }
            } else if (idx === selectedOption) {
              statusClass = "border-indigo-500 bg-indigo-50 ring-1 ring-indigo-500";
            }

            return (
              <button
                key={idx}
                onClick={() => handleOptionSelect(idx)}
                disabled={isAnswered}
                className={`w-full text-left p-4 rounded-lg border-2 transition-all ${statusClass}`}
              >
                <div className="flex items-center gap-3">
                  <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center text-xs font-bold shrink-0
                    ${isAnswered && idx === currentQ.correctAnswer ? 'border-emerald-500 bg-emerald-500 text-white' : 'border-current'}
                  `}>
                    {String.fromCharCode(65 + idx)}
                  </div>
                  <span>{opt}</span>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Footer / Explanation */}
      {isAnswered && (
        <div className="bg-slate-50 p-6 border-t border-slate-200 animate-fadeIn">
          <div className="flex gap-3 mb-4">
            <span className="text-2xl">{selectedOption === currentQ.correctAnswer ? '🎉' : '💡'}</span>
            <div>
              <p className={`font-bold ${selectedOption === currentQ.correctAnswer ? 'text-emerald-600' : 'text-slate-700'}`}>
                {selectedOption === currentQ.correctAnswer ? 'Correct!' : 'Not quite.'}
              </p>
              <p className="text-slate-600 text-sm mt-1">{currentQ.explanation}</p>
            </div>
          </div>
          <button
            onClick={nextQuestion}
            className="w-full bg-indigo-600 text-white py-3 rounded-lg font-bold hover:bg-indigo-700 transition-colors"
          >
            {currentIdx < questions.length - 1 ? 'Next Question →' : 'See Results'}
          </button>
        </div>
      )}
    </div>
  );
};

export default QuizMode;

import React, { useState } from 'react';

const CheckIcon = () => <span className="text-green-500 mr-2">✓</span>;
const CircleIcon = () => <span className="text-gray-300 mr-2">○</span>;

export default function CodeReviewLearning() {
  const [activeTab, setActiveTab] = useState('overview');
  const [checkedItems, setCheckedItems] = useState({});
  const [quizAnswers, setQuizAnswers] = useState({});
  const [showAnswers, setShowAnswers] = useState(false);

  const toggleCheck = (id) => {
    setCheckedItems(prev => ({ ...prev, [id]: !prev[id] }));
  };

  const tabs = [
    { id: 'overview', label: '📋 Overview' },
    { id: 'concepts', label: '🧠 Key Concepts' },
    { id: 'tools', label: '🔧 Tool Matrix' },
    { id: 'quiz', label: '✅ Self-Check' },
    { id: 'apply', label: '🎯 Apply It' }
  ];

  const keyConcepts = [
    { id: 'c1', category: 'Process Types', items: [
      'Code Reviews (during dev, team reviews PRs)',
      'QA (post-dev gatekeeper, mimics user behavior)'
    ]},
    { id: 'c2', category: 'Tool Categories', items: [
      'IDE-based: Real-time feedback on local saves (fastest loop)',
      'Git-based: Triggers on push/PR/merge actions',
      'Browser-based: Web interface reviews (least convenient)'
    ]},
    { id: 'c3', category: 'Analysis Depth', items: [
      'Linters: Syntax + style only (ESLint, Pylint)',
      'Static Analysis: Control/data flow, no execution (SonarQube)',
      'AI-Powered: ML patterns, context-aware suggestions (DeepCode, Codacy)'
    ]},
    { id: 'c4', category: 'Key Use Cases', items: [
      'Education: 24/7 pair programmer for juniors',
      'Velocity: Reduces PR regression cycles',
      'Tech Debt: Catches security issues early',
      'Depth: OWASP Top 10 vulnerability detection'
    ]}
  ];

  const tools = [
    { name: 'Codacy', score: '8/10', security: '2/2', performance: '0/2', 
      ux: 'Browser + Repo', strength: 'One-click fixes, blocks PR merge', 
      weakness: 'Missed performance issues' },
    { name: 'CodeRabbit', score: '7/10', security: '2/2', performance: '0/2',
      ux: 'Repo only', strength: 'Interactive PR comments, fast',
      weakness: 'Superficial explanations, no blocking' },
    { name: 'DeepCode/Snyk', score: '6/10', security: '1/2', performance: '0/2',
      ux: 'Browser + Repo', strength: 'Deep ML analysis, transparency',
      weakness: 'No one-click fixes, missed XSS' }
  ];

  const testVulnerabilities = [
    { type: 'SQL Injection', severity: 'Critical', detected: 'Codacy ✓, DeepCode ✓, CodeRabbit ✓',
      description: 'Direct user input in SQL query without sanitization' },
    { type: 'XSS', severity: 'Medium', detected: 'Codacy ✓, CodeRabbit ✓',
      description: 'User input rendered directly in HTML response' },
    { type: 'Memory Leak', severity: 'Performance', detected: 'None',
      description: 'Event listeners created but never removed' },
    { type: 'Inefficient Loop', severity: 'Performance', detected: 'None',
      description: 'Blocking computation that could use math formula' }
  ];

  const quizQuestions = [
    { q: 'Which tool type provides feedback on local saves?', 
      options: ['Git-based', 'IDE-based', 'Browser-based'], correct: 1 },
    { q: 'What distinguishes AI code analysis from static analysis?',
      options: ['Faster execution', 'ML patterns from many projects', 'Better UI'], correct: 1 },
    { q: 'Why should human reviews still happen with AI tools?',
      options: ['AI is always wrong', 'AI lacks business/feature context', 'Compliance only'], correct: 1 },
    { q: 'Which vulnerability type did ALL tested tools catch?',
      options: ['XSS', 'SQL Injection', 'Memory Leak'], correct: 1 }
  ];

  const completedCount = Object.values(checkedItems).filter(Boolean).length;
  const totalItems = keyConcepts.reduce((acc, cat) => acc + cat.items.length, 0);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 text-white p-6">
      <div className="max-w-4xl mx-auto">
        <div className="mb-6">
          <h1 className="text-2xl font-bold mb-2">Ch.3: Bug Detection & Code Review</h1>
          <div className="flex items-center gap-4">
            <div className="bg-slate-700 rounded-full h-2 flex-1">
              <div 
                className="bg-emerald-500 h-2 rounded-full transition-all"
                style={{ width: `${(completedCount / totalItems) * 100}%` }}
              />
            </div>
            <span className="text-sm text-slate-400">{completedCount}/{totalItems} concepts</span>
          </div>
        </div>

        <div className="flex gap-2 mb-6 flex-wrap">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                activeTab === tab.id 
                  ? 'bg-emerald-600 text-white' 
                  : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {activeTab === 'overview' && (
          <div className="space-y-4">
            <div className="bg-slate-800 rounded-xl p-5 border border-slate-700">
              <h2 className="text-lg font-semibold mb-3 text-emerald-400">⚡ 60-Second Summary</h2>
              <p className="text-slate-300 leading-relaxed">
                AI code review tools automate detection of bugs, security vulnerabilities, and style issues 
                before code reaches production. Three main categories exist: <strong>IDE-based</strong> (fastest feedback), 
                <strong> Git-based</strong> (workflow integration), and <strong>browser-based</strong> (least convenient). 
                While these tools excel at security issues (SQL injection, XSS), they currently miss performance problems. 
                <span className="text-amber-400"> Human review remains essential</span> for business context and feature intent.
              </p>
            </div>
            
            <div className="bg-slate-800 rounded-xl p-5 border border-slate-700">
              <h2 className="text-lg font-semibold mb-3 text-blue-400">🎯 Core Insight</h2>
              <p className="text-slate-300 italic">
                "AI tools add tremendous immediacy to the code-review process... but AI code reviews don't replace 
                human code reviews. The AI tool misses the context behind the code and the intent behind certain segments."
              </p>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="bg-slate-800 rounded-xl p-4 border border-emerald-800">
                <h3 className="font-semibold text-emerald-400 mb-2">✓ Tools Excel At</h3>
                <ul className="text-sm text-slate-300 space-y-1">
                  <li>• Security vulnerabilities (OWASP Top 10)</li>
                  <li>• Instant 24/7 feedback</li>
                  <li>• One-click suggested fixes</li>
                  <li>• Reducing regression cycles</li>
                </ul>
              </div>
              <div className="bg-slate-800 rounded-xl p-4 border border-amber-800">
                <h3 className="font-semibold text-amber-400 mb-2">⚠ Tools Miss</h3>
                <ul className="text-sm text-slate-300 space-y-1">
                  <li>• Performance issues</li>
                  <li>• Business/feature context</li>
                  <li>• Intent behind code decisions</li>
                  <li>• Complex memory leaks</li>
                </ul>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'concepts' && (
          <div className="space-y-4">
            {keyConcepts.map(category => (
              <div key={category.id} className="bg-slate-800 rounded-xl p-4 border border-slate-700">
                <h3 className="font-semibold text-emerald-400 mb-3">{category.category}</h3>
                <div className="space-y-2">
                  {category.items.map((item, idx) => {
                    const itemId = `${category.id}-${idx}`;
                    return (
                      <button
                        key={itemId}
                        onClick={() => toggleCheck(itemId)}
                        className="w-full text-left flex items-start p-2 rounded hover:bg-slate-700 transition-colors"
                      >
                        {checkedItems[itemId] ? <CheckIcon /> : <CircleIcon />}
                        <span className={checkedItems[itemId] ? 'text-slate-400' : 'text-slate-200'}>
                          {item}
                        </span>
                      </button>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'tools' && (
          <div className="space-y-4">
            <div className="bg-slate-800 rounded-xl p-4 border border-slate-700 overflow-x-auto">
              <h3 className="font-semibold text-emerald-400 mb-4">Tool Comparison Matrix</h3>
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-slate-400 border-b border-slate-700">
                    <th className="text-left py-2">Tool</th>
                    <th className="text-center py-2">Score</th>
                    <th className="text-center py-2">Security</th>
                    <th className="text-center py-2">Perf</th>
                    <th className="text-left py-2">Strength</th>
                  </tr>
                </thead>
                <tbody>
                  {tools.map(tool => (
                    <tr key={tool.name} className="border-b border-slate-700/50">
                      <td className="py-3 font-medium text-white">{tool.name}</td>
                      <td className="py-3 text-center">
                        <span className={`px-2 py-1 rounded ${
                          tool.score === '8/10' ? 'bg-emerald-900 text-emerald-300' :
                          tool.score === '7/10' ? 'bg-blue-900 text-blue-300' :
                          'bg-amber-900 text-amber-300'
                        }`}>{tool.score}</span>
                      </td>
                      <td className="py-3 text-center text-slate-300">{tool.security}</td>
                      <td className="py-3 text-center text-slate-500">{tool.performance}</td>
                      <td className="py-3 text-slate-300 text-xs">{tool.strength}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="bg-slate-800 rounded-xl p-4 border border-slate-700">
              <h3 className="font-semibold text-amber-400 mb-4">Test Vulnerabilities Used</h3>
              <div className="grid gap-3">
                {testVulnerabilities.map((vuln, idx) => (
                  <div key={idx} className="flex items-center justify-between p-3 bg-slate-700/50 rounded-lg">
                    <div>
                      <span className="font-medium">{vuln.type}</span>
                      <p className="text-xs text-slate-400 mt-1">{vuln.description}</p>
                    </div>
                    <span className={`text-xs px-2 py-1 rounded ${
                      vuln.severity === 'Critical' ? 'bg-red-900 text-red-300' :
                      vuln.severity === 'Medium' ? 'bg-amber-900 text-amber-300' :
                      'bg-slate-600 text-slate-300'
                    }`}>{vuln.severity}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'quiz' && (
          <div className="space-y-4">
            <div className="bg-slate-800 rounded-xl p-4 border border-slate-700">
              <div className="flex justify-between items-center mb-4">
                <h3 className="font-semibold text-emerald-400">Quick Comprehension Check</h3>
                <button 
                  onClick={() => setShowAnswers(!showAnswers)}
                  className="text-sm px-3 py-1 bg-slate-700 rounded hover:bg-slate-600"
                >
                  {showAnswers ? 'Hide Answers' : 'Show Answers'}
                </button>
              </div>
              <div className="space-y-4">
                {quizQuestions.map((q, qIdx) => (
                  <div key={qIdx} className="p-3 bg-slate-700/50 rounded-lg">
                    <p className="font-medium mb-2">{qIdx + 1}. {q.q}</p>
                    <div className="space-y-1">
                      {q.options.map((opt, oIdx) => (
                        <button
                          key={oIdx}
                          onClick={() => setQuizAnswers(prev => ({ ...prev, [qIdx]: oIdx }))}
                          className={`w-full text-left p-2 rounded text-sm transition-colors ${
                            showAnswers && oIdx === q.correct
                              ? 'bg-emerald-800 text-emerald-200'
                              : quizAnswers[qIdx] === oIdx
                              ? 'bg-blue-800 text-blue-200'
                              : 'bg-slate-600 hover:bg-slate-500'
                          }`}
                        >
                          {opt}
                        </button>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'apply' && (
          <div className="space-y-4">
            <div className="bg-slate-800 rounded-xl p-5 border border-emerald-800">
              <h3 className="font-semibold text-emerald-400 mb-3">🔗 Connect to Your Work</h3>
              <p className="text-slate-300 mb-4">
                Given your multi-agent dispute resolution system at BoA, here's how this applies:
              </p>
              <ul className="space-y-3 text-sm">
                <li className="flex items-start gap-2">
                  <span className="text-emerald-400 mt-1">→</span>
                  <span><strong>Agent Code Quality:</strong> AI review tools could catch issues in your 7-agent orchestration code before LangGraph deployment</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-emerald-400 mt-1">→</span>
                  <span><strong>Security-First:</strong> Financial services = critical. Codacy's OWASP detection aligns with SOX/PCI DSS requirements</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-emerald-400 mt-1">→</span>
                  <span><strong>Article Series Angle:</strong> "AI Reviewing AI" - code review tools evaluating LLM-generated code in agentic systems</span>
                </li>
              </ul>
            </div>

            <div className="bg-slate-800 rounded-xl p-5 border border-blue-800">
              <h3 className="font-semibold text-blue-400 mb-3">📝 Discussion Points</h3>
              <ul className="space-y-2 text-sm text-slate-300">
                <li>• How do evaluation frameworks (LangSmith) differ from code review tools?</li>
                <li>• Could AI code review detect issues in DSPy-optimized prompts?</li>
                <li>• What's the intersection of GuardRails validation + automated code review?</li>
              </ul>
            </div>

            <div className="bg-slate-800 rounded-xl p-5 border border-amber-800">
              <h3 className="font-semibold text-amber-400 mb-3">🚀 Action Items</h3>
              <ul className="space-y-2 text-sm text-slate-300">
                <li>□ Try Codacy on a personal GitHub repo to experience the workflow</li>
                <li>□ Consider adding to your "LLM Evaluation" article: "Code Review vs. Output Evaluation"</li>
                <li>□ Research: Do any tools specialize in reviewing Python/LangChain code patterns?</li>
              </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

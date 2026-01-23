import React from 'react';

const LandingPage = ({ onNavigate }) => {
  const guides = [
    {
      id: 'ml-fraud',
      title: 'ML Fraud Detection',
      description: 'First principles deep dive into machine learning fraud detection',
      icon: '△'
    },
    {
      id: 'stolen-card-fraud',
      title: 'Stolen Card Fraud Detection',
      description: 'Stolen credit card fraud detection guide',
      icon: '🔐'
    },
    {
      id: 'address-fraud',
      title: 'Address Fraud Detection',
      description: 'Address manipulation & shipping fraud detection guide',
      icon: '📦'
    }
  ];

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
            <div className="flex items-center gap-4 mb-4">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-amber-500 to-violet-600 flex items-center justify-center">
                <span className="text-2xl">🛡️</span>
              </div>
              <div>
                <h1 className="text-2xl font-serif text-slate-100">Fraud Detection: First Principles Guides</h1>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-6xl mx-auto px-6 py-8">
          <div className="bg-slate-800/50 rounded-xl p-8 border border-slate-700/50">
            <h2 className="text-2xl font-serif text-slate-100 mb-6">Available Guides</h2>
            
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-slate-700/50">
                    <th className="text-left text-slate-400 font-medium py-4 px-4">Title</th>
                    <th className="text-left text-slate-400 font-medium py-4 px-4">Description</th>
                    <th className="text-left text-slate-400 font-medium py-4 px-4">Action</th>
                  </tr>
                </thead>
                <tbody>
                  {guides.map((guide, index) => (
                    <tr 
                      key={guide.id}
                      className="border-b border-slate-800/50 hover:bg-slate-700/50 transition-colors"
                    >
                      <td className="py-4 px-4">
                        <div className="flex items-center gap-3">
                          <span className="text-2xl">{guide.icon}</span>
                          <span className="text-slate-100 font-medium">{guide.title}</span>
                        </div>
                      </td>
                      <td className="py-4 px-4 text-slate-300">
                        {guide.description}
                      </td>
                      <td className="py-4 px-4">
                        <button
                          onClick={() => onNavigate(guide.id)}
                          className="bg-amber-500 hover:bg-amber-400 text-slate-900 font-semibold px-6 py-2 rounded-lg transition-all hover:scale-105"
                        >
                          View Guide
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default LandingPage;

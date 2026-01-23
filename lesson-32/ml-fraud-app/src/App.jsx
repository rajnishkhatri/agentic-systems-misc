import { useState } from 'react'
import LandingPage from './components/LandingPage.jsx'
import MLFraudFirstPrinciplesGuide from './components/MLFraudFirstPrinciplesGuide.jsx'
import StolenCardFraudFirstPrinciplesGuide from './components/StolenCardFraudFirstPrinciplesGuide.jsx'
import AddressFraudFirstPrinciplesGuide from './components/AddressFraudFirstPrinciplesGuide.jsx'

function App() {
  const [currentView, setCurrentView] = useState('landing')

  const handleNavigate = (view) => {
    setCurrentView(view)
  }

  const handleBack = () => {
    setCurrentView('landing')
  }

  if (currentView === 'landing') {
    return <LandingPage onNavigate={handleNavigate} />
  }

  if (currentView === 'ml-fraud') {
    return <MLFraudFirstPrinciplesGuide onBack={handleBack} />
  }

  if (currentView === 'stolen-card-fraud') {
    return <StolenCardFraudFirstPrinciplesGuide onBack={handleBack} />
  }

  if (currentView === 'address-fraud') {
    return <AddressFraudFirstPrinciplesGuide onBack={handleBack} />
  }

  return <LandingPage onNavigate={handleNavigate} />
}

export default App

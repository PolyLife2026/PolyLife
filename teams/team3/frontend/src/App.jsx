import { useState } from 'react'
import { auth } from './api'
import Auth from './pages/Auth'
import GoalSelect from './pages/GoalSelect'
import HealthForm from './pages/HealthForm'
import Results from './pages/Results'
import Dashboard from './pages/Dashboard'
import './index.css'

export default function App() {
  const [screen, setScreen] = useState(auth.isLoggedIn() ? 'goal' : 'auth')
  const [goal, setGoal] = useState(null)
  const [profile, setProfile] = useState(null)

  if (screen === 'auth') {
    return <Auth onLoggedIn={() => setScreen('goal')} />
  }

  if (screen === 'goal') {
    return (
      <GoalSelect
        onNext={(g) => {
          setGoal(g)
          setScreen('health')
        }}
      />
    )
  }

  if (screen === 'health') {
    return (
      <HealthForm
        goal={goal}
        onDone={(result) => {
          setProfile(result)
          setScreen('results')
        }}
      />
    )
  }

  if (screen === 'results') {
    return (
      <Results
        profile={profile}
        onEdit={() => setScreen('health')}
        onStart={() => setScreen('dashboard')}
      />
    )
  }

  return <Dashboard />
}

import './App.css'
import Sidebar from './components/shared/Sidebar'
import WelcomeScreen from './WelcomeScreen'

function App() {
  // Sample conversation data
  const sampleConversations = [
    { id: '1', title: 'Introduction to AI concepts' },
    { id: '2', title: 'Machine learning algorithms' },
    { id: '3', title: 'Neural networks deep dive' },
  ]

  return (
    <div className="flex h-screen w-full overflow-hidden">
      <Sidebar conversations={sampleConversations} />
      <div className="flex-1 overflow-auto">
        <WelcomeScreen />
      </div>
    </div>
  )
}

export default App

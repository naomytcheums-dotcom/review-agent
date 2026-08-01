import { Route, Routes } from 'react-router-dom'
import Layout from './components/Layout.jsx'
import Reviews from './pages/Reviews.jsx'
import Settings from './pages/Settings.jsx'
import './App.css'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Reviews />} />
        <Route path="/settings" element={<Settings />} />
      </Routes>
    </Layout>
  )
}

export default App

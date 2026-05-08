import { Routes, Route, Navigate } from 'react-router-dom'
import ProtectedRoute from './components/ProtectedRoute'
import Layout from './components/Layout'
import Login from './pages/Login'
import Catalogue from './pages/Catalogue'
import Ajouter from './pages/Ajouter'
import Modifier from './pages/Modifier'
import Stats from './pages/Stats'

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route element={<ProtectedRoute />}>
        <Route element={<Layout />}>
          <Route path="/catalogue" element={<Catalogue />} />
          <Route path="/ajouter"        element={<Ajouter />} />
          <Route path="/modifier/:id"   element={<Modifier />} />
          <Route path="/stats"          element={<Stats />} />
        </Route>
      </Route>
      <Route path="*" element={<Navigate to="/catalogue" replace />} />
    </Routes>
  )
}

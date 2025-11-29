import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Pharmacies from './pages/Pharmacies'
import Branches from './pages/Branches'
import Drugs from './pages/Drugs'
import Inventory from './pages/Inventory'
import Orders from './pages/Orders'
import NearbyBranches from './pages/NearbyBranches'
import Layout from './components/Layout'

function PrivateRoute({ children, allowedRoles = null }) {
  const { user, loading } = useAuth()
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg">Yuklanmoqda...</div>
      </div>
    )
  }
  
  if (!user) {
    return <Navigate to="/login" />
  }
  
  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="card text-center">
          <h2 className="text-xl font-bold text-red-600 mb-2">Kirish rad etildi</h2>
          <p className="text-gray-600">Sizda bu sahifaga kirish huquqi yo'q.</p>
        </div>
      </div>
    )
  }
  
  return children
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route
        path="/"
        element={
          <PrivateRoute>
            <Layout />
          </PrivateRoute>
        }
      >
        <Route index element={<Dashboard />} />
        <Route
          path="nearby-branches"
          element={
            <PrivateRoute>
              <NearbyBranches />
            </PrivateRoute>
          }
        />
        <Route
          path="pharmacies"
          element={
            <PrivateRoute allowedRoles={['superadmin', 'operator', 'pharmacy_admin']}>
              <Pharmacies />
            </PrivateRoute>
          }
        />
        <Route
          path="branches"
          element={
            <PrivateRoute allowedRoles={['superadmin', 'operator', 'pharmacy_admin']}>
              <Branches />
            </PrivateRoute>
          }
        />
        <Route
          path="drugs"
          element={
            <PrivateRoute allowedRoles={['superadmin', 'operator', 'pharmacy_admin','branch_admin']}>
              <Drugs />
            </PrivateRoute>
          }
        />
        <Route
          path="inventory"
          element={
            <PrivateRoute allowedRoles={['superadmin', 'operator', 'pharmacy_admin', 'branch_admin']}>
              <Inventory />
            </PrivateRoute>
          }
        />
        <Route
          path="orders"
          element={
            <PrivateRoute allowedRoles={['superadmin', 'operator', 'pharmacy_admin', 'branch_admin', 'cashier']}>
              <Orders />
            </PrivateRoute>
          }
        />
      </Route>
    </Routes>
  )
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <AppRoutes />
      </Router>
    </AuthProvider>
  )
}

export default App


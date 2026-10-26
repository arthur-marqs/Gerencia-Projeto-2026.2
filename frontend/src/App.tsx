import { useState } from 'react'
import LoginPage from './features/auth/pages/LoginPage'
import AuthenticatedPage from './features/auth/pages/AuthenticatedPage'

function App() {
  const [usuarioNome, setUsuarioNome] = useState<string | null>(null)

  if (usuarioNome) {
    return <AuthenticatedPage nome={usuarioNome} />
  }

  return <LoginPage onLogin={setUsuarioNome} />
}

export default App

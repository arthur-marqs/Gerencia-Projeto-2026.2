import { useCallback, useEffect, useState } from 'react'
import LoginPage from './features/auth/pages/LoginPage'
import AuthenticatedPage from './features/auth/pages/AuthenticatedPage'
import { SESSION_EXPIRED_EVENT } from './lib/apiFetch'

type UsuarioAutenticado = {
  nome: string
  perfis: string[]
}

async function buscarUsuarioAutenticado(): Promise<UsuarioAutenticado | null> {
  const response = await fetch('http://localhost:8000/api/auth/me', {
    credentials: 'include',
  })

  if (response.status === 401) {
    return null
  }

  if (!response.ok) {
    throw new Error('Não foi possível verificar a sessão.')
  }

  const data: {
    usuario: UsuarioAutenticado
  } = await response.json()

  return data.usuario
}

function App() {
  const [usuario, setUsuario] = useState<UsuarioAutenticado | null>(null)
  const [carregandoSessao, setCarregandoSessao] = useState(true)
  const autenticado = usuario !== null

  useEffect(() => {
    if (!autenticado) return
    let ativo = true
    async function sincronizarSessao() {
      if (document.visibilityState === 'hidden') return
      try {
        const atual = await buscarUsuarioAutenticado()
        if (ativo) setUsuario(atual)
      } catch {
        // Uma falha de rede não equivale a uma sessão revogada.
      }
    }
    const intervalo = window.setInterval(() => void sincronizarSessao(), 30_000)
    window.addEventListener('focus', sincronizarSessao)
    document.addEventListener('visibilitychange', sincronizarSessao)
    return () => {
      ativo = false
      window.clearInterval(intervalo)
      window.removeEventListener('focus', sincronizarSessao)
      document.removeEventListener('visibilitychange', sincronizarSessao)
    }
  }, [autenticado])

  useEffect(() => {
    let ativo = true

    async function restaurarSessao() {
      try {
        const usuarioAutenticado = await buscarUsuarioAutenticado()

        if (ativo) {
          setUsuario(usuarioAutenticado)
        }
      } catch {
        if (ativo) {
          setUsuario(null)
        }
      } finally {
        if (ativo) {
          setCarregandoSessao(false)
        }
      }
    }

    void restaurarSessao()

    return () => {
      ativo = false
    }
  }, [])

  const carregarUsuarioAposLogin = useCallback(async () => {
    try {
      const usuarioAutenticado = await buscarUsuarioAutenticado()
      setUsuario(usuarioAutenticado)
    } catch {
      // Uma falha de rede não deve encerrar a sessão.
    }
  }, [])

  useEffect(() => {
    function tratarSessaoExpirada() {
      void carregarUsuarioAposLogin()
    }

    window.addEventListener(SESSION_EXPIRED_EVENT, tratarSessaoExpirada)

    return () => {
      window.removeEventListener(SESSION_EXPIRED_EVENT, tratarSessaoExpirada)
    }
  }, [carregarUsuarioAposLogin])

  async function sair() {
    const response = await fetch('http://localhost:8000/api/auth/logout', {
      method: 'POST',
      credentials: 'include',
    })

    if (response.ok) {
      setUsuario(null)
    }
  }

  if (carregandoSessao) {
    return (
      <main className="grid min-h-screen place-items-center bg-slate-950 text-white">
        <p>Carregando...</p>
      </main>
    )
  }

  if (usuario) {
    return (
      <AuthenticatedPage
        nome={usuario.nome}
        perfis={usuario.perfis}
        onLogout={sair}
        onSessionChange={carregarUsuarioAposLogin}
      />
    )
  }

  return <LoginPage onLogin={carregarUsuarioAposLogin} />
}

export default App

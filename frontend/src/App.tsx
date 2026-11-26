import { useCallback, useEffect, useRef, useState } from 'react'
import LoginPage from './features/auth/pages/LoginPage'
import AuthenticatedPage from './features/auth/pages/AuthenticatedPage'
import { SESSION_EXPIRED_EVENT } from './lib/apiFetch'

type UsuarioAutenticado = {
  nome: string
  perfis: string[]
}

type Sessao =
  | { estado: 'verificando' | 'indisponivel' | 'anonima' }
  | { estado: 'autenticada'; usuario: UsuarioAutenticado }

async function buscarUsuarioAutenticado(signal: AbortSignal): Promise<UsuarioAutenticado | null> {
  const response = await fetch('http://localhost:8000/api/auth/me', {
    credentials: 'include',
    signal,
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
  const [sessao, setSessao] = useState<Sessao>({ estado: 'verificando' })
  const consultaAtual = useRef<AbortController | null>(null)
  const autenticado = sessao.estado === 'autenticada'

  const verificarSessao = useCallback(() => {
    consultaAtual.current?.abort()
    const controle = new AbortController()
    consultaAtual.current = controle

    return buscarUsuarioAutenticado(controle.signal).then(
      (usuario) => {
        if (!controle.signal.aborted) {
          setSessao(usuario ? { estado: 'autenticada', usuario } : { estado: 'anonima' })
        }
      },
      () => {
        if (!controle.signal.aborted) {
          // Uma falha temporária preserva uma sessão que já foi confirmada.
          setSessao(atual => atual.estado === 'autenticada' ? atual : { estado: 'indisponivel' })
        }
      },
    ).finally(() => {
      if (consultaAtual.current === controle) consultaAtual.current = null
    })
  }, [])

  const encerrarSessao = useCallback(() => {
    consultaAtual.current?.abort()
    setSessao({ estado: 'anonima' })
  }, [])

  useEffect(() => {
    window.addEventListener(SESSION_EXPIRED_EVENT, encerrarSessao)
    void verificarSessao()

    return () => {
      consultaAtual.current?.abort()
      window.removeEventListener(SESSION_EXPIRED_EVENT, encerrarSessao)
    }
  }, [encerrarSessao, verificarSessao])

  useEffect(() => {
    if (!autenticado) return
    function sincronizarSessao() {
      if (document.visibilityState === 'hidden' || consultaAtual.current) return
      void verificarSessao()
    }

    const intervalo = window.setInterval(() => void sincronizarSessao(), 30_000)
    window.addEventListener('focus', sincronizarSessao)
    document.addEventListener('visibilitychange', sincronizarSessao)
    return () => {
      window.clearInterval(intervalo)
      window.removeEventListener('focus', sincronizarSessao)
      document.removeEventListener('visibilitychange', sincronizarSessao)
    }
  }, [autenticado, verificarSessao])

  function tentarRestaurarSessao() {
    setSessao({ estado: 'verificando' })
    void verificarSessao()
  }

  async function sair() {
    const response = await fetch('http://localhost:8000/api/auth/logout', {
      method: 'POST',
      credentials: 'include',
    })

    if (response.ok) {
      encerrarSessao()
    }
  }

  if (sessao.estado === 'verificando') {
    return (
      <main className="grid min-h-screen place-items-center bg-slate-950 text-white">
        <p role="status">Verificando a sessão…</p>
      </main>
    )
  }

  if (sessao.estado === 'indisponivel') {
    return (
      <main className="grid min-h-screen place-items-center bg-slate-950 px-4">
        <section className="w-full max-w-md rounded-2xl bg-white p-6 text-slate-900">
          <h1 role="alert" className="text-lg font-semibold">Não foi possível verificar a sessão.</h1>
          <button
            type="button"
            onClick={tentarRestaurarSessao}
            className="mt-4 rounded-lg bg-blue-600 px-4 py-2 font-medium text-white hover:bg-blue-700"
          >
            Tentar novamente
          </button>
        </section>
      </main>
    )
  }

  if (sessao.estado === 'autenticada') {
    return (
      <AuthenticatedPage
        nome={sessao.usuario.nome}
        perfis={sessao.usuario.perfis}
        onLogout={sair}
        onSessionChange={verificarSessao}
      />
    )
  }

  return <LoginPage onLogin={tentarRestaurarSessao} />
}

export default App

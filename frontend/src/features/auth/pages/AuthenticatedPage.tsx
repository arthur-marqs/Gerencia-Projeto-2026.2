import { useState } from 'react'
import Header from '../../../components/layout/Header'
import Sidebar from '../../../components/layout/Sidebar'
import FamiliesPage from '../../families/pages/FamiliesPage'
import ProdutosPage from '../../produtos/pages/ProdutosPage'

type Pagina = 'dashboard' | 'produtos' | 'familias'

type AuthenticatedPageProps = {
  nome: string
  perfis: string[]
  onLogout: () => void
}


function AuthenticatedPage({
  nome,
  perfis,
  onLogout,
}: AuthenticatedPageProps) {

  const [paginaAtual, setPaginaAtual] = useState<Pagina>('dashboard')
  const ehPlanejador = perfis.includes('PLANEJADOR')

  return (
    <div className="min-h-screen bg-slate-100">
      <Sidebar
        perfis={perfis}

        paginaAtual={paginaAtual}
        onNavigate={setPaginaAtual}

      />

      <div className="lg:pl-64">
        <Header
          nome={nome}
          perfis={perfis}
          onLogout={onLogout}
        />

        {paginaAtual === 'produtos' && ehPlanejador ? (
          <ProdutosPage />
        ) : paginaAtual === 'familias' && ehPlanejador ? (
          <main className="px-4 py-5 pt-[100px] sm:px-6 lg:px-7 xl:px-8">
            <div className="mx-auto max-w-[1500px]">
              <FamiliesPage />
            </div>
          </main>
        ) : (
          <main className="px-4 py-5 pt-[100px] sm:px-6 lg:px-7 xl:px-8">
            <div className="mx-auto max-w-[1500px]">

              <section className="relative overflow-hidden rounded-2xl border border-slate-200 bg-white px-6 py-6 shadow-sm sm:px-8 lg:px-9">
                <div className="relative z-10 max-w-2xl">
                  <div className="mb-3 flex flex-wrap gap-2">
                    {perfis.map((perfil) => (
                      <span
                        key={perfil}
                        className="inline-flex items-center rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-blue-700"
                      >
                        {perfil}
                      </span>
                    ))}
                  </div>

                  <h1 className="text-3xl font-bold tracking-tight text-slate-950 sm:text-4xl">
                    Bem-vindo, {nome}.
                  </h1>

                  <p className="mt-3 max-w-xl text-sm leading-6 text-slate-500 sm:text-base">
                    Acesse as funcionalidades disponíveis para sua conta.
                  </p>
                </div>
              </section>

            </div>
          </main>
        )}

      </div>
    </div>
  )
}

export default AuthenticatedPage

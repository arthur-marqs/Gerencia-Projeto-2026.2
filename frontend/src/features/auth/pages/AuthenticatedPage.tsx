type AuthenticatedPageProps = {
  nome: string
  perfis: string[]
}

function AuthenticatedPage({ nome, perfis }: AuthenticatedPageProps) {
  const ehPlanejador = perfis.includes('PLANEJADOR')
  const ehOperador = perfis.includes('OPERADOR')

  return (
    <main className="min-h-screen bg-slate-950 px-4 py-10 text-white">
      <div className="mx-auto max-w-4xl">
        <h1 className="text-3xl font-bold">
          Bem-vindo, {nome}.
        </h1>

        <p className="mt-3 text-slate-300">
          Acesse as áreas disponíveis para o seu perfil.
        </p>

        <div className="mt-4 flex flex-wrap gap-2">
          {perfis.map((perfil) => (
            <span
              className="rounded-full bg-blue-700 px-3 py-1 text-sm font-medium"
              key={perfil}
            >
              {perfil}
            </span>
          ))}
        </div>

        <section className="mt-8 grid gap-4 md:grid-cols-2">
          {ehPlanejador && (
            <article className="rounded-2xl bg-slate-900 p-6">
              <h2 className="text-xl font-semibold">
                Área do Planejador
              </h2>

              <p className="mt-2 text-slate-300">
                Acesso às funcionalidades de cadastro e planejamento da produção.
              </p>
            </article>
          )}

          {ehOperador && (
            <article className="rounded-2xl bg-slate-900 p-6">
              <h2 className="text-xl font-semibold">
                Área do Operador
              </h2>

              <p className="mt-2 text-slate-300">
                Acesso às funcionalidades de consulta e execução da produção.
              </p>
            </article>
          )}
        </section>
      </div>
    </main>
  )
}

export default AuthenticatedPage

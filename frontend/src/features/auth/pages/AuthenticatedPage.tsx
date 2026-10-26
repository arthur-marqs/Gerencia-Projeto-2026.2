type AuthenticatedPageProps = {
  nome: string
}

function AuthenticatedPage({ nome }: AuthenticatedPageProps) {
  return (
    <main className="min-h-screen bg-slate-950 px-4 py-10 text-white">
      <div className="mx-auto max-w-4xl">
        <h1 className="text-3xl font-bold">
          Bem-vindo, {nome}.
        </h1>

        <p className="mt-3 text-slate-300">
          Login realizado com sucesso.
        </p>
      </div>
    </main>
  )
}

export default AuthenticatedPage
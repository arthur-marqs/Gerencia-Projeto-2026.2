import type { FormEvent } from 'react'

function App() {
  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
  }

  return (
    <main className="min-h-screen bg-slate-950 px-4 py-10 text-slate-900">
      <div className="mx-auto grid min-h-[calc(100vh-5rem)] max-w-6xl items-center gap-10 lg:grid-cols-2">
        <section className="hidden text-white lg:block">
          <div className="mb-12 flex items-center gap-3">
            <div className="grid size-12 place-items-center rounded-xl bg-blue-500 text-lg font-bold">
              SF
            </div>
            <span className="text-2xl font-semibold">SetupFlow</span>
          </div>

          <p className="mb-3 text-sm font-semibold uppercase tracking-[0.2em] text-blue-300">
            Planejamento da produção
          </p>
          <h1 className="max-w-lg text-5xl font-bold leading-tight">
            Organize o fluxo da sua produção em um só lugar.
          </h1>
          <p className="mt-6 max-w-lg text-lg leading-8 text-slate-300">
            Entre na sua conta para acompanhar as atividades e informações do
            projeto.
          </p>
        </section>

        <section className="mx-auto w-full max-w-md rounded-3xl bg-white p-8 shadow-2xl sm:p-10">
          <div className="mb-8 lg:hidden">
            <span className="text-xl font-bold text-blue-700">SetupFlow</span>
          </div>

          <h2 className="text-3xl font-bold tracking-tight">Acesse sua conta</h2>
          <p className="mt-2 text-sm text-slate-600">
            Informe suas credenciais para continuar.
          </p>

          <form className="mt-8 space-y-5" onSubmit={handleSubmit}>
            <div>
              <label
                className="block text-sm font-medium text-slate-700"
                htmlFor="email"
              >
                E-mail
              </label>
              <input
                autoComplete="username"
                className="mt-2 w-full rounded-xl border border-slate-300 px-4 py-3 outline-none transition focus:border-blue-600 focus:ring-4 focus:ring-blue-100"
                id="email"
                name="email"
                placeholder="voce@empresa.com"
                required
                type="email"
              />
            </div>

            <div>
              <label
                className="block text-sm font-medium text-slate-700"
                htmlFor="password"
              >
                Senha
              </label>
              <input
                autoComplete="current-password"
                className="mt-2 w-full rounded-xl border border-slate-300 px-4 py-3 outline-none transition focus:border-blue-600 focus:ring-4 focus:ring-blue-100"
                id="password"
                name="password"
                placeholder="Digite sua senha"
                required
                type="password"
              />
            </div>

            <button
              className="w-full rounded-xl bg-blue-700 px-4 py-3 font-semibold text-white transition hover:bg-blue-800 focus-visible:outline-4 focus-visible:outline-offset-2 focus-visible:outline-blue-500"
              type="submit"
            >
              Entrar
            </button>
          </form>

          <p className="mt-6 text-center text-xs text-slate-500">
            SetupFlow · Planejamento e acompanhamento da produção
          </p>
        </section>
      </div>
    </main>
  )
}

export default App
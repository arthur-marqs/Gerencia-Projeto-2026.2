import { useState, type FormEvent } from 'react'

type LoginErrors = {
  email?: string
  password?: string
}

function App() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [errors, setErrors] = useState<LoginErrors>({})
  const [message, setMessage] = useState('')

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()

    const nextErrors: LoginErrors = {}
    const normalizedEmail = email.trim()

    if (!normalizedEmail) {
      nextErrors.email = 'Informe seu e-mail.'
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(normalizedEmail)) {
      nextErrors.email = 'Informe um e-mail válido.'
    }

    if (!password) {
      nextErrors.password = 'Informe sua senha.'
    }

    setErrors(nextErrors)

    if (Object.keys(nextErrors).length === 0) {
      setMessage('Os campos estão preenchidos. A autenticação será conectada depois.')
    } else {
      setMessage('')
    }
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

          <form
            className="mt-8 space-y-5"
            noValidate
            onSubmit={handleSubmit}
          >
            <div>
              <label
                className="block text-sm font-medium text-slate-700"
                htmlFor="email"
              >
                E-mail
              </label>
              <input
                autoComplete="username"
                aria-describedby={errors.email ? 'email-error' : undefined}
                aria-invalid={Boolean(errors.email)}
                className={`mt-2 w-full rounded-xl border px-4 py-3 outline-none transition focus:ring-4 ${
                    errors.email
                      ? 'border-red-500 focus:border-red-600 focus:ring-red-100'
                      : 'border-slate-300 focus:border-blue-600 focus:ring-blue-100'
                  }`}
                  onChange={(event) => {
                    setEmail(event.target.value)
                    setErrors((current) => ({ ...current, email: undefined }))
                    setMessage('')
                  }}
                placeholder="voce@empresa.com"
                required
                type="email"
                value={email}
              />
              {errors.email && (
                <p
                  className="mt-2 text-sm text-red-700"
                  id="email-error"
                  role="alert"
                >
                  {errors.email}
                </p>
              )}
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
                aria-describedby={errors.password ? 'password-error' : undefined}
                aria-invalid={Boolean(errors.password)}
                className={`mt-2 w-full rounded-xl border px-4 py-3 outline-none transition focus:ring-4 ${
                  errors.password
                    ? 'border-red-500 focus:border-red-600 focus:ring-red-100'
                    : 'border-slate-300 focus:border-blue-600 focus:ring-blue-100'
                }`}
                onChange={(event) => {
                  setPassword(event.target.value)
                  setErrors((current) => ({ ...current, password: undefined }))
                  setMessage('')
                }}
                placeholder="Digite sua senha"
                required
                type="password"
                value={password}
              />
              {errors.password && (
                <p
                  className="mt-2 text-sm text-red-700"
                  id="password-error"
                  role="alert"
                >
                  {errors.password}
                </p>
              )}
            </div>

            <button
              className="w-full rounded-xl bg-blue-700 px-4 py-3 font-semibold text-white transition hover:bg-blue-800 focus-visible:outline-4 focus-visible:outline-offset-2 focus-visible:outline-blue-500"
              type="submit"
            >
              Entrar
            </button>
          </form>

          {message && (
            <p className="mt-4 text-sm text-slate-600" role="status">
              {message}
            </p>
          )}

          <p className="mt-6 text-center text-xs text-slate-500">
            SetupFlow · Planejamento e acompanhamento da produção
          </p>
        </section>
      </div>
    </main>
  )
}

export default App
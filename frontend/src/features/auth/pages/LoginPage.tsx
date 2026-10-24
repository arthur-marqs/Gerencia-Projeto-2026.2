import { useState, type FormEvent } from 'react'
import { validateLogin, type LoginErrors } from '../validation/validateLogin'

function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [errors, setErrors] = useState<LoginErrors>({})
  const [message, setMessage] = useState('')
  const [showPassword, setShowPassword] = useState(false)

async function handleSubmit(event: FormEvent<HTMLFormElement>) {
  event.preventDefault()

  const validationErrors = validateLogin(email, password)
  setErrors(validationErrors)
  setMessage('')

  if (Object.keys(validationErrors).length > 0) {
    return
  }

  try {
const response = await fetch('http://127.0.0.1:8000/api/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({ email, password }),
    })

    const data: {
      detail?: string
      usuario?: { nome?: string }
    } = await response.json()

    if (!response.ok) {
      setMessage(data.detail ?? 'Não foi possível realizar o login.')
      return
    }

    setMessage(`Login realizado. Bem-vindo, ${data.usuario?.nome ?? ''}.`)
  } catch {
    setMessage('Não foi possível conectar à API. Verifique se ela está em execução.')
  }
}

  return (
    <main className="min-h-screen bg-slate-950 px-4 py-10 text-slate-900">
      <div className="mx-auto grid min-h-[calc(100vh-5rem)] max-w-6xl items-center gap-10 lg:grid-cols-2">
        <section className="hidden text-white lg:block">

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
          <div className="mb-8 flex justify-center">
            <img
              src="/images/setupflow-logo-completo.png"
              alt="logo completo SetupFlow"
              className="h-auto w-52 max-w-full"
            />
          </div>

          <h2 className="text-3xl font-bold tracking-tight">Acesse sua conta</h2>
          <p className="mt-2 text-sm text-slate-600">
            Informe suas credenciais para continuar.
          </p>

          <form className="space-y-5" onSubmit={handleSubmit} noValidate>
          
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

              <div className="relative mt-2">
                <input
                  id="password"
                  autoComplete="current-password"
                  aria-describedby={errors.password ? 'password-error' : undefined}
                  aria-invalid={Boolean(errors.password)}
                  className={`w-full rounded-xl border px-4 py-3 pr-20 outline-none transition focus:ring-4 ${
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
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                />

                <button
                  aria-controls="password"
                  aria-label={showPassword ? 'Ocultar senha' : 'Mostrar senha'}
                  className="absolute right-1 top-1/2 grid size-10 -translate-y-1/2 place-items-center rounded-lg text-blue-700 hover:bg-slate-100"
                  onClick={() => setShowPassword((current) => !current)}
                  type="button"
                >
                  <svg
                    aria-hidden="true"
                    className="size-5"
                    fill="none"
                    stroke="currentColor"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    viewBox="0 0 24 24"
                  >
                    {showPassword ? (
                      <>
                        <path d="M3 3l18 18" />
                        <path d="M10.6 10.6a2 2 0 0 0 2.8 2.8" />
                        <path d="M9.9 5.1A11 11 0 0 1 12 5c6.4 0 10 7 10 7a17 17 0 0 1-2.2 2.9" />
                        <path d="M6.2 6.2C3.5 8 2 12 2 12s3.6 7 10 7a11 11 0 0 0 4-.8" />
                      </>
                    ) : (
                      <>
                        <path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12Z" />
                        <circle cx="12" cy="12" r="3" />
                      </>
                    )}
                  </svg>
                </button>
              </div>

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

export default LoginPage
import { useCallback, useEffect, useState, type FormEvent } from 'react'

type Family = {
  id: string
  code: string
  name: string
  description: string | null
  is_active: boolean
  created_at: string
  updated_at: string
  version: number
}

type FamilyPayload = {
  code: string
  name: string
  description: string | null
}

const API_URL = 'http://localhost:8000/api/families'

async function readError(response: Response): Promise<string> {
  try {
    const body: { detail?: string | Array<{ loc?: (string | number)[]; msg?: string }> } =
      await response.json()

    if (typeof body.detail === 'string') {
      return body.detail
    }

    if (Array.isArray(body.detail)) {
      const campos = [...new Set(
        body.detail
          .map((item) => String(item.loc?.at(-1) ?? ''))
          .filter(Boolean),
      )]
      if (campos.length > 0) {
        return `Verifique os campos: ${campos.join(', ')}.`
      }
    }
  } catch {
    // Usa a mensagem padrão se a resposta não vier em JSON.
  }

  if (response.status === 401) return 'Sua sessão expirou. Entre novamente.'
  if (response.status === 403) return 'Somente o Planejador de Produção pode cadastrar famílias.'
  if (response.status === 409) return 'Já existe uma família cadastrada com este código.'
  return 'Não foi possível concluir a operação. Tente novamente.'
}

function FamiliesPage() {
  const [families, setFamilies] = useState<Family[]>([])
  const [code, setCode] = useState('')
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const loadFamilies = useCallback(async () => {
    setLoading(true)

    try {
      const response = await fetch(API_URL, { credentials: 'include' })

      if (!response.ok) {
        throw new Error(await readError(response))
      }

      setFamilies(await response.json() as Family[])
      setError('')
    } catch (cause) {
      setError(
        cause instanceof Error
          ? cause.message
          : 'Não foi possível carregar as famílias.',
      )
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    async function loadInitialFamilies() {
      try {
        const response = await fetch(API_URL, { credentials: 'include' })

        if (!response.ok) {
          throw new Error(await readError(response))
        }

        setFamilies(await response.json() as Family[])
        setError('')
      } catch (cause) {
        setError(
          cause instanceof Error
            ? cause.message
            : 'Não foi possível carregar as famílias.',
        )
      } finally {
        setLoading(false)
      }
    }

    void loadInitialFamilies()
  }, [])

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError('')
    setSuccess('')

    const payload: FamilyPayload = {
      code: code.trim().toUpperCase(),
      name: name.trim(),
      description: description.trim() || null,
    }

    if (!payload.code || !payload.name) {
      setError('Preencha os campos obrigatórios: código e nome.')
      return
    }

    setSaving(true)
    try {
      const response = await fetch(API_URL, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })

      if (!response.ok) {
        throw new Error(await readError(response))
      }

      const created = await response.json() as Family
      setFamilies((current) => [...current, created].sort((a, b) => a.name.localeCompare(b.name, 'pt-BR')))
      setCode('')
      setName('')
      setDescription('')
      setSuccess(`Família "${created.name}" cadastrada com sucesso.`)
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Não foi possível cadastrar a família.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="space-y-6">
      <section>
        <p className="text-sm font-semibold uppercase tracking-[0.16em] text-blue-700">Cadastros</p>
        <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-950">Famílias de produtos</h1>
        <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">
          Agrupe produtos com características relevantes para o planejamento da produção.
        </p>
      </section>

      <section className="grid gap-6 xl:grid-cols-[minmax(0,0.9fr)_minmax(0,1.1fr)]">
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm sm:p-7">
          <h2 className="text-lg font-semibold text-slate-900">Cadastrar família</h2>
          <p className="mt-1 text-sm text-slate-500">Os campos com * são obrigatórios.</p>

          <form className="mt-6 space-y-5" onSubmit={handleSubmit}>
            <div>
              <label htmlFor="family-code" className="mb-1.5 block text-sm font-medium text-slate-700">
                Código *
              </label>
              <input
                id="family-code"
                name="code"
                maxLength={50}
                required
                value={code}
                onChange={(event) => setCode(event.target.value)}
                placeholder="Ex.: EMB-001"
                className="w-full rounded-xl border border-slate-300 px-3.5 py-2.5 text-sm text-slate-900 outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-100"
              />
            </div>

            <div>
              <label htmlFor="family-name" className="mb-1.5 block text-sm font-medium text-slate-700">
                Nome *
              </label>
              <input
                id="family-name"
                name="name"
                maxLength={150}
                required
                value={name}
                onChange={(event) => setName(event.target.value)}
                placeholder="Ex.: Embalagens plásticas"
                className="w-full rounded-xl border border-slate-300 px-3.5 py-2.5 text-sm text-slate-900 outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-100"
              />
            </div>

            <div>
              <label htmlFor="family-description" className="mb-1.5 block text-sm font-medium text-slate-700">
                Descrição
              </label>
              <textarea
                id="family-description"
                name="description"
                rows={4}
                maxLength={5000}
                value={description}
                onChange={(event) => setDescription(event.target.value)}
                placeholder="Descreva as características desta família (opcional)."
                className="w-full resize-y rounded-xl border border-slate-300 px-3.5 py-2.5 text-sm text-slate-900 outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-100"
              />
            </div>

            {error && (
              <p role="alert" className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                {error}
              </p>
            )}
            {success && (
              <p role="status" className="rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800">
                {success}
              </p>
            )}

            <button
              type="submit"
              disabled={saving}
              className="inline-flex w-full items-center justify-center rounded-xl bg-blue-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {saving ? 'Cadastrando...' : 'Cadastrar família'}
            </button>
          </form>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm sm:p-7">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <h2 className="text-lg font-semibold text-slate-900">Famílias cadastradas</h2>
              <p className="mt-1 text-sm text-slate-500">Disponíveis para associação aos produtos.</p>
            </div>
            <span className="rounded-full bg-slate-100 px-3 py-1 text-sm font-semibold text-slate-600">
              {families.length}
            </span>
          </div>

          {loading ? (
            <p className="py-10 text-center text-sm text-slate-500">Carregando famílias...</p>
          ) : families.length === 0 ? (
            <div className="mt-6 rounded-xl border border-dashed border-slate-300 px-5 py-10 text-center">
              <p className="text-sm font-medium text-slate-700">Nenhuma família cadastrada.</p>
              <p className="mt-1 text-sm text-slate-500">Preencha o formulário para criar a primeira.</p>
            </div>
          ) : (
            <div className="mt-5 overflow-x-auto">
              <table className="w-full min-w-[360px] text-left text-sm">
                <thead>
                  <tr className="border-b border-slate-200 text-xs uppercase tracking-wide text-slate-500">
                    <th className="px-3 py-3 font-semibold">Código / Nome</th>
                    <th className="px-3 py-3 font-semibold">Estado</th>
                  </tr>
                </thead>
                <tbody>
                  {families.map((family) => (
                    <tr key={family.id} className="border-b border-slate-100 last:border-0">
                      <td className="px-3 py-4 align-top">
                        <p className="font-semibold text-slate-900">{family.name}</p>
                        <p className="mt-1 font-mono text-xs text-slate-500">{family.code}</p>
                        {family.description && (
                          <p className="mt-2 max-w-xs text-xs leading-5 text-slate-500">{family.description}</p>
                        )}
                      </td>
                      <td className="px-3 py-4 align-top">
                        <span className={`inline-flex rounded-full px-2.5 py-1 text-xs font-semibold ${family.is_active ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-600'}`}>
                          {family.is_active ? 'Ativa' : 'Inativa'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          <button
            type="button"
            onClick={() => void loadFamilies()}
            disabled={loading}
            className="mt-4 rounded-lg px-3 py-2 text-sm font-semibold text-blue-700 transition hover:bg-blue-50 disabled:opacity-50"
          >
            Atualizar lista
          </button>
        </div>
      </section>
    </div>
  )
}

export default FamiliesPage

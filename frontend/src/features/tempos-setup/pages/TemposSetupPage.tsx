import { useCallback, useEffect, useState, type FormEvent } from 'react'

type Familia = {
  id: string
  code: string
  name: string
}

type TempoSetup = {
  id_tempo_setup: string
  familia_origem: Familia
  familia_destino: Familia
  tempo_setup_minutos: number
  criado_em: string
  atualizado_em: string
}

type ErroApi = {
  detail?: string | Array<{ loc?: (string | number)[]; msg?: string }>
}

const FAMILIAS_API_URL = 'http://localhost:8000/api/families'
const TEMPOS_SETUP_API_URL = 'http://localhost:8000/api/tempos-setup'

async function lerErro(response: Response): Promise<string> {
  try {
    const body = await response.json() as ErroApi

    if (typeof body.detail === 'string') {
      return body.detail
    }

    if (Array.isArray(body.detail)) {
      const mensagens = body.detail
        .map((item) => item.msg)
        .filter((mensagem): mensagem is string => Boolean(mensagem))

      if (mensagens.length > 0) {
        return mensagens.join(' ')
      }
    }
  } catch {
    // Usa a mensagem padrão se a resposta não vier em JSON.
  }

  if (response.status === 401) return 'Sua sessão expirou. Entre novamente.'
  if (response.status === 403) return 'Somente o Planejador de Produção pode configurar tempos de setup.'
  if (response.status === 404) return 'Uma das famílias selecionadas não foi encontrada.'
  if (response.status === 409) return 'Já existe um tempo de setup configurado para essa combinação.'
  return 'Não foi possível concluir a operação. Tente novamente.'
}

function TemposSetupPage() {
  const [familias, setFamilias] = useState<Familia[]>([])
  const [temposSetup, setTemposSetup] = useState<TempoSetup[]>([])
  const [familiaOrigemId, setFamiliaOrigemId] = useState('')
  const [familiaDestinoId, setFamiliaDestinoId] = useState('')
  const [tempoMinutos, setTempoMinutos] = useState('')
  const [carregando, setCarregando] = useState(true)
  const [salvando, setSalvando] = useState(false)
  const [erro, setErro] = useState('')
  const [sucesso, setSucesso] = useState('')

  const carregarDados = useCallback(async () => {
    setCarregando(true)

    try {
      const [familiasResponse, temposResponse] = await Promise.all([
        fetch(FAMILIAS_API_URL, { credentials: 'include' }),
        fetch(TEMPOS_SETUP_API_URL, { credentials: 'include' }),
      ])

      if (!familiasResponse.ok) {
        throw new Error(await lerErro(familiasResponse))
      }
      if (!temposResponse.ok) {
        throw new Error(await lerErro(temposResponse))
      }

      const familiasData = await familiasResponse.json() as Familia[]
      const temposData = await temposResponse.json() as TempoSetup[]
      setFamilias(familiasData)
      setTemposSetup(temposData)
      setErro('')
    } catch (cause) {
      setErro(
        cause instanceof Error
          ? cause.message
          : 'Não foi possível carregar os dados de setup.',
      )
    } finally {
      setCarregando(false)
    }
  }, [])

  useEffect(() => {
    void carregarDados()
  }, [carregarDados])

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setErro('')
    setSucesso('')

    const minutos = Number(tempoMinutos)
    if (!familiaOrigemId || !familiaDestinoId) {
      setErro('Selecione as famílias de origem e destino.')
      return
    }
    if (familiaOrigemId === familiaDestinoId) {
      setErro('As famílias de origem e destino devem ser diferentes.')
      return
    }
    if (!Number.isSafeInteger(minutos) || minutos <= 0 || minutos > 2_147_483_647) {
      setErro('O tempo de setup informado é inválido. Informe um número inteiro de minutos maior que zero.')
      return
    }

    setSalvando(true)

    try {
      const response = await fetch(TEMPOS_SETUP_API_URL, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          familia_origem_id: familiaOrigemId,
          familia_destino_id: familiaDestinoId,
          tempo_setup_minutos: minutos,
        }),
      })

      if (!response.ok) {
        throw new Error(await lerErro(response))
      }

      const criado = await response.json() as TempoSetup
      setTemposSetup((atuais) => [criado, ...atuais])
      setTempoMinutos('')
      setSucesso(
        `Tempo de setup de ${criado.tempo_setup_minutos} minutos entre ${criado.familia_origem.name} e ${criado.familia_destino.name} cadastrado com sucesso.`,
      )
    } catch (cause) {
      setErro(
        cause instanceof Error
          ? cause.message
          : 'Não foi possível cadastrar o tempo de setup.',
      )
    } finally {
      setSalvando(false)
    }
  }

  const familiasDestino = familias.filter((familia) => familia.id !== familiaOrigemId)

  return (
    <main className="px-4 py-5 pt-[100px] sm:px-6 lg:px-7 xl:px-8">
      <div className="mx-auto max-w-[1500px] space-y-6">
        <section>
          <p className="text-sm font-semibold uppercase tracking-[0.16em] text-blue-700">
            Planejamento
          </p>
          <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-950">
            Tempos de setup entre famílias
          </h1>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-500">
            Informe o tempo necessário para preparar a produção ao trocar de uma família de produtos para outra.
          </p>
        </section>

        <section className="grid gap-6 xl:grid-cols-[minmax(0,420px)_minmax(0,1fr)]">
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="text-lg font-semibold text-slate-900">Configurar tempo de setup</h2>
            <p className="mt-1 text-sm text-slate-500">
              Selecione a família de origem, a família de destino e informe o tempo em minutos.
            </p>

            {familias.length < 2 && !carregando ? (
              <div className="mt-5 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
                Cadastre pelo menos duas famílias de produtos antes de configurar um tempo de setup.
              </div>
            ) : null}

            <form className="mt-6 space-y-5" onSubmit={handleSubmit}>
              <div>
                <label htmlFor="familia-origem" className="mb-1.5 block text-sm font-medium text-slate-700">
                  Família de origem *
                </label>
                <select
                  id="familia-origem"
                  name="familia_origem_id"
                  required
                  value={familiaOrigemId}
                  disabled={carregando || familias.length < 2}
                  onChange={(event) => {
                    const novaOrigem = event.target.value
                    setFamiliaOrigemId(novaOrigem)
                    if (novaOrigem === familiaDestinoId) setFamiliaDestinoId('')
                  }}
                  className="w-full rounded-xl border border-slate-300 bg-white px-3.5 py-2.5 text-sm text-slate-900 outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-100 disabled:bg-slate-100"
                >
                  <option value="">Selecione a família de origem</option>
                  {familias.map((familia) => (
                    <option key={familia.id} value={familia.id}>
                      {familia.code} — {familia.name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label htmlFor="familia-destino" className="mb-1.5 block text-sm font-medium text-slate-700">
                  Família de destino *
                </label>
                <select
                  id="familia-destino"
                  name="familia_destino_id"
                  required
                  value={familiaDestinoId}
                  disabled={carregando || !familiaOrigemId || familiasDestino.length === 0}
                  onChange={(event) => setFamiliaDestinoId(event.target.value)}
                  className="w-full rounded-xl border border-slate-300 bg-white px-3.5 py-2.5 text-sm text-slate-900 outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-100 disabled:bg-slate-100"
                >
                  <option value="">Selecione a família de destino</option>
                  {familiasDestino.map((familia) => (
                    <option key={familia.id} value={familia.id}>
                      {familia.code} — {familia.name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label htmlFor="tempo-setup-minutos" className="mb-1.5 block text-sm font-medium text-slate-700">
                  Tempo de setup (minutos) *
                </label>
                <input
                  id="tempo-setup-minutos"
                  name="tempo_setup_minutos"
                  type="number"
                  step="any"
                  value={tempoMinutos}
                  onChange={(event) => setTempoMinutos(event.target.value)}
                  placeholder="Ex.: 45"
                  className="w-full rounded-xl border border-slate-300 px-3.5 py-2.5 text-sm text-slate-900 outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-100"
                />
              </div>

              {erro && (
                <p role="alert" className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                  {erro}
                </p>
              )}
              {sucesso && (
                <p role="status" className="rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800">
                  {sucesso}
                </p>
              )}

              <button
                type="submit"
                disabled={salvando || carregando || familias.length < 2}
                className="inline-flex w-full items-center justify-center rounded-xl bg-blue-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {salvando ? 'Salvando...' : 'Salvar tempo de setup'}
              </button>
            </form>
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <h2 className="text-lg font-semibold text-slate-900">Tempos de setup cadastrados</h2>
                <p className="mt-1 text-sm text-slate-500">
                  Cada configuração representa uma transição da família de origem para a família de destino.
                </p>
              </div>
              <span className="rounded-full bg-slate-100 px-3 py-1 text-sm font-semibold text-slate-600">
                {temposSetup.length}
              </span>
            </div>

            {carregando ? (
              <p className="py-10 text-center text-sm text-slate-500">Carregando configurações...</p>
            ) : temposSetup.length === 0 ? (
              <div className="mt-6 rounded-xl border border-dashed border-slate-300 px-5 py-10 text-center">
                <p className="text-sm font-medium text-slate-700">Nenhum tempo de setup cadastrado.</p>
                <p className="mt-1 text-sm text-slate-500">
                  Cadastre a primeira transição usando o formulário.
                </p>
              </div>
            ) : (
              <div className="mt-5 overflow-x-auto">
                <table className="w-full min-w-[560px] text-left text-sm">
                  <thead>
                    <tr className="border-b border-slate-200 text-xs uppercase tracking-wide text-slate-500">
                      <th className="px-3 py-3 font-semibold">Origem</th>
                      <th className="px-3 py-3 font-semibold">Destino</th>
                      <th className="px-3 py-3 text-right font-semibold">Tempo</th>
                    </tr>
                  </thead>
                  <tbody>
                    {temposSetup.map((tempo) => (
                      <tr key={tempo.id_tempo_setup} className="border-b border-slate-100 last:border-0">
                        <td className="px-3 py-4 align-top">
                          <p className="font-semibold text-slate-900">{tempo.familia_origem.name}</p>
                          <p className="mt-1 font-mono text-xs text-slate-500">{tempo.familia_origem.code}</p>
                        </td>
                        <td className="px-3 py-4 align-top">
                          <p className="font-semibold text-slate-900">{tempo.familia_destino.name}</p>
                          <p className="mt-1 font-mono text-xs text-slate-500">{tempo.familia_destino.code}</p>
                        </td>
                        <td className="px-3 py-4 text-right align-top font-semibold tabular-nums text-slate-900">
                          {tempo.tempo_setup_minutos} min
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            <button
              type="button"
              onClick={() => void carregarDados()}
              disabled={carregando}
              className="mt-4 rounded-lg px-3 py-2 text-sm font-semibold text-blue-700 transition hover:bg-blue-50 disabled:opacity-50"
            >
              Atualizar lista
            </button>
          </div>
        </section>
      </div>
    </main>
  )
}

export default TemposSetupPage

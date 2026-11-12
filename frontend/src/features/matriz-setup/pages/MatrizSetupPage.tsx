
import { useCallback, useEffect, useState } from 'react'

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
}

type ErroApi = {
  detail?: string | Array<{ msg?: string }>
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
    // Utiliza a mensagem padrão abaixo.
  }

  if (response.status === 401) {
    return 'Sua sessão expirou. Entre novamente.'
  }

  if (response.status === 403) {
    return 'Somente o Planejador de Produção pode visualizar a matriz.'
  }

  return 'Não foi possível carregar os dados da matriz.'
}

function MatrizSetupPage() {
  const [familias, setFamilias] = useState<Familia[]>([])
  const [temposSetup, setTemposSetup] = useState<TempoSetup[]>([])
  const [carregando, setCarregando] = useState(true)
  const [erro, setErro] = useState('')
  const [recarregamento, setRecarregamento] = useState(0)

  // Busca os dados nas APIs e retorna os resultados.
  const buscarDados = useCallback(async () => {
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

    return {
      familias: familiasData,
      temposSetup: temposData,
    }
  }, [])

  // Solicita uma nova busca quando o usuário atualiza a matriz.
  const recarregar = () => {
    setCarregando(true)
    setErro('')
    setRecarregamento((atual) => atual + 1)
  }

  // Carrega os dados inicialmente e sempre que houver uma atualização.
  useEffect(() => {
    let ativo = true

    buscarDados()
      .then((dados) => {
        if (!ativo) return

        setFamilias(dados.familias)
        setTemposSetup(dados.temposSetup)
      })
      .catch((cause) => {
        if (!ativo) return

        setErro(
          cause instanceof Error
            ? cause.message
            : 'Não foi possível carregar a matriz de setup.',
        )
      })
      .finally(() => {
        if (ativo) {
          setCarregando(false)
        }
      })

    return () => {
      ativo = false
    }
  }, [buscarDados, recarregamento])

  // Organiza os tempos por família de origem e família de destino.
  const temposPorTransicao = new Map(
    temposSetup.map((tempo) => [
      `${tempo.familia_origem.id}:${tempo.familia_destino.id}`,
      tempo.tempo_setup_minutos,
    ]),
  )

  return (
    <main className="px-4 py-5 pt-[100px] sm:px-6 lg:px-7 xl:px-8">
      <div className="mx-auto max-w-[1500px] space-y-6">
        <section>
          <p className="text-sm font-semibold uppercase tracking-[0.16em] text-blue-700">
            Planejamento
          </p>

          <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-950">
            Matriz de setup
          </h1>

          <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-500">
            Consulte os tempos necessários para realizar a transição
            entre as famílias de produtos.
          </p>
        </section>

        {carregando ? (
          <div className="rounded-2xl border border-slate-200 bg-white px-5 py-12 text-center text-sm text-slate-500 shadow-sm">
            Carregando matriz de setup...
          </div>
        ) : erro ? (
          <div className="rounded-2xl border border-red-200 bg-white p-6 shadow-sm">
            <p role="alert" className="text-sm text-red-700">
              {erro}
            </p>

            <button
              type="button"
              onClick={recarregar}
              className="mt-4 rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700"
            >
              Tentar novamente
            </button>
          </div>
        ) : temposSetup.length === 0 ? (
          <div className="rounded-2xl border border-dashed border-slate-300 bg-white px-5 py-12 text-center shadow-sm">
            <h2 className="text-lg font-semibold text-slate-900">
              Nenhuma configuração de setup cadastrada
            </h2>

            <p className="mt-2 text-sm text-slate-500">
              Ainda não existem tempos de setup configurados entre as famílias de produtos.
            </p>
          </div>
        ) : (
          <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
            <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
              <div>
                <h2 className="text-lg font-semibold text-slate-900">
                  Tempos entre famílias
                </h2>

                <p className="mt-1 text-sm text-slate-500">
                  Linhas representam a origem e colunas representam o destino.
                </p>
              </div>

              <span className="rounded-full bg-blue-50 px-3 py-1 text-sm font-semibold text-blue-700">
                {temposSetup.length} configurações
              </span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full min-w-[600px] border-collapse text-center text-sm">
                <thead>
                  <tr>
                    <th className="sticky left-0 border border-slate-200 bg-slate-100 px-4 py-3 text-left font-semibold text-slate-700">
                      Origem / Destino
                    </th>

                    {familias.map((familia) => (
                      <th
                        key={familia.id}
                        className="border border-slate-200 bg-slate-100 px-4 py-3 font-semibold text-slate-700"
                      >
                        <span className="block">{familia.code}</span>

                        <span className="mt-1 block text-xs font-normal text-slate-500">
                          {familia.name}
                        </span>
                      </th>
                    ))}
                  </tr>
                </thead>

                <tbody>
                  {familias.map((origem) => (
                    <tr key={origem.id}>
                      <th className="sticky left-0 border border-slate-200 bg-slate-50 px-4 py-3 text-left font-semibold text-slate-800">
                        <span className="block">{origem.code}</span>

                        <span className="mt-1 block text-xs font-normal text-slate-500">
                          {origem.name}
                        </span>
                      </th>

                      {familias.map((destino) => {
                        const chave = `${origem.id}:${destino.id}`
                        const tempo = temposPorTransicao.get(chave)

                        return (
                          <td
                            key={destino.id}
                            className={`border border-slate-200 px-4 py-3 font-semibold tabular-nums ${
                              origem.id === destino.id
                                ? 'bg-slate-100 text-slate-400'
                                : tempo !== undefined
                                  ? 'bg-blue-50 text-blue-800'
                                  : 'text-slate-400'
                            }`}
                          >
                            {origem.id === destino.id
                              ? '—'
                              : tempo !== undefined
                                ? `${tempo} min`
                                : '—'}
                          </td>
                        )
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="mt-4 flex flex-wrap gap-5 text-xs text-slate-500">
              <span>— Sem configuração cadastrada</span>
              <span>Valores em minutos</span>
            </div>

            <button
              type="button"
              onClick={recarregar}
              className="mt-5 rounded-lg px-3 py-2 text-sm font-semibold text-blue-700 transition hover:bg-blue-50"
            >
              Atualizar matriz
            </button>
          </section>
        )}
      </div>
    </main>
  )
}

export default MatrizSetupPage

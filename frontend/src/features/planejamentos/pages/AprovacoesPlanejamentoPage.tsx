import { useEffect, useState } from 'react'
import { apiFetch } from '../../../lib/apiFetch'

type Origem = 'manual' | 'sugerida'

type ItemSequencia = {
  ordem_id: string
  codigo_ordem: string
  posicao: number
  codigo_maquina: string | null
}

type Sequencia = {
  origem: Origem
  origem_id: string
  nome: string
  itens: ItemSequencia[]
}

type Candidato = Sequencia & { criado_em: string }
type Aprovacao = Sequencia & { id_aprovacao: string; aprovado_em: string; status: 'APROVADO' }
type Painel = { candidatos: Candidato[]; aprovados: Aprovacao[] }

const API = 'http://localhost:8000/api/planejamentos/aprovacoes'
const SEM_PLANEJAMENTO = 'Não existe planejamento disponível para aprovação.'
const TIPOS = { manual: 'Manual', sugerida: 'Sugerida' }

function ListaSequencia({ itens }: { itens: ItemSequencia[] }) {
  return (
    <ol className="mt-3 space-y-2">
      {itens.map((item) => (
        <li key={item.ordem_id} className="flex flex-wrap items-center gap-3 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm">
          <span className="rounded-md bg-slate-100 px-2 py-1 text-slate-700">{item.posicao}º</span>
          <strong data-cy="ordem-sequenciada" className="text-slate-900">{item.codigo_ordem}</strong>
          <span className="text-slate-600">{item.codigo_maquina ?? 'Sem máquina atribuída'}</span>
        </li>
      ))}
    </ol>
  )
}

type Props = {
  podeAprovar: boolean
  voltarAoDashboard: () => void
}

export default function AprovacoesPlanejamentoPage({ podeAprovar, voltarAoDashboard }: Props) {
  const [painel, setPainel] = useState<Painel | null>(null)
  const [selecionado, setSelecionado] = useState<Candidato | null>(null)
  const [salvando, setSalvando] = useState(false)
  const [aviso, setAviso] = useState('')
  const [erro, setErro] = useState('')
  const [erroCarga, setErroCarga] = useState(false)

  useEffect(() => {
    const controle = new AbortController()
    const opcoes = { credentials: 'include', signal: controle.signal } as const

    async function carregar() {
      try {
        const [aprovados, candidatos] = await Promise.all([
          apiFetch(API, opcoes),
          podeAprovar ? apiFetch(`${API}/candidatos`, opcoes) : null,
        ])
        if (!aprovados.ok || (candidatos && !candidatos.ok)) {
          throw new Error('Falha na consulta de planejamentos.')
        }
        const dadosAprovados: Aprovacao[] = await aprovados.json()
        const dadosCandidatos: Candidato[] = candidatos ? await candidatos.json() : []
        if (!controle.signal.aborted) {
          setPainel({ aprovados: dadosAprovados, candidatos: dadosCandidatos })
        }
      } catch {
        if (!controle.signal.aborted) setErroCarga(true)
      }
    }

    void carregar()
    return () => controle.abort()
  }, [podeAprovar])

  async function aprovar() {
    if (!podeAprovar || !painel || salvando) return
    setErro('')
    setAviso('')
    if (!selecionado) {
      setErro(painel.candidatos.length > 0 ? 'Selecione um planejamento para aprovar.' : SEM_PLANEJAMENTO)
      return
    }

    setSalvando(true)
    try {
      const resposta = await apiFetch(API, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          origem: selecionado.origem,
          origem_id: selecionado.origem_id,
          ordens_ids: selecionado.itens.map((item) => item.ordem_id),
        }),
      })
      if (!resposta.ok) {
        const falha = await resposta.json().catch(() => null)
        throw new Error(typeof falha?.detail === 'string' ? falha.detail : 'Não foi possível aprovar o planejamento.')
      }

      const aprovado: Aprovacao = await resposta.json()
      const ordens = new Set(aprovado.itens.map((item) => item.ordem_id))
      setPainel({
        aprovados: [aprovado, ...painel.aprovados.filter((item) => item.id_aprovacao !== aprovado.id_aprovacao)],
        candidatos: painel.candidatos.filter((item) => !item.itens.some((ordem) => ordens.has(ordem.ordem_id))),
      })
      setSelecionado(null)
      setAviso('Planejamento aprovado e disponível para execução.')
    } catch (falha) {
      setErro(falha instanceof Error ? falha.message : 'Não foi possível aprovar o planejamento.')
    } finally {
      setSalvando(false)
    }
  }

  return (
    <main className="px-4 py-5 pt-[100px] sm:px-6 lg:px-7 xl:px-8">
      <div className="mx-auto max-w-[1200px] space-y-6">
        <button type="button" onClick={voltarAoDashboard} className="text-sm font-semibold text-blue-700 lg:hidden">
          Voltar ao dashboard
        </button>
        <h1 className="text-2xl font-bold text-slate-950">Execução da produção</h1>
        {erroCarga ? (
          <p role="alert" className="rounded-xl bg-red-50 p-4 text-sm text-red-800">Não foi possível consultar os planejamentos.</p>
        ) : !painel ? (
          <p role="status" className="text-sm text-slate-600">Carregando planejamentos…</p>
        ) : (
          <>
            {podeAprovar && (
              <section aria-labelledby="titulo-aprovacao" className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
                <h2 id="titulo-aprovacao" className="text-lg font-semibold text-slate-900">Aprovar planejamento</h2>
                {painel.candidatos.length === 0 ? (
                  <p className="mt-3 text-sm text-slate-600">Nenhum planejamento disponível para aprovação.</p>
                ) : (
                  <div className="mt-4 grid gap-5 md:grid-cols-2">
                    <fieldset disabled={salvando} className="space-y-2">
                      <legend className="mb-2 text-sm font-semibold text-slate-700">Selecione uma sequência</legend>
                      {painel.candidatos.map((candidato) => (
                        <label key={`${candidato.origem}:${candidato.origem_id}`} className="flex cursor-pointer gap-3 rounded-xl border border-slate-200 p-3 text-sm has-checked:border-blue-300 has-checked:bg-blue-50">
                          <input type="radio" name="planejamento" checked={selecionado === candidato}
                            onChange={() => { setSelecionado(candidato); setErro(''); setAviso('') }}
                            data-cy={`candidato-${candidato.origem}`} className="accent-blue-600" />
                          <span>
                            <strong className="block text-slate-900">{candidato.nome}</strong>
                            <span className="text-slate-600">
                              {TIPOS[candidato.origem]} · {new Date(candidato.criado_em).toLocaleString('pt-BR')}
                            </span>
                          </span>
                        </label>
                      ))}
                    </fieldset>
                    {selecionado && (
                      <div data-cy="sequencia-selecionada" className="rounded-xl bg-slate-50 p-4">
                        <h3 className="text-sm font-semibold text-slate-900">Sequência selecionada</h3>
                        <ListaSequencia itens={selecionado.itens} />
                      </div>
                    )}
                  </div>
                )}
                <button type="button" data-cy="aprovar-planejamento" disabled={salvando} onClick={() => void aprovar()}
                  className="mt-4 rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-50">
                  {salvando ? 'Aprovando…' : 'Aprovar planejamento'}
                </button>
                {erro && <p role="alert" className="mt-4 rounded-xl bg-red-50 p-3 text-sm text-red-800">{erro}</p>}
                {aviso && <p role="status" className="mt-4 rounded-xl bg-green-50 p-3 text-sm text-green-800">{aviso}</p>}
              </section>
            )}
            <section aria-labelledby="titulo-aprovados" className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
              <h2 id="titulo-aprovados" className="text-lg font-semibold text-slate-900">Planejamentos aprovados</h2>
              {painel.aprovados.length === 0 ? (
                <p className="mt-3 text-sm text-slate-600">Nenhum planejamento aprovado para execução.</p>
              ) : (
                <div className="mt-4 grid gap-4 md:grid-cols-2">
                  {painel.aprovados.map((aprovado) => (
                    <article key={aprovado.id_aprovacao} data-cy="planejamento-aprovado" className="rounded-xl bg-slate-50 p-4">
                      <div className="flex flex-wrap items-start justify-between gap-2">
                        <h3 className="font-semibold text-slate-900">{aprovado.nome}</h3>
                        <span className="rounded-md bg-green-100 px-2 py-1 text-xs font-semibold text-green-800">Aprovado</span>
                      </div>
                      <p className="mt-1 text-xs text-slate-600">
                        {TIPOS[aprovado.origem]} · {new Date(aprovado.aprovado_em).toLocaleString('pt-BR')}
                      </p>
                      <ListaSequencia itens={aprovado.itens} />
                    </article>
                  ))}
                </div>
              )}
            </section>
          </>
        )}
      </div>
    </main>
  )
}

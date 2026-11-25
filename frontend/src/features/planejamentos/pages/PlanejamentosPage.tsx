import { useEffect, useRef, useState } from 'react'
import { apiFetch } from '../../../lib/apiFetch'
import { ComparacaoSequencias } from '../components/ComparacaoSequencias'
import type { ComparacaoPlanejamento, Planejamento, SugestaoPlanejamento } from '../types'

type OrdemProducao = {
  id_ordem: string
  codigo: string
  status: string
}

type Maquina = {
  id_maquina: string
  codigo: string
  nome: string
}

type PedidoSugestao =
  | { acao: 'gerar' }
  | { acao: 'consultar' | 'comparar'; planejamentoId: string }

const ERROS_SUGESTAO = {
  gerar: 'Não foi possível gerar a sequência sugerida.',
  consultar: 'Não foi possível consultar a sequência sugerida.',
  comparar: 'Não foi possível comparar as sequências.',
}

const API_URL = 'http://localhost:8000/api'

function PlanejamentosPage() {
  const [nome, setNome] = useState('')
  const [ordens, setOrdens] = useState<OrdemProducao[]>([])
  const [maquinas, setMaquinas] = useState<Maquina[]>([])
  const [selecionadas, setSelecionadas] = useState<OrdemProducao[]>([])
  const [planejamentos, setPlanejamentos] = useState<Planejamento[]>([])
  const [planejamentoEmEdicao, setPlanejamentoEmEdicao] = useState<string | null>(null)
  const [carregando, setCarregando] = useState(true)
  const [salvando, setSalvando] = useState(false)
  const [pedidoSugestao, setPedidoSugestao] = useState<PedidoSugestao | null>(null)
  const [sugestao, setSugestao] = useState<SugestaoPlanejamento | null>(null)
  const [comparacao, setComparacao] = useState<ComparacaoPlanejamento | null>(null)
  const [erroSugestao, setErroSugestao] = useState('')
  const [erro, setErro] = useState('')
  const [mensagem, setMensagem] = useState('')
  const formularioRef = useRef<HTMLElement | null>(null)
  const resultadoSugestaoRef = useRef<HTMLDivElement | null>(null)
  const ocupado = salvando || pedidoSugestao !== null

  useEffect(() => {
    let ativo = true

    async function carregarDados() {
      try {

        const [respostaOrdens, respostaPlanejamentos, respostaMaquinas] = await Promise.all([
          apiFetch(`${API_URL}/ordens-producao`, { credentials: 'include' }),
          apiFetch(`${API_URL}/planejamentos`, { credentials: 'include' }),
          apiFetch(`${API_URL}/maquinas`, { credentials: 'include' }),
        ])

        if (!respostaOrdens.ok || !respostaPlanejamentos.ok || !respostaMaquinas.ok) {
          throw new Error('Não foi possível carregar os dados.')
        }

        const dadosOrdens: OrdemProducao[] = await respostaOrdens.json()
        const dadosPlanejamentos: Planejamento[] = await respostaPlanejamentos.json()
        const dadosMaquinas: Maquina[] = await respostaMaquinas.json()

        if (ativo) {
          setOrdens(dadosOrdens)
          setPlanejamentos(dadosPlanejamentos)
          setMaquinas(dadosMaquinas)
        }

      } catch (error) {
        if (ativo) {
          setErro(error instanceof Error ? error.message : 'Erro ao carregar os dados.')
        }
      } finally {
        if (ativo) setCarregando(false)
      }
    }

    void carregarDados()

    return () => {
      ativo = false
    }
  }, [])

  useEffect(() => {
    if (sugestao || comparacao || erroSugestao) {
      resultadoSugestaoRef.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
    }
  }, [sugestao, comparacao, erroSugestao])

  async function carregarPlanejamentos() {
    const resposta = await apiFetch(`${API_URL}/planejamentos`, {
      credentials: 'include',
    })

    if (!resposta.ok) {
      throw new Error('Não foi possível atualizar os planejamentos.')
    }

    const dados: Planejamento[] = await resposta.json()
    setPlanejamentos(dados)
  }

  function limparSugestao() {
    setSugestao(null)
    setComparacao(null)
    setErroSugestao('')
  }

  function selecionarOrdem(ordem: OrdemProducao) {
    if (ocupado) return
    limparSugestao()
    setMensagem('')
    setSelecionadas((atual) =>
      atual.some((item) => item.id_ordem === ordem.id_ordem)
        ? atual.filter((item) => item.id_ordem !== ordem.id_ordem)
        : [...atual, ordem],
    )
  }

  function moverOrdem(indice: number, direcao: number) {
    if (ocupado) return
    limparSugestao()
    setSelecionadas((atual) => {
      const destino = indice + direcao
      if (destino < 0 || destino >= atual.length) return atual

      const novaLista = [...atual]
      ;[novaLista[indice], novaLista[destino]] = [
        novaLista[destino],
        novaLista[indice],
      ]
      return novaLista
    })
  }

  function editarPlanejamento(planejamento: Planejamento) {
    const itensOrdenados = [...planejamento.itens].sort((a, b) => a.posicao - b.posicao)
    const ordensEdicao = itensOrdenados
      .map((item) => ordens.find((ordem) => ordem.id_ordem === item.ordem_id))
      .filter((ordem): ordem is OrdemProducao => ordem !== undefined)

    if (ordensEdicao.length !== itensOrdenados.length) {
      setMensagem('')
      setErro('Não foi possível carregar todas as ordens do planejamento.')
      return
    }

    setPlanejamentoEmEdicao(planejamento.id_planejamento)
    setNome(planejamento.nome)
    setSelecionadas(ordensEdicao)
    limparSugestao()
    setErro('')
    setMensagem('')
    formularioRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }

  function cancelarEdicao() {
    setPlanejamentoEmEdicao(null)
    setNome('')
    setSelecionadas([])
    limparSugestao()
    setErro('')
    setMensagem('')
  }

  async function salvarPlanejamento() {
    if (!nome.trim() || selecionadas.length === 0 || ocupado || carregando) return

    setSalvando(true)
    setErro('')
    setMensagem('')

    const editando = planejamentoEmEdicao !== null
    const url = editando
      ? `${API_URL}/planejamentos/${planejamentoEmEdicao}`
      : `${API_URL}/planejamentos`

    try {
      const resposta = await apiFetch(url, {
        method: editando ? 'PUT' : 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          nome: nome.trim(),
          ordens_ids: selecionadas.map((ordem) => ordem.id_ordem),
        }),
      })

      if (!resposta.ok) {
        const dadosErro = await resposta.json().catch(() => null)
        throw new Error(
          typeof dadosErro?.detail === 'string'
            ? dadosErro.detail
            : 'Não foi possível salvar o planejamento.',
        )
      }

      setPlanejamentoEmEdicao(null)
      setNome('')
      setSelecionadas([])
      limparSugestao()
      setMensagem(
        editando
          ? 'Planejamento atualizado com sucesso!'
          : 'Planejamento salvo com sucesso!',
      )

      try {
        await carregarPlanejamentos()
      } catch {
        setErro('Alterações salvas, mas não foi possível atualizar a listagem.')
      }
    } catch (error) {
      setErro(error instanceof Error ? error.message : 'Erro ao salvar planejamento.')
    } finally {
      setSalvando(false)
    }
  }

  async function solicitarSugestao(pedido: PedidoSugestao) {
    if (ocupado || carregando) return
    limparSugestao()

    if (pedido.acao === 'gerar' && selecionadas.length === 0) {
      setErroSugestao('Selecione pelo menos uma ordem para gerar a sugestão.')
      return
    }

    setPedidoSugestao(pedido)
    const erroPadrao = ERROS_SUGESTAO[pedido.acao]

    try {
      const resposta = pedido.acao === 'gerar'
        ? await apiFetch(`${API_URL}/planejamentos/sugestoes`, {
          method: 'POST',
          credentials: 'include',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ ordens_ids: selecionadas.map((ordem) => ordem.id_ordem) }),
        })
        : await apiFetch(
          `${API_URL}/planejamentos/${pedido.planejamentoId}/${pedido.acao === 'comparar' ? 'comparacao' : 'sugestao'}`,
          { credentials: 'include' },
        )

      if (!resposta.ok) {
        const dadosErro = await resposta.json().catch(() => null)
        setErroSugestao(typeof dadosErro?.detail === 'string' ? dadosErro.detail : erroPadrao)
        return
      }

      if (pedido.acao === 'comparar') {
        setComparacao(await resposta.json())
      } else {
        setSugestao(await resposta.json())
      }
    } catch {
      setErroSugestao(erroPadrao)
    } finally {
      setPedidoSugestao(null)
    }
  }

  const ordensPlanejadasEmOutros = new Set(
    planejamentos
      .filter((planejamento) => planejamento.id_planejamento !== planejamentoEmEdicao)
      .flatMap((planejamento) => planejamento.itens.map((item) => item.ordem_id)),
  )

  const ordensDisponiveis = ordens.filter(
    (ordem) =>
      ordem.status === 'PENDENTE' &&
      !ordensPlanejadasEmOutros.has(ordem.id_ordem),
  )

  const idsSelecionados = new Set(selecionadas.map((ordem) => ordem.id_ordem))

  function codigoDaOrdem(ordemId: string) {
    return ordens.find((ordem) => ordem.id_ordem === ordemId)?.codigo ?? ordemId.slice(0, 8)
  }

  function identificarMaquina(maquinaId: string | null) {
    if (!maquinaId) return 'Máquina não atribuída'

    const maquina = maquinas.find(
      (item) => item.id_maquina === maquinaId,
    )

    return maquina
      ? `${maquina.codigo} — ${maquina.nome}`
      : `Máquina ${maquinaId.slice(0, 8)}`
  }

  return (
    <main className="px-4 py-5 pt-[100px] sm:px-6 lg:px-7 xl:px-8">
      <div className="mx-auto max-w-[1500px] space-y-6">
        <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <h1 className="text-2xl font-bold text-slate-950">Planejamento manual</h1>
          <p className="mt-2 text-sm text-slate-500">
            Selecione as ordens para montar a sequência manual ou gerar uma sugestão de produção.
          </p>

          {mensagem && (
            <p role="status" className="mt-4 rounded-xl bg-green-50 p-3 text-sm text-green-700">
              {mensagem}
            </p>
          )}
          {erro && (
            <p role="alert" className="mt-4 rounded-xl bg-red-50 p-3 text-sm text-red-700">
              {erro}
            </p>
          )}
        </section>

        <section ref={formularioRef} className="scroll-mt-28 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-900">
            {planejamentoEmEdicao ? 'Editar planejamento' : 'Novo planejamento'}
          </h2>
          {planejamentoEmEdicao && (
            <p className="mt-1 text-sm text-blue-700">
              Você está editando um planejamento cadastrado.
            </p>
          )}

          <label htmlFor="nome-planejamento" className="mt-5 block text-sm font-medium text-slate-700">
            Nome do planejamento
          </label>
          <input
            id="nome-planejamento"
            type="text"
            data-cy="nome-planejamento"
            value={nome}
            maxLength={150}
            disabled={ocupado}
            onChange={(evento) => setNome(evento.target.value)}
            placeholder="Ex.: Planejamento de segunda-feira"
            className="mt-2 w-full rounded-xl border border-slate-300 px-4 py-3 text-sm outline-none focus:border-blue-500 disabled:opacity-60"
          />
        </section>

        <div className="grid gap-6 lg:grid-cols-2">
          <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="text-lg font-semibold text-slate-900">Ordens disponíveis</h2>
            <p className="mt-1 text-sm text-slate-500">
              Selecione as ordens que deseja incluir.
            </p>

            {carregando ? (
              <p className="mt-5 text-sm text-slate-500">Carregando ordens...</p>
            ) : ordensDisponiveis.length === 0 ? (
              <p className="mt-5 text-sm text-slate-500">Nenhuma ordem pendente disponível.</p>
            ) : (
              <div className="mt-5 space-y-2">
                {ordensDisponiveis.map((ordem) => (
                  <label
                    key={ordem.id_ordem}
                    className="flex cursor-pointer items-center gap-3 rounded-xl border border-slate-200 p-3 hover:bg-slate-50"
                  >
                    <input
                      type="checkbox"
                      checked={idsSelecionados.has(ordem.id_ordem)}
                      disabled={ocupado}
                      onChange={() => selecionarOrdem(ordem)}
                      className="h-4 w-4 accent-blue-600"
                    />
                    <span className="text-sm font-medium text-slate-800">{ordem.codigo}</span>
                  </label>
                ))}
              </div>
            )}
          </section>

          <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="text-lg font-semibold text-slate-900">Sequência de execução</h2>
            <p className="mt-1 text-sm text-slate-500">
              Use as setas para alterar a ordem de execução.
            </p>

            {selecionadas.length === 0 ? (
              <p className="mt-5 text-sm text-slate-500">Nenhuma ordem selecionada.</p>
            ) : (
              <div className="mt-5 space-y-2">
                {selecionadas.map((ordem, indice) => (
                  <div
                    key={ordem.id_ordem}
                    className="flex items-center gap-3 rounded-xl border border-slate-200 p-3"
                  >
                    <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-50 text-sm font-semibold text-blue-700">
                      {indice + 1}
                    </span>
                    <span className="flex-1 text-sm font-medium text-slate-800">{ordem.codigo}</span>
                    <button
                      type="button"
                      aria-label={`Subir ${ordem.codigo}`}
                      disabled={indice === 0 || ocupado}
                      onClick={() => moverOrdem(indice, -1)}
                      className="rounded-lg border px-3 py-2 text-sm disabled:opacity-30"
                    >
                      ↑
                    </button>
                    <button
                      type="button"
                      aria-label={`Descer ${ordem.codigo}`}
                      disabled={indice === selecionadas.length - 1 || ocupado}
                      onClick={() => moverOrdem(indice, 1)}
                      className="rounded-lg border px-3 py-2 text-sm disabled:opacity-30"
                    >
                      ↓
                    </button>
                  </div>
                ))}
              </div>
            )}
          </section>
        </div>

        <div className="flex flex-wrap justify-end gap-3">
          {planejamentoEmEdicao && (
            <button
              type="button"
              onClick={cancelarEdicao}
              disabled={ocupado}
              className="rounded-xl border border-slate-300 px-6 py-3 text-sm font-semibold text-slate-700 hover:bg-slate-50 disabled:opacity-50"
            >
              Cancelar edição
            </button>
          )}
          <button
            type="button"
            data-cy="gerar-sugestao"
            onClick={() => void solicitarSugestao({ acao: 'gerar' })}
            disabled={ocupado || carregando}
            className="rounded-xl border border-blue-200 px-6 py-3 text-sm font-semibold text-blue-700 hover:bg-blue-50 disabled:opacity-50"
          >
            {pedidoSugestao?.acao === 'gerar' ? 'Gerando sugestão...' : 'Gerar sequência sugerida'}
          </button>
          <button
            type="button"
            data-cy="salvar-planejamento"
            onClick={() => void salvarPlanejamento()}
            disabled={!nome.trim() || selecionadas.length === 0 || ocupado || carregando}
            className="rounded-xl bg-blue-600 px-6 py-3 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-50"
          >
            {salvando
              ? 'Salvando...'
              : planejamentoEmEdicao
                ? 'Salvar alterações'
                : 'Salvar planejamento'}
          </button>
        </div>

        {(sugestao || comparacao || erroSugestao) && (
          <div ref={resultadoSugestaoRef} className="scroll-mt-28">
            {erroSugestao && (
              <p role="alert" className="whitespace-pre-line rounded-xl bg-red-50 p-4 text-sm text-red-700">
                {erroSugestao}
              </p>
            )}
            {comparacao && (
              <ComparacaoSequencias
                comparacao={comparacao}
                codigoDaOrdem={codigoDaOrdem}
                identificarMaquina={identificarMaquina}
              />
            )}
            {sugestao && (
              <section aria-labelledby="titulo-sugestao" className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
                <h2 id="titulo-sugestao" className="text-lg font-semibold text-slate-900">Sequência sugerida</h2>
                <p role="status" className="mt-2 text-sm text-slate-700">
                  Tempo total estimado de setup de <strong>{sugestao.tempo_setup_total_minutos} {sugestao.tempo_setup_total_minutos === 1 ? 'minuto' : 'minutos'}</strong>
                </p>
                <ol className="mt-4 space-y-2">
                  {sugestao.itens.map((item) => (
                    <li key={item.ordem_id} className="flex items-center gap-3 rounded-xl border border-slate-200 p-3 text-sm">
                      <span className="rounded-lg bg-blue-50 px-3 py-2 font-semibold text-blue-700">{item.posicao}</span>

                      <div className="min-w-0 flex-1">
                        <span
                          data-cy="sugestao-ordem"
                          className="wrap-anywhere font-medium text-slate-800"
                        >
                          {codigoDaOrdem(item.ordem_id)}
                        </span>
                        <p
                          data-cy="sugestao-maquina"
                          className="mt-1 wrap-anywhere text-xs text-slate-500"
                        >
                          {identificarMaquina(item.maquina_id)}
                        </p>
                      </div>

                      <span className="shrink-0 text-slate-600">Setup de {item.setup_minutos} min</span>
                    </li>
                  ))}
                </ol>
              </section>
            )}
          </div>
        )}

        <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-900">Planejamentos cadastrados</h2>
          <p className="mt-1 text-sm text-slate-500">
            Consulte os planejamentos que já foram salvos.
          </p>

          {carregando ? (
            <p className="mt-5 text-sm text-slate-500">Carregando planejamentos...</p>
          ) : planejamentos.length === 0 ? (
            <p className="mt-5 text-sm text-slate-500">Nenhum planejamento cadastrado.</p>
          ) : (
            <div className="mt-5 space-y-3">
              {planejamentos.map((planejamento) => (
                <div
                  key={planejamento.id_planejamento}
                  data-cy="planejamento-card"
                  className="rounded-xl border border-slate-200 p-4"
                >
                  <div className="flex flex-wrap items-center justify-between gap-3">
                    <div>
                      <h3 className="font-semibold text-slate-900">{planejamento.nome}</h3>
                      <p className="mt-1 text-xs text-slate-500">
                        {planejamento.itens.length} ordem(ns) de produção
                      </p>
                    </div>
                    <div className="flex flex-wrap items-center gap-3">
                      <span className="text-xs text-slate-500">
                        {new Date(planejamento.criado_em).toLocaleDateString('pt-BR')}
                      </span>
                      <button
                        type="button"
                        onClick={() => void solicitarSugestao({
                          acao: 'consultar', planejamentoId: planejamento.id_planejamento,
                        })}
                        disabled={ocupado || carregando}
                        className="rounded-lg border border-blue-200 px-4 py-2 text-sm font-medium text-blue-700 hover:bg-blue-50 disabled:opacity-50"
                      >
                        Consultar sugestão
                      </button>
                      <button
                        type="button"
                        data-cy="comparar-sequencias"
                        onClick={() => void solicitarSugestao({
                          acao: 'comparar', planejamentoId: planejamento.id_planejamento,
                        })}
                        disabled={ocupado || carregando}
                        className="rounded-lg border border-blue-200 px-4 py-2 text-sm font-medium text-blue-700 hover:bg-blue-50 disabled:opacity-50"
                      >
                        {pedidoSugestao?.acao === 'comparar'
                          && pedidoSugestao.planejamentoId === planejamento.id_planejamento
                          ? 'Comparando...' : 'Comparar sequências'}
                      </button>
                      <button
                        type="button"
                        onClick={() => editarPlanejamento(planejamento)}
                        disabled={ocupado || carregando}
                        className="rounded-lg border border-blue-200 px-4 py-2 text-sm font-medium text-blue-700 hover:bg-blue-50 disabled:opacity-50"
                      >
                        Editar
                      </button>
                    </div>
                  </div>

                  <div className="mt-4 flex flex-wrap gap-2">
                    {[...planejamento.itens]
                      .sort((a, b) => a.posicao - b.posicao)
                      .map((item) => (
                        <span
                          key={item.id_item}
                          className="rounded-lg bg-blue-50 px-3 py-2 text-xs font-medium text-blue-700"
                        >
                          {item.posicao}º — {codigoDaOrdem(item.ordem_id)}
                        </span>
                      ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      </div>
    </main>
  )
}

export default PlanejamentosPage

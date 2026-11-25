import type { ComparacaoPlanejamento } from '../types'

type ItemSequencia = {
  ordem_id: string
  posicao: number
  maquina_id?: string | null
}

type SequenciaProps = {
  titulo: string
  seletor: string
  itens: ItemSequencia[]
  outrasPosicoes: Map<string, number>
  outraSequencia: string
  codigoDaOrdem: (id: string) => string
  identificarMaquina: (id: string | null) => string
}

function Sequencia({
  titulo, seletor, itens, outrasPosicoes, outraSequencia, codigoDaOrdem, identificarMaquina,
}: SequenciaProps) {
  return (
    <section className="rounded-xl border border-slate-200 bg-slate-50 p-4">
      <h3 className="font-semibold text-slate-900">{titulo}</h3>
      <ol data-cy={seletor} className="mt-3 space-y-2">
        {itens.map((item) => {
          const outraPosicao = outrasPosicoes.get(item.ordem_id)
          return (
            <li key={item.ordem_id} className="flex flex-wrap items-center gap-2 rounded-lg bg-white p-2 text-sm">
              <span className="rounded-md bg-slate-100 px-2 py-1 text-slate-700">{item.posicao}º</span>
              <span data-cy="ordem-comparada" className="wrap-anywhere font-medium text-slate-900">
                {codigoDaOrdem(item.ordem_id)}
              </span>
              {item.maquina_id !== undefined && (
                <span className="wrap-anywhere text-xs text-slate-600">
                  {identificarMaquina(item.maquina_id)}
                </span>
              )}
              {outraPosicao !== undefined && outraPosicao !== item.posicao && (
                <span data-cy="posicao-alternativa" className="rounded-md bg-blue-50 px-2 py-1 text-xs font-medium text-blue-800">
                  {outraPosicao}º na {outraSequencia}
                </span>
              )}
            </li>
          )
        })}
      </ol>
    </section>
  )
}

type ComparacaoSequenciasProps = {
  comparacao: ComparacaoPlanejamento
  codigoDaOrdem: (id: string) => string
  identificarMaquina: (id: string | null) => string
}

export function ComparacaoSequencias({
  comparacao, codigoDaOrdem, identificarMaquina,
}: ComparacaoSequenciasProps) {
  const { planejamento, sugestao, setup } = comparacao
  const posicoesManuais = new Map(planejamento.itens.map((item) => [item.ordem_id, item.posicao]))
  const posicoesSugeridas = new Map(sugestao.itens.map((item) => [item.ordem_id, item.posicao]))
  const ordensMovidas = planejamento.itens.filter(
    (item) => posicoesSugeridas.get(item.ordem_id) !== item.posicao,
  ).length

  return (
    <section
      data-cy="comparacao-sequencias"
      aria-labelledby="titulo-comparacao"
      className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"
    >
      <h2 id="titulo-comparacao" className="text-lg font-semibold text-slate-900">
        Comparação de sequências · {planejamento.nome}
      </h2>
      <p role="status" className="mt-2 text-sm text-slate-700">
        {ordensMovidas === 0
          ? 'Nenhuma ordem mudou de posição.'
          : `${ordensMovidas} de ${planejamento.itens.length} ordens mudaram de posição.`}
      </p>

      <div className="mt-4 grid gap-4 md:grid-cols-2">
        <Sequencia
          titulo="Sequência manual"
          seletor="sequencia-manual"
          itens={planejamento.itens}
          outrasPosicoes={posicoesSugeridas}
          outraSequencia="sugerida"
          codigoDaOrdem={codigoDaOrdem}
          identificarMaquina={identificarMaquina}
        />
        <Sequencia
          titulo="Sequência sugerida"
          seletor="sequencia-sugerida"
          itens={sugestao.itens}
          outrasPosicoes={posicoesManuais}
          outraSequencia="manual"
          codigoDaOrdem={codigoDaOrdem}
          identificarMaquina={identificarMaquina}
        />
      </div>

      {setup ? (
        <div className="mt-4 rounded-xl border border-blue-100 bg-blue-50 p-4 text-sm text-slate-800">
          <h3 className="font-semibold text-slate-900">Tempo estimado de setup</h3>
          <dl className="mt-2 grid gap-3 sm:grid-cols-3">
            <div>
              <dt>Sequência manual</dt>
              <dd data-cy="setup-manual" className="font-semibold">{setup.manual_minutos} min</dd>
            </div>
            <div>
              <dt>Sequência sugerida</dt>
              <dd data-cy="setup-sugerido" className="font-semibold">{setup.sugerido_minutos} min</dd>
            </div>
            <div>
              <dt>Diferença na sugerida</dt>
              <dd data-cy="diferenca-setup" className="font-semibold">
                {setup.diferenca_minutos === 0
                  ? 'Sem diferença'
                  : `${Math.abs(setup.diferenca_minutos)} min a ${setup.diferenca_minutos < 0 ? 'menos' : 'mais'}`}
              </dd>
            </div>
          </dl>
          <p className="mt-3 text-xs text-slate-700">
            {setup.referencia === 'registrado'
              ? 'Tempos registrados quando a sugestão foi gerada.'
              : 'Tempos recalculados com a configuração atual e a distribuição por máquina da sugestão.'}
          </p>
        </div>
      ) : (
        <p className="mt-4 rounded-xl bg-slate-100 p-4 text-sm text-slate-700">
          Tempos de setup indisponíveis com os cadastros atuais de famílias e tempos de troca.
        </p>
      )}
    </section>
  )
}

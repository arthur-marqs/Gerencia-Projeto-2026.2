export type Planejamento = {
  id_planejamento: string
  nome: string
  criado_em: string
  itens: {
    id_item: string
    ordem_id: string
    posicao: number
  }[]
}

export type SugestaoPlanejamento = {
  tempo_setup_total_minutos: number
  itens: {
    ordem_id: string
    maquina_id: string | null
    posicao: number
    setup_minutos: number
  }[]
}

export type ComparacaoPlanejamento = {
  planejamento: Planejamento
  sugestao: SugestaoPlanejamento
  setup: {
    manual_minutos: number
    sugerido_minutos: number
    diferenca_minutos: number
    referencia: 'registrado' | 'atual'
  } | null
}

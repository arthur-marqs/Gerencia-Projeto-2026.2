import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'

const API_URL = 'http://localhost:8000/api/ordens-producao'
const PRODUTOS_URL = 'http://localhost:8000/api/produtos'

type Produto = {
  id_produto: string
  codigo: string
  nome: string
  unidade: string
  ativo: boolean
}

type OrdemProducao = {
  id_ordem: string
  codigo: string
  produto_id: string
  quantidade: string | number
  status: string
  criado_em: string
  prazo: string | null
  prioridade: 'Baixa' | 'Média' | 'Alta' | null
}

type ErrosFormulario = {
  codigo?: string
  produto_id?: string
  quantidade?: string
}

type ErrosEdicao = {
  prazo?: string
  prioridade?: string
}

function formatarQuantidade(quantidade: string | number) {
  return new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 3 }).format(Number(quantidade))
}

function formatarData(data: string) {
  return new Intl.DateTimeFormat('pt-BR', { dateStyle: 'short', timeStyle: 'short' }).format(new Date(data))
}

function formatarPrazo(prazo: string) {
  return new Intl.DateTimeFormat('pt-BR', { dateStyle: 'short', timeZone: 'UTC' }).format(new Date(`${prazo}T00:00:00Z`))
}

function dataAtualLocal() {
  return new Date(Date.now() - new Date().getTimezoneOffset() * 60_000)
    .toISOString()
    .slice(0, 10)
}

function OrdensProducaoPage() {
  const [codigo, setCodigo] = useState('')
  const [produtoId, setProdutoId] = useState('')
  const [quantidade, setQuantidade] = useState('')
  const [ordens, setOrdens] = useState<OrdemProducao[]>([])
  const [produtos, setProdutos] = useState<Produto[]>([])
  const [erros, setErros] = useState<ErrosFormulario>({})
  const [mensagemErro, setMensagemErro] = useState('')
  const [mensagemSucesso, setMensagemSucesso] = useState('')
  const [carregando, setCarregando] = useState(true)
  const [salvando, setSalvando] = useState(false)
  const [ordemEmEdicao, setOrdemEmEdicao] = useState<OrdemProducao | null>(null)
  const [prazo, setPrazo] = useState('')
  const [prioridade, setPrioridade] = useState('')
  const [errosEdicao, setErrosEdicao] = useState<ErrosEdicao>({})

  function iniciarEdicao(ordem: OrdemProducao) {
    setOrdemEmEdicao(ordem)
    setPrazo(ordem.prazo ?? '')
    setPrioridade(ordem.prioridade ?? '')
    setErrosEdicao({})
    setMensagemErro('')
    setMensagemSucesso('')
  }

  function cancelarEdicao() {
    setOrdemEmEdicao(null)
    setPrazo('')
    setPrioridade('')
    setErrosEdicao({})
  }

  async function atualizarPrazoPrioridade(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setMensagemErro('')
    setMensagemSucesso('')

    const novosErros: ErrosEdicao = {}
    const hoje = dataAtualLocal()
    if (!prazo) novosErros.prazo = 'O prazo é obrigatório.'
    else if (prazo < hoje) novosErros.prazo = 'O prazo não pode estar no passado.'
    if (!['Baixa', 'Média', 'Alta'].includes(prioridade)) {
      novosErros.prioridade = 'Uma prioridade válida é obrigatória.'
    }
    setErrosEdicao(novosErros)
    if (Object.keys(novosErros).length > 0) {
      setMensagemErro('Revise o prazo e a prioridade antes de confirmar.')
      return
    }
    if (!ordemEmEdicao) return

    setSalvando(true)
    try {
      const response = await fetch(`${API_URL}/${ordemEmEdicao.id_ordem}`, {
        method: 'PUT',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prazo, prioridade }),
      })
      if (response.status === 404) {
        const data = await response.json() as { detail?: string }
        setMensagemErro(data.detail ?? 'Ordem de produção não encontrada.')
        return
      }
      if (response.status === 422) {
        const data = await response.json() as { detail?: Array<{ loc?: (string | number)[] }> }
        const campos = new Set((data.detail ?? []).map((erro) => String(erro.loc?.at(-1) ?? '')))
        const errosServidor: ErrosEdicao = {}
        if (campos.has('prazo')) errosServidor.prazo = 'Informe um prazo válido, igual ou posterior à data atual.'
        if (campos.has('prioridade')) errosServidor.prioridade = 'Selecione uma prioridade válida.'
        setErrosEdicao(errosServidor)
        setMensagemErro('Revise o prazo e a prioridade antes de confirmar.')
        return
      }
      if (!response.ok) {
        setMensagemErro('Não foi possível atualizar a ordem. Tente novamente.')
        return
      }
      const atualizada = await response.json() as OrdemProducao
      cancelarEdicao()
      setMensagemSucesso(`Prazo e prioridade da ordem ${atualizada.codigo} atualizados.`)
      await carregarDados()
    } catch {
      setMensagemErro('Não foi possível conectar ao servidor.')
    } finally {
      setSalvando(false)
    }
  }

  async function carregarDados() {
    setCarregando(true)
    try {
      const [responseOrdens, responseProdutos] = await Promise.all([
        fetch(API_URL, { credentials: 'include' }),
        fetch(PRODUTOS_URL, { credentials: 'include' }),
      ])
      if (!responseOrdens.ok || !responseProdutos.ok) {
        setMensagemErro('Não foi possível carregar as ordens ou os produtos. Confira sua sessão e tente novamente.')
        return
      }
      const [ordensData, produtosData] = await Promise.all([
        responseOrdens.json() as Promise<OrdemProducao[]>,
        responseProdutos.json() as Promise<Produto[]>,
      ])
      setOrdens(ordensData)
      setProdutos(produtosData.filter((produto) => produto.ativo))
    } catch {
      setMensagemErro('Não foi possível conectar ao servidor.')
    } finally {
      setCarregando(false)
    }
  }

  useEffect(() => {
    let ativa = true
    async function carregarInicial() {
      try {
        const [responseOrdens, responseProdutos] = await Promise.all([
          fetch(API_URL, { credentials: 'include' }),
          fetch(PRODUTOS_URL, { credentials: 'include' }),
        ])
        if (!responseOrdens.ok || !responseProdutos.ok) {
          if (ativa) setMensagemErro('Não foi possível carregar as ordens ou os produtos. Confira sua sessão e tente novamente.')
          return
        }
        const [ordensData, produtosData] = await Promise.all([
          responseOrdens.json() as Promise<OrdemProducao[]>,
          responseProdutos.json() as Promise<Produto[]>,
        ])
        if (ativa) {
          setOrdens(ordensData)
          setProdutos(produtosData.filter((produto) => produto.ativo))
        }
      } catch {
        if (ativa) setMensagemErro('Não foi possível conectar ao servidor.')
      } finally {
        if (ativa) setCarregando(false)
      }
    }
    void carregarInicial()
    return () => { ativa = false }
  }, [])

  function validarFormulario() {
    const novosErros: ErrosFormulario = {}
    if (!codigo.trim()) novosErros.codigo = 'Informe o código da ordem.'
    if (!produtoId) novosErros.produto_id = 'Selecione um produto.'
    if (!quantidade.trim()) {
      novosErros.quantidade = 'Informe a quantidade.'
    } else if (!Number.isFinite(Number(quantidade)) || Number(quantidade) <= 0) {
      novosErros.quantidade = 'A quantidade deve ser maior que zero.'
    } else {
      const casasDecimais = quantidade.split('.')[1]?.length ?? 0
      if (casasDecimais > 3) novosErros.quantidade = 'Informe no máximo três casas decimais.'
    }
    setErros(novosErros)
    return Object.keys(novosErros).length === 0
  }

  async function cadastrarOrdem(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setMensagemErro('')
    setMensagemSucesso('')
    if (!validarFormulario()) {
      setMensagemErro('Preencha os campos obrigatórios indicados antes de confirmar.')
      return
    }

    setSalvando(true)
    try {
      const response = await fetch(API_URL, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ codigo: codigo.trim(), produto_id: produtoId, quantidade: Number(quantidade) }),
      })
      if (response.status === 409 || response.status === 404) {
        const data = await response.json() as { detail?: string }
        setMensagemErro(data.detail ?? 'Não foi possível cadastrar a ordem.')
        return
      }
      if (response.status === 422) {
        const data = await response.json() as { detail?: Array<{ loc?: (string | number)[] }> }
        const campos = new Set((data.detail ?? []).map((erro) => String(erro.loc?.at(-1) ?? '')))
        const novosErros: ErrosFormulario = {}
        if (campos.has('codigo')) novosErros.codigo = 'Informe um código válido.'
        if (campos.has('produto_id')) novosErros.produto_id = 'Selecione um produto válido.'
        if (campos.has('quantidade')) novosErros.quantidade = 'Informe uma quantidade maior que zero, com até três casas decimais.'
        setErros(novosErros)
        setMensagemErro('Revise os campos obrigatórios da ordem de produção.')
        return
      }
      if (!response.ok) {
        setMensagemErro('Não foi possível cadastrar a ordem. Tente novamente.')
        return
      }
      const criada = await response.json() as OrdemProducao
      setCodigo('')
      setProdutoId('')
      setQuantidade('')
      setErros({})
      setMensagemSucesso(`Ordem ${criada.codigo} cadastrada e disponível para planejamento.`)
      await carregarDados()
    } catch {
      setMensagemErro('Não foi possível conectar ao servidor.')
    } finally {
      setSalvando(false)
    }
  }

  const produtoPorId = new Map<string, Produto>(
    produtos.map((produto): [string, Produto] => [produto.id_produto, produto]),
  )

  return (
    <main className="px-4 py-5 pt-[100px] sm:px-6 lg:px-7 xl:px-8">
      <div className="mx-auto max-w-[1500px] space-y-6">
        <section>
          <p className="text-sm font-semibold uppercase tracking-[0.16em] text-blue-700">Produção</p>
          <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-950">Ordens de produção</h1>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">Cadastre ordens vinculadas a produtos ativos para disponibilizá-las ao planejamento da produção.</p>
        </section>

        {mensagemErro && <p role="alert" className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{mensagemErro}</p>}
        {mensagemSucesso && <p role="status" className="rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800">{mensagemSucesso}</p>}

        <section className="grid gap-6 xl:grid-cols-[minmax(0,0.85fr)_minmax(0,1.15fr)]">
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm sm:p-7">
            <h2 className="text-lg font-semibold text-slate-900">Cadastrar ordem</h2>
            <p className="mt-1 text-sm text-slate-500">Os campos com * são obrigatórios.</p>
            <form className="mt-6 space-y-5" onSubmit={cadastrarOrdem} noValidate>
              <div>
                <label htmlFor="ordem-codigo" className="mb-1.5 block text-sm font-medium text-slate-700">Código *</label>
                <input id="ordem-codigo" name="codigo" value={codigo} maxLength={50} onChange={(event) => setCodigo(event.target.value)} aria-invalid={Boolean(erros.codigo)} aria-describedby={erros.codigo ? 'ordem-codigo-erro' : undefined} placeholder="Ex.: OP-001" className="w-full rounded-xl border border-slate-300 px-3.5 py-2.5 text-sm text-slate-900 outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-100" />
                {erros.codigo && <p id="ordem-codigo-erro" className="mt-1 text-sm text-red-700">{erros.codigo}</p>}
              </div>
              <div>
                <label htmlFor="ordem-produto" className="mb-1.5 block text-sm font-medium text-slate-700">Produto *</label>
                <select id="ordem-produto" name="produto_id" value={produtoId} onChange={(event) => setProdutoId(event.target.value)} aria-invalid={Boolean(erros.produto_id)} aria-describedby={erros.produto_id ? 'ordem-produto-erro' : undefined} className="w-full rounded-xl border border-slate-300 bg-white px-3.5 py-2.5 text-sm text-slate-900 outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-100">
                  <option value="">Selecione um produto</option>
                  {produtos.map((produto) => <option key={produto.id_produto} value={produto.id_produto}>{produto.codigo} — {produto.nome} ({produto.unidade})</option>)}
                </select>
                {erros.produto_id && <p id="ordem-produto-erro" className="mt-1 text-sm text-red-700">{erros.produto_id}</p>}
                {produtos.length === 0 && <p className="mt-1 text-sm text-amber-700">Cadastre um produto ativo antes de criar uma ordem.</p>}
              </div>
              <div>
                <label htmlFor="ordem-quantidade" className="mb-1.5 block text-sm font-medium text-slate-700">Quantidade *</label>
                <input id="ordem-quantidade" name="quantidade" type="number" min="0.001" step="0.001" value={quantidade} onChange={(event) => setQuantidade(event.target.value)} aria-invalid={Boolean(erros.quantidade)} aria-describedby={erros.quantidade ? 'ordem-quantidade-erro' : undefined} placeholder="Ex.: 120" className="w-full rounded-xl border border-slate-300 px-3.5 py-2.5 text-sm text-slate-900 outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-100" />
                {erros.quantidade && <p id="ordem-quantidade-erro" className="mt-1 text-sm text-red-700">{erros.quantidade}</p>}
              </div>
              <button type="submit" disabled={salvando || produtos.length === 0} className="inline-flex w-full items-center justify-center rounded-xl bg-blue-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60">{salvando ? 'Cadastrando...' : 'Cadastrar ordem'}</button>
            </form>
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm sm:p-7">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div><h2 className="text-lg font-semibold text-slate-900">Ordens cadastradas</h2><p className="mt-1 text-sm text-slate-500">Ordens registradas e disponíveis para planejamento.</p></div>
              <span className="rounded-full bg-slate-100 px-3 py-1 text-sm font-semibold text-slate-600">{ordens.length}</span>
            </div>
            {carregando ? (
              <p className="py-10 text-center text-sm text-slate-500">Carregando ordens...</p>
            ) : ordens.length === 0 ? (
              <div className="mt-6 rounded-xl border border-dashed border-slate-300 px-5 py-10 text-center"><p className="text-sm font-medium text-slate-700">Nenhuma ordem cadastrada.</p><p className="mt-1 text-sm text-slate-500">Preencha o formulário para cadastrar a primeira ordem.</p></div>
            ) : (
              <div className="mt-5 overflow-x-auto">
                <table className="w-full min-w-[500px] text-left text-sm">
                  <thead><tr className="border-b border-slate-200 text-xs uppercase tracking-wide text-slate-500"><th className="px-3 py-3 font-semibold">Ordem</th><th className="px-3 py-3 font-semibold">Produto</th><th className="px-3 py-3 font-semibold">Quantidade</th><th className="px-3 py-3 font-semibold">Prazo</th><th className="px-3 py-3 font-semibold">Prioridade</th><th className="px-3 py-3 font-semibold">Status</th><th className="px-3 py-3 font-semibold">Criada em</th><th className="px-3 py-3 font-semibold">Ações</th></tr></thead>
                  <tbody>{ordens.map((ordem) => {
                    const produto = produtoPorId.get(ordem.produto_id)
                    return <tr key={ordem.id_ordem} className="border-b border-slate-100 last:border-0"><td className="px-3 py-4 font-semibold text-slate-900">{ordem.codigo}</td><td className="px-3 py-4 text-slate-600">{produto ? `${produto.codigo} — ${produto.nome}` : 'Produto indisponível'}</td><td className="px-3 py-4 text-slate-600">{formatarQuantidade(ordem.quantidade)}{produto ? ` ${produto.unidade}` : ''}</td><td className="px-3 py-4 text-slate-600">{ordem.prazo ? formatarPrazo(ordem.prazo) : 'Não definido'}</td><td className="px-3 py-4 text-slate-600">{ordem.prioridade ?? 'Não definida'}</td><td className="px-3 py-4"><span className="inline-flex rounded-full bg-blue-50 px-2.5 py-1 text-xs font-semibold text-blue-700">{ordem.status}</span></td><td className="px-3 py-4 text-slate-600">{formatarData(ordem.criado_em)}</td><td className="px-3 py-4"><button type="button" onClick={() => iniciarEdicao(ordem)} className="font-semibold text-blue-700 hover:text-blue-900">Editar</button></td></tr>
                  })}</tbody>
                </table>
              </div>
            )}
            {ordemEmEdicao && (
              <form className="mt-6 space-y-4 rounded-xl border border-blue-200 bg-blue-50/50 p-4" onSubmit={atualizarPrazoPrioridade} noValidate>
                <h3 className="font-semibold text-slate-900">Editar prazo e prioridade — {ordemEmEdicao.codigo}</h3>
                <div className="grid gap-4 sm:grid-cols-2">
                  <div>
                    <label htmlFor="ordem-prazo" className="mb-1.5 block text-sm font-medium text-slate-700">Prazo *</label>
                    <input id="ordem-prazo" name="prazo" type="date" min={dataAtualLocal()} value={prazo} onChange={(event) => setPrazo(event.target.value)} aria-invalid={Boolean(errosEdicao.prazo)} aria-describedby={errosEdicao.prazo ? 'ordem-prazo-erro' : undefined} className="w-full rounded-xl border border-slate-300 bg-white px-3.5 py-2.5 text-sm text-slate-900 outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-100" />
                    {errosEdicao.prazo && <p id="ordem-prazo-erro" className="mt-1 text-sm text-red-700">{errosEdicao.prazo}</p>}
                  </div>
                  <div>
                    <label htmlFor="ordem-prioridade" className="mb-1.5 block text-sm font-medium text-slate-700">Prioridade *</label>
                    <select id="ordem-prioridade" name="prioridade" value={prioridade} onChange={(event) => setPrioridade(event.target.value)} aria-invalid={Boolean(errosEdicao.prioridade)} aria-describedby={errosEdicao.prioridade ? 'ordem-prioridade-erro' : undefined} className="w-full rounded-xl border border-slate-300 bg-white px-3.5 py-2.5 text-sm text-slate-900 outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-100">
                      <option value="">Selecione uma prioridade</option>
                      <option value="Baixa">Baixa</option>
                      <option value="Média">Média</option>
                      <option value="Alta">Alta</option>
                    </select>
                    {errosEdicao.prioridade && <p id="ordem-prioridade-erro" className="mt-1 text-sm text-red-700">{errosEdicao.prioridade}</p>}
                  </div>
                </div>
                <div className="flex flex-wrap gap-3">
                  <button type="submit" disabled={salvando} className="rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60">{salvando ? 'Salvando...' : 'Confirmar alteração'}</button>
                  <button type="button" onClick={cancelarEdicao} disabled={salvando} className="rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 hover:bg-slate-50 disabled:opacity-60">Cancelar</button>
                </div>
              </form>
            )}
          </div>
        </section>
      </div>
    </main>
  )
}

export default OrdensProducaoPage

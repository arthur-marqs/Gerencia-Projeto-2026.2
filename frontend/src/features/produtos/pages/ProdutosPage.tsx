import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'

type ErrosFormulario = {
  codigo?: string
  nome?: string
  unidade?: string
}

type Produto = {
  id_produto: string
  codigo: string
  nome: string
  unidade: string
  ativo: boolean
  criado_em: string
}

function ProdutosPage() {
  const [codigo, setCodigo] = useState('')
  const [nome, setNome] = useState('')
  const [unidade, setUnidade] = useState('')
  const [erros, setErros] = useState<ErrosFormulario>({})
  const [mensagemErro, setMensagemErro] = useState('')
  const [mensagemSucesso, setMensagemSucesso] = useState('')
  const [salvando, setSalvando] = useState(false)

  const [produtos, setProdutos] = useState<Produto[]>([])
  const [carregandoProdutos, setCarregandoProdutos] = useState(true)
  const [erroListagem, setErroListagem] = useState('')

  async function carregarProdutos() {
    setCarregandoProdutos(true)
    setErroListagem('')

    try {
      const response = await fetch('http://localhost:8000/api/produtos', {
        credentials: 'include',
      })

      if (!response.ok) {
        setErroListagem('Não foi possível carregar os produtos.')
        return
      }

      const data: Produto[] = await response.json()
      setProdutos(data)
    } catch {
      setErroListagem('Não foi possível conectar ao servidor.')
    } finally {
      setCarregandoProdutos(false)
    }
  }

  useEffect(() => {
    async function carregarProdutosIniciais() {
      try {
        const response = await fetch('http://localhost:8000/api/produtos', {
          credentials: 'include',
        })

        if (!response.ok) {
          setErroListagem('Não foi possível carregar os produtos.')
          return
        }

        const data: Produto[] = await response.json()
        setProdutos(data)
      } catch {
        setErroListagem('Não foi possível conectar ao servidor.')
      } finally {
        setCarregandoProdutos(false)
      }
    }

    void carregarProdutosIniciais()
  }, [])

  function validarFormulario() {
    const novosErros: ErrosFormulario = {}

    if (!codigo.trim()) {
      novosErros.codigo = 'Informe o código do produto.'
    }

    if (!nome.trim()) {
      novosErros.nome = 'Informe o nome do produto.'
    }

    if (!unidade.trim()) {
      novosErros.unidade = 'Informe a unidade do produto.'
    }

    setErros(novosErros)

    return Object.keys(novosErros).length === 0
  }

  async function cadastrarProduto(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()

    setMensagemErro('')
    setMensagemSucesso('')

    if (!validarFormulario()) {
      return
    }

    setSalvando(true)

    try {
      const response = await fetch('http://localhost:8000/api/produtos', {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          codigo,
          nome,
          unidade,
        }),
      })

      if (response.status === 409) {
        const data = await response.json()
        setMensagemErro(data.detail)
        return
      }

      if (!response.ok) {
        setMensagemErro('Não foi possível cadastrar o produto.')
        return
      }

      setCodigo('')
      setNome('')
      setUnidade('')
      setErros({})
      setMensagemSucesso('Produto cadastrado com sucesso.')

      await carregarProdutos()
    } catch {
      setMensagemErro('Não foi possível conectar ao servidor.')
    } finally {
      setSalvando(false)
    }
  }

  return (
    <main className="px-4 py-5 pt-[100px] sm:px-6 lg:px-7 xl:px-8">
      <div className="mx-auto max-w-[1500px]">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-slate-950">
            Produtos
          </h1>

          <p className="mt-1 text-sm text-slate-500">
            Cadastre e consulte os produtos utilizados na produção.
          </p>
        </div>

        <div className="grid gap-6 xl:grid-cols-[420px_1fr]">
          <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="mb-6">
              <h2 className="text-lg font-semibold text-slate-900">
                Novo produto
              </h2>

              <p className="mt-1 text-sm text-slate-500">
                Preencha os dados obrigatórios.
              </p>
            </div>

            <form
              className="space-y-5"
              onSubmit={cadastrarProduto}
              noValidate
            >
              <div>
                <label
                  htmlFor="codigo"
                  className="mb-2 block text-sm font-medium text-slate-700"
                >
                  Código
                </label>

                <input
                  id="codigo"
                  data-cy="produto-codigo"
                  type="text"
                  value={codigo}
                  onChange={(event) => setCodigo(event.target.value)}
                  placeholder="Ex.: PRD-001"
                  className="w-full rounded-xl border border-slate-300 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                />

                {erros.codigo && (
                  <p className="mt-1.5 text-sm text-red-600">
                    {erros.codigo}
                  </p>
                )}
              </div>

              <div>
                <label
                  htmlFor="nome"
                  className="mb-2 block text-sm font-medium text-slate-700"
                >
                  Nome
                </label>

                <input
                  id="nome"
                  data-cy="produto-nome"
                  type="text"
                  value={nome}
                  onChange={(event) => setNome(event.target.value)}
                  placeholder="Ex.: Tampa plástica"
                  className="w-full rounded-xl border border-slate-300 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                />

                {erros.nome && (
                  <p className="mt-1.5 text-sm text-red-600">
                    {erros.nome}
                  </p>
                )}
              </div>

              <div>
                <label
                  htmlFor="unidade"
                  className="mb-2 block text-sm font-medium text-slate-700"
                >
                  Unidade
                </label>

                <input
                  id="unidade"
                  data-cy="produto-unidade"
                  type="text"
                  value={unidade}
                  onChange={(event) => setUnidade(event.target.value)}
                  placeholder="Ex.: un"
                  className="w-full rounded-xl border border-slate-300 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                />

                {erros.unidade && (
                  <p className="mt-1.5 text-sm text-red-600">
                    {erros.unidade}
                  </p>
                )}
              </div>

              {mensagemErro && (
                <div
                  data-cy="produto-erro"
                  className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
                >
                  {mensagemErro}
                </div>
              )}

              {mensagemSucesso && (
                <div
                  data-cy="produto-sucesso"
                  className="rounded-xl border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-700"
                >
                  {mensagemSucesso}
                </div>
              )}

              <button
                data-cy="produto-salvar"
                type="submit"
                disabled={salvando}
                className="w-full cursor-pointer rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {salvando ? 'Salvando...' : 'Cadastrar produto'}
              </button>
            </form>
          </section>

          <section className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
            <div className="border-b border-slate-200 px-6 py-5">
              <h2 className="text-lg font-semibold text-slate-900">
                Produtos cadastrados
              </h2>

              <p className="mt-1 text-sm text-slate-500">
                Produtos disponíveis para utilização no planejamento.
              </p>
            </div>

            {carregandoProdutos ? (
              <div className="p-8 text-center text-sm text-slate-500">
                Carregando produtos...
              </div>
            ) : erroListagem ? (
              <div className="p-6">
                <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                  {erroListagem}
                </div>
              </div>
            ) : produtos.length === 0 ? (
              <div className="p-8 text-center">
                <p className="text-sm font-medium text-slate-700">
                  Nenhum produto cadastrado.
                </p>

                <p className="mt-1 text-sm text-slate-500">
                  Cadastre o primeiro produto usando o formulário ao lado.
                </p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table
                  data-cy="produtos-tabela"
                  className="w-full text-left text-sm"
                >
                  <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
                    <tr>
                      <th className="px-6 py-4 font-semibold">
                        Código
                      </th>

                      <th className="px-6 py-4 font-semibold">
                        Nome
                      </th>

                      <th className="px-6 py-4 font-semibold">
                        Unidade
                      </th>

                      <th className="px-6 py-4 font-semibold">
                        Status
                      </th>
                    </tr>
                  </thead>

                  <tbody className="divide-y divide-slate-100">
                    {produtos.map((produto) => (
                      <tr
                        key={produto.id_produto}
                        data-cy="produto-item"
                        className="text-slate-700"
                      >
                        <td className="px-6 py-4 font-semibold text-slate-900">
                          {produto.codigo}
                        </td>

                        <td className="px-6 py-4">
                          {produto.nome}
                        </td>

                        <td className="px-6 py-4">
                          {produto.unidade}
                        </td>

                        <td className="px-6 py-4">
                          <span
                            className={
                              produto.ativo
                                ? 'inline-flex rounded-full bg-green-50 px-2.5 py-1 text-xs font-semibold text-green-700'
                                : 'inline-flex rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-600'
                            }
                          >
                            {produto.ativo ? 'Ativo' : 'Inativo'}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>
        </div>
      </div>
    </main>
  )
}

export default ProdutosPage

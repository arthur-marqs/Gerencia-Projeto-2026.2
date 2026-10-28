import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'

type ErrosFormulario = {
  codigo?: string
  nome?: string
}

type Maquina = {
  id_maquina: string
  codigo: string
  nome: string
  descricao: string | null
  ativo: boolean
  criado_em: string
}

function MaquinasPage() {
  const [codigo, setCodigo] = useState('')
  const [nome, setNome] = useState('')
  const [descricao, setDescricao] = useState('')
  const [erros, setErros] = useState<ErrosFormulario>({})
  const [mensagemErro, setMensagemErro] = useState('')
  const [mensagemSucesso, setMensagemSucesso] = useState('')
  const [salvando, setSalvando] = useState(false)
  const [maquinas, setMaquinas] = useState<Maquina[]>([])
  const [carregando, setCarregando] = useState(true)
  const [erroListagem, setErroListagem] = useState('')
  const [maquinaEmEdicao, setMaquinaEmEdicao] = useState<string | null>(null)
  const [maquinaEmAcao, setMaquinaEmAcao] = useState<string | null>(null)

  async function carregarMaquinas() {
    setCarregando(true)
    setErroListagem('')

    try {
      const response = await fetch('http://localhost:8000/api/maquinas', {
        credentials: 'include',
      })

      if (!response.ok) {
        setErroListagem('Não foi possível carregar as máquinas.')
        return
      }

      const data: Maquina[] = await response.json()
      setMaquinas(data)
    } catch {
      setErroListagem('Não foi possível conectar ao servidor.')
    } finally {
      setCarregando(false)
    }
  }

  useEffect(() => {
    let ativa = true

    async function carregarMaquinasIniciais() {
      try {
        const response = await fetch('http://localhost:8000/api/maquinas', {
          credentials: 'include',
        })

        if (!response.ok) {
          if (ativa) {
            setErroListagem('Não foi possível carregar as máquinas.')
          }
          return
        }

        const data: Maquina[] = await response.json()

        if (ativa) {
          setMaquinas(data)
        }
      } catch {
        if (ativa) {
          setErroListagem('Não foi possível conectar ao servidor.')
        }
      } finally {
        if (ativa) {
          setCarregando(false)
        }
      }
    }

    void carregarMaquinasIniciais()

    return () => {
      ativa = false
    }
  }, [])

  function validarFormulario() {
    const novosErros: ErrosFormulario = {}

    if (!codigo.trim()) {
      novosErros.codigo = 'Informe o código da máquina.'
    }

    if (!nome.trim()) {
      novosErros.nome = 'Informe o nome da máquina.'
    }

    setErros(novosErros)
    return Object.keys(novosErros).length === 0
  }

  function cancelarEdicao() {
    setMaquinaEmEdicao(null)
    setCodigo('')
    setNome('')
    setDescricao('')
    setErros({})
    setMensagemErro('')
    setMensagemSucesso('')
  }

  function editarMaquina(maquina: Maquina) {
    setMaquinaEmEdicao(maquina.id_maquina)
    setCodigo(maquina.codigo)
    setNome(maquina.nome)
    setDescricao(maquina.descricao ?? '')
    setErros({})
    setMensagemErro('')
    setMensagemSucesso('')
  }

  async function salvarMaquina(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setMensagemErro('')
    setMensagemSucesso('')

    if (!validarFormulario()) {
      return
    }

    setSalvando(true)

    try {
      const endpoint = maquinaEmEdicao
        ? `http://localhost:8000/api/maquinas/${maquinaEmEdicao}`
        : 'http://localhost:8000/api/maquinas'
      const response = await fetch(endpoint, {
        method: maquinaEmEdicao ? 'PUT' : 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ codigo, nome, descricao }),
      })

      if (response.status === 409) {
        const data = await response.json()
        setMensagemErro(data.detail)
        return
      }

      if (response.status === 422) {
        const data = await response.json()
        const campos = new Set<string>(
          data.detail.flatMap((erro: { loc: string[] }) =>
            erro.loc.filter((campo) => campo === 'codigo' || campo === 'nome'),
          ),
        )
        const novosErros: ErrosFormulario = {}

        if (campos.has('codigo')) {
          novosErros.codigo = 'Informe um código válido para a máquina.'
        }

        if (campos.has('nome')) {
          novosErros.nome = 'Informe um nome válido para a máquina.'
        }

        setErros(novosErros)
        setMensagemErro('Revise os campos obrigatórios da máquina.')
        return
      }

      if (!response.ok) {
        setMensagemErro(
          maquinaEmEdicao
            ? 'Não foi possível atualizar a máquina.'
            : 'Não foi possível cadastrar a máquina.',
        )
        return
      }

      const estavaEditando = Boolean(maquinaEmEdicao)
      cancelarEdicao()
      setMensagemSucesso(
        estavaEditando
          ? 'Máquina atualizada com sucesso.'
          : 'Máquina cadastrada com sucesso.',
      )
      await carregarMaquinas()
    } catch {
      setMensagemErro('Não foi possível conectar ao servidor.')
    } finally {
      setSalvando(false)
    }
  }

  async function alterarStatus(maquina: Maquina) {
    const novoStatus = !maquina.ativo
    const confirmacao = novoStatus
      ? `Deseja ativar a máquina ${maquina.codigo}?`
      : `Deseja inativar a máquina ${maquina.codigo}? Ela não será disponibilizada para novos planejamentos.`
    if (!window.confirm(confirmacao)) {
      return
    }

    setMaquinaEmAcao(maquina.id_maquina)
    setMensagemErro('')
    setMensagemSucesso('')
    try {
      const response = await fetch(
        `http://localhost:8000/api/maquinas/${maquina.id_maquina}/status`,
        {
          method: 'PATCH',
          credentials: 'include',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ ativo: novoStatus }),
        },
      )
      if (!response.ok) {
        setMensagemErro(
          novoStatus
            ? 'Não foi possível ativar a máquina.'
            : 'Não foi possível inativar a máquina.',
        )
        return
      }

      setMensagemSucesso(
        novoStatus
          ? 'Máquina ativada com sucesso.'
          : 'Máquina inativada com sucesso.',
      )
      await carregarMaquinas()
    } catch {
      setMensagemErro('Não foi possível conectar ao servidor.')
    } finally {
      setMaquinaEmAcao(null)
    }
  }

  async function excluirMaquina(maquina: Maquina) {
    if (
      !window.confirm(
        `Deseja excluir definitivamente a máquina ${maquina.codigo}?`,
      )
    ) {
      return
    }

    setMaquinaEmAcao(maquina.id_maquina)
    setMensagemErro('')
    setMensagemSucesso('')
    try {
      const response = await fetch(
        `http://localhost:8000/api/maquinas/${maquina.id_maquina}`,
        { method: 'DELETE', credentials: 'include' },
      )
      if (response.status === 409) {
        const data = await response.json()
        setMensagemErro(data.detail)
        return
      }
      if (!response.ok) {
        setMensagemErro('Não foi possível excluir a máquina.')
        return
      }

      setMensagemSucesso('Máquina excluída com sucesso.')
      await carregarMaquinas()
    } catch {
      setMensagemErro('Não foi possível conectar ao servidor.')
    } finally {
      setMaquinaEmAcao(null)
    }
  }

  return (
    <main className="px-4 py-5 pt-[100px] sm:px-6 lg:px-7 xl:px-8">
      <div className="mx-auto max-w-[1500px]">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-slate-950">Máquinas</h1>
          <p className="mt-1 text-sm text-slate-500">
            Cadastre e consulte as máquinas utilizadas no planejamento da
            produção.
          </p>
        </div>

        <div className="grid gap-6 xl:grid-cols-[420px_1fr]">
          <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="mb-6">
              <h2 className="text-lg font-semibold text-slate-900">
                {maquinaEmEdicao ? 'Editar máquina' : 'Nova máquina'}
              </h2>
              <p className="mt-1 text-sm text-slate-500">
                Preencha o código e o nome obrigatórios.
              </p>
            </div>

            <form className="space-y-5" onSubmit={salvarMaquina} noValidate>
              <div>
                <label
                  htmlFor="maquina-codigo"
                  className="mb-2 block text-sm font-medium text-slate-700"
                >
                  Código
                </label>
                <input
                  id="maquina-codigo"
                  data-cy="maquina-codigo"
                  type="text"
                  value={codigo}
                  onChange={(event) => setCodigo(event.target.value)}
                  placeholder="Ex.: MAQ-001"
                  aria-invalid={Boolean(erros.codigo)}
                  className="w-full rounded-xl border border-slate-300 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                />
                {erros.codigo && (
                  <p className="mt-1.5 text-sm text-red-600">{erros.codigo}</p>
                )}
              </div>

              <div>
                <label
                  htmlFor="maquina-nome"
                  className="mb-2 block text-sm font-medium text-slate-700"
                >
                  Nome
                </label>
                <input
                  id="maquina-nome"
                  data-cy="maquina-nome"
                  type="text"
                  value={nome}
                  onChange={(event) => setNome(event.target.value)}
                  placeholder="Ex.: Cortadora"
                  aria-invalid={Boolean(erros.nome)}
                  className="w-full rounded-xl border border-slate-300 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                />
                {erros.nome && (
                  <p className="mt-1.5 text-sm text-red-600">{erros.nome}</p>
                )}
              </div>

              <div>
                <label
                  htmlFor="maquina-descricao"
                  className="mb-2 block text-sm font-medium text-slate-700"
                >
                  Descrição{' '}
                  <span className="font-normal text-slate-400">(opcional)</span>
                </label>
                <textarea
                  id="maquina-descricao"
                  data-cy="maquina-descricao"
                  value={descricao}
                  onChange={(event) => setDescricao(event.target.value)}
                  rows={3}
                  placeholder="Detalhes sobre a máquina"
                  className="w-full resize-y rounded-xl border border-slate-300 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                />
              </div>

              {mensagemErro && (
                <div
                  data-cy="maquina-erro"
                  role="alert"
                  className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
                >
                  {mensagemErro}
                </div>
              )}

              {mensagemSucesso && (
                <div
                  data-cy="maquina-sucesso"
                  role="status"
                  className="rounded-xl border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-700"
                >
                  {mensagemSucesso}
                </div>
              )}

              <button
                data-cy="maquina-salvar"
                type="submit"
                disabled={salvando}
                className="w-full cursor-pointer rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {salvando
                  ? 'Salvando...'
                  : maquinaEmEdicao
                    ? 'Salvar alterações'
                    : 'Cadastrar máquina'}
              </button>
              {maquinaEmEdicao && (
                <button
                  type="button"
                  onClick={cancelarEdicao}
                  className="w-full cursor-pointer rounded-xl border border-slate-300 px-5 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
                >
                  Cancelar edição
                </button>
              )}
            </form>
          </section>

          <section className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
            <div className="border-b border-slate-200 px-6 py-5">
              <h2 className="text-lg font-semibold text-slate-900">
                Máquinas cadastradas
              </h2>
              <p className="mt-1 text-sm text-slate-500">
                Consulte o status e gerencie a disponibilidade das máquinas.
              </p>
            </div>

            {carregando ? (
              <div className="p-8 text-center text-sm text-slate-500">
                Carregando máquinas...
              </div>
            ) : erroListagem ? (
              <div className="p-6">
                <div
                  role="alert"
                  className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
                >
                  {erroListagem}
                </div>
              </div>
            ) : maquinas.length === 0 ? (
              <div className="p-8 text-center">
                <p className="text-sm font-medium text-slate-700">
                  Nenhuma máquina cadastrada.
                </p>
                <p className="mt-1 text-sm text-slate-500">
                  Cadastre a primeira máquina usando o formulário ao lado.
                </p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table
                  data-cy="maquinas-tabela"
                  className="w-full text-left text-sm"
                >
                  <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
                    <tr>
                      <th className="px-6 py-4 font-semibold">Código</th>
                      <th className="px-6 py-4 font-semibold">Nome</th>
                      <th className="px-6 py-4 font-semibold">Descrição</th>
                      <th className="px-6 py-4 font-semibold">Status</th>
                      <th className="px-6 py-4 font-semibold">Ações</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {maquinas.map((maquina) => (
                      <tr
                        key={maquina.id_maquina}
                        data-cy="maquina-item"
                        className="text-slate-700"
                      >
                        <td className="px-6 py-4 font-semibold text-slate-900">
                          {maquina.codigo}
                        </td>
                        <td className="px-6 py-4">{maquina.nome}</td>
                        <td className="px-6 py-4">
                          {maquina.descricao || '—'}
                        </td>
                        <td className="px-6 py-4">
                          <span
                            className={
                              maquina.ativo
                                ? 'inline-flex rounded-full bg-green-50 px-2.5 py-1 text-xs font-semibold text-green-700'
                                : 'inline-flex rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-600'
                            }
                          >
                            {maquina.ativo ? 'Ativa' : 'Inativa'}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex flex-wrap gap-2">
                            <button
                              type="button"
                              onClick={() => editarMaquina(maquina)}
                              className="cursor-pointer rounded-lg border border-slate-300 px-3 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-50"
                            >
                              Editar
                            </button>
                            <button
                              type="button"
                              disabled={maquinaEmAcao === maquina.id_maquina}
                              onClick={() => void alterarStatus(maquina)}
                              className="cursor-pointer rounded-lg border border-blue-200 px-3 py-1.5 text-xs font-semibold text-blue-700 hover:bg-blue-50 disabled:opacity-50"
                            >
                              {maquina.ativo ? 'Inativar' : 'Ativar'}
                            </button>
                            <button
                              type="button"
                              disabled={maquinaEmAcao === maquina.id_maquina}
                              onClick={() => void excluirMaquina(maquina)}
                              className="cursor-pointer rounded-lg border border-red-200 px-3 py-1.5 text-xs font-semibold text-red-700 hover:bg-red-50 disabled:opacity-50"
                            >
                              Excluir
                            </button>
                          </div>
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

export default MaquinasPage

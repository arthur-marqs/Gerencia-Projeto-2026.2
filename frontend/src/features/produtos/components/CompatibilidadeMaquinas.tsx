
import { useEffect, useState } from 'react'

type Maquina = {
  id_maquina: string
  codigo: string
  nome: string
  descricao: string | null
  ativo: boolean
  criado_em: string
}

type CompatibilidadeResponse = {
  id_produto: string
  maquinas_compativeis: Maquina[]
  possui_maquina_compativel: boolean
}

type Props = {
  produtoId: string
  produtoNome: string
  produtoCodigo: string
  onClose: () => void
}

function CompatibilidadeMaquinas({
  produtoId,
  produtoNome,
  produtoCodigo,
  onClose,
}: Props) {
  const [maquinas, setMaquinas] = useState<Maquina[]>([])
  const [selecionadas, setSelecionadas] = useState<string[]>([])
  const [carregando, setCarregando] = useState(true)
  const [salvando, setSalvando] = useState(false)
  const [mensagemErro, setMensagemErro] = useState('')
  const [mensagemSucesso, setMensagemSucesso] = useState('')

  useEffect(() => {
    let ativo = true

    async function carregarDados() {
      try {
        const [responseMaquinas, responseCompatibilidade] =
          await Promise.all([
            fetch('http://localhost:8000/api/maquinas', {
              credentials: 'include',
            }),
            fetch(
              `http://localhost:8000/api/produtos/${produtoId}/maquinas`,
              { credentials: 'include' },
            ),
          ])

        if (!responseMaquinas.ok || !responseCompatibilidade.ok) {
          throw new Error()
        }

        const maquinasData: Maquina[] = await responseMaquinas.json()
        const compatibilidadeData: CompatibilidadeResponse =
          await responseCompatibilidade.json()

        if (!ativo) return

        setMaquinas(maquinasData)
        setSelecionadas(
          compatibilidadeData.maquinas_compativeis.map(
            (maquina) => maquina.id_maquina,
          ),
        )
      } catch {
        if (ativo) {
          setMensagemErro('Não foi possível carregar as compatibilidades.')
        }
      } finally {
        if (ativo) setCarregando(false)
      }
    }

    void carregarDados()

    return () => {
      ativo = false
    }
  }, [produtoId])

  function alternarMaquina(maquinaId: string) {
    setSelecionadas((atuais) =>
      atuais.includes(maquinaId)
        ? atuais.filter((id) => id !== maquinaId)
        : [...atuais, maquinaId],
    )

    setMensagemErro('')
    setMensagemSucesso('')
  }

  async function salvarCompatibilidades() {
    setSalvando(true)
    setMensagemErro('')
    setMensagemSucesso('')

    try {
      const response = await fetch(
        `http://localhost:8000/api/produtos/${produtoId}/maquinas`,
        {
          method: 'PUT',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            maquinas_ids: selecionadas,
          }),
        },
      )

      if (!response.ok) {
        const data = await response.json()
        setMensagemErro(
          typeof data.detail === 'string'
            ? data.detail
            : 'Não foi possível salvar as compatibilidades.',
        )
        return
      }

      const data: CompatibilidadeResponse = await response.json()

      setSelecionadas(
        data.maquinas_compativeis.map(
          (maquina) => maquina.id_maquina,
        ),
      )

      setMensagemSucesso('Compatibilidades salvas com sucesso.')
    } catch {
      setMensagemErro('Não foi possível conectar ao servidor.')
    } finally {
      setSalvando(false)
    }
  }

  const possuiMaquinaInativa = maquinas.some(
    (maquina) => !maquina.ativo && selecionadas.includes(maquina.id_maquina),
  )

  return (
    <div
      data-cy="compatibilidade-modal"
      className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/50 p-4"
    >
      <section
        role="dialog"
        aria-modal="true"
        aria-labelledby="compatibilidade-titulo"
        className="flex max-h-[90vh] w-full max-w-2xl flex-col overflow-hidden rounded-2xl bg-white shadow-2xl"
      >
        <div className="flex items-start justify-between gap-4 border-b border-slate-200 px-6 py-5">
          <div>
            <h2
              id="compatibilidade-titulo"
              className="text-lg font-semibold text-slate-900"
            >
              Máquinas compatíveis
            </h2>
            <p className="mt-1 text-sm text-slate-500">
              {produtoCodigo} — {produtoNome}
            </p>
          </div>

          <button
            type="button"
            onClick={onClose}
            disabled={salvando}
            aria-label="Fechar compatibilidade"
            className="cursor-pointer rounded-lg border border-slate-300 px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-50"
          >
            Fechar
          </button>
        </div>

        <div className="overflow-y-auto px-6 py-5">
          <p className="mb-5 text-sm text-slate-600">
            Selecione as máquinas que podem fabricar este produto.
          </p>

          {carregando ? (
            <p className="py-6 text-center text-sm text-slate-500">
              Carregando máquinas...
            </p>
          ) : (
            <div className="space-y-3">
              {maquinas.length === 0 && !mensagemErro ? (
                <p className="rounded-xl bg-slate-50 p-4 text-sm text-slate-500">
                  Nenhuma máquina cadastrada.
                </p>
              ) : (
                maquinas.map((maquina) => {
                  const selecionada = selecionadas.includes(maquina.id_maquina)

                  return (
                    <label
                      key={maquina.id_maquina}
                      className="flex cursor-pointer items-center gap-3 rounded-xl border border-slate-200 p-4 transition hover:bg-slate-50"
                    >
                      <input
                        type="checkbox"
                        data-cy={`compatibilidade-maquina-${maquina.id_maquina}`}
                        checked={selecionada}
                        disabled={
                          salvando || (!maquina.ativo && !selecionada)
                        }
                        onChange={() => alternarMaquina(maquina.id_maquina)}
                        className="h-4 w-4 accent-blue-600"
                      />

                      <div className="flex-1">
                        <p className="text-sm font-semibold text-slate-900">
                          {maquina.codigo} — {maquina.nome}
                        </p>
                        <p className="text-xs text-slate-500">
                          {maquina.ativo ? 'Ativa' : 'Inativa'}
                        </p>
                      </div>
                    </label>
                  )
                })
              )}

              {possuiMaquinaInativa && (
                <p className="text-sm text-amber-700">
                  Remova as máquinas inativas antes de salvar.
                </p>
              )}

              {!possuiMaquinaInativa && selecionadas.length === 0 && (
                <p className="text-sm text-slate-500">
                  Este produto está sem máquinas compatíveis.
                </p>
              )}
            </div>
          )}

          {mensagemErro && (
            <div
              role="alert"
              data-cy="compatibilidade-erro"
              className="mt-4 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700"
            >
              {mensagemErro}
            </div>
          )}

          {mensagemSucesso && (
            <div
              role="status"
              data-cy="compatibilidade-sucesso"
              className="mt-4 rounded-xl border border-green-200 bg-green-50 p-4 text-sm text-green-700"
            >
              {mensagemSucesso}
            </div>
          )}
        </div>

        <div className="flex flex-wrap justify-end gap-3 border-t border-slate-200 bg-slate-50 px-6 py-4">
          <button
            type="button"
            onClick={onClose}
            disabled={salvando}
            className="cursor-pointer rounded-xl border border-slate-300 bg-white px-5 py-2.5 text-sm font-semibold text-slate-700 hover:bg-slate-100 disabled:opacity-50"
          >
            Cancelar
          </button>

          <button
            type="button"
            data-cy="compatibilidade-salvar"
            onClick={() => void salvarCompatibilidades()}
            disabled={
              carregando ||
              salvando ||
              Boolean(mensagemErro && maquinas.length === 0) ||
              possuiMaquinaInativa
            }
            className="cursor-pointer rounded-xl bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {salvando ? 'Salvando...' : 'Salvar compatibilidade'}
          </button>
        </div>
      </section>
    </div>
  )
}

export default CompatibilidadeMaquinas

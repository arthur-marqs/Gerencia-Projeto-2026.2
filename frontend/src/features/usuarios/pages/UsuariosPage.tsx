import { useEffect, useState, type FormEvent } from 'react'

type Usuario = { id: string; nome: string; email: string; perfis: string[]; ativo: boolean }
type Formulario = { nome: string; email: string; senha: string; perfis: string[] }
type Acao = 'excluir' | 'desativar' | 'reativar'
type Erros = Record<string, string>
type Falha = { mensagem: string; campos: Erros; podeDesativar: boolean }

const API = 'http://localhost:8000/api/usuarios'
const PERFIS = ['ADMINISTRADOR', 'PLANEJADOR', 'OPERADOR']
const vazio = (): Formulario => ({ nome: '', email: '', senha: '', perfis: [] })
const inputClass = 'mt-1 w-full rounded-xl border border-slate-300 px-3 py-2 text-slate-900 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100'
const buttonClass = 'rounded-xl border border-slate-300 px-4 py-2 text-sm font-semibold hover:bg-slate-50 disabled:opacity-50'

async function lerFalha(response: Response): Promise<Falha> {
  const falha: Falha = { mensagem: 'Não foi possível concluir a operação.', campos: {}, podeDesativar: false }
  if (response.status === 401) falha.mensagem = 'Sua sessão expirou. Entre novamente.'
  if (response.status === 403) falha.mensagem = 'Somente administradores podem gerenciar usuários.'
  try {
    const { detail } = await response.json()
    if (typeof detail === 'string') falha.mensagem = detail
    else if (Array.isArray(detail)) {
      for (const erro of detail) {
        const campo = String(erro.loc?.[1] ?? '')
        falha.campos[campo] = campo === 'perfis' ? 'Selecione pelo menos um perfil válido.'
          : campo === 'senha' ? 'A senha deve ter pelo menos 8 caracteres.'
            : campo === 'nome' ? 'Informe um nome de 1 a 150 caracteres.' : 'Informe um e-mail válido de até 254 caracteres.'
      }
      falha.mensagem = 'Confira os campos indicados.'
    } else if (detail) {
      falha.campos = detail.campos ?? {}
      falha.mensagem = detail.mensagem ?? Object.values(falha.campos).join(' ')
      falha.podeDesativar = detail.pode_desativar === true
    }
  } catch { /* Mantém a mensagem correspondente ao status. */ }
  return falha
}

export default function UsuariosPage({ onSessionChange }: { onSessionChange: () => Promise<void> }) {
  const [usuarios, setUsuarios] = useState<Usuario[]>([])
  const [selecionado, setSelecionado] = useState<Usuario | null>(null)
  const [form, setForm] = useState<Formulario>(vazio)
  const [modo, setModo] = useState<'novo' | 'consulta' | 'edicao'>('novo')
  const [carregando, setCarregando] = useState(true)
  const [ocupado, setOcupado] = useState(false)
  const [erro, setErro] = useState('')
  const [campos, setCampos] = useState<Erros>({})
  const [sucesso, setSucesso] = useState('')
  const [confirmacao, setConfirmacao] = useState<Acao | null>(null)
  const [oferecerDesativacao, setOferecerDesativacao] = useState(false)

  useEffect(() => {
    let ativo = true
    async function carregar() {
      try {
        const response = await fetch(API, { credentials: 'include' })
        if (!response.ok) {
          const falha = await lerFalha(response)
          if (ativo) setErro(falha.mensagem)
          return
        }
        const lista = await response.json() as Usuario[]
        if (ativo) setUsuarios(lista)
      } catch {
        if (ativo) setErro('Não foi possível carregar os usuários.')
      } finally {
        if (ativo) setCarregando(false)
      }
    }
    void carregar()
    return () => { ativo = false }
  }, [])

  function limparAvisos() {
    setErro(''); setSucesso(''); setCampos({}); setOferecerDesativacao(false)
  }

  function preencher(usuario: Usuario) {
    setSelecionado(usuario)
    setForm({ nome: usuario.nome, email: usuario.email, perfis: usuario.perfis, senha: '' })
    setModo('consulta')
  }

  async function consultar(usuario: Usuario) {
    limparAvisos(); setOcupado(true)
    try {
      const response = await fetch(`${API}/${usuario.id}`, { credentials: 'include' })
      if (!response.ok) { setErro((await lerFalha(response)).mensagem); return }
      preencher(await response.json() as Usuario)
    } catch { setErro('Não foi possível consultar o usuário.') }
    finally { setOcupado(false) }
  }

  function atualizarLista(usuario: Usuario) {
    setUsuarios((atual) => [...atual.filter((item) => item.id !== usuario.id), usuario]
      .sort((a, b) => a.nome.localeCompare(b.nome, 'pt-BR')))
    preencher(usuario)
  }

  async function salvar(event: FormEvent) {
    event.preventDefault(); limparAvisos()
    const invalidos: Erros = {}
    if (!form.nome.trim() || form.nome.trim().length > 150) invalidos.nome = 'Informe um nome de 1 a 150 caracteres.'
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email.trim()) || form.email.trim().length > 254) invalidos.email = 'Informe um e-mail válido de até 254 caracteres.'
    if (form.perfis.length === 0) invalidos.perfis = 'Selecione pelo menos um perfil.'
    if ((modo === 'novo' || form.senha !== '') && form.senha.length < 8) invalidos.senha = 'A senha deve ter pelo menos 8 caracteres.'
    if (Object.keys(invalidos).length) { setCampos(invalidos); setErro('Confira os campos indicados.'); return }
    setOcupado(true)
    try {
      const response = await fetch(modo === 'novo' ? API : `${API}/${selecionado!.id}`, {
        method: modo === 'novo' ? 'POST' : 'PUT', credentials: 'include',
        headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(form),
      })
      if (!response.ok) {
        const falha = await lerFalha(response); setErro(falha.mensagem); setCampos(falha.campos); return
      }
      const usuario = await response.json() as Usuario
      setSucesso(modo === 'novo' ? 'Usuário cadastrado com sucesso.' : 'Usuário atualizado com sucesso.')
      atualizarLista(usuario)
      await onSessionChange()
    } catch { setErro('Não foi possível salvar o usuário. Tente novamente.') }
    finally { setOcupado(false) }
  }

  async function executarAcao() {
    if (!selecionado || !confirmacao) return
    const acao = confirmacao
    limparAvisos(); setOcupado(true)
    try {
      const response = await fetch(`${API}/${selecionado.id}${acao === 'excluir' ? '' : '/status'}`, {
        method: acao === 'excluir' ? 'DELETE' : 'PATCH', credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        ...(acao === 'excluir' ? {} : { body: JSON.stringify({ ativo: acao === 'reativar' }) }),
      })
      if (!response.ok) {
        const falha = await lerFalha(response)
        setErro(falha.mensagem); setOferecerDesativacao(falha.podeDesativar); return
      }
      if (acao === 'excluir') {
        setUsuarios((atual) => atual.filter((item) => item.id !== selecionado.id))
        setSelecionado(null); setForm(vazio()); setModo('novo')
      } else atualizarLista(await response.json() as Usuario)
      setSucesso(`Usuário ${acao === 'excluir' ? 'excluído' : acao === 'desativar' ? 'desativado' : 'reativado'} com sucesso.`)
      await onSessionChange()
    } catch { setErro('Não foi possível concluir a operação. Tente novamente.') }
    finally { setOcupado(false); setConfirmacao(null) }
  }

  const consulta = modo === 'consulta'
  return (
    <main className="space-y-6 px-4 pb-8 pt-[100px] sm:px-6 lg:px-8">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div><h1 className="text-3xl font-bold text-slate-950">Usuários</h1>
          <p className="mt-2 text-sm text-slate-500">Gerencie contas, situações e perfis de acesso ao SetupFlow.</p></div>
        <button data-cy="usuario-novo" className={buttonClass} disabled={ocupado} onClick={() => {
          limparAvisos(); setSelecionado(null); setForm(vazio()); setModo('novo')
        }}>Novo usuário</button>
      </div>
      {erro && <p data-cy="usuario-erro" role="alert" className="rounded-xl bg-red-50 p-4 text-red-700">{erro}</p>}
      {sucesso && <p data-cy="usuario-sucesso" role="status" className="rounded-xl bg-emerald-50 p-4 text-emerald-800">{sucesso}</p>}
      {oferecerDesativacao && selecionado && <button data-cy="usuario-oferecer-desativacao" disabled={ocupado} className={buttonClass}
        onClick={() => setConfirmacao('desativar')}>Desativar usuário</button>}
      <div className="grid items-start gap-6 xl:grid-cols-2">
        <section className="overflow-x-auto rounded-2xl border border-slate-200 bg-white p-6 shadow-sm" aria-label="Lista de usuários">
          <h2 className="mb-4 text-lg font-semibold">Usuários cadastrados</h2>
          {carregando ? <p>Carregando usuários...</p> : usuarios.length === 0 ? <p>Nenhum usuário cadastrado.</p> : (
            <table className="w-full text-left text-sm">
              <thead><tr className="border-b text-slate-500"><th className="py-3">Nome / E-mail</th><th>Perfis</th><th>Situação</th></tr></thead>
              <tbody>{usuarios.map((usuario) => <tr data-cy="usuario-linha" data-usuario-id={usuario.id} key={usuario.id} className={`border-b border-slate-100 ${selecionado?.id === usuario.id ? 'bg-blue-50' : ''}`}>
                <td className="py-4 pr-3"><button disabled={ocupado} className="text-left font-semibold text-blue-700 hover:underline" onClick={() => void consultar(usuario)}>{usuario.nome}</button>
                  <p className="mt-1 break-all text-xs text-slate-500">{usuario.email}</p></td>
                <td className="pr-3 text-xs">{usuario.perfis.join(', ')}</td>
                <td><span className={`rounded-full px-2 py-1 text-xs ${usuario.ativo ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-600'}`}>{usuario.ativo ? 'Ativo' : 'Inativo'}</span></td>
              </tr>)}</tbody>
            </table>
          )}
        </section>
        <section data-cy="usuario-detalhes" className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-semibold">{modo === 'novo' ? 'Cadastrar usuário' : consulta ? 'Dados do usuário' : 'Editar usuário'}</h2>
          {selecionado && <p className="mt-2 text-sm text-slate-500">Situação: {selecionado.ativo ? 'Ativo' : 'Inativo'}</p>}
          <form className="mt-5 space-y-5" noValidate onSubmit={(event) => void salvar(event)}>
            <fieldset disabled={ocupado || consulta} className="space-y-5 disabled:opacity-80">
              {(['nome', 'email'] as const).map((campo) => <div key={campo}>
                <label htmlFor={`usuario-${campo}`} className="text-sm font-medium">{campo === 'nome' ? 'Nome' : 'E-mail'} *</label>
                <input data-cy={`usuario-${campo}`} id={`usuario-${campo}`} name={campo} type={campo === 'email' ? 'email' : 'text'} autoComplete={campo === 'email' ? 'off' : 'name'}
                  value={form[campo]} maxLength={campo === 'nome' ? 150 : 254} required className={inputClass}
                  aria-invalid={Boolean(campos[campo])} aria-describedby={campos[campo] ? `erro-${campo}` : undefined}
                  onChange={(event) => setForm({ ...form, [campo]: event.target.value })} />
                {campos[campo] && <p id={`erro-${campo}`} className="mt-1 text-sm text-red-700">{campos[campo]}</p>}
              </div>)}
              {!consulta && <div><label htmlFor="usuario-senha" className="text-sm font-medium">{modo === 'novo' ? 'Senha inicial *' : 'Nova senha'}</label>
                <input data-cy="usuario-senha" id="usuario-senha" name="senha" type="password" autoComplete="new-password" value={form.senha} minLength={8} required={modo === 'novo'} className={inputClass}
                  aria-invalid={Boolean(campos.senha)} aria-describedby="ajuda-senha erro-senha" onChange={(event) => setForm({ ...form, senha: event.target.value })} />
                <p id="ajuda-senha" className="mt-1 text-xs text-slate-500">Mínimo de 8 caracteres.{modo === 'edicao' && ' Deixe em branco para manter a senha atual. Ao substituir, as sessões abertas serão encerradas.'}</p>
                {campos.senha && <p id="erro-senha" className="mt-1 text-sm text-red-700">{campos.senha}</p>}</div>}
              <fieldset aria-describedby={campos.perfis ? 'erro-perfis' : undefined}>
                <legend className="mb-2 text-sm font-medium">Perfis de acesso *</legend>
                {PERFIS.map((perfil) => <label key={perfil} className="mb-2 flex items-center gap-2 text-sm">
                  <input data-cy={`usuario-perfil-${perfil}`} type="checkbox" checked={form.perfis.includes(perfil)} onChange={(event) => setForm({ ...form,
                    perfis: event.target.checked ? [...form.perfis, perfil] : form.perfis.filter((p) => p !== perfil),
                  })} />{perfil === 'ADMINISTRADOR' ? 'Administrador' : perfil === 'PLANEJADOR' ? 'Planejador' : 'Operador'}
                </label>)}
                {campos.perfis && <p id="erro-perfis" className="text-sm text-red-700">{campos.perfis}</p>}
              </fieldset>
            </fieldset>
            <div className="flex flex-wrap gap-2">
              {!consulta && <button data-cy="usuario-salvar" disabled={ocupado} type="submit" className="rounded-xl bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-50">{ocupado ? 'Salvando...' : 'Salvar usuário'}</button>}
              {consulta && <button data-cy="usuario-editar" disabled={ocupado} type="button" className={buttonClass} onClick={() => { limparAvisos(); setModo('edicao') }}>Editar</button>}
              {modo === 'edicao' && <button data-cy="usuario-cancelar-edicao" disabled={ocupado} type="button" className={buttonClass} onClick={() => { limparAvisos(); preencher(selecionado!) }}>Cancelar edição</button>}
              {consulta && selecionado && <>
                <button data-cy="usuario-status" disabled={ocupado} type="button" className={buttonClass} onClick={() => setConfirmacao(selecionado.ativo ? 'desativar' : 'reativar')}>{selecionado.ativo ? 'Desativar' : 'Reativar'}</button>
                <button data-cy="usuario-excluir" disabled={ocupado} type="button" className={`${buttonClass} text-red-700`} onClick={() => setConfirmacao('excluir')}>Excluir</button>
              </>}
            </div>
          </form>
        </section>
      </div>
      {confirmacao && selecionado && <div className="fixed inset-0 z-50 grid place-items-center bg-slate-950/50 p-4">
        <section data-cy="usuario-confirmacao" role="dialog" aria-modal="true" aria-labelledby="confirmacao-titulo" aria-describedby="confirmacao-descricao" className="w-full max-w-md rounded-2xl bg-white p-6 shadow-xl">
          <h2 id="confirmacao-titulo" className="text-xl font-semibold">{confirmacao === 'excluir' ? 'Excluir' : confirmacao === 'desativar' ? 'Desativar' : 'Reativar'} usuário?</h2>
          <p className="mt-4 font-semibold">{selecionado.nome}</p><p className="break-all text-slate-600">{selecionado.email}</p>
          <p id="confirmacao-descricao" className="mt-4 text-sm text-slate-600">{confirmacao === 'excluir' ? 'A conta será removida permanentemente. Contas com vínculos de produção devem ser desativadas.' : confirmacao === 'desativar' ? 'As sessões serão encerradas e novos logins serão bloqueados. O histórico de produção será preservado.' : 'A conta poderá fazer um novo login. As sessões anteriores continuarão inválidas.'}</p>
          <div className="mt-6 flex justify-end gap-3">
            <button data-cy="usuario-cancelar" autoFocus disabled={ocupado} className={buttonClass} onClick={() => setConfirmacao(null)}>Cancelar</button>
            <button data-cy="usuario-confirmar" disabled={ocupado} className="rounded-xl bg-blue-600 px-4 py-2 text-sm font-semibold text-white disabled:opacity-50" onClick={() => void executarAcao()}>{ocupado ? 'Aguarde...' : 'Confirmar'}</button>
          </div>
        </section>
      </div>}
    </main>
  )
}

type SidebarProps = {
  perfis: string[]
  paginaAtiva: 'dashboard' | 'produtos' | 'maquinas'
  onNavegar: (pagina: 'dashboard' | 'produtos' | 'maquinas') => void
}

function Sidebar({
  perfis,
  paginaAtiva,
  onNavegar,
}: SidebarProps) {
  const podeGerenciarCadastros = perfis.includes('PLANEJADOR')

  function classeItem(ativo: boolean) {
    return [
      'flex w-full items-center rounded-lg px-4 py-2.5 text-left text-sm font-semibold transition-colors duration-200',
      ativo
        ? 'bg-blue-600 text-white hover:bg-blue-700'
        : 'text-slate-300 hover:bg-slate-800 hover:text-white',
    ].join(' ')
  }

  return (
    <aside className="fixed inset-y-0 left-0 hidden w-64 flex-col bg-slate-950 text-white lg:flex">
      <div className="flex h-20 items-center px-7">
        <img
          src="/images/setupflow-wordmark-branco.png"
          alt="SetupFlow"
          className="w-32 object-contain opacity-80"
        />
      </div>

      <nav className="flex-1 space-y-1 px-3 pt-2">
        <button
          type="button"
          onClick={() => onNavegar('dashboard')}
          className={classeItem(paginaAtiva === 'dashboard')}
        >
          Dashboard
        </button>

        {podeGerenciarCadastros && (
          <>
            <button
              type="button"
              data-cy="menu-produtos"
              onClick={() => onNavegar('produtos')}
              className={classeItem(paginaAtiva === 'produtos')}
            >
              Produtos
            </button>
            <button
              type="button"
              data-cy="menu-maquinas"
              onClick={() => onNavegar('maquinas')}
              className={classeItem(paginaAtiva === 'maquinas')}
            >
              Máquinas
            </button>
          </>
        )}
      </nav>
    </aside>
  )
}

export default Sidebar

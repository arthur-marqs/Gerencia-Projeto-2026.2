type Pagina = 'dashboard' | 'produtos' | 'familias' | 'maquinas'

type SidebarProps = {
  perfis: string[]
  paginaAtual: Pagina
  onNavigate: (pagina: Pagina) => void
}

function Sidebar({ perfis, paginaAtual, onNavigate }: SidebarProps) {
  const ehPlanejador = perfis.includes('PLANEJADOR')

  function classeItem(pagina: Pagina) {
    return [
      'flex w-full items-center rounded-lg px-4 py-2.5 text-left text-sm font-semibold transition-colors duration-200',
      paginaAtual === pagina
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

      <nav
        aria-label="Navegação principal"
        className="flex-1 space-y-1 px-3 pt-2"
      >
        <button
          type="button"
          aria-current={paginaAtual === 'dashboard' ? 'page' : undefined}
          onClick={() => onNavigate('dashboard')}
          className={classeItem('dashboard')}
        >
          Dashboard
        </button>

        {ehPlanejador && (
          <>
            <button
              type="button"
              data-cy="menu-produtos"
              aria-current={paginaAtual === 'produtos' ? 'page' : undefined}
              onClick={() => onNavigate('produtos')}
              className={classeItem('produtos')}
            >
              Produtos
            </button>
            <button
              type="button"
              aria-current={paginaAtual === 'familias' ? 'page' : undefined}
              onClick={() => onNavigate('familias')}
              className={classeItem('familias')}
            >
              Famílias de produtos
            </button>
            <button
              type="button"
              data-cy="menu-maquinas"
              aria-current={paginaAtual === 'maquinas' ? 'page' : undefined}
              onClick={() => onNavigate('maquinas')}
              className={classeItem('maquinas')}
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

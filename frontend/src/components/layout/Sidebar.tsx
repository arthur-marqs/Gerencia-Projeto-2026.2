type Pagina = 'dashboard' | 'familias'

type SidebarProps = {
  perfis: string[]
<<<<<<< Updated upstream
  paginaAtiva: 'dashboard' | 'produtos'
  onNavegar: (pagina: 'dashboard' | 'produtos') => void
}

function Sidebar({
  perfis,
  paginaAtiva,
  onNavegar,
}: SidebarProps) {
  const podeGerenciarProdutos = perfis.includes('PLANEJADOR')

  function classeItem(ativo: boolean) {
    return [
      'flex w-full items-center rounded-lg px-4 py-2.5 text-left text-sm font-semibold transition-colors duration-200',
      ativo
        ? 'bg-blue-600 text-white hover:bg-blue-700'
        : 'text-slate-300 hover:bg-slate-800 hover:text-white',
    ].join(' ')
  }
=======
  paginaAtual: Pagina
  onNavigate: (pagina: Pagina) => void
}

function Sidebar({ perfis, paginaAtual, onNavigate }: SidebarProps) {
  const ehPlanejador = perfis.includes('PLANEJADOR')

  const classeItem = (pagina: Pagina) =>
    `flex w-full items-center rounded-lg px-4 py-2.5 text-left text-sm font-semibold transition-colors duration-200 ${
      paginaAtual === pagina
        ? 'bg-blue-600 text-white hover:bg-blue-700'
        : 'text-slate-300 hover:bg-slate-800 hover:text-white'
    }`
>>>>>>> Stashed changes

  return (
    <aside className="fixed inset-y-0 left-0 hidden w-64 flex-col bg-slate-950 text-white lg:flex">
      <div className="flex h-20 items-center px-7">
        <img
          src="/images/setupflow-wordmark-branco.png"
          alt="SetupFlow"
          className="w-32 object-contain opacity-80"
        />
      </div>

<<<<<<< Updated upstream
      <nav className="flex-1 space-y-1 px-3 pt-2">
        <button
          type="button"
          onClick={() => onNavegar('dashboard')}
          className={classeItem(paginaAtiva === 'dashboard')}
=======
      <nav aria-label="Navegação principal" className="flex-1 space-y-1 px-3 pt-2">
        <button
          type="button"
          aria-current={paginaAtual === 'dashboard' ? 'page' : undefined}
          onClick={() => onNavigate('dashboard')}
          className={classeItem('dashboard')}
>>>>>>> Stashed changes
        >
          Dashboard
        </button>

<<<<<<< Updated upstream
        {podeGerenciarProdutos && (
          <button
            type="button"
            data-cy="menu-produtos"
            onClick={() => onNavegar('produtos')}
            className={classeItem(paginaAtiva === 'produtos')}
          >
            Produtos
=======
        {ehPlanejador && (
          <button
            type="button"
            aria-current={paginaAtual === 'familias' ? 'page' : undefined}
            onClick={() => onNavigate('familias')}
            className={classeItem('familias')}
          >
            Famílias de produtos
>>>>>>> Stashed changes
          </button>
        )}
      </nav>
    </aside>
  )
}

export default Sidebar

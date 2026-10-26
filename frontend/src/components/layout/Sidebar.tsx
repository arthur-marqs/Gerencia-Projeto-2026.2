type SidebarProps = {
  perfis: string[]
}

function Sidebar({
  perfis,
}: SidebarProps) {
  const ehPlanejador = perfis.includes('PLANEJADOR')
  const ehOperador = perfis.includes('OPERADOR')

  return (
    <aside className="fixed inset-y-0 left-0 hidden w-64 flex-col bg-slate-950 text-white lg:flex">
      <div className="flex h-20 items-center px-7">
        <img
          src="/images/setupflow-wordmark-branco.png"
          alt="SetupFlow"
          className="w-32 object-contain opacity-80"
        />
      </div>

      <nav className="flex-1 px-3 pt-2">
        <button
          type="button"
          className="flex w-full items-center rounded-lg bg-blue-600 px-4 py-2.5 text-left text-sm font-semibold text-white transition-colors duration-200 hover:bg-blue-700"
        >
          Dashboard
        </button>

        {/*
          FUTURAMENTE:

          {ehPlanejador && (
            <>
              Máquinas
              Produtos
              Famílias
              Ordens
              Sequenciamento
            </>
          )}

          {ehOperador && (
            <>
              Funcionalidades do operador
            </>
          )}
        */}

        {ehPlanejador && null}
        {ehOperador && null}
      </nav>
    </aside>
  )
}

export default Sidebar

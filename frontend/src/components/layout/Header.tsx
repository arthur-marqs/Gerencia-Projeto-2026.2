type HeaderProps = {
    nome: string
    perfis: string[]
    onLogout: () => void
}

function ProfileIcon() {
    return (
        <svg
            className="size-4"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            viewBox="0 0 24 24"
        >
            <circle cx="12" cy="8" r="4" />
            <path d="M4 21a8 8 0 0 1 16 0" />
        </svg>
    )
}

function LogoutIcon() {
    return (
        <svg
            className="size-4"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            viewBox="0 0 24 24"
        >
            <path d="M10 17l5-5-5-5" />
            <path d="M15 12H3" />
            <path d="M21 19V5a2 2 0 0 0-2-2h-6" />
        </svg>
    )
}

function ChevronDownIcon() {
    return (
        <svg
            className="size-4"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            viewBox="0 0 24 24"
        >
            <path d="m6 9 6 6 6-6" />
        </svg>
    )
}

function Header({ nome, onLogout }: HeaderProps) {
    const initials = nome
        .split(' ')
        .map((part) => part[0])
        .join('')
        .slice(0, 2)
        .toUpperCase()

    return (
        <header className="fixed top-0 right-0 z-30 h-20 border-b border-slate-200 bg-white/95 backdrop-blur lg:left-64">
            <div className="flex h-full items-center justify-end px-5 sm:px-7 lg:px-8">
                <div className="group relative">
                    <button
                        type="button"
                        className="flex items-center gap-3 rounded-xl px-3 py-2 transition-colors hover:bg-slate-100"
                    >
                        <div className="flex size-10 items-center justify-center rounded-full bg-blue-100 text-sm font-bold text-blue-700">
                            {initials}
                        </div>

                        <div className="hidden text-left sm:block">
                            <p className="max-w-44 truncate text-sm font-semibold text-slate-900">
                                {nome}
                            </p>
                        </div>

                        <span className="hidden text-slate-400 transition-transform duration-200 group-hover:rotate-180 sm:block">
                            <ChevronDownIcon />
                        </span>
                    </button>

                    <div className="invisible absolute right-0 top-full z-50 mt-2 w-52 translate-y-1 rounded-xl border border-slate-200 bg-white p-2 opacity-0 shadow-lg transition-all duration-150 group-hover:visible group-hover:translate-y-0 group-hover:opacity-100">
                        <button
                            type="button"
                            className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-left text-sm font-medium text-slate-700 transition-colors hover:bg-slate-100"
                        >
                            <ProfileIcon />
                            Meu perfil
                        </button>

                        <div className="my-1 h-px bg-slate-100" />

                        <button
                            type="button"
                            onClick={onLogout}
                            className="flex w-full cursor-pointer items-center gap-3 rounded-lg px-3 py-2.5 text-left text-sm font-medium text-red-600 transition-all duration-150 hover:bg-red-50 hover:text-red-700"
                        >
                            <LogoutIcon />
                            Sair
                        </button>
                    </div>
                </div>
            </div>
        </header>
    )
}

export default Header

const api = 'http://localhost:8000/api'
const identidade = api + '/auth/me'
const login = api + '/auth/login'
const nav = 'nav[aria-label="Navegação principal"]'

function prepararSessao() {
  cy.task('bug005:seed').then(({ usuarios }) => {
    cy.env(['fixturePassword'], { log: false }).then(({ fixturePassword }) => {
      cy.request({
        method: 'POST', url: login, log: false,
        body: { email: usuarios.ana.email, password: fixturePassword },
      }).its('status').should('eq', 200)
    })
  })
  cy.visit('/')
  cy.get(nav).should('be.visible')
  cy.request({url: identidade, log: false}).its('status').should('eq', 200)
}

function induzirFalhaNaAbertura() {
  cy.intercept({ method: 'GET', url: '**/api/auth/me', times: 1 }, { statusCode: 503 }).as('falhaNaAbertura')
  cy.reload()
  cy.wait('@falhaNaAbertura').its('response.statusCode').should('eq', 503)
  cy.contains('[role="alert"]', 'Não foi possível verificar a sessão.').should('be.visible')
  cy.get('[data-cy="login-email"]').should('not.exist')
  cy.get(nav).should('not.exist')
  cy.intercept('POST', '**/api/auth/login').as('novoLogin')
}

it('BUG-005 — recupera a sessão real após 503 inicial sem novo login ou recarga', () => {
  prepararSessao()
  induzirFalhaNaAbertura()
  cy.screenshot('503-aviso-e-retry')
  cy.request({url: identidade, log: false}).its('status').should('eq', 200)
  let recarregou = false
  cy.window().then(win => win.addEventListener('beforeunload', () => { recarregou = true }))
  cy.intercept('GET', '**/api/auth/me').as('identidadeReal')
  cy.contains('button', 'Tentar novamente').click()
  cy.wait('@identidadeReal').its('response.statusCode').should('eq', 200)
  cy.contains('h1', 'Bem-vindo, Ana E2E.').should('be.visible')
  cy.get(nav).should('be.visible')
  cy.get('@novoLogin.all').should('have.length', 0)
  cy.then(() => expect(recarregou).to.equal(false))
  cy.screenshot('200-painel-sem-novo-login')
})

it('BUG-005 — mostra login quando o retry recebe 401 para a sessão expirada no banco', () => {
  prepararSessao()
  induzirFalhaNaAbertura()
  cy.task('bug005:expirar').should('eq', 'UPDATE 1')
  cy.getCookie('setupflow_session', {log: false}).should('exist')
  cy.intercept('GET', '**/api/auth/me').as('identidadeReal')
  cy.contains('button', 'Tentar novamente').click()
  cy.wait('@identidadeReal').its('response.statusCode').should('eq', 401)
  cy.contains('h2', 'Acesse sua conta').should('be.visible')
  cy.get(nav).should('not.exist')
  cy.get('@novoLogin.all').should('have.length', 0)
  cy.screenshot('401-login')
})

it('Driver06 — uma identidade 200 atrasada não restaura o painel após recusa real', () => {
  prepararSessao()
  let entregarIdentidade
  cy.window().then(win => {
    const fetchReal = win.fetch.bind(win)
    // Simula uma resposta já em trânsito, entregue mesmo após o cancelamento.
    cy.stub(win, 'fetch').callsFake((entrada, opcoes) => {
      if (entrada !== identidade) return fetchReal(entrada, opcoes)
      return new Promise(resolve => {
        entregarIdentidade = () => resolve(new win.Response(JSON.stringify({
          usuario: { nome: 'Identidade atrasada', perfis: ['PLANEJADOR'] },
        }), { status: 200 }))
      })
    })
    win.dispatchEvent(new win.Event('focus'))
  })
  cy.wrap(null).should(() => expect(entregarIdentidade).to.be.a('function'))
  cy.task('bug005:expirar').should('eq', 'UPDATE 1')
  cy.intercept('GET', '**/api/families').as('familiasRejeitadas')
  cy.contains('nav button', 'Famílias de produtos').click()
  cy.wait('@familiasRejeitadas').its('response.statusCode').should('eq', 401)
  cy.contains('h2', 'Acesse sua conta').should('be.visible')
  cy.then(() => entregarIdentidade())
  cy.contains('h2', 'Acesse sua conta').should('be.visible')
  cy.get(nav).should('not.exist')
})

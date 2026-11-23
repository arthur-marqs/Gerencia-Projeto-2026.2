// Investigação adicional de falhas de identidade e resposta antiga em voo.
describe('QA Driver06: identidade em voo durante 401', () => {
  for (const modulo of ['Famílias de produtos', 'Máquinas']) {
    for (const falha of ['503', 'rede', 'tardia200']) {
      it(`${modulo}: login após 401 com identidade ${falha}`, () => {
        let sincronizando = false
        let liberar: (() => void) | undefined
        cy.intercept('GET', '**/api/auth/me', req => {
          if (!sincronizando) {
            req.reply({ statusCode: 200, body: { usuario: { nome: 'QA', perfis: ['PLANEJADOR'] } } })
            return
          }
          req.alias = 'identidadeEmVoo'
          return new Cypress.Promise<void>(resolve => {
            liberar = () => {
              if (falha === 'rede') req.destroy()
              else req.reply({ statusCode: falha === '503' ? 503 : 200, delay: 150,
                body: falha === '503' ? { detail: 'Indisponível' } : { usuario: { nome: 'QA', perfis: ['PLANEJADOR'] } } })
              resolve()
            }
          })
        })
        const rota = modulo === 'Máquinas' ? 'maquinas' : 'families'
        cy.intercept('GET', `**/api/${rota}`, { statusCode: 401, body: { detail: 'Sessão inválida ou expirada.' } }).as('protegida')
        cy.viewport(1280, 800)
        cy.visit('/')
        cy.get('nav').should('be.visible')
        cy.window().then(win => { sincronizando = true; win.dispatchEvent(new Event('focus')) })
        cy.wrap(null).should(() => expect(liberar).to.be.a('function'))
        cy.contains('nav button', modulo).click()
        cy.wait('@protegida').its('response.statusCode').should('eq', 401)
        cy.contains('h2', 'Acesse sua conta').should('be.visible')
        cy.then(() => liberar!())
        cy.wait('@identidadeEmVoo').then(result => {
          if (falha !== 'rede') expect(result.response?.statusCode).to.eq(falha === '503' ? 503 : 200)
          else expect(result.error).to.exist
        })
        cy.contains('h2', 'Acesse sua conta').should('be.visible')
        cy.get('nav[aria-label="Navegação principal"]').should('not.exist')
      })
    }
  }
})

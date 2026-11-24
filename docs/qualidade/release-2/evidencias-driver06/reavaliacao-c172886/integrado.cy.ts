// QA adicional: navegador, API e banco reais. Intercept apenas observa o transporte.
describe('Driver06 integrado', () => {
  for (const estado of ['expirar', 'invalidar']) {
    it(`sessão válida, ${estado}, negar acesso, login e acesso novamente`, () => {
      cy.task('prepararQA', 'reset')
      cy.intercept('GET', '**/api/families').as('familias')
      cy.intercept('POST', '**/api/auth/login').as('login')
      cy.viewport(1280, 800)
      cy.visit('/')
      const entrar = () => {
        cy.get('[data-cy="login-email"]').type('ana.e2e@example.com')
        cy.get('input[type="password"]').type('SenhaE2E!2026', { log: false })
        cy.contains('button', 'Entrar').click()
        cy.wait('@login').its('response.statusCode').should('eq', 200)
        cy.get('nav').should('be.visible')
      }
      entrar()
      cy.contains('nav button', 'Famílias de produtos').click()
      cy.wait('@familias').its('response.statusCode').should('eq', 200)
      cy.contains('h2', 'Famílias cadastradas').should('be.visible')
      cy.task('prepararQA', estado).its('sessoes_alteradas').should('be.greaterThan', 0)
      cy.intercept('GET', '**/api/families').as('familiasNegada')
      cy.contains('button', 'Atualizar lista').click()
      cy.wait('@familiasNegada').its('response.statusCode').should('eq', 401)
      cy.contains('h2', 'Acesse sua conta').should('be.visible')
      cy.get('nav').should('not.exist')
      cy.screenshot(estado + '-login-real', { capture: 'viewport' })
      entrar()
      cy.contains('nav button', 'Famílias de produtos').click()
      cy.wait('@familias').its('response.statusCode').should('eq', 200)
      cy.contains('h2', 'Famílias cadastradas').should('be.visible')
    })
  }
})

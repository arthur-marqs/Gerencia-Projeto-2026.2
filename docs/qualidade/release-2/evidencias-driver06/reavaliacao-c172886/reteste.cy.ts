// Reteste dos mesmos quatro comportamentos de QA, sem exigir reconsulta removida pela correção.
describe('Reteste BUG002', () => {
  for (const modulo of [
    { nome: 'Famílias de produtos', rota: 'families' },
    { nome: 'Máquinas', rota: 'maquinas' },
  ]) {
    it(`deve solicitar autenticação após 401 em ${modulo.nome}, mesmo se /me retornar 503`, () => {
      let rejeitada = false
      cy.intercept('GET', '**/api/auth/me', req => {
        req.reply(rejeitada
          ? { statusCode: 503, body: { detail: 'Indisponibilidade temporária' } }
          : { statusCode: 200, body: { usuario: { nome: 'QA Driver06', perfis: ['PLANEJADOR'] } } })
      })
      cy.intercept('GET', `**/api/${modulo.rota}`, req => {
        rejeitada = true
        req.reply({ statusCode: 401, body: { detail: 'Sessão inválida ou expirada.' } })
      }).as('protegida')
      cy.viewport(1280, 800)
      cy.visit('/')
      cy.contains('nav button', modulo.nome).click()
      cy.wait('@protegida').its('response.statusCode').should('eq', 401)
      // A correção encerra o estado autenticado sem precisar consultar /me.
      // Preservar a asserção funcional; não exigir que a reconsulta exista.
      cy.contains('h2', 'Acesse sua conta', { timeout: 3000 }).should('be.visible')
      cy.get('nav[aria-label="Navegação principal"]').should('not.exist')
      cy.get('input[type="email"]').should('be.visible')
      cy.screenshot(modulo.rota + '-login-apos-401', { capture: 'viewport' })
    })
  }
  for (const status of [403, 500]) {
    it(`preserva sessão quando somente a funcionalidade retorna ${status}`, () => {
      cy.intercept('GET', '**/api/auth/me', {
        statusCode: 200, body: { usuario: { nome: 'QA Driver06', perfis: ['PLANEJADOR'] } },
      })
      cy.intercept('GET', '**/api/maquinas', { statusCode: status, body: { detail: 'Falha de QA' } }).as('protegida')
      cy.viewport(1280, 800)
      cy.visit('/')
      cy.contains('nav button', 'Máquinas').click()
      cy.wait('@protegida')
      cy.get('nav').should('be.visible')
      cy.get('input[type="email"]').should('not.exist')
    })
  }
})

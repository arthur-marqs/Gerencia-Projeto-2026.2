
import { Given, Then } from '@badeball/cypress-cucumber-preprocessor'

Given('que o usuário acessa o SetupFlow', () => {
  cy.intercept('GET', 'http://localhost:8000/api/auth/me', {
    statusCode: 401,
    body: { detail: 'Não autenticado' },
  })

  cy.visit('/')
})

Then('a tela de login deve ser exibida', () => {
  cy.contains('h2', 'Acesse sua conta').should('be.visible')

  cy.get('input[type="email"]').should('be.visible')
  cy.get('input[type="password"]').should('be.visible')

  cy.get('button[type="submit"]')
    .contains('Entrar')
    .should('be.visible')
})

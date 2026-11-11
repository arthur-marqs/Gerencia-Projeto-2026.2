
import {
  Given,
  When,
  Then,
} from '@badeball/cypress-cucumber-preprocessor'

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
  cy.get('button[type="submit"]').should('contain', 'Entrar')
})

When('ele tenta entrar sem preencher os campos', () => {
  cy.get('button[type="submit"]').click()
})

When('ele informa o e-mail {string} e a senha {string}', (email: string, senha: string) => {
  cy.get('input[type="email"]').type(email)
  cy.get('input[type="password"]').type(senha)
})

When('ele informa o e-mail {string}', (email: string) => {
  cy.get('input[type="email"]').type(email)
})

When('tenta entrar no sistema', () => {
  cy.get('button[type="submit"]').click()
})

Then('deve aparecer a mensagem {string}', (mensagem: string) => {
  cy.contains('[role="alert"]', mensagem).should('be.visible')
})


When('a API rejeita as credenciais', () => {
  cy.intercept('POST', 'http://localhost:8000/api/auth/login', {
    statusCode: 401,
    body: { detail: 'Credenciais inválidas.' },
  }).as('loginInvalido')
})

Then('deve aparecer o erro de autenticação {string}', (mensagem: string) => {
  cy.wait('@loginInvalido')
  cy.contains('[role="status"]', mensagem).should('be.visible')
})

const { defineConfig } = require('cypress')
const createBundler = require('@bahmutov/cypress-esbuild-preprocessor')
const { addCucumberPreprocessorPlugin } = require('@badeball/cypress-cucumber-preprocessor')
const { createEsbuildPlugin } = require('@badeball/cypress-cucumber-preprocessor/esbuild')
const { execFile } = require('node:child_process')
const { promisify } = require('node:util')
const path = require('node:path')

const executar = promisify(execFile)
const backend = path.resolve(__dirname, '../backend')
const api = process.env.E2E_API_URL || 'http://localhost:8000'
const artifacts = process.env.E2E_ARTIFACTS_DIR || 'artifacts/cypress/local'

async function prepararBanco(modo = 'normal') {
  const container = process.env.E2E_SEED_CONTAINER
  const comando = container ? 'docker' : (process.env.E2E_PYTHON || 'python')
  const argumentos = container
    ? ['exec', container, 'python', '-m', 'scripts.seed_e2e', modo]
    : ['-m', 'scripts.seed_e2e', modo]
  const { stdout } = await executar(comando, argumentos, { cwd: backend, timeout: 60_000 })
  return JSON.parse(stdout)
}

async function requisitarSessao({ caminho, token }) {
  if (!['/api/auth/me', '/api/produtos'].includes(caminho)) {
    throw new Error('Rota de verificação de sessão não permitida no task de teste.')
  }
  const resposta = await fetch(api + caminho, { headers: { Cookie: `setupflow_session=${token}` } })
  return { status: resposta.status, corpo: await resposta.json() }
}

module.exports = defineConfig({
  viewportWidth: 1440,
  viewportHeight: 1000,
  video: true,
  screenshotOnRunFailure: true,
  screenshotsFolder: `${artifacts}/screenshots`,
  videosFolder: `${artifacts}/videos`,
  downloadsFolder: `${artifacts}/downloads`,
  reporter: 'junit',
  reporterOptions: { mochaFile: `${artifacts}/junit/results-[hash].xml`, toConsole: true },
  e2e: {
    baseUrl: 'http://localhost:5173',
    specPattern: 'cypress/e2e/usuarios.feature',
    supportFile: 'cypress/support/e2e.js',
    testIsolation: true,
    async setupNodeEvents(on, config) {
      // Cypress 16 e preprocessor 28 usam expose para opções públicas de BDD.
      // Credenciais e URL do banco ficam apenas no processo Node/Python.
      config.expose = {
        ...config.expose,
        tags: process.env.E2E_TAGS || config.expose?.tags || '@regressao and not @wip',
        jsonOutput: path.join(artifacts, 'cucumber-report.json'),
        htmlOutput: path.join(artifacts, 'cucumber-report.html'),
      }
      await addCucumberPreprocessorPlugin(on, config)
      on('file:preprocessor', createBundler({ plugins: [createEsbuildPlugin(config)] }))
      on('before:browser:launch', (browser, options) => {
        if (browser.name === 'electron') {
          options.preferences.width = 1600
          options.preferences.height = 1200
        } else if (browser.family === 'chromium') {
          options.args.push('--window-size=1600,1200', '--force-device-scale-factor=1')
        }
        return options
      })
      on('task', {
        'e2e:reset': prepararBanco,
        'e2e:bootstrap': () => prepararBanco('bootstrap'),
        'e2e:inspect': () => prepararBanco('inspecionar'),
        'e2e:session': requisitarSessao,
        async 'e2e:credentials'({ email, senha }) {
          const resposta = await fetch(`${api}/api/auth/login`, {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password: senha }),
          })
          return { status: resposta.status, corpo: await resposta.json() }
        },
        async 'e2e:login'({ email, senha }) {
          const resposta = await fetch(`${api}/api/auth/login`, {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password: senha }),
          })
          const token = /setupflow_session=([^;]+)/.exec(resposta.headers.get('set-cookie') || '')?.[1]
          if (resposta.status !== 200 || !token) throw new Error('Não foi possível abrir a sessão de teste.')
          return token
        },
      })
      return config
    },
  },
})

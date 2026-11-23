// Executor exclusivo desta revisão. Executar na pasta frontend.
const path = require('node:path')
const fs = require('node:fs')
const { createRequire } = require('node:module')
const requireFrontend = createRequire(path.resolve('package.json'))
const cypress = requireFrontend('cypress')
delete process.env.ELECTRON_RUN_AS_NODE
const output = path.resolve('../docs/qualidade/release-2/evidencias-driver06')
const adicional = process.argv.includes('--adicional')
const suite = adicional ? 'adicional' : 'existente'
const temporary = path.resolve('cypress/e2e/autenticacao/qa-driver06.cy.ts')
if (adicional) {
  if (fs.existsSync(temporary)) throw new Error('Teste temporário já existe: não sobrescrever.')
  fs.copyFileSync(path.join(output, 'qa-driver06.cy.ts'), temporary)
}
const spec = adicional ? 'cypress/e2e/autenticacao/qa-driver06.cy.ts' : 'cypress/e2e/autenticacao/*.feature'
process.env.E2E_ARTIFACTS_DIR = path.join(output, suite)
cypress.run({
  browser: 'chrome', configFile: 'cypress.config.ts', spec,
  config: {
    specPattern: spec,
    expose: { filterSpecsMixedMode: 'show' },
    screenshotsFolder: path.join(output, suite, 'screenshots'),
    video: false,
  },
}).then(result => {
  if ('failures' in result) throw new Error(result.message)
  const summary = {
    commit: require('node:child_process').execFileSync('git', ['rev-parse', 'HEAD'], {encoding:'utf8'}).trim(),
    executedAt: new Date().toISOString(), tipo: 'Frontend com respostas simuladas',
    browser: result.browserName, browserVersion: result.browserVersion,
    cypress: result.cypressVersion, node: process.version,
    total: result.totalTests, passed: result.totalPassed, failed: result.totalFailed,
    pending: result.totalPending, skipped: result.totalSkipped,
    tests: result.runs.flatMap(run => run.tests.map(t => ({title:t.title, state:t.state, error:t.displayError}))),
  }
  fs.mkdirSync(path.join(output, suite), {recursive:true})
  fs.writeFileSync(path.join(output, suite, 'resumo.json'), JSON.stringify(summary, null, 2))
  process.exitCode = result.totalFailed || !result.totalTests ? 1 : 0
}).catch(error => { console.error(error); process.exitCode = 1 })
  .finally(() => { if (adicional) fs.unlinkSync(temporary) })

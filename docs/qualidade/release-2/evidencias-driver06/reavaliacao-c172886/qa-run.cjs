// Executor da reavaliação. Executar em frontend. Evidências antigas são preservadas.
const path = require('node:path')
const fs = require('node:fs')
const { createRequire } = require('node:module')
const { execFileSync } = require('node:child_process')
const req = createRequire(path.resolve('package.json'))
const cypress = req('cypress')
delete process.env.ELECTRON_RUN_AS_NODE
const out = __dirname
const mode = process.argv[2] || 'existente'
const custom = mode !== 'existente'
const temp = path.resolve('cypress/e2e/autenticacao/qa-reavaliacao-driver06.cy.ts')
const spec = custom ? 'cypress/e2e/autenticacao/qa-reavaliacao-driver06.cy.ts' : 'cypress/e2e/autenticacao/*.feature'
if (custom) {
  if (fs.existsSync(temp)) throw new Error('Não sobrescrever teste temporário existente')
  fs.copyFileSync(path.join(out, mode + '.cy.ts'), temp)
}
const output = path.join(out, mode)
fs.mkdirSync(output, { recursive: true })
process.env.E2E_ARTIFACTS_DIR = output
cypress.run({
  browser: 'chrome',
  configFile: mode === 'integrado' ? path.join(out, 'qa-integrado.config.cjs') : 'cypress.config.ts',
  spec,
  config: { specPattern: spec, expose: { filterSpecsMixedMode: 'show' },
    screenshotsFolder: path.join(output, 'screenshots'), video: false },
}).then(result => {
  if ('failures' in result) throw new Error(result.message)
  const summary = {
    commit: execFileSync('git', ['rev-parse', 'HEAD'], { encoding: 'utf8' }).trim(),
    executedAt: new Date().toISOString(), mode,
    tipo: mode === 'integrado' ? 'Navegador + API + PostgreSQL reais' : 'Frontend com respostas simuladas',
    browser: result.browserName, browserVersion: result.browserVersion,
    cypress: result.cypressVersion, node: process.version,
    total: result.totalTests, passed: result.totalPassed, failed: result.totalFailed,
    pending: result.totalPending, skipped: result.totalSkipped,
    tests: result.runs.flatMap(r => r.tests.map(t => ({ title: t.title, state: t.state, error: t.displayError }))),
  }
  fs.writeFileSync(path.join(output, 'resumo.json'), JSON.stringify(summary, null, 2))
  process.exitCode = result.totalFailed || !result.totalTests ? 1 : 0
}).catch(error => { console.error(error); process.exitCode = 1 })
  .finally(() => { if (custom) fs.unlinkSync(temp) })

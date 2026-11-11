import cypress from 'cypress'
import { execFileSync } from 'node:child_process'
import { createHash } from 'node:crypto'
import { mkdir, readFile, writeFile } from 'node:fs/promises'
import path from 'node:path'
import process from 'node:process'
import os from 'node:os'

const args = process.argv.slice(2)
// Terminais hospedados em Electron podem definir esta variável; o Cypress deve
// iniciar seu aplicativo de navegador, sem herdar o modo de execução do terminal.
delete process.env.ELECTRON_RUN_AS_NODE
const option = (name, fallback) => args.includes(name) ? args[args.indexOf(name) + 1] : fallback
const browser = option('--browser', 'electron')
const tags = option('--tags', '@regressao and not @wip')
const suite = tags.includes('@smoke') ? 'smoke' : 'regressao'
const output = path.resolve(process.env.E2E_ARTIFACTS_DIR || `artifacts/cypress/${browser}/${suite}`)
process.env.E2E_ARTIFACTS_DIR = output
process.env.E2E_TAGS = tags
const root = path.resolve('..')
const git = (...arguments_) => execFileSync('git', ['-C', root, ...arguments_], { encoding: 'utf8' }).trim()
const hash = createHash('sha256')
const sources = git('ls-files', '-co', '--exclude-standard', '--',
  'frontend/src', 'frontend/cypress', 'frontend/scripts', 'frontend/cypress.config.cjs',
  'frontend/.cypress-cucumber-preprocessorrc.json', 'frontend/package.json', 'frontend/package-lock.json',
  'backend/app', 'backend/scripts', 'backend/testes', 'backend/migrations', 'backend/requirements.txt', '.github/workflows')
for (const file of [...new Set(sources.split('\n'))].sort()) {
  if (file) { hash.update(file); hash.update(await readFile(path.join(root, file))) }
}
const metadata = {
  startedAt: new Date().toISOString(), branch: git('branch', '--show-current'), commit: git('rev-parse', 'HEAD'),
  dirty: Boolean(git('status', '--porcelain')), sourceSha256: hash.digest('hex'),
  browser, tags, node: process.version, platform: `${os.platform()} ${os.release()}`,
}
await mkdir(output, { recursive: true })
let summary
try {
  const result = await cypress.run({ browser })
  if ('failures' in result) throw new Error(result.message)
  summary = {
    ...metadata, finishedAt: new Date().toISOString(), browserVersion: result.browserVersion,
    cypressVersion: result.cypressVersion, total: result.totalTests, passed: result.totalPassed,
    failed: result.totalFailed, pending: result.totalPending, skipped: result.totalSkipped,
    durationMs: result.totalDuration,
    tests: result.runs.flatMap(run => run.tests.map(test => ({ title: test.title.join(' / '), state: test.state }))),
  }
  process.exitCode = result.totalFailed || !result.totalTests ? 1 : 0
} catch (error) {
  summary = { ...metadata, finishedAt: new Date().toISOString(), error: String(error) }
  process.exitCode = 1
}
await writeFile(path.join(output, 'run-summary.json'), JSON.stringify(summary, null, 2) + '\n')
console.log('Evidências Cypress:', output)

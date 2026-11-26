const { execFileSync } = require('node:child_process')
const path = require('node:path')
const pg = new URL(process.env.E2E_DATABASE_URL)
if (pg.hostname !== '127.0.0.1' || pg.port !== '55483' ||
    !/^\/release2_(main|corrigida)_e2e_test$/.test(pg.pathname)) {
  throw new Error('Use somente o banco E2E descartável deste ciclo.')
}

module.exports = {
  viewportWidth: 1440,
  viewportHeight: 1000,
  video: false,
  env: { fixturePassword: process.env.QA_BUG005_FIXTURE_PASSWORD },
  reporter: 'junit',
  reporterOptions: { mochaFile: path.join(process.env.QA_BUG_OUT, 'junit.xml') },
  screenshotsFolder: path.join(process.env.QA_BUG_OUT, 'screenshots'),
  e2e: {
    baseUrl: 'http://localhost:5173',
    specPattern: '.qa-cycle/bug005.cy.js',
    supportFile: false,
    setupNodeEvents(on) {
      on('task', {
        'bug005:seed': () => JSON.parse(execFileSync(process.env.E2E_PYTHON,
          ['-m', 'scripts.seed_e2e', 'normal'],
          { cwd: path.resolve(__dirname, '../backend'), encoding: 'utf8', windowsHide: true })),
        'bug005:expirar': () => execFileSync('psql.exe', [
          '-h', pg.hostname, '-p', pg.port, '-U', pg.username, '-d', pg.pathname.slice(1),
          '-v', 'ON_ERROR_STOP=1', '-c',
          `UPDATE sessoes SET criada_em=now()-interval '2 days', expira_em=now()-interval '1 day'
           WHERE id_usuario = (SELECT id_usuario FROM usuarios WHERE email='ana.e2e@example.com')
             AND invalidada_em IS NULL`,
        ], { encoding: 'utf8', windowsHide: true, env: { ...process.env, PGPASSWORD: pg.password } }).trim(),
      })
    },
  },
}

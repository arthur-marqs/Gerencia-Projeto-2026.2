const path = require('node:path')
const fs = require('node:fs')
const { createRequire } = require('node:module')
const { execFileSync } = require('node:child_process')
let root = __dirname
while (!fs.existsSync(path.join(root, 'backend/app'))) root = path.dirname(root)
const req = createRequire(path.join(root, 'frontend/package.json'))
const bundler = req('@bahmutov/cypress-esbuild-preprocessor')
module.exports = { e2e: {
  baseUrl: 'http://localhost:5173', supportFile: false,
  setupNodeEvents(on) {
    on('file:preprocessor', bundler())
    on('task', { prepararQA(modo) {
      return JSON.parse(execFileSync(path.join(root, 'backend/.venv/Scripts/python.exe'),
        ['-X', 'utf8', path.join(__dirname, 'qa-db.py'), modo],
        { cwd: path.join(root, 'backend'), encoding: 'utf8', windowsHide: true }))
    } })
  },
} }

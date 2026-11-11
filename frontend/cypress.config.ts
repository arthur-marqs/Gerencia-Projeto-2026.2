
import { defineConfig } from 'cypress'
import createBundler from '@bahmutov/cypress-esbuild-preprocessor'
import { addCucumberPreprocessorPlugin } from '@badeball/cypress-cucumber-preprocessor'
import { createEsbuildPlugin } from '@badeball/cypress-cucumber-preprocessor/esbuild'

export default defineConfig({
  e2e: {
    baseUrl: 'http://localhost:5173',
    specPattern: 'cypress/e2e/autenticacao/**/*.feature',
    supportFile: false,

    async setupNodeEvents(on, config) {
      const artifacts = process.env.E2E_ARTIFACTS_DIR || 'artifacts/cypress/login'
      config.expose = {
        ...config.expose,
        tags: process.env.E2E_TAGS || config.expose?.tags || '@regressao and not @wip',
        jsonOutput: `${artifacts}/cucumber-report.json`,
        htmlOutput: `${artifacts}/cucumber-report.html`,
      }
      await addCucumberPreprocessorPlugin(on, config)

      on(
        'file:preprocessor',
        createBundler({
          plugins: [createEsbuildPlugin(config)],
        })
      )

      return config
    },
  },
})

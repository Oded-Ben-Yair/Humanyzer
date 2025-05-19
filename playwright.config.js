// @ts-check
const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests',
  timeout: 30000,
  expect: {
    timeout: 5000
  },
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [['html', { outputFolder: 'qa_results/playwright-report' }], ['json', { outputFile: 'qa_results/playwright-results.json' }]],
  use: {
    actionTimeout: 0,
    trace: 'on-first-retry',
    screenshot: 'on',
  },
});

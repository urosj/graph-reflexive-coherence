import { defineConfig } from '../web/node_modules/@playwright/test/index.mjs';
import { fileURLToPath } from 'node:url';
export default defineConfig({
  testDir: '.', testMatch: 'browser.spec.mjs',
  outputDir: fileURLToPath(new URL('../generated/phase9-verification/browser', import.meta.url)),
  timeout: 45000, expect: {timeout: 10000}, reporter: 'line', workers: 1,
  use: {baseURL: process.env.PHASE9_TEST_URL, reducedMotion: 'reduce', trace: 'retain-on-failure'},
  projects: [
    {name: 'desktop', use: {viewport: {width: 1440, height: 900}}},
    {name: 'mobile', use: {viewport: {width: 390, height: 844}, isMobile: true}},
  ],
});

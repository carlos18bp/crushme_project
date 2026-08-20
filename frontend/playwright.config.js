import { defineConfig, devices } from '@playwright/test';

const FRONTEND_PORT = Number(process.env.E2E_PORT || 5174);
const BACKEND_PORT = Number(process.env.E2E_BACKEND_PORT || 8001);
const baseURL = process.env.E2E_BASE_URL || `http://127.0.0.1:${FRONTEND_PORT}`;
const parsedBaseURL = new URL(baseURL);
const productionHosts = new Set(['crushme.com.co', 'www.crushme.com.co']);
const localHosts = new Set(['127.0.0.1', 'localhost']);
const isLocal = localHosts.has(parsedBaseURL.hostname);
const remoteStagingEnabled = process.env.E2E_REMOTE_STAGING === '1';

if (productionHosts.has(parsedBaseURL.hostname)) {
  throw new Error(`Playwright refuses the production host: ${parsedBaseURL.hostname}`);
}
if (!isLocal && !remoteStagingEnabled) {
  throw new Error('Remote E2E requires E2E_REMOTE_STAGING=1.');
}
if (!isLocal && parsedBaseURL.protocol !== 'https:') {
  throw new Error('Remote E2E requires an HTTPS staging URL.');
}

const reuseExistingServer = process.env.E2E_REUSE_SERVER === '1' && !process.env.CI;
const e2eDatabasePath = process.env.E2E_DB_PATH || '/tmp/crushme-e2e.sqlite3';
const webServer = isLocal
  ? [
      {
        command: 'bash ../scripts/run-e2e-backend.sh',
        url: `http://127.0.0.1:${BACKEND_PORT}/api/health/`,
        reuseExistingServer,
        timeout: 120_000,
        env: {
          ...process.env,
          E2E_DB_PATH: e2eDatabasePath,
          E2E_BACKEND_PORT: String(BACKEND_PORT),
        },
      },
      {
        command: `npm run dev -- --host 127.0.0.1 --port ${FRONTEND_PORT} --strictPort`,
        url: baseURL,
        reuseExistingServer,
        timeout: 120_000,
        env: {
          ...process.env,
          VITE_BACKEND_URL: `http://127.0.0.1:${BACKEND_PORT}`,
        },
      },
    ]
  : undefined;

export default defineConfig({
  testDir: './e2e',
  timeout: 30_000,
  expect: { timeout: 8_000 },
  fullyParallel: false,
  forbidOnly: Boolean(process.env.CI),
  retries: process.env.CI ? 2 : 0,
  workers: 1,
  reporter: [
    ['list'],
    ['html', { open: 'never' }],
    ['json', { outputFile: 'e2e-results/results.json' }],
    ['./e2e/reporters/flow-coverage-reporter.mjs', { outputDir: 'e2e-results' }],
  ],
  use: {
    baseURL,
    navigationTimeout: 25_000,
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: 'off',
  },
  webServer,
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
  ],
});

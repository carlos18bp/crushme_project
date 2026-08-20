import { test as base, expect } from "@playwright/test";

const shouldLogErrors = process.env.E2E_LOG_ERRORS === "1";

export const test = base.extend({
  page: async ({ page, request }, use) => {
    // Cold Vite workers may compile large lazy routes during the first UI action.
    page.setDefaultTimeout(20000);
    page.setDefaultNavigationTimeout(25000);

    const health = await request.get('/api/health/');
    if (!health.ok()) {
      throw new Error(`E2E backend health check failed with ${health.status()}`);
    }
    const identity = await health.json();
    if (identity.environment === 'production') {
      throw new Error('E2E refuses a production backend.');
    }

    const remoteStaging = process.env.E2E_REMOTE_STAGING === '1';
    const expectedEnvironment = remoteStaging ? 'staging' : 'e2e';
    if (identity.environment !== expectedEnvironment) {
      throw new Error(
        `E2E expected ${expectedEnvironment}, received ${identity.environment}.`,
      );
    }

    if (remoteStaging && process.env.E2E_ALLOW_STAGING_WRITES !== '1') {
      await page.route('**/api/**', (route) => {
        const method = route.request().method();
        return ['GET', 'HEAD', 'OPTIONS'].includes(method)
          ? route.continue()
          : route.abort('blockedbyclient');
      });
    }

    await page.addInitScript(() => {
      localStorage.setItem('language', 'en');
    });

    if (shouldLogErrors) {
      page.on("pageerror", (err) => {
        console.error("[e2e:pageerror]", err);
      });
      page.on("console", (msg) => {
        if (msg.type() === "error") {
          console.error("[e2e:console:error]", msg.text());
        }
      });
    }
    await use(page);
  },
});

export { expect };

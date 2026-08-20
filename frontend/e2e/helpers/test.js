import { test as base, expect } from "@playwright/test";

const shouldLogErrors = process.env.E2E_LOG_ERRORS === "1";

export const test = base.extend({
  page: async ({ page, request }, use) => {
    page.setDefaultTimeout(10000);
    page.setDefaultNavigationTimeout(25000);

    const health = await request.get('/api/health/');
    if (!health.ok()) {
      throw new Error(`E2E backend health check failed with ${health.status()}`);
    }
    const identity = await health.json();
    if (identity.environment === 'production') {
      throw new Error('E2E refuses a production backend.');
    }

    if (identity.environment !== 'e2e') {
      throw new Error(
        `E2E expected e2e, received ${identity.environment}.`,
      );
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

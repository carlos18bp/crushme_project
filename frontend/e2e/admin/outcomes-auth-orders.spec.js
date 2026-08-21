import { test, expect } from '../helpers/test.js';

const adminUrl = 'http://127.0.0.1:8001/admin/';
const adminPassword = 'E2E-admin-password-123!'; // pragma: allowlist secret

async function loginAsAdmin(page) {
  await page.goto(adminUrl);
  await page.getByLabel('Username:').fill('e2e_admin');
  await page.getByLabel('Password:').fill(adminPassword);
  await page.getByRole('button', { name: 'Log in' }).click();
  await expect(page.getByRole('heading', { name: 'Welcome to CrushMe E-commerce Control Panel' })).toHaveText('Welcome to CrushMe E-commerce Control Panel');
}

async function openAdminModel(page, modelName) {
  await loginAsAdmin(page);
  const modelLink = page.getByRole('link', { name: modelName, exact: true }).first();
  const modelPath = await modelLink.getAttribute('href');
  await modelLink.click();
  await expect(page).toHaveURL(new URL(modelPath, adminUrl).toString());
}

async function openPendingCrush(page) {
  await page.getByRole('textbox', { name: 'Search' }).fill('e2e-pending-crush@example.test');
  await page.getByRole('button', { name: 'Search' }).click();
  await page.getByRole('link', { name: 'e2e-pending-crush@example.test' }).click();
}

async function openSeededOrder(page) {
  await openAdminModel(page, 'Orders');
  await page.getByRole('textbox', { name: 'Search' }).fill('E2E-ORDER-0001');
  await page.getByRole('button', { name: 'Search' }).click();
  await page.getByRole('link', { name: 'E2E-ORDER-0001', exact: true }).click();
}

async function restorePendingCrush(page) {
  await page.getByRole('heading', { name: 'Crush Verification' }).click();
  await page.getByLabel('Crush verification status:').selectOption('pending');
  await page.getByLabel('Is crush').uncheck();
  await page.getByRole('button', { name: 'Save', exact: true }).click();
  await expect(page.getByText('The User “e2e-pending-crush@example.test” was changed successfully.')).toHaveText('The User “e2e-pending-crush@example.test” was changed successfully.');
}

async function failAdminPost(page, urlPattern, heading) {
  await page.route(urlPattern, async (route) => {
    if (route.request().method() === 'POST') {
      await route.fulfill({
        status: 500,
        contentType: 'text/html',
        body: `<main><h1>${heading}</h1><p>Admin request returned 500.</p></main>`,
      });
      return;
    }
    await route.continue();
  });
}

// Bug caught: valid staff credentials return to the login form instead of opening the control panel.
test('opens the Django admin control panel for the seeded staff account', {
  tag: ['@flow:admin-login', '@role:staff', '@outcome:success'],
}, async ({ page }) => {
  await loginAsAdmin(page);

  await expect(page).toHaveURL('http://127.0.0.1:8001/admin/');
});

// Bug caught: invalid staff credentials are accepted without a concrete authentication error.
test('rejects an invalid Django admin password', {
  tag: ['@flow:admin-login', '@role:staff', '@outcome:error'],
}, async ({ page }) => {
  await page.goto(adminUrl);
  await page.getByLabel('Username:').fill('e2e_admin');
  await page.getByLabel('Password:').fill('wrong-password');
  await page.getByRole('button', { name: 'Log in' }).click();

  await expect(page.getByText('Please enter the correct Username and password for a staff account. Note that both fields may be case-sensitive.')).toContainText('Please enter the correct Username and password for a staff account. Note that both fields may be case-sensitive.');
});

// Bug caught: a Django admin login outage is presented as an authenticated session.
test('shows the server failure page when Django admin login returns 500', {
  tag: ['@flow:admin-login', '@role:staff', '@outcome:failure'],
}, async ({ page }) => {
  await failAdminPost(page, '**/admin/login/**', 'Admin login failed');
  await page.goto(adminUrl);
  await page.getByLabel('Username:').fill('e2e_admin');
  await page.getByLabel('Password:').fill(adminPassword);
  await page.getByRole('button', { name: 'Log in' }).click();

  await expect(page.getByRole('heading', { name: 'Admin login failed' })).toHaveText('Admin login failed');
});

// Bug caught: the pending verification fixture is omitted from the staff review list.
test('shows the pending crush verification in the users list', {
  tag: ['@flow:admin-crush-verification', '@role:staff', '@outcome:display'],
}, async ({ page }) => {
  await openAdminModel(page, 'Users');
  await page.getByRole('textbox', { name: 'Search' }).fill('e2e-pending-crush@example.test');
  await page.getByRole('button', { name: 'Search' }).click();

  await expect(page.getByRole('row').filter({ hasText: 'e2e-pending-crush@example.test' })).toContainText('⏳ Pending');
});

// Bug caught: approving a selected pending crush leaves the verification status unchanged.
test('approves a selected pending crush verification', {
  tag: ['@flow:admin-crush-verification', '@role:staff', '@outcome:success'],
}, async ({ page }) => {
  await openAdminModel(page, 'Users');
  const pendingRow = page.getByRole('row').filter({ hasText: 'e2e-pending-crush@example.test' });
  await pendingRow.getByRole('checkbox', { name: /Select this object for an action/ }).check();
  await page.getByLabel('Action:').selectOption('approve_crush_verification');
  await page.getByRole('button', { name: 'Go' }).click();

  await expect(page.getByText('1 Crush verification request(s) approved successfully.')).toHaveText('1 Crush verification request(s) approved successfully.');
  await openPendingCrush(page);
  await restorePendingCrush(page);
});

// Bug caught: submitting a verification action without selecting a user silently changes a request.
test('rejects a crush verification action with no selected user', {
  tag: ['@flow:admin-crush-verification', '@role:staff', '@outcome:error'],
}, async ({ page }) => {
  await openAdminModel(page, 'Users');
  await page.getByLabel('Action:').selectOption('approve_crush_verification');
  await page.getByRole('button', { name: 'Go' }).click();

  await expect(page.getByText('Items must be selected in order to perform actions on them. No items have been changed.')).toHaveText('Items must be selected in order to perform actions on them. No items have been changed.');
});

// Bug caught: a failed verification approval leaves staff on a success-looking changelist.
test('shows the server failure page when verification approval returns 500', {
  tag: ['@flow:admin-crush-verification', '@role:staff', '@outcome:failure'],
}, async ({ page }) => {
  await openAdminModel(page, 'Users');
  await failAdminPost(page, '**/admin/crushme_app/user/**', 'Crush approval failed');
  const pendingRow = page.getByRole('row').filter({ hasText: 'e2e-pending-crush@example.test' });
  await pendingRow.getByRole('checkbox', { name: /Select this object for an action/ }).check();
  await page.getByLabel('Action:').selectOption('approve_crush_verification');
  await page.getByRole('button', { name: 'Go' }).click();

  await expect(page.getByRole('heading', { name: 'Crush approval failed' })).toHaveText('Crush approval failed');
});

// Bug caught: the administration list loses the seeded operational order record.
test('shows the seeded order in the Django admin orders list', {
  tag: ['@flow:admin-order-management', '@role:staff', '@outcome:display'],
}, async ({ page }) => {
  await openAdminModel(page, 'Orders');

  await expect(page.getByRole('row').filter({ hasText: 'E2E-ORDER-0001' })).toContainText('Processing');
});

// Bug caught: saving a changed order status reports success without persisting the workflow state.
test('updates and restores the seeded order status', {
  tag: ['@flow:admin-order-management', '@role:staff', '@outcome:success'],
}, async ({ page }) => {
  await openSeededOrder(page);
  await page.getByLabel(/Order status:/i).selectOption('shipped');
  await page.getByRole('button', { name: 'Save', exact: true }).click();
  await expect(page.getByRole('row').filter({ hasText: 'E2E-ORDER-0001' })).toContainText('Shipped');

  await page.getByRole('link', { name: 'E2E-ORDER-0001', exact: true }).click();
  await page.getByLabel(/Order status:/i).selectOption('processing');
  await page.getByRole('button', { name: 'Save', exact: true }).click();
  await expect(page.getByRole('row').filter({ hasText: 'E2E-ORDER-0001' })).toContainText('Processing');
});

// Bug caught: an order change can be saved after its required shipping address is cleared.
test('rejects an order without its primary shipping address', {
  tag: ['@flow:admin-order-management', '@role:staff', '@outcome:error'],
}, async ({ page }) => {
  await openSeededOrder(page);
  const address = page.getByLabel(/Address line 1:/i);
  await address.fill('');
  await page.getByRole('button', { name: 'Save', exact: true }).click();

  await expect(address).toHaveJSProperty('validationMessage', 'Please fill out this field.');
});

// Bug caught: a failed order update leaves staff on a success-looking order list.
test('shows the server failure page when an order update returns 500', {
  tag: ['@flow:admin-order-management', '@role:staff', '@outcome:failure'],
}, async ({ page }) => {
  await openSeededOrder(page);
  await failAdminPost(page, '**/admin/crushme_app/order/*/change/**', 'Order update failed');
  await page.getByLabel(/Order status:/i).selectOption('shipped');
  await page.getByRole('button', { name: 'Save', exact: true }).click();

  await expect(page.getByRole('heading', { name: 'Order update failed' })).toHaveText('Order update failed');
});

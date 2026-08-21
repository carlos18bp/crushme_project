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

async function searchAndOpen(page, value) {
  await page.getByRole('textbox', { name: 'Search' }).fill(value);
  await page.getByRole('button', { name: 'Search' }).click();
  await page.getByRole('link', { name: value, exact: true }).click();
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

async function createMargin(page, percentage) {
  await page.getByRole('link', { name: 'Add category price margin' }).click();
  await page.getByLabel('Category:').selectOption({ label: 'Juguetes (ID: 134)' });
  await page.getByLabel('Margin Percentage:').fill(String(percentage));
  await page.getByRole('button', { name: 'Save', exact: true }).click();
  await expect(page.getByText('The Category Price Margin “Juguetes: +' + percentage + '%” was added successfully.')).toHaveText('The Category Price Margin “Juguetes: +' + percentage + '%” was added successfully.');
}

async function deleteMargin(page) {
  await page.getByRole('link', { name: 'Category Price Margins', exact: true }).first().click();
  const marginRow = page.getByRole('row').filter({ hasText: 'Juguetes' });
  await marginRow.getByRole('checkbox', { name: /Select this object for an action/ }).check();
  await page.getByLabel('Action:').selectOption('delete_selected');
  await page.getByRole('button', { name: 'Go' }).click();
  await page.getByRole('button', { name: 'Yes, I’m sure' }).click();
  await expect(page.getByText('Successfully deleted 1 Category Price Margin.')).toHaveText('Successfully deleted 1 Category Price Margin.');
}

// Bug caught: the staff users list no longer shows the deterministic E2E account.
test('shows the seeded customer in the Django admin users list', {
  tag: ['@flow:admin-user-management', '@role:staff', '@outcome:display'],
}, async ({ page }) => {
  await openAdminModel(page, 'Users');
  await page.getByRole('textbox', { name: 'Search' }).fill('e2e-user@example.test');
  await page.getByRole('button', { name: 'Search' }).click();

  await expect(page.getByRole('row').filter({ hasText: 'e2e-user@example.test' })).toContainText('e2e_user');
});

// Bug caught: saving a user edit reports success without persisting the changed name.
test('updates and restores the seeded customer first name', {
  tag: ['@flow:admin-user-management', '@role:staff', '@outcome:success'],
}, async ({ page }) => {
  await openAdminModel(page, 'Users');
  await searchAndOpen(page, 'e2e-user@example.test');
  await page.getByLabel('First name:').fill('Coverage');
  await page.getByRole('button', { name: 'Save', exact: true }).click();
  await expect(page.getByText('The User “e2e-user@example.test” was changed successfully.')).toHaveText('The User “e2e-user@example.test” was changed successfully.');

  await searchAndOpen(page, 'e2e-user@example.test');
  await page.getByLabel('First name:').fill('E2E');
  await page.getByRole('button', { name: 'Save', exact: true }).click();
  await expect(page.getByText('The User “e2e-user@example.test” was changed successfully.')).toHaveText('The User “e2e-user@example.test” was changed successfully.');
});

// Bug caught: a duplicate email is accepted when a staff user edits an account.
test('rejects a user edit with the existing admin email address', {
  tag: ['@flow:admin-user-management', '@role:staff', '@outcome:error'],
}, async ({ page }) => {
  await openAdminModel(page, 'Users');
  await searchAndOpen(page, 'e2e-user@example.test');
  await page.getByLabel('Email address:').fill('e2e-admin@example.test');
  await page.getByRole('button', { name: 'Save', exact: true }).click();

  await expect(page.getByText('User with this Email Address already exists.')).toHaveText('User with this Email Address already exists.');
});

// Bug caught: a failed user update leaves staff on a success-looking change form.
test('shows the server failure page when a user update returns 500', {
  tag: ['@flow:admin-user-management', '@role:staff', '@outcome:failure'],
}, async ({ page }) => {
  await openAdminModel(page, 'Users');
  await searchAndOpen(page, 'e2e-user@example.test');
  await failAdminPost(page, '**/admin/crushme_app/user/*/change/**', 'User update failed');
  await page.getByLabel('First name:').fill('Failed update');
  await page.getByRole('button', { name: 'Save', exact: true }).click();

  await expect(page.getByRole('heading', { name: 'User update failed' })).toHaveText('User update failed');
});

// Bug caught: catalog margin records cannot be reached through the Django admin UI.
test('shows an admin-created category price margin in its changelist', {
  tag: ['@flow:admin-catalog-management', '@role:staff', '@outcome:display'],
}, async ({ page }) => {
  await openAdminModel(page, 'Category Price Margins');
  await createMargin(page, 25);
  await page.getByRole('link', { name: 'Category Price Margins', exact: true }).first().click();

  await expect(page.getByRole('row').filter({ hasText: 'Juguetes' })).toContainText('+25.00%');
  await deleteMargin(page);
});

// Bug caught: creating a category margin silently fails instead of reporting a saved configuration.
test('creates and removes a category price margin through Django admin', {
  tag: ['@flow:admin-catalog-management', '@role:staff', '@outcome:success'],
}, async ({ page }) => {
  await openAdminModel(page, 'Category Price Margins');
  await createMargin(page, 30);
  await expect(page.getByRole('row').filter({ hasText: 'Juguetes' })).toContainText('+30.00%');

  await deleteMargin(page);
});

// Bug caught: a category margin form submits without the required catalog category.
test('blocks a category margin save with no selected category', {
  tag: ['@flow:admin-catalog-management', '@role:staff', '@outcome:error'],
}, async ({ page }) => {
  await openAdminModel(page, 'Category Price Margins');
  await page.getByRole('link', { name: 'Add category price margin' }).click();
  await page.getByLabel('Margin Percentage:').fill('25');
  await page.getByRole('button', { name: 'Save', exact: true }).click();

  await expect(page.getByLabel('Category:')).toHaveJSProperty('validationMessage', 'Please select an item in the list.');
});

// Bug caught: a category-margin server failure is indistinguishable from a saved catalog change.
test('shows the server failure page when adding a category margin returns 500', {
  tag: ['@flow:admin-catalog-management', '@role:staff', '@outcome:failure'],
}, async ({ page }) => {
  await openAdminModel(page, 'Category Price Margins');
  await page.getByRole('link', { name: 'Add category price margin' }).click();
  await failAdminPost(page, '**/admin/crushme_app/categorypricemargin/add/**', 'Category margin save failed');
  await page.getByLabel('Category:').selectOption({ label: 'Juguetes (ID: 134)' });
  await page.getByLabel('Margin Percentage:').fill('35');
  await page.getByRole('button', { name: 'Save', exact: true }).click();

  await expect(page.getByRole('heading', { name: 'Category margin save failed' })).toHaveText('Category margin save failed');
});

// Bug caught: the deterministic E2E discount is missing from the staff discount list.
test('shows the seeded E2E discount code in Django admin', {
  tag: ['@flow:admin-discount-management', '@role:staff', '@outcome:display'],
}, async ({ page }) => {
  await openAdminModel(page, 'Discount Codes');
  await page.getByRole('textbox', { name: 'Search' }).fill('E2E10');
  await page.getByRole('button', { name: 'Search' }).click();

  await expect(page.getByRole('row').filter({ hasText: 'E2E10' })).toContainText('10.00%');
});

// Bug caught: saving an inactive discount state does not persist the administrative change.
test('deactivates and restores the seeded discount code', {
  tag: ['@flow:admin-discount-management', '@role:staff', '@outcome:success'],
}, async ({ page }) => {
  await openAdminModel(page, 'Discount Codes');
  await searchAndOpen(page, 'E2E10');
  await page.getByLabel('Is Active').uncheck();
  await page.getByRole('button', { name: 'Save', exact: true }).click();
  await expect(page.getByText('The Discount Code “E2E10 (10.00%)” was changed successfully.')).toHaveText('The Discount Code “E2E10 (10.00%)” was changed successfully.');

  await searchAndOpen(page, 'E2E10');
  await expect(page.getByLabel('Is Active')).not.toBeChecked();
  await page.getByLabel('Is Active').check();
  await page.getByRole('button', { name: 'Save', exact: true }).click();
  await expect(page.getByText('The Discount Code “E2E10 (10.00%)” was changed successfully.')).toHaveText('The Discount Code “E2E10 (10.00%)” was changed successfully.');

  await searchAndOpen(page, 'E2E10');
  await expect(page.getByLabel('Is Active')).toBeChecked();
});

// Bug caught: discount percentages above 100 are accepted by the administrative form.
test('rejects an out-of-range discount percentage', {
  tag: ['@flow:admin-discount-management', '@role:staff', '@outcome:error'],
}, async ({ page }) => {
  const invalidCode = `E2EINVALID${Date.now()}`;
  await openAdminModel(page, 'Discount Codes');
  await page.getByRole('link', { name: 'Add discount code' }).click();
  await page.getByLabel('Discount Code:').fill(invalidCode);
  await page.getByLabel('Discount Percentage:').fill('101');
  await page.getByRole('button', { name: 'Save', exact: true }).click();

  await expect(page.getByText('Ensure this value is less than or equal to 100.')).toHaveText('Ensure this value is less than or equal to 100.');
});

// Bug caught: a failed discount update leaves staff on a success-looking change form.
test('shows the server failure page when a discount update returns 500', {
  tag: ['@flow:admin-discount-management', '@role:staff', '@outcome:failure'],
}, async ({ page }) => {
  await openAdminModel(page, 'Discount Codes');
  await searchAndOpen(page, 'E2E10');
  await failAdminPost(page, '**/admin/crushme_app/discountcode/*/change/**', 'Discount update failed');
  await page.getByLabel('Is Active').uncheck();
  await page.getByRole('button', { name: 'Save', exact: true }).click();

  await expect(page.getByRole('heading', { name: 'Discount update failed' })).toHaveText('Discount update failed');
});

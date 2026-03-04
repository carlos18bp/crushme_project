export async function setAuthLocalStorage(page, { token, userAuth }) {
  await page.addInitScript(
    ({ token: t, userAuth: u }) => {
      localStorage.setItem("access_token", t);
      localStorage.setItem("refresh_token", "fake-refresh-token");
      localStorage.setItem("user", JSON.stringify(u));
    },
    { token, userAuth }
  );
}

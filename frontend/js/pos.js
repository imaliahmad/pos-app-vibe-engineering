// Placeholder until the POS screen (feature 5): shows who is signed in.

async function loadCurrentUser() {
  const result = await apiMe();
  if (result.status) {
    const user = result.data;
    document.getElementById("current-user").textContent =
      `Signed in as ${user.username} (${user.role})`;
  }
}

document.getElementById("logout-button").addEventListener("click", async () => {
  await apiLogout();
  window.location = "/";
});

loadCurrentUser();

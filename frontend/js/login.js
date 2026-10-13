const form = document.getElementById("login-form");
const button = document.getElementById("login-button");
const message = document.getElementById("login-message");

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  message.textContent = "";
  button.disabled = true;

  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;
  const result = await apiLogin(username, password);

  if (result.status) {
    window.location = "/pos";
    return;
  }
  message.textContent = result.message;
  button.disabled = false;
});

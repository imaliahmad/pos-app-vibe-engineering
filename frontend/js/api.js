// The only file that calls fetch(). One function per endpoint.

async function apiRequest(method, path, body, redirectOn401 = true) {
  const options = { method, headers: {} };
  if (body !== undefined) {
    options.headers["Content-Type"] = "application/json";
    options.body = JSON.stringify(body);
  }

  let response;
  try {
    response = await fetch(path, options);
  } catch (error) {
    return { status: false, message: "Cannot reach the server", data: null, errors: [] };
  }

  if (response.status === 401 && redirectOn401) {
    window.location = "/";
    // The page is leaving for login: an empty message keeps the screen from flashing an error.
    return { status: false, message: "", data: null, errors: [] };
  }

  try {
    return await response.json();
  } catch (error) {
    return { status: false, message: "Unexpected server response", data: null, errors: [] };
  }
}

function apiLogin(username, password) {
  // A wrong password returns 401: show the message instead of redirecting.
  return apiRequest("POST", "/api/auth/login", { username, password }, false);
}

function apiLogout() {
  return apiRequest("POST", "/api/auth/logout");
}

function apiMe() {
  return apiRequest("GET", "/api/auth/me");
}

function apiCategories() {
  return apiRequest("GET", "/api/categories");
}

function apiCategoryItems(categoryId) {
  return apiRequest("GET", `/api/categories/${categoryId}/items`);
}

function apiSaveSale(lines) {
  return apiRequest("POST", "/api/sales", { lines });
}

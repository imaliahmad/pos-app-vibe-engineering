// The POS screen: categories → items → order.

const MAX_QUANTITY = 999;

let selectedCategoryId = null;

// True while a save request is in flight: blocks a second save and order changes.
let saving = false;

// The current order. name and price are for display only; the server prices the sale.
const order = { lines: [] };

function formatMoney(amount) {
  return (amount / 100).toFixed(2);
}

// Shows an API error; an empty text clears it. A 401 never gets here: api.js goes to login.
function showMessage(text) {
  document.getElementById("message").textContent = text;
}

// Shows the saved order; an empty text clears it.
function showConfirmation(text) {
  document.getElementById("sale-confirmation").textContent = text;
}

async function saveOrder() {
  if (saving || order.lines.length === 0) {
    return;
  }
  saving = true;
  render();

  // Only ids and quantities are sent: the server prices the sale from the database.
  const lines = order.lines.map((l) => ({ item_id: l.item_id, quantity: l.quantity }));
  const result = await apiSaveSale(lines);
  saving = false;
  if (!result.status) {
    // Keep the order so the cashier can try again.
    showMessage(result.message);
    render();
    return;
  }
  showMessage("");
  order.lines = [];
  render();
  const sale = result.data;
  showConfirmation(`Order #${sale.sale_id} saved, total ${formatMoney(sale.total)}`);
}

function addItem(item) {
  if (saving) {
    return;
  }
  showConfirmation("");
  const line = order.lines.find((l) => l.item_id === item.id);
  if (line) {
    line.quantity = Math.min(line.quantity + 1, MAX_QUANTITY);
  } else {
    order.lines.push({ item_id: item.id, name: item.name, price: item.price, quantity: 1 });
  }
  render();
}

function changeQuantity(itemId, delta) {
  if (saving) {
    return;
  }
  const line = order.lines.find((l) => l.item_id === itemId);
  if (!line) {
    return;
  }
  const quantity = line.quantity + delta;
  if (quantity < 1) {
    removeLine(itemId);
    return;
  }
  line.quantity = Math.min(quantity, MAX_QUANTITY);
  render();
}

function removeLine(itemId) {
  if (saving) {
    return;
  }
  order.lines = order.lines.filter((l) => l.item_id !== itemId);
  render();
}

// ariaLabel names a button that shows only a symbol (e.g. "−") for screen readers.
function createButton(label, className, onClick, ariaLabel) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = className;
  button.textContent = label;
  if (ariaLabel) {
    button.setAttribute("aria-label", ariaLabel);
  }
  button.addEventListener("click", onClick);
  return button;
}

function render() {
  const container = document.getElementById("order-lines");
  container.replaceChildren();

  if (order.lines.length === 0) {
    const empty = document.createElement("p");
    empty.className = "order-empty";
    empty.textContent = "No items yet";
    container.appendChild(empty);
  }

  let total = 0;
  for (const line of order.lines) {
    const lineTotal = line.price * line.quantity;
    total += lineTotal;

    const row = document.createElement("div");
    row.className = "order-line";

    const name = document.createElement("span");
    name.className = "order-line-name";
    name.textContent = line.name;
    const quantity = document.createElement("span");
    quantity.className = "order-line-qty";
    quantity.textContent = `x${line.quantity}`;
    const amount = document.createElement("span");
    amount.className = "order-line-total";
    amount.textContent = formatMoney(lineTotal);

    row.append(
      name,
      quantity,
      amount,
      createButton("−", "qty-button", () => changeQuantity(line.item_id, -1), "Decrease"),
      createButton("+", "qty-button", () => changeQuantity(line.item_id, 1), "Increase"),
      createButton("✕", "qty-button remove-button", () => removeLine(line.item_id), "Remove"),
    );
    container.appendChild(row);
  }

  document.getElementById("order-total").textContent = formatMoney(total);
  document.getElementById("save-button").disabled = saving || order.lines.length === 0;
}

async function loadCurrentUser() {
  const result = await apiMe();
  if (!result.status) {
    showMessage(result.message);
    return;
  }
  const user = result.data;
  document.getElementById("current-user").textContent =
    `Signed in as ${user.username} (${user.role})`;
}

async function loadCategories() {
  const result = await apiCategories();
  if (!result.status) {
    showMessage(result.message);
    return;
  }
  showMessage("");

  const container = document.getElementById("categories");
  container.replaceChildren();
  for (const category of result.data) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "category-button";
    button.dataset.categoryId = category.id;
    button.textContent = category.name;
    button.addEventListener("click", () => selectCategory(category.id));
    container.appendChild(button);
  }

  if (result.data.length > 0) {
    selectCategory(result.data[0].id);
  }
}

function selectCategory(categoryId) {
  selectedCategoryId = categoryId;
  for (const button of document.querySelectorAll(".category-button")) {
    button.classList.toggle("selected", Number(button.dataset.categoryId) === categoryId);
  }
  loadItems(categoryId);
}

async function loadItems(categoryId) {
  const result = await apiCategoryItems(categoryId);
  // Ignore a slow response for a category the user has already left.
  if (categoryId !== selectedCategoryId) {
    return;
  }

  const container = document.getElementById("items");
  container.replaceChildren();
  if (!result.status) {
    showMessage(result.message);
    return;
  }
  showMessage("");
  for (const item of result.data) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "item-button";

    const name = document.createElement("span");
    name.className = "item-name";
    name.textContent = item.name;
    const price = document.createElement("span");
    price.className = "item-price";
    price.textContent = formatMoney(item.price);

    button.append(name, price);
    button.addEventListener("click", () => addItem(item));
    container.appendChild(button);
  }
}

document.getElementById("save-button").addEventListener("click", saveOrder);

document.getElementById("logout-button").addEventListener("click", async () => {
  const result = await apiLogout();
  if (!result.status) {
    // Still signed in (e.g. server down): going to "/" would only bounce back here.
    showMessage(result.message);
    return;
  }
  window.location = "/";
});

loadCurrentUser();
loadCategories();
render();

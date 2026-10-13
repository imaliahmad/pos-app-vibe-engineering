// The admin reports page.

// The orders filter; Today is selected when the page opens.
let selectedPeriod = "today";

function formatMoney(amount) {
  return (amount / 100).toFixed(2);
}

// Shows an API error; an empty text clears it. A 401 never gets here: api.js goes to login.
function showMessage(text) {
  document.getElementById("message").textContent = text;
}

// One table cell; numbers are right-aligned.
function createCell(text, isNumber = false) {
  const cell = document.createElement("td");
  cell.textContent = text;
  if (isNumber) {
    cell.className = "number";
  }
  return cell;
}

// Fills a table body with one row per item, or one "empty" row when there are none.
function renderRows(tbodyId, rows, toCells, emptyText) {
  const tbody = document.getElementById(tbodyId);
  tbody.replaceChildren();
  if (rows.length === 0) {
    const cell = createCell(emptyText);
    cell.className = "report-empty";
    cell.colSpan = tbody.closest("table").tHead.rows[0].cells.length;
    const row = document.createElement("tr");
    row.appendChild(cell);
    tbody.appendChild(row);
    return;
  }
  for (const item of rows) {
    const row = document.createElement("tr");
    row.append(...toCells(item));
    tbody.appendChild(row);
  }
}

async function loadCategoryReport() {
  const result = await apiCategoryReport();
  if (!result.status) {
    showMessage(result.message);
    return;
  }
  renderRows(
    "category-report",
    result.data,
    (c) => [createCell(c.name), createCell(c.quantity, true), createCell(formatMoney(c.revenue), true)],
    "No categories",
  );
}

async function loadItemReport() {
  const result = await apiItemReport();
  if (!result.status) {
    showMessage(result.message);
    return;
  }
  renderRows(
    "item-report",
    result.data,
    (i) => [
      createCell(i.name),
      createCell(i.category),
      createCell(i.quantity, true),
      createCell(formatMoney(i.revenue), true),
    ],
    "No items",
  );
}

function selectPeriod(period) {
  selectedPeriod = period;
  for (const button of document.querySelectorAll(".period-button")) {
    button.classList.toggle("selected", button.dataset.period === period);
  }
  loadOrders(period);
}

async function loadOrders(period) {
  const result = await apiOrders(period);
  // Ignore a slow response for a period the user has already left.
  if (period !== selectedPeriod) {
    return;
  }
  if (!result.status) {
    showMessage(result.message);
    return;
  }
  showMessage("");
  renderRows(
    "order-list",
    result.data,
    (o) => [
      createCell(`#${o.id}`),
      createCell(o.created_at),
      createCell(o.cashier),
      createCell(formatMoney(o.total), true),
    ],
    "No orders in this period",
  );

  // Each order row opens its details: click, or Enter / Space when focused.
  const rows = document.getElementById("order-list").rows;
  result.data.forEach((order, index) => {
    const row = rows[index];
    row.className = "order-row";
    row.tabIndex = 0;
    row.addEventListener("click", () => openOrder(order.id));
    row.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        openOrder(order.id);
      }
    });
  });
}

async function openOrder(orderId) {
  const dialog = document.getElementById("order-dialog");
  if (dialog.open) {
    return;
  }
  const result = await apiOrder(orderId);
  if (!result.status) {
    showMessage(result.message);
    return;
  }
  showMessage("");
  const order = result.data;
  document.getElementById("order-dialog-title").textContent = `Order #${order.id}`;
  document.getElementById("order-dialog-info").textContent =
    `${order.created_at} · ${order.cashier}`;
  renderRows(
    "order-dialog-lines",
    order.lines,
    (l) => [
      createCell(l.item_name),
      createCell(l.quantity, true),
      createCell(formatMoney(l.unit_price), true),
      createCell(formatMoney(l.line_total), true),
    ],
    "No lines",
  );
  document.getElementById("order-dialog-total").textContent = formatMoney(order.total);
  dialog.showModal();
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
loadCategoryReport();
loadItemReport();
for (const button of document.querySelectorAll(".period-button")) {
  button.addEventListener("click", () => selectPeriod(button.dataset.period));
}
selectPeriod(selectedPeriod);

const statusEl = document.getElementById("status");
const reqIdEl = document.getElementById("reqId");
const productsEl = document.getElementById("products");
const checkoutResultEl = document.getElementById("checkoutResult");
const healthResultEl = document.getElementById("healthResult");

function setStatus(msg) {
  statusEl.textContent = msg;
}

function setReqIdFromResponse(resp) {
  const rid = resp.headers.get("x-request-id") || resp.headers.get("X-Request-ID");
  if (rid) reqIdEl.textContent = rid;
}

async function apiFetch(url, opts = {}) {
  const resp = await fetch(url, {
    ...opts,
    headers: {
      "Content-Type": "application/json",
      ...(opts.headers || {}),
    },
    credentials: "include",
  });
  setReqIdFromResponse(resp);
  if (!resp.ok) {
    const txt = await resp.text();
    throw new Error(`${resp.status} ${resp.statusText}: ${txt}`);
  }
  return resp;
}

function renderProducts(items) {
  productsEl.innerHTML = "";
  for (const p of items) {
    const div = document.createElement("div");
    div.className = "product";
    div.innerHTML = `
      <div><strong>${p.name}</strong></div>
      <div class="muted">id: <code>${p.id}</code></div>
      <div>price_cents: <code>${p.price_cents}</code></div>
    `;
    productsEl.appendChild(div);
  }
}

async function loadProducts() {
  setStatus("Loading products…");
  const resp = await apiFetch("/products");
  const items = await resp.json();
  renderProducts(items);
  setStatus(`Loaded ${items.length} products.`);
}

async function login() {
  setStatus("Logging in (creating session cookie)…");
  const resp = await apiFetch("/login", { method: "POST", body: JSON.stringify({}) });
  const data = await resp.json();
  setStatus(`Logged in. session_id=${data.session_id}`);
}

async function viewCart() {
  setStatus("Fetching cart…");
  const resp = await apiFetch("/cart");
  const data = await resp.json();
  setStatus("Cart fetched.");
  alert(JSON.stringify(data, null, 2));
}

async function callHealth(path) {
  setStatus(`Calling ${path}…`);
  const resp = await apiFetch(path);
  const data = await resp.json();
  healthResultEl.textContent = JSON.stringify(data, null, 2);
  setStatus(`${path} OK`);
}

document.getElementById("btnLogin").addEventListener("click", () => login().catch(e => setStatus(e.message)));
document.getElementById("btnRefresh").addEventListener("click", () => loadProducts().catch(e => setStatus(e.message)));
document.getElementById("btnCart").addEventListener("click", () => viewCart().catch(e => setStatus(e.message)));
document.getElementById("btnHealth").addEventListener("click", () => callHealth("/healthz").catch(e => setStatus(e.message)));
document.getElementById("btnReady").addEventListener("click", () => callHealth("/readyz").catch(e => setStatus(e.message)));

document.getElementById("checkoutForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  checkoutResultEl.textContent = "";
  setStatus("Creating order…");

  const total = Number(document.getElementById("totalCents").value);
  const userId = document.getElementById("userId").value;

  try {
    const resp = await apiFetch("/checkout", {
      method: "POST",
      body: JSON.stringify({ user_id: userId, total_cents: total }),
    });
    const data = await resp.json();
    checkoutResultEl.textContent = JSON.stringify(data, null, 2);
    setStatus("Order created.");
  } catch (err) {
    setStatus(err.message);
  }
});

// initial load
loadProducts().catch(e => setStatus(e.message));
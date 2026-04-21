const state = {
  token: localStorage.getItem("token"),
  user: null,
  cart: null,
};

const $ = (id) => document.getElementById(id);
const authHeaders = () =>
  state.token ? { Authorization: `Bearer ${state.token}`, "Content-Type": "application/json" } : {};

function toast(message) {
  const el = $("toast");
  el.innerText = message;
  el.style.display = "block";
  setTimeout(() => (el.style.display = "none"), 2200);
}

async function api(path, options = {}) {
  const response = await fetch(path, options);
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.detail || "Request failed");
  return data;
}

function productCard(p) {
  return `
    <div class="card">
      <h3>${p.name}</h3>
      <p>${p.description}</p>
      <p>Category: ${p.category}</p>
      <p>Price: $${p.price} | Rating: ${p.rating}</p>
      <p>Stock: ${p.stock}</p>
      ${p.image_url ? `<img src="${p.image_url}" alt="${p.name}" width="120" />` : ""}
      <button onclick="addToCart(${p.id})">Add to cart</button>
    </div>
  `;
}

function renderProducts(products) {
  $("products").innerHTML = products.map(productCard).join("") || "No products found.";
}

function renderCart(cart) {
  if (!cart || !cart.items || cart.items.length === 0) {
    $("cart").innerHTML = "Cart is empty.";
    return;
  }
  $("cart").innerHTML = `
    ${cart.items
      .map(
        (item) => `
      <div class="card">
        <strong>${item.product_name}</strong> x ${item.quantity} = $${item.line_total}
        <div class="button-row">
          <button onclick="changeQty(${item.id}, ${item.quantity + 1})">+</button>
          <button onclick="changeQty(${item.id}, ${Math.max(1, item.quantity - 1)})">-</button>
          <button onclick="removeItem(${item.id})">Remove</button>
        </div>
      </div>
    `
      )
      .join("")}
    <h3>Total: $${cart.cart_total}</h3>
  `;
}

function renderOrders(orders) {
  $("orders").innerHTML =
    orders
      .map(
        (order) => `
      <div class="card">
        <strong>Order #${order.id}</strong> - ${order.status}<br/>
        Amount: $${order.total_amount}<br/>
        Address: ${order.shipping_address}<br/>
        Items: ${order.items.map((i) => `${i.product_name} x${i.quantity}`).join(", ")}
      </div>
    `
      )
      .join("") || "No orders yet.";
}

async function loadProducts() {
  const q = $("searchInput").value;
  const category = $("categoryInput").value;
  const sortBy = $("sortByInput").value;
  const order = $("sortOrderInput").value;
  const params = new URLSearchParams({ q, category, sort_by: sortBy, order });
  const products = await api(`/api/products?${params.toString()}`);
  renderProducts(products);
  const categories = [...new Set(products.map((p) => p.category))];
  $("categoryInput").innerHTML =
    '<option value="">All Categories</option>' +
    categories.map((cat) => `<option value="${cat}">${cat}</option>`).join("");
}

async function loadProfileAndData() {
  if (!state.token) return;
  try {
    state.user = await api("/api/users/me", { headers: authHeaders() });
    $("authStatus").innerText = `Logged in as ${state.user.full_name} (${state.user.email})`;
    $("adminPanel").style.display = state.user.is_admin ? "block" : "none";
    await loadCart();
    await loadOrders();
    if (state.user.is_admin) await loadAdmin();
  } catch (e) {
    toast(e.message);
  }
}

async function loadCart() {
  if (!state.token) return;
  state.cart = await api("/api/cart", { headers: authHeaders() });
  renderCart(state.cart);
}

async function loadOrders() {
  if (!state.token) return;
  const orders = await api("/api/orders", { headers: authHeaders() });
  renderOrders(orders);
}

async function loadAdmin() {
  const dash = await api("/api/admin/dashboard", { headers: authHeaders() });
  $("adminSummary").innerText = `Users: ${dash.users_count}, Products: ${dash.products_count}, Orders: ${dash.orders_count}, Revenue: $${dash.revenue}`;
}

async function signup() {
  const payload = {
    full_name: $("nameInput").value,
    email: $("emailInput").value,
    password: $("passwordInput").value,
  };
  const data = await api("/api/auth/signup", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  state.token = data.access_token;
  localStorage.setItem("token", state.token);
  toast("Signup successful");
  await loadProfileAndData();
}

async function login() {
  const payload = { email: $("emailInput").value, password: $("passwordInput").value };
  const data = await api("/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  state.token = data.access_token;
  localStorage.setItem("token", state.token);
  toast("Login successful");
  await loadProfileAndData();
}

function logout() {
  state.token = null;
  state.user = null;
  localStorage.removeItem("token");
  $("authStatus").innerText = "Not logged in";
  $("adminPanel").style.display = "none";
  $("cart").innerHTML = "Cart is empty.";
  $("orders").innerHTML = "No orders yet.";
  toast("Logged out");
}

async function addToCart(productId) {
  if (!state.token) return toast("Please login first");
  await api("/api/cart", {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({ product_id: productId, quantity: 1 }),
  });
  toast("Added to cart");
  await loadCart();
}

async function changeQty(itemId, qty) {
  await api(`/api/cart/${itemId}`, {
    method: "PUT",
    headers: authHeaders(),
    body: JSON.stringify({ quantity: qty }),
  });
  await loadCart();
}

async function removeItem(itemId) {
  await api(`/api/cart/${itemId}`, { method: "DELETE", headers: authHeaders() });
  await loadCart();
}

async function checkout() {
  const shipping_address = $("shippingAddress").value;
  await api("/api/orders/checkout", {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({ shipping_address }),
  });
  toast("Order placed");
  await loadCart();
  await loadOrders();
  if (state.user?.is_admin) await loadAdmin();
}

async function createProduct() {
  const fileInput = $("adminProductImage");
  let imageUrl = null;
  if (fileInput.files[0]) {
    const form = new FormData();
    form.append("image", fileInput.files[0]);
    const upload = await api("/api/admin/products/upload-image", {
      method: "POST",
      headers: state.token ? { Authorization: `Bearer ${state.token}` } : {},
      body: form,
    });
    imageUrl = upload.image_url;
  }

  const payload = {
    name: $("adminProductName").value,
    category: $("adminProductCategory").value,
    price: Number($("adminProductPrice").value),
    stock: Number($("adminProductStock").value),
    rating: Number($("adminProductRating").value || 0),
    description: $("adminProductDesc").value,
    image_url: imageUrl,
  };
  await api("/api/admin/products", {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify(payload),
  });
  toast("Product created");
  await loadProducts();
  await loadAdmin();
}

$("refreshBtn").onclick = () => loadProducts().catch((e) => toast(e.message));
$("signupBtn").onclick = () => signup().catch((e) => toast(e.message));
$("loginBtn").onclick = () => login().catch((e) => toast(e.message));
$("logoutBtn").onclick = logout;
$("checkoutBtn").onclick = () => checkout().catch((e) => toast(e.message));
$("createProductBtn").onclick = () => createProduct().catch((e) => toast(e.message));

loadProducts().catch((e) => toast(e.message));
loadProfileAndData();

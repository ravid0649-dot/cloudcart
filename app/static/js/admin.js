async function loadAdmin() {
  const user = await CloudCart.requireUser();
  if (!user) return (location.href = "/static/auth.html");
  if (!user.is_admin) return (CloudCart.$("adminStats").innerHTML = '<div class="empty">Admin access only.</div>');

  const dash = await CloudCart.api("/api/admin/dashboard", { headers: CloudCart.authHeaders(false) });
  const orders = await CloudCart.api("/api/admin/orders", { headers: CloudCart.authHeaders(false) });

  CloudCart.$("adminStats").innerHTML = `
    <div class="stat-card"><div class="stat-title">Users</div><div class="stat-value">${dash.users_count}</div></div>
    <div class="stat-card"><div class="stat-title">Products</div><div class="stat-value">${dash.products_count}</div></div>
    <div class="stat-card"><div class="stat-title">Orders</div><div class="stat-value">${dash.orders_count}</div></div>
    <div class="stat-card"><div class="stat-title">Revenue</div><div class="stat-value">${CloudCart.money(dash.revenue)}</div></div>
  `;

  CloudCart.$("adminOrders").innerHTML = orders.orders
    .slice(0, 8)
    .map(
      (order) => `
      <div class="list-item">
        <div class="row space-between">
          <strong>#${order.id}</strong>
          ${CloudCart.statusBadge(order.status)}
        </div>
        <div class="product-meta">${CloudCart.money(order.total_amount)} • ${order.items.length} items</div>
      </div>
    `
    )
    .join("");
}

async function createProduct() {
  let image_url = null;
  const file = CloudCart.$("pImage").files[0];
  if (file) {
    const form = new FormData();
    form.append("image", file);
    const upload = await CloudCart.api("/api/admin/products/upload-image", {
      method: "POST",
      headers: { Authorization: `Bearer ${CloudCart.state.token}` },
      body: form,
    });
    image_url = upload.image_url;
  }

  await CloudCart.api("/api/admin/products", {
    method: "POST",
    headers: CloudCart.authHeaders(),
    body: JSON.stringify({
      name: CloudCart.$("pName").value,
      category: CloudCart.$("pCategory").value,
      price: Number(CloudCart.$("pPrice").value),
      stock: Number(CloudCart.$("pStock").value),
      rating: Number(CloudCart.$("pRating").value || 0),
      description: CloudCart.$("pDescription").value,
      image_url,
    }),
  });
  CloudCart.toast("Product created");
  await loadAdmin();
}

(async () => {
  CloudCart.mountAuthChip();
  await loadAdmin();
  CloudCart.$("createProductBtn").onclick = () => createProduct().catch((e) => CloudCart.toast(e.message));
})().catch((error) => CloudCart.toast(error.message));

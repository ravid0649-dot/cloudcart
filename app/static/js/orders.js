(async () => {
  CloudCart.mountAuthChip();
  const user = await CloudCart.requireUser();
  if (!user) return (location.href = "/static/auth.html");
  const orders = await CloudCart.api("/api/orders", { headers: CloudCart.authHeaders(false) });
  CloudCart.$("ordersList").innerHTML =
    orders.length === 0
      ? '<div class="empty">No orders yet. Start shopping and place your first order.</div>'
      : orders
          .map(
            (order) => `
      <div class="list-item">
        <div class="row space-between">
          <strong>Order #${order.id}</strong>
          ${CloudCart.statusBadge(order.status)}
        </div>
        <div class="product-meta">Total: ${CloudCart.money(order.total_amount)} • ${new Date(order.created_at).toLocaleString()}</div>
        <div>Address: ${order.shipping_address}</div>
        <div class="product-meta">Items: ${order.items.map((x) => `${x.product_name} x${x.quantity}`).join(", ")}</div>
      </div>
    `
          )
          .join("");
})().catch((error) => CloudCart.toast(error.message));

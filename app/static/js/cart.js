async function loadCart() {
  const user = await CloudCart.requireUser();
  if (!user) return (location.href = "/static/auth.html");

  const cart = await CloudCart.api("/api/cart", { headers: CloudCart.authHeaders(false) });
  CloudCart.$("cartTotal").innerText = CloudCart.money(cart.cart_total);
  const html =
    cart.items.length === 0
      ? '<div class="empty">Your cart is empty. Add products to continue.</div>'
      : cart.items
          .map(
            (item) => `
      <div class="list-item">
        <div class="row space-between">
          <strong>${item.product_name}</strong>
          <span>${CloudCart.money(item.line_total)}</span>
        </div>
        <div class="product-meta">Qty: ${item.quantity} • Unit: ${CloudCart.money(item.unit_price)}</div>
        <div class="row" style="margin-top:8px;">
          <button class="btn" onclick="changeQty(${item.id}, ${item.quantity + 1})">+</button>
          <button class="btn" onclick="changeQty(${item.id}, ${Math.max(1, item.quantity - 1)})">-</button>
          <button class="btn danger" onclick="removeItem(${item.id})">Remove</button>
        </div>
      </div>
    `
          )
          .join("");
  CloudCart.$("cartItems").innerHTML = html;
}

async function changeQty(itemId, qty) {
  await CloudCart.api(`/api/cart/${itemId}`, {
    method: "PUT",
    headers: CloudCart.authHeaders(),
    body: JSON.stringify({ quantity: qty }),
  });
  await loadCart();
}

async function removeItem(itemId) {
  await CloudCart.api(`/api/cart/${itemId}`, {
    method: "DELETE",
    headers: CloudCart.authHeaders(false),
  });
  await loadCart();
}

async function checkout() {
  const shippingAddress = CloudCart.$("shippingAddress").value.trim();
  if (shippingAddress.length < 10) return CloudCart.toast("Please enter full shipping address");
  await CloudCart.api("/api/orders/checkout", {
    method: "POST",
    headers: CloudCart.authHeaders(),
    body: JSON.stringify({ shipping_address: shippingAddress }),
  });
  CloudCart.toast("Order placed successfully");
  await loadCart();
}

(async () => {
  CloudCart.mountAuthChip();
  await loadCart();
  CloudCart.$("placeOrderBtn").onclick = () => checkout().catch((e) => CloudCart.toast(e.message));
})();

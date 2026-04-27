const CloudCart = (() => {
  const state = {
    token: localStorage.getItem("token"),
    user: null,
    wishlist: JSON.parse(localStorage.getItem("wishlist") || "[]"),
  };

  const $ = (id) => document.getElementById(id);
  const money = (n) => `$${Number(n || 0).toFixed(2)}`;

  function toast(message) {
    const el = $("toast");
    if (!el) return;
    el.innerText = message;
    el.style.display = "block";
    setTimeout(() => {
      el.style.display = "none";
    }, 2200);
  }

  async function api(path, options = {}) {
    const response = await fetch(path, options);
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.detail || "Request failed");
    return data;
  }

  function authHeaders(isJson = true) {
    const headers = {};
    if (state.token) headers.Authorization = `Bearer ${state.token}`;
    if (isJson) headers["Content-Type"] = "application/json";
    return headers;
  }

  async function requireUser() {
    if (!state.token) return null;
    if (state.user) return state.user;
    state.user = await api("/api/users/me", { headers: authHeaders(false) });
    return state.user;
  }

  function setToken(token) {
    state.token = token;
    localStorage.setItem("token", token);
    state.user = null;
  }

  function logout() {
    state.token = null;
    state.user = null;
    localStorage.removeItem("token");
  }

  function toggleWishlist(productId) {
    const idx = state.wishlist.indexOf(productId);
    if (idx >= 0) {
      state.wishlist.splice(idx, 1);
      toast("Removed from wishlist");
    } else {
      state.wishlist.push(productId);
      toast("Saved to wishlist");
    }
    localStorage.setItem("wishlist", JSON.stringify(state.wishlist));
  }

  function wishlistHas(productId) {
    return state.wishlist.includes(productId);
  }

  function navAuthLabel() {
    return state.token ? "Logged in" : "Guest";
  }

  async function addToCart(productId, quantity = 1) {
    if (!state.token) {
      toast("Please login to add items");
      location.href = "/static/auth.html";
      return;
    }
    await api("/api/cart", {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify({ product_id: productId, quantity }),
    });
    toast("Added to cart");
  }

  function productCard(product) {
    const name = product?.name || "Unnamed product";
    const category = product?.category || "General";
    const rating = Number(product?.rating ?? 0).toFixed(1);
    const description = (product?.description || "No description available.").slice(0, 92);
    const heart = wishlistHas(product.id) ? "♥" : "♡";
    const image = product.image_url
      ? `<img src="${product.image_url}" alt="${name}" />`
      : '<div class="placeholder-thumb">🛍️</div>';
    return `
      <article class="product-card">
        <div class="product-thumb">${image}</div>
        <div class="product-body">
          <div class="row space-between">
            <strong>${name}</strong>
            <span class="price">${money(product.price)}</span>
          </div>
          <div class="product-meta">${category} • Rating ${rating}</div>
          <p>${description}...</p>
          <div class="row">
            <button class="btn primary" onclick="CloudCart.addToCart(${product.id})">Add to cart</button>
            <button class="btn ghost" onclick="CloudCart.toggleWishlist(${product.id}); CloudCart.refreshProducts?.()">${heart}</button>
          </div>
        </div>
      </article>
    `;
  }

  function statusBadge(status) {
    return `<span class="badge ${status}">${status}</span>`;
  }

  function mountAuthChip() {
    const el = $("authChip");
    if (el) el.innerText = navAuthLabel();
  }

  return {
    state,
    $,
    api,
    toast,
    money,
    authHeaders,
    setToken,
    logout,
    requireUser,
    mountAuthChip,
    productCard,
    addToCart,
    toggleWishlist,
    wishlistHas,
    statusBadge,
  };
})();

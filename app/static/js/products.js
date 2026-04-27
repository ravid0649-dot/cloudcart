const grid = CloudCart.$("productsGrid");
const searchInput = CloudCart.$("searchInput");
const categoryInput = CloudCart.$("categoryInput");
const sortByInput = CloudCart.$("sortByInput");
const sortOrderInput = CloudCart.$("sortOrderInput");

function buildQuery() {
  const params = new URLSearchParams();
  const q = searchInput.value.trim();
  const category = categoryInput.value.trim();
  const sort_by = sortByInput.value;
  const order = sortOrderInput.value;

  if (q) params.set("q", q);
  if (category) params.set("category", category);
  if (sort_by) params.set("sort_by", sort_by);
  if (order) params.set("order", order);
  return params.toString();
}

async function loadCategoryOptions(products) {
  const categories = [
    ...new Set(products.map((p) => (p.category || "General").trim()).filter(Boolean)),
  ].sort();
  const current = categoryInput.value;
  categoryInput.innerHTML =
    '<option value="">All categories</option>' +
    categories.map((category) => `<option value="${category}">${category}</option>`).join("");
  categoryInput.value = categories.includes(current) ? current : "";
}

async function loadProducts() {
  const selectedCategory = categoryInput.value.trim();
  const query = buildQuery();
  const endpoint = query ? `/api/products?${query}` : "/api/products";
  const payload = await CloudCart.api(endpoint);
  const products = Array.isArray(payload) ? payload : [];

  await loadCategoryOptions(products);
  categoryInput.value =
    selectedCategory && [...categoryInput.options].some((option) => option.value === selectedCategory)
      ? selectedCategory
      : "";

  if (!products.length) {
    grid.innerHTML = '<div class="empty">No products match these filters.</div>';
    return;
  }

  grid.innerHTML = products.map(renderProductCard).join("");
}

function renderProductCard(product) {
  const id = Number(product?.id || 0);
  const name = String(product?.name || "Unnamed product");
  const category = String(product?.category || "General");
  const rating = Number(product?.rating ?? 0).toFixed(1);
  const price = CloudCart.money(product?.price ?? 0);
  const description = String(product?.description || "No description available.").slice(0, 92);
  const image = product?.image_url
    ? `<img src="${product.image_url}" alt="${name}" />`
    : '<div class="placeholder-thumb">🛍️</div>';

  return `
    <article class="product-card">
      <div class="product-thumb">${image}</div>
      <div class="product-body">
        <div class="row space-between">
          <strong>${name}</strong>
          <span class="price">${price}</span>
        </div>
        <div class="product-meta">${category} • Rating ${rating}</div>
        <p>${description}...</p>
        <div class="row">
          <button class="btn primary" onclick="CloudCart.addToCart(${id || 0})">Add to cart</button>
          <button class="btn ghost" onclick="CloudCart.toggleWishlist(${id || 0}); CloudCart.refreshProducts?.()">♡</button>
        </div>
      </div>
    </article>
  `;
}

async function bootstrapProductsPage() {
  CloudCart.mountAuthChip();
  const initialProducts = await CloudCart.api("/api/products");
  await loadCategoryOptions(initialProducts);
  await loadProducts();
}

CloudCart.refreshProducts = () => loadProducts().catch((error) => CloudCart.toast(error.message));

CloudCart.$("applyFiltersBtn").onclick = () => loadProducts().catch((error) => CloudCart.toast(error.message));
CloudCart.$("clearFiltersBtn").onclick = () => {
  searchInput.value = "";
  categoryInput.value = "";
  sortByInput.value = "created_at";
  sortOrderInput.value = "desc";
  loadProducts().catch((error) => CloudCart.toast(error.message));
};

bootstrapProductsPage().catch((error) => {
  grid.innerHTML = `<div class="empty">Failed to load products: ${String(error?.message || error)}</div>`;
  CloudCart.toast(error.message || "Failed to load products");
});
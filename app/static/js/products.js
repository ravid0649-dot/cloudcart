async function loadProducts() {
  const q = CloudCart.$("searchInput").value || "";
  const category = CloudCart.$("categoryInput").value || "";
  const sortBy = CloudCart.$("sortByInput").value;
  const order = CloudCart.$("sortOrderInput").value;
  const params = new URLSearchParams({ q, category, sort_by: sortBy, order });
  const products = await CloudCart.api(`/api/products?${params.toString()}`);

  CloudCart.$("productsGrid").innerHTML =
    products.length > 0
      ? products.map(CloudCart.productCard).join("")
      : '<div class="empty">No products match your search.</div>';

  const categories = [...new Set(products.map((p) => p.category))];
  const currentValue = CloudCart.$("categoryInput").value;
  CloudCart.$("categoryInput").innerHTML =
    '<option value="">All categories</option>' +
    categories.map((cat) => `<option value="${cat}">${cat}</option>`).join("");
  CloudCart.$("categoryInput").value = currentValue;
}

(async () => {
  CloudCart.mountAuthChip();
  await loadProducts();
  CloudCart.refreshProducts = loadProducts;
  CloudCart.$("applyFiltersBtn").onclick = () => loadProducts().catch((e) => CloudCart.toast(e.message));
  CloudCart.$("clearFiltersBtn").onclick = () => {
    CloudCart.$("searchInput").value = "";
    CloudCart.$("categoryInput").value = "";
    CloudCart.$("sortByInput").value = "created_at";
    CloudCart.$("sortOrderInput").value = "desc";
    loadProducts().catch((e) => CloudCart.toast(e.message));
  };
})().catch((error) => CloudCart.toast(error.message));

const container = document.getElementById("trendingProducts");

async function loadProducts() {
  try {
    CloudCart.mountAuthChip();
    const products = await CloudCart.api("/api/products?sort_by=rating&order=desc");

    if (!products.length) {
      container.innerHTML = '<div class="empty">No products available right now.</div>';
      return;
    }

    container.innerHTML = products
      .slice(0, 6)
      .map((product) => CloudCart.productCard(product))
      .join("");
  } catch (err) {
    container.innerHTML = '<div class="empty">Failed to load products.</div>';
  }
}

loadProducts();
(async () => {
  CloudCart.mountAuthChip();
  const products = await CloudCart.api("/api/products?sort_by=rating&order=desc");
  const trending = products.slice(0, 8);
  const target = CloudCart.$("trendingProducts");
  target.innerHTML = trending.map(CloudCart.productCard).join("");
  CloudCart.refreshProducts = () => {
    target.innerHTML = trending.map(CloudCart.productCard).join("");
  };
})().catch((error) => CloudCart.toast(error.message));

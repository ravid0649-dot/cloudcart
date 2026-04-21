async function login() {
  const email = CloudCart.$("emailInput").value;
  const password = CloudCart.$("passwordInput").value;
  const data = await CloudCart.api("/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  CloudCart.setToken(data.access_token);
  CloudCart.toast("Welcome back");
  location.href = "/";
}

async function signup() {
  const full_name = CloudCart.$("fullNameInput").value;
  const email = CloudCart.$("emailInput").value;
  const password = CloudCart.$("passwordInput").value;
  const data = await CloudCart.api("/api/auth/signup", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ full_name, email, password }),
  });
  CloudCart.setToken(data.access_token);
  CloudCart.toast("Account created");
  location.href = "/";
}

CloudCart.mountAuthChip();
CloudCart.$("loginBtn").onclick = () => login().catch((e) => CloudCart.toast(e.message));
CloudCart.$("signupBtn").onclick = () => signup().catch((e) => CloudCart.toast(e.message));

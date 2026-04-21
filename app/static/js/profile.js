async function loadProfile() {
  const user = await CloudCart.requireUser();
  if (!user) return (location.href = "/static/auth.html");
  CloudCart.$("fullNameInput").value = user.full_name || "";
  CloudCart.$("phoneInput").value = user.phone || "";
  CloudCart.$("addressInput").value = user.address || "";
  CloudCart.$("profileSnapshot").innerHTML = `
    <div class="list-item"><strong>Email:</strong> ${user.email}</div>
    <div class="list-item"><strong>Role:</strong> ${user.is_admin ? "Admin" : "Customer"}</div>
    <div class="list-item"><strong>Member Since:</strong> ${new Date(user.created_at).toLocaleDateString()}</div>
  `;
}

async function saveProfile() {
  await CloudCart.api("/api/users/me", {
    method: "PUT",
    headers: CloudCart.authHeaders(),
    body: JSON.stringify({
      full_name: CloudCart.$("fullNameInput").value,
      phone: CloudCart.$("phoneInput").value,
      address: CloudCart.$("addressInput").value,
    }),
  });
  CloudCart.state.user = null;
  await loadProfile();
  CloudCart.toast("Profile updated");
}

(async () => {
  CloudCart.mountAuthChip();
  await loadProfile();
  CloudCart.$("saveProfileBtn").onclick = () => saveProfile().catch((e) => CloudCart.toast(e.message));
  CloudCart.$("logoutBtn").onclick = () => {
    CloudCart.logout();
    location.href = "/";
  };
})().catch((error) => CloudCart.toast(error.message));

const api = "/api";
const state = { coaches: [], selectedCoach: null, threadId: null };

const elements = {
  coachList: document.querySelector("#coach-list"),
  specialtyFilter: document.querySelector("#specialty-filter"),
  onlineCount: document.querySelector("#online-count"),
  emptyState: document.querySelector("#empty-state"),
  coachDetail: document.querySelector("#coach-detail"),
  detailName: document.querySelector("#detail-name"),
  detailBio: document.querySelector("#detail-bio"),
  detailSpecialties: document.querySelector("#detail-specialties"),
  detailExperience: document.querySelector("#detail-experience"),
  detailRate: document.querySelector("#detail-rate"),
  detailRating: document.querySelector("#detail-rating"),
  detailOnline: document.querySelector("#detail-online"),
  slotList: document.querySelector("#slot-list"),
  chatSection: document.querySelector("#chat-section"),
  threadId: document.querySelector("#thread-id"),
  attachmentForm: document.querySelector("#attachment-form"),
  attachmentInput: document.querySelector("#attachment-input"),
  appointmentList: document.querySelector("#appointment-list"),
  toast: document.querySelector("#toast"),
};

async function request(path, options = {}) {
  const response = await fetch(`${api}${path}`, {
    credentials: "same-origin",
    ...options,
    headers: { Accept: "application/json", ...(options.headers || {}) },
  });
  if (!response.ok) {
    let message = "Something went wrong.";
    try {
      const payload = await response.json();
      message = payload.detail || payload.error?.message || message;
    } catch (_) {
      message = response.status === 401 ? "Please sign in through PolyLife first." : message;
    }
    throw new Error(message);
  }
  return response.status === 204 ? null : response.json();
}

function showToast(message, isError = false) {
  elements.toast.textContent = message;
  elements.toast.classList.toggle("error", isError);
  elements.toast.hidden = false;
  window.clearTimeout(showToast.timeout);
  showToast.timeout = window.setTimeout(() => { elements.toast.hidden = true; }, 4200);
}

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>'"]/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" })[char]);
}

function formatDate(value) {
  return new Intl.DateTimeFormat(undefined, { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
}

function renderCoaches() {
  const query = elements.specialtyFilter.value.trim().toLowerCase();
  const visible = state.coaches.filter((coach) => {
    return !query || (coach.specialties || []).join(" ").toLowerCase().includes(query);
  });
  if (!visible.length) {
    elements.coachList.innerHTML = '<p class="empty-list">No coaches match this specialty.</p>';
    return;
  }
  elements.coachList.innerHTML = visible.map((coach) => `
    <button class="coach-card" type="button" data-coach-id="${coach.user_id}" aria-current="${state.selectedCoach?.user_id === coach.user_id}">
      <span class="coach-card-top"><strong>Coach #${coach.user_id}</strong><i class="online-indicator ${coach.is_online ? "online" : ""}"></i></span>
      <span class="card-meta"><span>${escapeHtml((coach.specialties || ["General wellness"]).join(" · "))}</span><span>${coach.avg_rating ? `${coach.avg_rating.toFixed(1)} / 5` : "New"}</span></span>
    </button>
  `).join("");
}

async function loadCoaches() {
  const [coaches, online] = await Promise.all([
    request("/reserve/coaches"),
    request("/chat/coaches/online"),
  ]);
  const onlineIds = new Set(online.data.map((coach) => coach.user_id));
  state.coaches = coaches.data.map((coach) => ({ ...coach, is_online: onlineIds.has(coach.user_id) }));
  elements.onlineCount.textContent = `${onlineIds.size} coach${onlineIds.size === 1 ? "" : "es"} online now`;
  renderCoaches();
}

async function selectCoach(coachId) {
  const response = await request(`/reserve/coaches/${coachId}`);
  state.selectedCoach = response.data;
  state.threadId = null;
  elements.chatSection.hidden = true;
  elements.emptyState.hidden = true;
  elements.coachDetail.hidden = false;
  const coach = state.selectedCoach;
  elements.detailName.textContent = `Coach #${coach.user_id}`;
  elements.detailBio.textContent = coach.bio || "This coach has not added a bio yet.";
  elements.detailSpecialties.textContent = (coach.specialties || ["General wellness"]).join(", ");
  elements.detailExperience.textContent = coach.years_experience == null ? "Not listed" : `${coach.years_experience} years`;
  elements.detailRate.textContent = `${coach.hourly_rate} per hour`;
  elements.detailRating.textContent = coach.avg_rating ? `${coach.avg_rating.toFixed(1)} / 5 (${coach.rating_count})` : "No ratings yet";
  elements.detailOnline.textContent = coach.is_online ? "Online" : "Offline";
  elements.detailOnline.classList.toggle("availability-pill", coach.is_online);
  renderCoaches();
  await loadSlots();
}

async function loadSlots() {
  if (!state.selectedCoach) return;
  elements.slotList.innerHTML = '<p class="empty-list">Loading open times...</p>';
  const response = await request(`/reserve/coaches/${state.selectedCoach.user_id}/availability`);
  if (!response.data.length) {
    elements.slotList.innerHTML = '<p class="empty-list">No open times are listed right now.</p>';
    return;
  }
  elements.slotList.innerHTML = response.data.map((slot) => `
    <article class="slot-card">
      <div><time datetime="${slot.start_at}">${formatDate(slot.start_at)}</time><small>Ends ${formatDate(slot.end_at)}</small></div>
      <button class="button button-quiet" data-book-slot="${slot.id}" type="button">Reserve</button>
    </article>
  `).join("");
}

async function bookSlot(slotId) {
  const notes = window.prompt("Optional note for your coach:", "");
  if (notes === null) return;
  await request("/reserve/appointments", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ availability_id: Number(slotId), notes: notes || null }),
  });
  showToast("Your session is reserved.");
  await loadSlots();
}

async function openConversation() {
  if (!state.selectedCoach) return;
  const response = await request("/chat/threads", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ coach_user_id: state.selectedCoach.user_id }),
  });
  state.threadId = response.data.id;
  elements.threadId.textContent = `Thread #${state.threadId}`;
  elements.chatSection.hidden = false;
  showToast("Private conversation opened.");
}

async function uploadAttachment(event) {
  event.preventDefault();
  if (!state.threadId || !elements.attachmentInput.files[0]) return;
  const form = new FormData();
  form.append("file", elements.attachmentInput.files[0]);
  await request(`/chat/threads/${state.threadId}/attachments`, { method: "POST", body: form });
  elements.attachmentForm.reset();
  showToast("Your attachment was shared with the coach.");
}

async function loadAppointments() {
  const response = await request("/reserve/appointments");
  if (!response.data.length) {
    elements.appointmentList.innerHTML = '<p class="empty-list">You do not have any appointments yet.</p>';
    return;
  }
  elements.appointmentList.innerHTML = response.data.map((appointment) => `
    <article class="appointment-card"><div><strong>Coach #${appointment.coach_user_id}</strong><br><small>Status: ${escapeHtml(appointment.status)} · Slot #${appointment.availability_id}</small></div><span class="status-dot">${escapeHtml(appointment.status)}</span></article>
  `).join("");
}

document.querySelector("#refresh-button").addEventListener("click", () => loadCoaches().catch((error) => showToast(error.message, true)));
document.querySelector("#reload-slots-button").addEventListener("click", () => loadSlots().catch((error) => showToast(error.message, true)));
document.querySelector("#start-chat-button").addEventListener("click", () => openConversation().catch((error) => showToast(error.message, true)));
document.querySelector("#appointments-button").addEventListener("click", () => loadAppointments().catch((error) => showToast(error.message, true)));
elements.specialtyFilter.addEventListener("input", renderCoaches);
elements.coachList.addEventListener("click", (event) => {
  const card = event.target.closest("[data-coach-id]");
  if (card) selectCoach(card.dataset.coachId).catch((error) => showToast(error.message, true));
});
elements.slotList.addEventListener("click", (event) => {
  const button = event.target.closest("[data-book-slot]");
  if (button) bookSlot(button.dataset.bookSlot).catch((error) => showToast(error.message, true));
});
elements.attachmentForm.addEventListener("submit", (event) => {
  uploadAttachment(event).catch((error) => showToast(error.message, true));
});

loadCoaches().catch((error) => showToast(error.message, true));

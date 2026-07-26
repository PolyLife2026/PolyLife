const api = "/api";
const authApi = "/auth";
const ACCESS_KEY = "polylife_token";
const REFRESH_KEY = "polylife_refresh";
const USER_KEY = "polylife_username";
const USER_ID_KEY = "polylife_user_id";
const LANGUAGE_KEY = "polylife_language";
const translations = {
  en: {
    documentTitle: "PolyLife | Coach Booking Space",
    brandLabel: "PolyLife Coach Booking Space",
    brandSpace: "Coach Booking Space",
    languageSwitchLabel: "Switch language to Persian",
    languageSwitchText: "فارسی",
    languageSwitchFlag: "🇮🇷",
    signedOut: "Signed out",
    signIn: "Sign in",
    signOut: "Sign out",
    refresh: "Refresh",
    signedInAs: "Signed in as {username}",
    authenticatedAs: "Authenticated as {username}",
    authenticatedThrough: "Authenticated through PolyLife",
    accountEyebrow: "PolyLife account",
    authHeading: "Your coach booking space;<br><em>simple, safe, and private.</em>",
    authDescription: "Sign in with your PolyLife account to browse coaches, reserve a session, and open your conversations.",
    username: "Username",
    password: "Password",
    enterCoachSpace: "Enter Coach Booking Space",
    developmentUsers: "Development users: user1, user2, or user3.",
    heroEyebrow: "A calmer way to grow",
    heroHeading: "Find the right coach.<br><em>Make time for yourself.</em>",
    heroDescription: "Browse available coaches, reserve an open session, and start a private conversation from one place.",
    checkingAvailability: "Checking availability...",
    workspaceLabel: "Coach booking workspace",
    directory: "Directory",
    meetCoaches: "Meet the coaches",
    searchSpecialty: "Search specialty",
    filterSpecialty: "Filter specialty",
    selectCoach: "Select a coach",
    selectCoachDescription: "View their profile, choose an open time, or begin a conversation.",
    coachProfile: "Coach profile",
    specialties: "Specialties",
    experience: "Experience",
    sessionRate: "Session rate",
    communityRating: "Community rating",
    openConversation: "Open conversation",
    reloadTimes: "Reload times",
    availability: "Availability",
    reserveTime: "Reserve a time",
    privateSpace: "Private space",
    conversation: "Conversation",
    chatNote: "Messages are saved privately in your conversation with this coach.",
    messageLabel: "Message",
    messagePlaceholder: "Write a message...",
    sendMessage: "Send",
    sendingMessage: "Sending...",
    messageSent: "Message sent.",
    noMessages: "No messages yet. Start the conversation.",
    you: "You",
    coach: "Coach",
    orShareFile: "or share a file",
    chooseAttachment: "Choose an attachment",
    noFileSelected: "No file selected",
    shareFile: "Share file",
    yourSchedule: "Your schedule",
    upcomingAppointments: "Upcoming appointments",
    loadAppointments: "Load appointments",
    cancelAppointment: "Cancel appointment",
    cancelAppointmentTitle: "Cancel this appointment?",
    cancelAppointmentDescription: "The appointment will be marked as cancelled and cannot be restored from this page.",
    keepAppointment: "Keep appointment",
    confirmCancellation: "Yes, cancel it",
    cancellingAppointment: "Cancelling...",
    appointmentCancelled: "Your appointment was cancelled.",
    statusConfirmed: "Confirmed",
    statusCancelled: "Cancelled",
    statusCompleted: "Completed",
    statusNoShow: "No-show",
    sessionExpired: "Your PolyLife session has expired.",
    genericError: "Something went wrong.",
    loginFailed: "Sign-in failed",
    incompleteLogin: "Core returned an incomplete login response.",
    noCoachMatch: "No coaches match this specialty.",
    coachLoadError: "Coach information could not be loaded.",
    availabilityError: "Availability is temporarily unavailable.",
    generalWellness: "General wellness",
    newCoach: "New",
    coachName: "Coach #{id}",
    coachesOnlineOne: "{count} coach online now",
    coachesOnlineMany: "{count} coaches online now",
    noBio: "This coach has not added a bio yet.",
    notListed: "Not listed",
    years: "{count} years",
    perHour: "{amount} per hour",
    rating: "{rating} / 5 ({count})",
    noRatings: "No ratings yet",
    online: "Online",
    offline: "Offline",
    loadingTimes: "Loading open times...",
    noOpenTimes: "No open times are listed right now.",
    ends: "Ends {date}",
    reserve: "Reserve",
    confirmReservation: "Confirm reservation",
    reserveSession: "Reserve this session?",
    optionalNote: "Optional note for your coach",
    notePlaceholder: "Anything your coach should know before the session...",
    cancel: "Cancel",
    confirmAndReserve: "Confirm reservation",
    reserving: "Reserving...",
    sessionReserved: "Your session is reserved.",
    thread: "Thread #{id}",
    conversationOpened: "Private conversation opened.",
    attachmentShared: "Your attachment was shared with the coach.",
    noAppointments: "You do not have any appointments yet.",
    status: "Status: {status}",
    slot: "Slot #{id}",
  },
  fa: {
    documentTitle: "پلی‌لایف | فضای رزرو مربی",
    brandLabel: "فضای رزرو مربی پلی‌لایف",
    brandSpace: "فضای رزرو مربی",
    languageSwitchLabel: "تغییر زبان به انگلیسی",
    languageSwitchText: "English",
    languageSwitchFlag: "🇺🇸",
    signedOut: "وارد نشده‌اید",
    signIn: "ورود",
    signOut: "خروج",
    refresh: "به‌روزرسانی",
    signedInAs: "واردشده با نام {username}",
    authenticatedAs: "احراز هویت‌شده با نام {username}",
    authenticatedThrough: "احراز هویت از طریق پلی‌لایف",
    accountEyebrow: "حساب پلی‌لایف",
    authHeading: "فضای رزرو مربی؛<br><em>ساده، امن و خصوصی.</em>",
    authDescription: "با حساب پلی‌لایف خود وارد شوید تا مربی‌ها را ببینید، جلسه رزرو کنید و گفت‌وگوهای خود را آغاز کنید.",
    username: "نام کاربری",
    password: "رمز عبور",
    enterCoachSpace: "ورود به فضای رزرو مربی",
    developmentUsers: "کاربران آزمایشی: user1، user2 یا user3.",
    heroEyebrow: "راهی آرام‌تر برای پیشرفت",
    heroHeading: "مربی مناسب را پیدا کنید.<br><em>برای خودتان وقت بگذارید.</em>",
    heroDescription: "مربی‌های در دسترس را ببینید، یک زمان آزاد رزرو کنید و از یک مکان گفت‌وگوی خصوصی خود را آغاز کنید.",
    checkingAvailability: "در حال بررسی وضعیت مربی‌ها...",
    workspaceLabel: "فضای رزرو مربی",
    directory: "فهرست مربی‌ها",
    meetCoaches: "با مربی‌ها آشنا شوید",
    searchSpecialty: "جست‌وجوی تخصص",
    filterSpecialty: "فیلتر براساس تخصص",
    selectCoach: "یک مربی انتخاب کنید",
    selectCoachDescription: "پروفایل مربی را ببینید، زمان آزاد انتخاب کنید یا گفت‌وگویی را آغاز کنید.",
    coachProfile: "پروفایل مربی",
    specialties: "تخصص‌ها",
    experience: "سابقه",
    sessionRate: "هزینه جلسه",
    communityRating: "امتیاز کاربران",
    openConversation: "شروع گفت‌وگو",
    reloadTimes: "بارگذاری دوباره زمان‌ها",
    availability: "زمان‌های آزاد",
    reserveTime: "یک زمان رزرو کنید",
    privateSpace: "فضای خصوصی",
    conversation: "گفت‌وگو",
    chatNote: "پیام‌ها به‌صورت خصوصی در گفت‌وگوی شما با این مربی ذخیره می‌شوند.",
    messageLabel: "پیام",
    messagePlaceholder: "پیام خود را بنویسید...",
    sendMessage: "ارسال",
    sendingMessage: "در حال ارسال...",
    messageSent: "پیام ارسال شد.",
    noMessages: "هنوز پیامی وجود ندارد. گفت‌وگو را آغاز کنید.",
    you: "شما",
    coach: "مربی",
    orShareFile: "یا یک فایل ارسال کنید",
    chooseAttachment: "انتخاب فایل",
    noFileSelected: "فایلی انتخاب نشده است",
    shareFile: "ارسال فایل",
    yourSchedule: "برنامه شما",
    upcomingAppointments: "جلسه‌های پیش رو",
    loadAppointments: "نمایش جلسه‌ها",
    cancelAppointment: "لغو رزرو",
    cancelAppointmentTitle: "این رزرو لغو شود؟",
    cancelAppointmentDescription: "وضعیت این جلسه به لغوشده تغییر می‌کند و از همین صفحه قابل بازگردانی نیست.",
    keepAppointment: "حفظ رزرو",
    confirmCancellation: "بله، لغو شود",
    cancellingAppointment: "در حال لغو...",
    appointmentCancelled: "رزرو شما با موفقیت لغو شد.",
    statusConfirmed: "تأییدشده",
    statusCancelled: "لغوشده",
    statusCompleted: "تکمیل‌شده",
    statusNoShow: "عدم حضور",
    sessionExpired: "نشست پلی‌لایف شما منقضی شده است.",
    genericError: "مشکلی پیش آمد.",
    loginFailed: "ورود ناموفق بود",
    incompleteLogin: "پاسخ ورود دریافت‌شده از Core کامل نیست.",
    noCoachMatch: "مربی‌ای با این تخصص پیدا نشد.",
    coachLoadError: "اطلاعات مربی‌ها دریافت نشد.",
    availabilityError: "وضعیت مربی‌ها موقتاً در دسترس نیست.",
    generalWellness: "سلامت عمومی",
    newCoach: "جدید",
    coachName: "مربی شماره {id}",
    coachesOnlineOne: "{count} مربی اکنون آنلاین است",
    coachesOnlineMany: "{count} مربی اکنون آنلاین هستند",
    noBio: "این مربی هنوز توضیحی درباره خود ثبت نکرده است.",
    notListed: "ثبت نشده",
    years: "{count} سال",
    perHour: "{amount} برای هر ساعت",
    rating: "{rating} از ۵ ({count} رأی)",
    noRatings: "هنوز امتیازی ثبت نشده است",
    online: "آنلاین",
    offline: "آفلاین",
    loadingTimes: "در حال دریافت زمان‌های آزاد...",
    noOpenTimes: "در حال حاضر زمان آزادی ثبت نشده است.",
    ends: "پایان: {date}",
    reserve: "رزرو",
    confirmReservation: "تأیید رزرو",
    reserveSession: "این جلسه رزرو شود؟",
    optionalNote: "یادداشت اختیاری برای مربی",
    notePlaceholder: "اگر نکته‌ای هست که مربی باید پیش از جلسه بداند، اینجا بنویسید...",
    cancel: "انصراف",
    confirmAndReserve: "تأیید و رزرو",
    reserving: "در حال رزرو...",
    sessionReserved: "جلسه شما با موفقیت رزرو شد.",
    thread: "گفت‌وگوی شماره {id}",
    conversationOpened: "گفت‌وگوی خصوصی ایجاد شد.",
    attachmentShared: "فایل برای مربی ارسال شد.",
    noAppointments: "هنوز جلسه‌ای رزرو نکرده‌اید.",
    status: "وضعیت: {status}",
    slot: "زمان شماره {id}",
  },
};
const storedLanguage = localStorage.getItem(LANGUAGE_KEY);
const state = {
  coaches: [],
  coachesError: false,
  coachesLoaded: false,
  selectedCoach: null,
  slots: [],
  slotsLoaded: false,
  appointments: [],
  appointmentsLoaded: false,
  threadId: null,
  thread: null,
  messages: [],
  messagesLoaded: false,
  messagePoll: null,
  pendingSlot: null,
  pendingCancellation: null,
  refreshing: null,
  language: storedLanguage === "fa" ? "fa" : "en",
};

const elements = {
  appMain: document.querySelector("#app-main"),
  authPanel: document.querySelector("#auth-panel"),
  authButton: document.querySelector("#auth-button"),
  languageButton: document.querySelector("#language-button"),
  languageLabel: document.querySelector("#language-label"),
  languageFlag: document.querySelector("#language-flag"),
  authUser: document.querySelector("#auth-user"),
  authSummary: document.querySelector("#auth-summary"),
  refreshButton: document.querySelector("#refresh-button"),
  loginForm: document.querySelector("#login-form"),
  loginButton: document.querySelector("#login-button"),
  loginUsername: document.querySelector("#login-username"),
  loginPassword: document.querySelector("#login-password"),
  loginError: document.querySelector("#login-error"),
  loginErrorMessage: document.querySelector("#login-error-message"),
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
  messageList: document.querySelector("#message-list"),
  messageForm: document.querySelector("#message-form"),
  messageInput: document.querySelector("#message-input"),
  sendMessageButton: document.querySelector("#send-message-button"),
  attachmentForm: document.querySelector("#attachment-form"),
  attachmentInput: document.querySelector("#attachment-input"),
  attachmentFilename: document.querySelector("#attachment-filename"),
  appointmentList: document.querySelector("#appointment-list"),
  reservationDialog: document.querySelector("#reservation-dialog"),
  reservationForm: document.querySelector("#reservation-form"),
  reservationCoach: document.querySelector("#reservation-coach"),
  reservationTime: document.querySelector("#reservation-time"),
  reservationNotes: document.querySelector("#reservation-notes"),
  confirmReservationButton: document.querySelector("#confirm-reservation-button"),
  cancelReservationButton: document.querySelector("#cancel-reservation-button"),
  cancellationDialog: document.querySelector("#cancellation-dialog"),
  cancellationForm: document.querySelector("#cancellation-form"),
  cancellationCoach: document.querySelector("#cancellation-coach"),
  cancellationSlot: document.querySelector("#cancellation-slot"),
  keepAppointmentButton: document.querySelector("#keep-appointment-button"),
  confirmCancellationButton: document.querySelector("#confirm-cancellation-button"),
  toast: document.querySelector("#toast"),
};

function t(key, replacements = {}) {
  const template = translations[state.language][key] ?? translations.en[key] ?? key;
  return Object.entries(replacements).reduce((message, [name, value]) => {
    return message.replaceAll(`{${name}}`, String(value));
  }, template);
}

function locale() {
  return state.language === "fa" ? "fa-IR" : "en-US";
}

function formatNumber(value, options = {}) {
  return new Intl.NumberFormat(locale(), options).format(value);
}

function renderAttachmentName() {
  elements.attachmentFilename.textContent = elements.attachmentInput.files[0]?.name || t("noFileSelected");
}

function applyLanguage(language) {
  state.language = language === "fa" ? "fa" : "en";
  localStorage.setItem(LANGUAGE_KEY, state.language);
  document.documentElement.lang = state.language;
  document.documentElement.dir = state.language === "fa" ? "rtl" : "ltr";
  document.title = t("documentTitle");

  document.querySelectorAll("[data-i18n]").forEach((element) => {
    element.textContent = t(element.dataset.i18n);
  });
  document.querySelectorAll("[data-i18n-html]").forEach((element) => {
    element.innerHTML = t(element.dataset.i18nHtml);
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach((element) => {
    element.placeholder = t(element.dataset.i18nPlaceholder);
  });
  document.querySelectorAll("[data-i18n-aria-label]").forEach((element) => {
    element.setAttribute("aria-label", t(element.dataset.i18nAriaLabel));
  });

  elements.languageLabel.textContent = t("languageSwitchText");
  elements.languageFlag.textContent = t("languageSwitchFlag");
  elements.languageButton.setAttribute("aria-label", t("languageSwitchLabel"));
  elements.languageButton.title = t("languageSwitchLabel");
  renderAttachmentName();
  window.clearTimeout(showToast.timeout);
  elements.toast.hidden = true;

  const username = localStorage.getItem(USER_KEY);
  if (accessToken() && username) showApp(username);
  else showLogin();

  renderOnlineCount();
  renderCoaches();
  if (state.selectedCoach) renderCoachDetail();
  if (state.slotsLoaded) renderSlots();
  if (state.pendingSlot) renderReservationSummary();
  if (state.pendingCancellation) renderCancellationSummary();
  if (state.messagesLoaded) renderMessages();
  if (state.appointmentsLoaded) renderAppointments();
}

function accessToken() {
  return localStorage.getItem(ACCESS_KEY);
}

function clearAuth() {
  localStorage.removeItem(ACCESS_KEY);
  localStorage.removeItem(REFRESH_KEY);
  localStorage.removeItem(USER_KEY);
  localStorage.removeItem(USER_ID_KEY);
}

function showLogin(message = "") {
  elements.appMain.hidden = true;
  elements.authPanel.hidden = false;
  elements.refreshButton.hidden = true;
  elements.authButton.textContent = t("signIn");
  elements.authUser.textContent = t("signedOut");
  elements.loginErrorMessage.textContent = message;
  elements.loginError.hidden = !message;
}

function showApp(username) {
  elements.authPanel.hidden = true;
  elements.appMain.hidden = false;
  elements.refreshButton.hidden = false;
  elements.authButton.textContent = t("signOut");
  elements.authUser.textContent = t("signedInAs", { username });
  elements.authSummary.textContent = t("authenticatedAs", { username });
}

async function responseError(response) {
  let message = response.status === 401 ? t("sessionExpired") : t("genericError");
  try {
    const payload = await response.json();
    message = payload.detail || payload.message || payload.error?.message || message;
  } catch (_) {
    // Keep the status-based fallback for non-JSON responses.
  }
  return message;
}

async function refreshAccessToken() {
  if (state.refreshing) return state.refreshing;
  const refresh = localStorage.getItem(REFRESH_KEY);
  if (!refresh) return false;

  state.refreshing = fetch(`${authApi}/refresh`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ refresh }),
  }).then(async (response) => {
    if (!response.ok) return false;
    const payload = await response.json();
    if (!payload.token) return false;
    localStorage.setItem(ACCESS_KEY, payload.token);
    return true;
  }).catch(() => false).finally(() => {
    state.refreshing = null;
  });

  return state.refreshing;
}

async function request(path, options = {}, retried = false) {
  const token = accessToken();
  const response = await fetch(`${api}${path}`, {
    credentials: "same-origin",
    ...options,
    headers: {
      Accept: "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers || {}),
    },
  });

  if (response.status === 401 && !retried && await refreshAccessToken()) {
    return request(path, options, true);
  }

  if (!response.ok) {
    const message = await responseError(response);
    if (response.status === 401) {
      clearAuth();
      showLogin(message);
    }
    throw new Error(message);
  }
  return response.status === 204 ? null : response.json();
}

async function login(event) {
  event.preventDefault();
  elements.loginButton.disabled = true;
  elements.loginError.hidden = true;

  try {
    const response = await fetch(`${authApi}/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify({
        username: elements.loginUsername.value.trim(),
        password: elements.loginPassword.value,
      }),
    });
    if (!response.ok) throw new Error(await responseError(response));

    const payload = await response.json();
    if (!payload.token || !payload.refresh || !payload.user?.username) {
      throw new Error(t("incompleteLogin"));
    }
    localStorage.setItem(ACCESS_KEY, payload.token);
    localStorage.setItem(REFRESH_KEY, payload.refresh);
    localStorage.setItem(USER_KEY, payload.user.username);
    if (payload.user.id) localStorage.setItem(USER_ID_KEY, String(payload.user.id));
    elements.loginForm.reset();
    showApp(payload.user.username);
  } catch (error) {
    clearAuth();
    showLogin(error.message);
    return;
  } finally {
    elements.loginButton.disabled = false;
  }

  await loadCoaches();
}

async function logout() {
  const token = accessToken();
  try {
    if (token) {
      await fetch(`${authApi}/logout`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}`, Accept: "application/json" },
      });
    }
  } finally {
    clearAuth();
    stopMessagePolling();
    state.coaches = [];
    state.selectedCoach = null;
    state.threadId = null;
    state.thread = null;
    state.messages = [];
    state.messagesLoaded = false;
    showLogin();
  }
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
  return new Intl.DateTimeFormat(locale(), { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
}

function renderCoaches() {
  if (state.coachesError) {
    elements.coachList.innerHTML = `<p class="empty-list">${t("coachLoadError")}</p>`;
    return;
  }
  const query = elements.specialtyFilter.value.trim().toLowerCase();
  const visible = state.coaches.filter((coach) => {
    return !query || (coach.specialties || []).join(" ").toLowerCase().includes(query);
  });
  if (!visible.length) {
    elements.coachList.innerHTML = `<p class="empty-list">${t("noCoachMatch")}</p>`;
    return;
  }
  elements.coachList.innerHTML = visible.map((coach) => `
    <button class="coach-card" type="button" data-coach-id="${coach.user_id}" aria-current="${state.selectedCoach?.user_id === coach.user_id}">
      <span class="coach-card-top"><strong>${t("coachName", { id: formatNumber(coach.user_id) })}</strong><i class="online-indicator ${coach.is_online ? "online" : ""}"></i></span>
      <span class="card-meta"><span>${escapeHtml((coach.specialties || [t("generalWellness")]).join(" · "))}</span><span>${coach.avg_rating ? `${formatNumber(coach.avg_rating, { minimumFractionDigits: 1, maximumFractionDigits: 1 })} / ${formatNumber(5)}` : t("newCoach")}</span></span>
    </button>
  `).join("");
}

function renderOnlineCount() {
  if (state.coachesError) {
    elements.onlineCount.textContent = t("availabilityError");
    return;
  }
  if (!state.coachesLoaded) {
    elements.onlineCount.textContent = t("checkingAvailability");
    return;
  }
  const onlineCount = state.coaches.filter((coach) => coach.is_online).length;
  const onlineKey = onlineCount === 1 ? "coachesOnlineOne" : "coachesOnlineMany";
  elements.onlineCount.textContent = t(onlineKey, { count: formatNumber(onlineCount) });
}

async function loadCoaches() {
  state.coachesError = false;
  state.coachesLoaded = false;
  renderOnlineCount();
  try {
    const [coaches, online] = await Promise.all([
      request("/reserve/coaches"),
      request("/chat/coaches/online"),
    ]);
    const onlineIds = new Set(online.data.map((coach) => coach.user_id));
    state.coaches = coaches.data.map((coach) => ({ ...coach, is_online: onlineIds.has(coach.user_id) }));
    state.coachesLoaded = true;
    renderOnlineCount();
    renderCoaches();
  } catch (error) {
    state.coaches = [];
    state.coachesError = true;
    renderOnlineCount();
    renderCoaches();
    throw error;
  }
}

function renderCoachDetail() {
  const coach = state.selectedCoach;
  if (!coach) return;
  elements.detailName.textContent = t("coachName", { id: formatNumber(coach.user_id) });
  elements.detailBio.textContent = coach.bio || t("noBio");
  elements.detailSpecialties.textContent = (coach.specialties || [t("generalWellness")]).join(state.language === "fa" ? "، " : ", ");
  elements.detailExperience.textContent = coach.years_experience == null
    ? t("notListed")
    : t("years", { count: formatNumber(coach.years_experience) });
  elements.detailRate.textContent = t("perHour", { amount: formatNumber(coach.hourly_rate) });
  elements.detailRating.textContent = coach.avg_rating
    ? t("rating", {
      rating: formatNumber(coach.avg_rating, { minimumFractionDigits: 1, maximumFractionDigits: 1 }),
      count: formatNumber(coach.rating_count),
    })
    : t("noRatings");
  elements.detailOnline.textContent = coach.is_online ? t("online") : t("offline");
  elements.detailOnline.classList.toggle("availability-pill", coach.is_online);
}

async function selectCoach(coachId) {
  const response = await request(`/reserve/coaches/${coachId}`);
  stopMessagePolling();
  state.selectedCoach = response.data;
  state.slots = [];
  state.slotsLoaded = false;
  state.threadId = null;
  state.thread = null;
  state.messages = [];
  state.messagesLoaded = false;
  elements.chatSection.hidden = true;
  elements.emptyState.hidden = true;
  elements.coachDetail.hidden = false;
  renderCoachDetail();
  renderCoaches();
  await loadSlots();
}

function renderSlots() {
  if (!state.slots.length) {
    elements.slotList.innerHTML = `<p class="empty-list">${t("noOpenTimes")}</p>`;
    return;
  }
  elements.slotList.innerHTML = state.slots.map((slot) => `
    <article class="slot-card">
      <div><time datetime="${slot.start_at}">${formatDate(slot.start_at)}</time><small>${t("ends", { date: formatDate(slot.end_at) })}</small></div>
      <button class="button button-quiet" data-book-slot="${slot.id}" type="button">${t("reserve")}</button>
    </article>
  `).join("");
}

async function loadSlots() {
  if (!state.selectedCoach) return;
  elements.slotList.innerHTML = `<p class="empty-list">${t("loadingTimes")}</p>`;
  const response = await request(`/reserve/coaches/${state.selectedCoach.user_id}/availability`);
  state.slots = response.data;
  state.slotsLoaded = true;
  renderSlots();
}

function renderReservationSummary() {
  if (!state.pendingSlot || !state.selectedCoach) return;
  elements.reservationCoach.textContent = t("coachName", {
    id: formatNumber(state.selectedCoach.user_id),
  });
  elements.reservationTime.textContent = `${formatDate(state.pendingSlot.start_at)} · ${t("ends", {
    date: formatDate(state.pendingSlot.end_at),
  })}`;
}

function openReservation(slotId) {
  const slot = state.slots.find((item) => item.id === Number(slotId));
  if (!slot || !state.selectedCoach) return;
  state.pendingSlot = slot;
  elements.reservationNotes.value = "";
  renderReservationSummary();
  elements.reservationDialog.showModal();
  window.setTimeout(() => elements.reservationNotes.focus(), 0);
}

function closeReservation() {
  if (elements.reservationDialog.open) elements.reservationDialog.close();
  state.pendingSlot = null;
}

async function confirmReservation(event) {
  event.preventDefault();
  if (!state.pendingSlot) return;
  const slotId = state.pendingSlot.id;
  const notes = elements.reservationNotes.value.trim();
  elements.confirmReservationButton.disabled = true;
  elements.confirmReservationButton.textContent = t("reserving");

  try {
    await request("/reserve/appointments", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ availability_id: Number(slotId), notes: notes || null }),
    });
    closeReservation();
    showToast(t("sessionReserved"));
    await Promise.all([loadSlots(), loadAppointments()]);
  } finally {
    elements.confirmReservationButton.disabled = false;
    elements.confirmReservationButton.textContent = t("confirmAndReserve");
  }
}

function currentUserId() {
  const stored = Number(localStorage.getItem(USER_ID_KEY));
  if (Number.isInteger(stored) && stored > 0) return stored;
  return state.thread?.user_id || null;
}

function renderMessages() {
  const messages = state.messages.filter((message) => message.body);
  if (!messages.length) {
    elements.messageList.innerHTML = `<p class="empty-list">${t("noMessages")}</p>`;
    return;
  }
  const userId = currentUserId();
  elements.messageList.innerHTML = messages.map((message) => {
    const own = message.sender_user_id === userId;
    const sender = own ? t("you") : t("coach");
    return `
      <article class="message-bubble ${own ? "message-own" : "message-other"}">
        <div class="message-meta"><strong>${sender}</strong><time datetime="${message.sent_at}">${formatDate(message.sent_at)}</time></div>
        <p dir="auto">${escapeHtml(message.body)}</p>
      </article>
    `;
  }).join("");
  elements.messageList.scrollTop = elements.messageList.scrollHeight;
}

async function loadMessages({ quiet = false } = {}) {
  if (!state.threadId) return;
  const requestedThreadId = state.threadId;
  try {
    const response = await request(`/chat/threads/${requestedThreadId}/messages`);
    if (state.threadId !== requestedThreadId) return;
    state.messages = response.data;
    state.messagesLoaded = true;
    renderMessages();
  } catch (error) {
    if (!quiet) throw error;
  }
}

function stopMessagePolling() {
  if (state.messagePoll) {
    window.clearInterval(state.messagePoll);
    state.messagePoll = null;
  }
}

function startMessagePolling() {
  stopMessagePolling();
  state.messagePoll = window.setInterval(() => {
    if (!document.hidden && state.threadId) loadMessages({ quiet: true });
  }, 4000);
}

async function sendMessage(event) {
  event.preventDefault();
  if (!state.threadId) return;
  const body = elements.messageInput.value.trim();
  if (!body) return;
  elements.sendMessageButton.disabled = true;
  elements.sendMessageButton.textContent = t("sendingMessage");

  try {
    const response = await request(`/chat/threads/${state.threadId}/messages`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ body }),
    });
    state.messages.push(response.data);
    state.messagesLoaded = true;
    elements.messageForm.reset();
    renderMessages();
  } finally {
    elements.sendMessageButton.disabled = false;
    elements.sendMessageButton.textContent = t("sendMessage");
    elements.messageInput.focus();
  }
}

async function openConversation() {
  if (!state.selectedCoach) return;
  const response = await request("/chat/threads", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ coach_user_id: state.selectedCoach.user_id }),
  });
  state.thread = response.data;
  state.threadId = response.data.id;
  elements.threadId.textContent = t("thread", { id: formatNumber(state.threadId) });
  elements.chatSection.hidden = false;
  await loadMessages();
  startMessagePolling();
  showToast(t("conversationOpened"));
  elements.messageInput.focus();
}

async function uploadAttachment(event) {
  event.preventDefault();
  if (!state.threadId || !elements.attachmentInput.files[0]) return;
  const form = new FormData();
  form.append("file", elements.attachmentInput.files[0]);
  await request(`/chat/threads/${state.threadId}/attachments`, { method: "POST", body: form });
  elements.attachmentForm.reset();
  renderAttachmentName();
  showToast(t("attachmentShared"));
}

function renderAppointments() {
  if (!state.appointments.length) {
    elements.appointmentList.innerHTML = `<p class="empty-list">${t("noAppointments")}</p>`;
    return;
  }
  elements.appointmentList.innerHTML = state.appointments.map((appointment) => `
    <article class="appointment-card">
      <div>
        <strong>${t("coachName", { id: formatNumber(appointment.coach_user_id) })}</strong><br>
        <small>${t("status", { status: appointmentStatusLabel(appointment.status) })} · ${t("slot", { id: formatNumber(appointment.availability_id) })}</small>
      </div>
      <div class="appointment-actions">
        <span class="status-dot">${appointmentStatusLabel(appointment.status)}</span>
        ${appointment.status === "confirmed" ? `<button class="button button-danger button-small" type="button" data-cancel-appointment="${appointment.id}">${t("cancelAppointment")}</button>` : ""}
      </div>
    </article>
  `).join("");
}

function appointmentStatusLabel(status) {
  const key = {
    confirmed: "statusConfirmed",
    cancelled: "statusCancelled",
    completed: "statusCompleted",
    no_show: "statusNoShow",
  }[status];
  return key ? t(key) : escapeHtml(status);
}

function renderCancellationSummary() {
  if (!state.pendingCancellation) return;
  elements.cancellationCoach.textContent = t("coachName", {
    id: formatNumber(state.pendingCancellation.coach_user_id),
  });
  elements.cancellationSlot.textContent = t("slot", {
    id: formatNumber(state.pendingCancellation.availability_id),
  });
}

function openCancellation(appointmentId) {
  const appointment = state.appointments.find((item) => item.id === Number(appointmentId));
  if (!appointment || appointment.status !== "confirmed") return;
  state.pendingCancellation = appointment;
  renderCancellationSummary();
  elements.cancellationDialog.showModal();
}

function closeCancellation() {
  if (elements.cancellationDialog.open) elements.cancellationDialog.close();
  state.pendingCancellation = null;
}

async function confirmCancellation(event) {
  event.preventDefault();
  if (!state.pendingCancellation) return;
  const appointmentId = state.pendingCancellation.id;
  elements.confirmCancellationButton.disabled = true;
  elements.confirmCancellationButton.textContent = t("cancellingAppointment");

  try {
    const response = await request(`/reserve/appointments/${appointmentId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: "cancelled" }),
    });
    state.appointments = state.appointments.map((appointment) => {
      return appointment.id === appointmentId ? response.data : appointment;
    });
    closeCancellation();
    renderAppointments();
    showToast(t("appointmentCancelled"));
  } finally {
    elements.confirmCancellationButton.disabled = false;
    elements.confirmCancellationButton.textContent = t("confirmCancellation");
  }
}

async function loadAppointments() {
  const response = await request("/reserve/appointments");
  state.appointments = response.data;
  state.appointmentsLoaded = true;
  renderAppointments();
}

elements.languageButton.addEventListener("click", () => {
  applyLanguage(state.language === "en" ? "fa" : "en");
});
elements.refreshButton.addEventListener("click", () => loadCoaches().catch((error) => showToast(error.message, true)));
elements.authButton.addEventListener("click", () => {
  if (accessToken()) {
    logout().catch((error) => showToast(error.message, true));
  } else {
    showLogin();
    elements.loginUsername.focus();
  }
});
elements.loginForm.addEventListener("submit", (event) => {
  login(event).catch((error) => showToast(error.message, true));
});
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
  if (button) openReservation(button.dataset.bookSlot);
});
elements.reservationForm.addEventListener("submit", (event) => {
  confirmReservation(event).catch((error) => showToast(error.message, true));
});
elements.cancelReservationButton.addEventListener("click", closeReservation);
elements.reservationDialog.addEventListener("close", () => {
  state.pendingSlot = null;
});
elements.reservationDialog.addEventListener("click", (event) => {
  if (event.target === elements.reservationDialog) closeReservation();
});
elements.messageForm.addEventListener("submit", (event) => {
  sendMessage(event).catch((error) => showToast(error.message, true));
});
elements.messageInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    elements.messageForm.requestSubmit();
  }
});
elements.attachmentForm.addEventListener("submit", (event) => {
  uploadAttachment(event).catch((error) => showToast(error.message, true));
});
elements.attachmentInput.addEventListener("change", renderAttachmentName);
elements.appointmentList.addEventListener("click", (event) => {
  const button = event.target.closest("[data-cancel-appointment]");
  if (button) openCancellation(button.dataset.cancelAppointment);
});
elements.cancellationForm.addEventListener("submit", (event) => {
  confirmCancellation(event).catch((error) => showToast(error.message, true));
});
elements.keepAppointmentButton.addEventListener("click", closeCancellation);
elements.cancellationDialog.addEventListener("close", () => {
  state.pendingCancellation = null;
});
elements.cancellationDialog.addEventListener("click", (event) => {
  if (event.target === elements.cancellationDialog) closeCancellation();
});

applyLanguage(state.language);
const username = localStorage.getItem(USER_KEY);
if (accessToken() && username) {
  showApp(username);
  loadCoaches().catch((error) => {
    if (!elements.appMain.hidden) showToast(error.message, true);
  });
} else {
  clearAuth();
  showLogin();
}

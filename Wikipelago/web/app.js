const APP_VERSION = "2026.03.08.4";
console.log("Wikipelago web version", APP_VERSION);

const state = {
  sessionId: localStorage.getItem("wikipelago_session_id") || "",
  status: null,
  currentTitle: "Wikipedia",
  clicksUsed: 0,
  announcedGoalComplete: false,
};

const el = {
  connBadge: document.getElementById("connBadge"),
  articleInput: document.getElementById("articleInput"),
  openBtn: document.getElementById("openBtn"),
  articleTitle: document.getElementById("articleTitle"),
  articleBody: document.getElementById("articleBody"),
  serverInput: document.getElementById("serverInput"),
  slotInput: document.getElementById("slotInput"),
  passwordInput: document.getElementById("passwordInput"),
  connectBtn: document.getElementById("connectBtn"),
  roundText: document.getElementById("roundText"),
  targetText: document.getElementById("targetText"),
  goalText: document.getElementById("goalText"),
  clicksText: document.getElementById("clicksText"),
  fragmentsText: document.getElementById("fragmentsText"),
  compassHint: document.getElementById("compassHint"),
  roundProgress: document.getElementById("roundProgress"),
  backItem: document.getElementById("backItem"),
  searchItem: document.getElementById("searchItem"),
  compassItem: document.getElementById("compassItem"),
  toast: document.getElementById("toast"),
};

el.serverInput.value = "archipelago.gg:";
el.slotInput.value = "WikiTester";

function toast(text, kind = "ok") {
  el.toast.textContent = text;
  el.toast.className = `toast ${kind}`;
  setTimeout(() => { el.toast.className = "toast hidden"; }, 2200);
}

async function api(path, method = "GET", body = null, retryOnInvalidSession = true) {
  const options = { method, headers: { "Content-Type": "application/json" } };
  if (body) options.body = JSON.stringify(body);
  const res = await fetch(path, options);
  const data = await res.json().catch(() => ({}));
  if (!res.ok || data.ok === false) {
    const errText = data.error || `HTTP ${res.status}`;

    // Server-side sessions are in-memory; on restart/deploy, browser session IDs go stale.
    if (retryOnInvalidSession && String(errText).toLowerCase() === "invalid session") {
      state.sessionId = "";
      localStorage.removeItem("wikipelago_session_id");
      await ensureSession();
      const fixedPath = path.replace(/\/api\/session\/[^/]+/, `/api/session/${state.sessionId}`);
      return api(fixedPath, method, body, false);
    }

    throw new Error(errText);
  }
  return data;
}

async function ensureSession() {
  if (state.sessionId) return;
  const data = await api("/api/session", "POST", {});
  state.sessionId = data.session_id;
  localStorage.setItem("wikipelago_session_id", state.sessionId);
}

function updateHUD(status) {
  const wasComplete = state.status?.boss_completed === true;
  state.status = status;
  el.connBadge.textContent = status.connected_to_ap ? "Connected" : "Offline";
  el.connBadge.className = status.connected_to_ap ? "badge online" : "badge offline";

  if (status.boss_completed) {
    el.roundText.textContent = "COMPLETE";
    el.targetText.textContent = "GOAL COMPLETE";
    el.goalText.textContent = `${status.goal_article || "..."} (Complete)`;
  } else {
    el.roundText.textContent = `${status.round}/${status.check_count}`;
    el.targetText.textContent = status.current_target || "...";
    el.goalText.textContent = status.goal_article || "...";
  }

  el.clicksText.textContent = String(state.clicksUsed);
  el.fragmentsText.textContent = `${status.fragments}/${status.required_fragments}`;
  if (!status.compass_unlocked) {
    el.compassHint.textContent = "Locked";
  } else {
    el.compassHint.textContent = status.warmer_colder || "Calibrating";
  }

  const p = Math.max(0, Math.min(100, (status.round / Math.max(status.check_count, 1)) * 100));
  el.roundProgress.style.width = `${p}%`;

  el.backItem.textContent = status.back_button_unlocked ? "Unlocked" : "Locked";
  el.searchItem.textContent = status.ctrl_f_unlocked ? "Unlocked" : "Locked";
  el.compassItem.textContent = status.compass_unlocked ? "Unlocked" : "Locked";

  if (status.boss_completed && !wasComplete && !state.announcedGoalComplete) {
    toast("GOAL COMPLETE! Seed finished.", "ok");
    state.announcedGoalComplete = true;
  }

  if (status.last_error) toast(status.last_error, "warn");
}
async function pollStatus() {
  try {
    await ensureSession();
    const data = await api(`/api/session/${state.sessionId}/status`);
    updateHUD(data.status);
  } catch {
    el.connBadge.textContent = "Offline";
    el.connBadge.className = "badge offline";
  }
}

function sanitizeHtml(root) {
  root.querySelectorAll("script,style,noscript,.reference,.mw-editsection").forEach((n) => n.remove());
}

function rewriteLinks(root) {
  root.querySelectorAll("a").forEach((a) => {
    const href = a.getAttribute("href") || "";
    if (!href.startsWith("/wiki/")) return;
    const wikiPart = href.replace("/wiki/", "");
    if (!wikiPart) return;
    const title = decodeURIComponent(wikiPart).replace(/_/g, " ");
    const ns = title.split(":", 1)[0].toLowerCase();
    const blockedNamespaces = new Set(["file", "category", "help", "template", "special", "portal", "talk", "user", "wikipedia", "module", "book", "draft", "mediawiki"]);
    if (title.includes(":") && blockedNamespaces.has(ns)) return;
    a.dataset.title = title;
    a.href = "#";
  });
}

async function fetchWikiHtml(title) {
  const url = `https://en.wikipedia.org/w/api.php?action=parse&page=${encodeURIComponent(title)}&prop=text&formatversion=2&format=json&origin=*`;
  const res = await fetch(url);
  const data = await res.json();
  if (!data.parse || !data.parse.text) throw new Error("Article unavailable");
  return data.parse.text;
}

async function openArticle(title, countAsClick = false) {
  if (!title) return;
  try {
    const html = await fetchWikiHtml(title);
    state.currentTitle = title;
    el.articleTitle.textContent = title;
    el.articleInput.value = title;

    el.articleBody.innerHTML = html;
    sanitizeHtml(el.articleBody);
    rewriteLinks(el.articleBody);

    if (countAsClick) state.clicksUsed += 1;
    el.clicksText.textContent = String(state.clicksUsed);

    await ensureSession();
    const result = await api(`/api/session/${state.sessionId}/check`, "POST", {
      page_title: title,
      clicks_used: state.clicksUsed,
    });

    if (result.matched) toast("Target hit: " + result.target, "ok");
    if (result.locked) toast("Round locked. Find Round Access items.", "warn");
    if (result.status) updateHUD(result.status);

    history.pushState({ title }, "", `#${encodeURIComponent(title)}`);
  } catch {
    toast(`Could not open article: ${title}`, "warn");
  }
}

el.openBtn.addEventListener("click", () => openArticle(el.articleInput.value.trim(), false));
el.articleInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") openArticle(el.articleInput.value.trim(), false);
});

el.articleBody.addEventListener("click", (e) => {
  const a = e.target.closest("a[data-title]");
  if (!a) return;
  e.preventDefault();
  openArticle(a.dataset.title, true);
});

el.connectBtn.addEventListener("click", async () => {
  try {
    await ensureSession();
    await api(`/api/session/${state.sessionId}/connect`, "POST", {
      server: el.serverInput.value.trim(),
      slot_name: el.slotInput.value.trim(),
      password: el.passwordInput.value,
    });
    toast("Connecting to Archipelago...", "ok");
    await pollStatus();
  } catch (err) {
    toast(err.message || "Connect failed", "warn");
  }
});

document.addEventListener("keydown", (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "f") {
    if (state.status && !state.status.ctrl_f_unlocked) {
      e.preventDefault();
      toast("Ctrl+F Lens is locked", "warn");
    }
  }
  if (e.altKey && e.key === "ArrowLeft") {
    if (state.status && !state.status.back_button_unlocked) {
      e.preventDefault();
      toast("Back Button is locked", "warn");
    }
  }
  if (e.key === "Backspace") {
    const typing = ["INPUT", "TEXTAREA"].includes(document.activeElement?.tagName);
    if (!typing && state.status && !state.status.back_button_unlocked) {
      e.preventDefault();
      toast("Back Button is locked", "warn");
    }
  }
});

window.addEventListener("popstate", (e) => {
  if (state.status && !state.status.back_button_unlocked) {
    history.pushState({ title: state.currentTitle }, "", `#${encodeURIComponent(state.currentTitle)}`);
    toast("Back Button is locked", "warn");
    return;
  }
  const title = e.state?.title;
  if (title) openArticle(title, false);
});

setInterval(pollStatus, 1500);

(async () => {
  await ensureSession();
  await pollStatus();
  openArticle("Wikipedia", false);
})();














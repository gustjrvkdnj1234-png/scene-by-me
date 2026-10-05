// 메모 화면: 노트에 적듯 메모를 쌓는다. 사용자 입력은 textContent 로만 넣는다.
const $ = (id) => document.getElementById(id);
const notebook = $("notebook"), input = $("input"), form = $("form");
const errorEl = $("error"), sendBtn = $("send");
let lastDate = null;

const WEEK = ["일", "월", "화", "수", "목", "금", "토"];

function dayLabel(iso) {
  const d = new Date(iso + "T00:00:00");
  return `${d.getFullYear()}년 ${d.getMonth() + 1}월 ${d.getDate()}일 (${WEEK[d.getDay()]})`;
}

function showError(msg) {
  errorEl.textContent = msg || "";
  errorEl.hidden = !msg;
}

function appendMemo(m, animate) {
  $("empty")?.remove();
  if (m.local_date !== lastDate) {
    const h = document.createElement("h2");
    h.className = "day";
    h.textContent = dayLabel(m.local_date);
    notebook.append(h);
    lastDate = m.local_date;
  }
  const el = document.createElement("div");
  el.className = "memo" + (animate ? " new" : "");
  const t = document.createElement("time");
  t.textContent = m.created_at.slice(11, 16) + (m.source !== "chat" ? ` · ${m.source.toUpperCase()}` : "");
  const body = document.createElement("span");
  body.textContent = m.content;
  el.append(t, body);
  notebook.append(el);
}

async function api(url, opts) {
  const r = await fetch(url, opts);
  if (!r.ok) {
    let detail = "잠시 후 다시 시도해 주세요.";
    try { const j = await r.json(); if (typeof j.detail === "string") detail = j.detail; } catch {}
    throw new Error(detail);
  }
  return r.json();
}

async function refreshStatus() {
  try {
    const s = await api("/api/status");
    $("progress").textContent = s.memo_count === 0
      ? "오늘의 한 줄을 적어보세요"
      : `${s.days}일째 기록 중 · 첫 장면까지 ${s.met ? "준비 완료" : s.days_left + "일"}`;
  } catch {}
}

async function load() {
  try {
    const memos = await api("/api/memos");
    memos.forEach((m) => appendMemo(m, false));
    notebook.scrollTop = notebook.scrollHeight;
  } catch (e) { showError("메모를 불러오지 못했어요: " + e.message); }
  refreshStatus();
}

function scrollEnd() { notebook.scrollTo({ top: notebook.scrollHeight, behavior: "smooth" }); }

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const content = input.value.trim();
  if (!content) return;
  sendBtn.disabled = true; showError("");
  try {
    const m = await api("/api/memos", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content }),
    });
    input.value = "";
    appendMemo(m, true); scrollEnd(); refreshStatus();
  } catch (err) { showError(err.message); }
  sendBtn.disabled = false; input.focus();
});

// Enter 전송, Shift+Enter 줄바꿈 (한글 조합 중에는 전송하지 않음)
input.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey && !e.isComposing) { e.preventDefault(); form.requestSubmit(); }
});

$("file").addEventListener("change", async (e) => {
  const file = e.target.files[0];
  e.target.value = "";
  if (!file) return;
  showError("");
  const fd = new FormData(); fd.append("file", file);
  try {
    const r = await api("/api/memos/upload", { method: "POST", body: fd });
    r.memos.forEach((m) => appendMemo(m, true)); scrollEnd(); refreshStatus();
  } catch (err) { showError(err.message); }
});

load();

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export async function sendChatMessage(sessionId, message, currentForm) {
  const res = await fetch(`${API_BASE}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id: sessionId,
      message,
      current_form: currentForm,
    }),
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`Chat request failed: ${detail}`);
  }
  return res.json(); // { reply, form }
}

export async function saveInteraction(sessionId, form) {
  const res = await fetch(`${API_BASE}/api/interactions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, form }),
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`Save request failed: ${detail}`);
  }
  return res.json(); // { id, status }
}

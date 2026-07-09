import { useMemo, useState } from "react";
import LogForm from "./components/LogForm.jsx";
import ChatPanel from "./components/ChatPanel.jsx";
import { emptyForm } from "./emptyForm.js";
import { sendChatMessage, saveInteraction } from "./api.js";

function makeSessionId() {
  return `session-${Math.random().toString(36).slice(2)}-${Date.now()}`;
}

export default function App() {
  const sessionId = useMemo(makeSessionId, []);
  const [form, setForm] = useState(emptyForm);
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        'Log interaction details here (e.g., "Met Dr. Smith, discussed Prodo-X efficacy, positive sentiment, shared brochure") or ask for help.',
    },
  ]);
  const [loading, setLoading] = useState(false);
  const [saveStatus, setSaveStatus] = useState("");

  async function handleSend(text) {
    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setLoading(true);
    try {
      const { reply, form: updatedForm } = await sendChatMessage(sessionId, text, form);
      setForm(updatedForm);
      setMessages((prev) => [...prev, { role: "assistant", content: reply }]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: `Sorry, something went wrong: ${err.message}` },
      ]);
    } finally {
      setLoading(false);
    }
  }

  async function handleSave() {
    setSaveStatus("Saving...");
    try {
      const result = await saveInteraction(sessionId, form);
      setSaveStatus(`Saved (id #${result.id})`);
    } catch (err) {
      setSaveStatus(`Save failed: ${err.message}`);
    }
  }

  return (
    <div className="app-shell">
      <LogForm form={form} setForm={setForm} onSave={handleSave} saveStatus={saveStatus} />
      <ChatPanel messages={messages} onSend={handleSend} loading={loading} />
    </div>
  );
}

import { useEffect, useRef, useState } from "react";

export default function ChatPanel({ messages, onSend, loading }) {
  const [draft, setDraft] = useState("");
  const scrollRef = useRef(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, loading]);

  function handleSend() {
    const text = draft.trim();
    if (!text || loading) return;
    onSend(text);
    setDraft("");
  }

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  return (
    <div className="chat-panel">
      <div className="chat-header">
        <div className="chat-header-title">🤖 AI Assistant</div>
        <div className="chat-header-sub">Log Interaction details here via chat</div>
      </div>

      <div className="chat-messages" ref={scrollRef}>
        {messages.map((m, idx) => (
          <div key={idx} className={`chat-bubble ${m.role}`}>
            {m.content}
          </div>
        ))}
        {loading && <div className="chat-bubble assistant loading">Thinking...</div>}
      </div>

      <div className="chat-input-bar">
        <textarea
          placeholder='Describe Interaction... (e.g. "Met Dr. Smith, discussed Prodo-X efficacy, positive sentiment, shared brochure")'
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={handleKeyDown}
        />
        <button className="send-btn" onClick={handleSend} disabled={loading}>
          A Log
        </button>
      </div>
    </div>
  );
}

import { useState } from "react";

/**
 * Small reusable "add a tag" control used for Attendees, Materials
 * Shared, and Samples Distributed - each of these is just a list of
 * strings in the form model.
 */
export default function ChipList({ items, onChange, placeholder, addLabel }) {
  const [draft, setDraft] = useState("");

  function addItem() {
    const value = draft.trim();
    if (!value) return;
    if (!items.includes(value)) {
      onChange([...items, value]);
    }
    setDraft("");
  }

  function removeItem(idx) {
    onChange(items.filter((_, i) => i !== idx));
  }

  function handleKeyDown(e) {
    if (e.key === "Enter") {
      e.preventDefault();
      addItem();
    }
  }

  return (
    <div>
      <div className="chip-field">
        {items.length === 0 && <span className="chip-placeholder">{placeholder}</span>}
        {items.map((item, idx) => (
          <span className="chip" key={`${item}-${idx}`}>
            {item}
            <button type="button" onClick={() => removeItem(idx)} aria-label={`Remove ${item}`}>
              ×
            </button>
          </span>
        ))}
      </div>
      <div style={{ display: "flex", gap: 8, marginTop: 8 }}>
        <input
          type="text"
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type and press Enter..."
        />
        <button type="button" className="pill-btn" onClick={addItem}>
          {addLabel}
        </button>
      </div>
    </div>
  );
}

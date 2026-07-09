import ChipList from "./ChipList.jsx";

const SENTIMENTS = [
  { value: "Positive", emoji: "🙂" },
  { value: "Neutral", emoji: "😐" },
  { value: "Negative", emoji: "😕" },
];

export default function LogForm({ form, setForm, onSave, saveStatus }) {
  function update(field, value) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  return (
    <div className="form-panel">
      <h1 className="form-header">Log HCP Interaction</h1>

      <div className="section-title">Interaction Details</div>
      <div className="field-row">
        <div className="field">
          <label>HCP Name</label>
          <input
            type="text"
            placeholder="Search or select HCP..."
            value={form.hcp_name}
            onChange={(e) => update("hcp_name", e.target.value)}
          />
        </div>
        <div className="field">
          <label>Interaction Type</label>
          <select
            value={form.interaction_type}
            onChange={(e) => update("interaction_type", e.target.value)}
          >
            <option>Meeting</option>
            <option>Call</option>
            <option>Email</option>
            <option>Conference</option>
          </select>
        </div>
      </div>

      <div className="field-row">
        <div className="field">
          <label>Date</label>
          <input type="date" value={form.date} onChange={(e) => update("date", e.target.value)} />
        </div>
        <div className="field">
          <label>Time</label>
          <input type="time" value={form.time} onChange={(e) => update("time", e.target.value)} />
        </div>
      </div>

      <div className="section-title">Attendees</div>
      <ChipList
        items={form.attendees}
        onChange={(items) => update("attendees", items)}
        placeholder="Enter names or search..."
        addLabel="Add"
      />

      <div className="section-title">Topics Discussed</div>
      <div className="field">
        <textarea
          placeholder="Enter key discussion points..."
          value={form.topics_discussed}
          onChange={(e) => update("topics_discussed", e.target.value)}
        />
      </div>
      <p className="voice-note-link">🎙️ Summarize from Voice Note (Requires Consent)</p>

      <div className="section-title">Materials Shared / Samples Distributed</div>

      <div className="subsection">
        <h4>Materials Shared</h4>
      </div>
      <ChipList
        items={form.materials_shared}
        onChange={(items) => update("materials_shared", items)}
        placeholder="No materials added."
        addLabel="🔍 Search/Add"
      />

      <div className="subsection">
        <h4>Samples Distributed</h4>
      </div>
      <ChipList
        items={form.samples_distributed}
        onChange={(items) => update("samples_distributed", items)}
        placeholder="No samples added."
        addLabel="＋ Add Sample"
      />

      <hr className="divider" />

      <div className="section-title" style={{ marginTop: 0 }}>
        Observed/Inferred HCP Sentiment
      </div>
      <div className="sentiment-row">
        {SENTIMENTS.map((s) => (
          <label className="sentiment-option" key={s.value}>
            <input
              type="radio"
              name="sentiment"
              checked={form.sentiment === s.value}
              onChange={() => update("sentiment", s.value)}
            />
            {s.emoji} {s.value}
          </label>
        ))}
      </div>

      <div className="section-title">Outcomes</div>
      <div className="field">
        <textarea
          placeholder="Key outcomes or agreements..."
          value={form.outcomes}
          onChange={(e) => update("outcomes", e.target.value)}
        />
      </div>

      <div className="save-bar">
        {saveStatus && <span className="save-status">{saveStatus}</span>}
        <button className="save-btn" onClick={onSave}>
          Save Interaction
        </button>
      </div>
    </div>
  );
}

import { useEffect, useRef, useState } from "react";
import "./styles/app.css";

// Parse le texte du joueur en segments typés selon la syntaxe utilisée.
// — texte    → player-dialogue
// *texte*    → player-action
// [texte]    → player-intention
// > texte    → player-texto
// reste      → player
function tokenizePlayerInput(raw) {
  const segments = [];
  let rest = raw.trim();

  while (rest.length > 0) {
    let m;

    // *action*
    m = rest.match(/^\*([^*]+)\*/);
    if (m) {
      if (m[1].trim()) segments.push({ type: "player-action", text: m[1].trim() });
      rest = rest.slice(m[0].length).trimStart();
      continue;
    }

    // [intention]
    m = rest.match(/^\[([^\]]+)\]/);
    if (m) {
      if (m[1].trim()) segments.push({ type: "player-intention", text: m[1].trim() });
      rest = rest.slice(m[0].length).trimStart();
      continue;
    }

    // > texto
    m = rest.match(/^>\s*([^\n]+)/);
    if (m) {
      if (m[1].trim()) segments.push({ type: "player-texto", text: m[1].trim() });
      rest = rest.slice(m[0].length).trimStart();
      continue;
    }

    // — dialogue (em-dash ou en-dash), s'arrête au prochain marqueur
    m = rest.match(/^[—–]\s*(.+?)(?=\s*[—–]|\s*\*|\s*\[|\s*>|$)/s);
    if (m) {
      if (m[1].trim()) segments.push({ type: "player-dialogue", text: m[1].trim() });
      rest = rest.slice(m[0].length).trimStart();
      continue;
    }

    // Texte libre jusqu'au prochain marqueur
    m = rest.match(/^(.+?)(?=[—–]|\*|\[|>|$)/s);
    if (m && m[1].trim()) {
      segments.push({ type: "player", text: m[1].trim() });
      rest = rest.slice(m[0].length).trimStart();
      continue;
    }

    // Fallback : tout le reste en plain
    if (rest.trim()) segments.push({ type: "player", text: rest.trim() });
    break;
  }

  return segments;
}

function useGame() {
  const [entries, setEntries] = useState([]);
  const [messages, setMessages] = useState([]);
  const [contacts, setContacts] = useState([]);
  const [meta, setMeta] = useState({ scenario: "", player_character: "", current_date: "", current_time: "" });
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch("/game/start", { method: "POST" })
      .then((r) => r.json())
      .then((data) => {
        setMeta({ scenario: data.scenario, player_character: data.player_character, current_date: data.current_date ?? "", current_time: data.current_time ?? "" });
        setEntries(data.entries ?? []);
        setMessages(data.messages ?? []);
        setContacts(data.contacts ?? []);
        setLoading(false);
      });
  }, []);

  async function sendAction(text) {
    setSending(true);
    setError(null);

    const trimmed = text.trim();
    const segments = tokenizePlayerInput(trimmed);
    const playerEntries = (segments.length > 0 ? segments : [{ type: "player", text: trimmed }])
      .map((seg, i) => ({ id: `player_${Date.now()}_${i}`, type: seg.type, character: null, text: seg.text }));

    setEntries((prev) => [...prev, ...playerEntries]);

    try {
      const response = await fetch("/game/action/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });

      if (!response.ok || !response.body) {
        setError(`Erreur serveur (${response.status})`);
        return;
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() ?? "";
        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          try {
            const event = JSON.parse(line.slice(6));
            if (event.type === "entry") {
              setEntries((prev) => [...prev, event.entry]);
            } else if (event.type === "done") {
              if (event.new_messages?.length) setMessages((prev) => [...prev, ...event.new_messages]);
              if (event.current_date || event.current_time) {
                setMeta((prev) => ({ ...prev, current_date: event.current_date ?? prev.current_date, current_time: event.current_time ?? prev.current_time }));
              }
            }
          } catch {
            /* event malformé, on ignore */
          }
        }
      }
    } catch {
      setError("Connexion perdue. Vérifie que le backend tourne.");
    } finally {
      setSending(false);
    }
  }

  async function sendSms(to, text) {
    const data = await fetch("/game/sms", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ to, text }),
    }).then((r) => r.json());
    const additions = [];
    if (data.player_message) additions.push(data.player_message);
    if (data.npc_replies?.length) additions.push(...data.npc_replies);
    if (additions.length) setMessages((prev) => [...prev, ...additions]);
    return data.sent;
  }

  async function resetGame() {
    await fetch("/game/reset", { method: "POST" });
    window.location.reload();
  }

  return { entries, messages, contacts, meta, loading, sending, error, sendAction, sendSms, resetGame };
}

function StoryFeed({ entries }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [entries]);

  return (
    <main className="story">
      {entries.map((entry) => (
        <article key={entry.id} className={`story-card ${entry.type}`}>
          {entry.character && <h3>{entry.character}</h3>}
          <p>{entry.text}</p>
        </article>
      ))}
      <div ref={bottomRef} />
    </main>
  );
}

const SYNTAX = [
  { label: "*action*", prefix: "*", suffix: "*", placeholder: "action" },
  { label: "— dialogue", prefix: "— ", suffix: "", placeholder: "dialogue" },
  { label: "> texto", prefix: "> ", suffix: "", placeholder: "" },
  { label: "[intention]", prefix: "[", suffix: "]", placeholder: "intention" },
];

function ReplyArea({ onSend, disabled }) {
  const [input, setInput] = useState("");
  const textareaRef = useRef(null);

  function handleSend() {
    const text = input.trim();
    if (!text || disabled) return;
    onSend(text);
    setInput("");
  }

  useEffect(() => {
    const ta = textareaRef.current;
    if (!ta) return;
    ta.style.height = "auto";
    ta.style.height = `${ta.scrollHeight}px`;
  }, [input]);

  function handleKeyDown(e) {
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) handleSend();
  }

  function insertSyntax(prefix, suffix, placeholder) {
    const ta = textareaRef.current;
    if (!ta) return;
    const start = ta.selectionStart;
    const end = ta.selectionEnd;
    const selected = input.slice(start, end);
    const inner = selected || placeholder;
    const replacement = prefix + inner + suffix;
    const newVal = input.slice(0, start) + replacement + input.slice(end);
    setInput(newVal);
    setTimeout(() => {
      ta.focus();
      if (selected) {
        ta.setSelectionRange(start + replacement.length, start + replacement.length);
      } else {
        ta.setSelectionRange(start + prefix.length, start + prefix.length + inner.length);
      }
    }, 0);
  }

  return (
    <footer className="reply-area">
      <textarea
        ref={textareaRef}
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={disabled ? "En cours…" : "Écris la réponse d'Elina…"}
        disabled={disabled}
      />
      <div className="reply-footer">
        <div className="syntax-list">
          {SYNTAX.map((s) => (
            <button
              key={s.label}
              type="button"
              onClick={() => insertSyntax(s.prefix, s.suffix, s.placeholder)}
              disabled={disabled}
            >
              {s.label}
            </button>
          ))}
        </div>
        <button className="send-button" onClick={handleSend} disabled={disabled}>
          {disabled ? "…" : "Envoyer"}
        </button>
      </div>
    </footer>
  );
}

function PhonePanel({ messages, contacts, playerCharacter, onSendSms }) {
  const [activeId, setActiveId] = useState(null);
  const [smsInput, setSmsInput] = useState("");

  // Fusionner les contacts connus avec les conversations existantes, sans le joueur lui-même
  const contactIds = Array.from(
    new Set([
      ...contacts,
      ...messages.map((m) => m.sender).filter(Boolean),
      ...messages.map((m) => m.recipient).filter(Boolean),
    ])
  ).filter((id) => id !== playerCharacter);
  const conversations = contactIds.map((id) => {
    const lastMsg = [...messages].reverse().find((m) => m.sender === id || m.recipient === id);
    return { sender: id, content: lastMsg?.content ?? "" };
  });

  const active = conversations.find((c) => c.sender === activeId) ?? conversations[0];

  const thread = messages.filter(
    (m) => m.sender === active?.sender || m.recipient === active?.sender
  );

  async function handleSmsSend() {
    const text = smsInput.trim();
    if (!text || !active) return;
    await onSendSms(active.sender, text);
    setSmsInput("");
  }

  return (
    <aside className="phone-panel">
      <header className="phone-header">
        <span>📱</span>
        <div>
          <p className="eyebrow">Téléphone</p>
          <h2>Messages</h2>
        </div>
      </header>

      <div className="conversation-list">
        {conversations.map((conv) => (
          <button
            key={conv.sender}
            className={`conversation ${active?.sender === conv.sender ? "active" : ""}`}
            onClick={() => setActiveId(conv.sender)}
          >
            <strong>{conv.sender}</strong>
            <span>{conv.content}</span>
          </button>
        ))}
        {conversations.length === 0 && (
          <p className="empty-inbox">Aucun message pour l'instant.</p>
        )}
      </div>

      {active && (
        <div className="message-preview">
          <h3>{active.sender}</h3>
          {thread.map((m, i) => (
            <p key={i} className={m.sender === active.sender ? "msg-npc" : "msg-player"}>
              {m.content}
            </p>
          ))}
          <div className="sms-reply">
            <input
              value={smsInput}
              onChange={(e) => setSmsInput(e.target.value)}
              placeholder="Répondre…"
              onKeyDown={(e) => e.key === "Enter" && handleSmsSend()}
            />
            <button onClick={handleSmsSend}>→</button>
          </div>
        </div>
      )}
    </aside>
  );
}

export default function App() {
  const { entries, messages, contacts, meta, loading, sending, error, sendAction, sendSms, resetGame } = useGame();

  if (loading) {
    return <div className="app loading">Chargement…</div>;
  }

  return (
    <div className="app">
      <section className="game-panel">
        <header className="topbar">
          <div>
            <p className="eyebrow">Scénario</p>
            <h1>{meta.scenario || "Ink & Fate"}</h1>
          </div>
          <div className="player-badge">
            <span>Personnage</span>
            <strong>{meta.player_character}</strong>
          </div>
          {(meta.current_date || meta.current_time) && (
            <div className="time-badge">
              {meta.current_date && <span>{meta.current_date}</span>}
              {meta.current_time && <span>{meta.current_time}</span>}
            </div>
          )}
          <button className="reset-button" onClick={resetGame} title="Recommencer depuis zéro">↺</button>
        </header>

        <StoryFeed entries={entries} />
        {error && <div className="error-banner">{error}</div>}
        <ReplyArea onSend={sendAction} disabled={sending} />
      </section>

      <PhonePanel messages={messages} contacts={contacts} playerCharacter={meta.player_character} onSendSms={sendSms} />
    </div>
  );
}

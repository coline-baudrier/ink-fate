import { useState } from "react";
import "./index.css";
import { conversations } from "./data/conversations";
import { characters } from "./data/characters";
import { currentScene } from "./data/scene";
import { player } from "./data/player";
import { timelineEvents } from "./data/timeline";
import { settings } from "./data/settings";

type View =
  | "scene"
  | "phone"
  | "player"
  | "characters"
  | "relations"
  | "timeline"
  | "journal"
  | "settings";

function App() {
  const [activeView, setActiveView] = useState<View>("scene");
  const [activeConversationId, setActiveConversationId] = useState("dean");
  const phoneNotifications = player.notifications.filter(
    (notification) => notification.type === "phone_message",
  );

  const unreadTotal = phoneNotifications.length;

  const activeConversation = conversations.find(
    (conversation) => conversation.id === activeConversationId,
  );

  const renderContent = () => {
    switch (activeView) {
      case "phone":
        return (
          <div className="content-card">
            <div className="section-title">
              <h2>📱 Téléphone</h2>

              {unreadTotal > 0 && (
                <span className="notification-pill">
                  {unreadTotal} nouveau message
                </span>
              )}
            </div>

            <div className="phone-shell">
              <div className="phone-conversations">
                <h3>Messages</h3>

                {conversations.map((conversation) => (
                  <button
                    key={conversation.id}
                    className={
                      activeConversationId === conversation.id
                        ? "conversation-row active"
                        : "conversation-row"
                    }
                    onClick={() => setActiveConversationId(conversation.id)}
                  >
                    <div className={`avatar-circle ${conversation.id}`}>
                      {conversation.canText ? conversation.initials : "🔒"}
                    </div>

                    <div className="conversation-text">
                      <div>
                        <strong>{conversation.name}</strong>

                        {conversation.unreadCount > 0 && (
                          <span className="unread-badge">
                            {conversation.unreadCount}
                          </span>
                        )}
                      </div>

                      <p>
                        {conversation.canText
                          ? conversation.preview
                          : conversation.lockedReason}
                      </p>
                    </div>
                  </button>
                ))}
              </div>

              <div className="phone-chat">
                {activeConversation && (
                  <>
                    <div className="phone-chat-header">
                      <div className={`avatar-circle ${activeConversation.id}`}>
                        {activeConversation.canText
                          ? activeConversation.initials
                          : "🔒"}
                      </div>

                      <div>
                        <strong>{activeConversation.name}</strong>
                        <p>
                          {activeConversation.canText
                            ? "Disponible par SMS"
                            : activeConversation.lockedReason}
                        </p>
                      </div>
                    </div>

                    {activeConversation.canText ? (
                      <>
                        <div className="phone-messages">
                          {activeConversation.messages.map((message, index) => (
                            <div
                              key={index}
                              className={
                                message.sender === "player"
                                  ? "sms-bubble player"
                                  : "sms-bubble character"
                              }
                            >
                              {message.text}
                            </div>
                          ))}
                        </div>

                        <div className="phone-input">
                          <input placeholder="Écrire un SMS..." />
                          <button>Envoyer</button>
                        </div>
                      </>
                    ) : (
                      <div className="locked-chat">
                        <div className="locked-icon">🔒</div>
                        <h3>Conversation verrouillée</h3>
                        <p>{activeConversation.lockedReason}</p>
                      </div>
                    )}
                  </>
                )}
              </div>
            </div>
          </div>
        );

      case "player":
        return (
          <div className="content-card">
            <div className="player-profile">
              <div className="player-profile-header">
                <div className="player-profile-avatar">
                  {player.avatarInitials}
                </div>

                <div>
                  <p className="profile-kicker">Personnage principal</p>
                  <h2>{player.name}</h2>
                  <p className="profile-subtitle">
                    Nouvelle année à Briar University · Off Campus
                  </p>
                </div>
              </div>

              <div className="player-profile-grid">
                <section className="profile-panel">
                  <h3>État actuel</h3>
                  <p>
                    <strong>Lieu :</strong> {currentScene.location}
                  </p>
                  <p>
                    <strong>Scène :</strong> {currentScene.title}
                  </p>
                  <p>
                    <strong>Notifications :</strong>{" "}
                    {player.notifications.length}
                  </p>
                </section>

                <section className="profile-panel">
                  <h3>Téléphone</h3>
                  <p>
                    <strong>Contacts disponibles :</strong> Dean, Beau
                  </p>
                  <p>
                    <strong>Contact verrouillé :</strong> Hannah
                  </p>
                  <p>
                    <strong>Messages non lus :</strong> {unreadTotal}
                  </p>
                </section>

                <section className="profile-panel wide">
                  <h3>Résumé narratif</h3>
                  <p>
                    Elina vient d’arriver sur le campus de Briar University.
                    Elle retrouve Beau, son frère protecteur, et rencontre Dean,
                    dont l’attitude taquine pourrait vite devenir un point de
                    tension.
                  </p>
                </section>
              </div>
            </div>
          </div>
        );

      case "characters":
        return (
          <div className="content-card">
            <h2>👤 Personnages</h2>

            <div className="character-grid">
              {characters.map((character) => (
                <div
                  key={character.id}
                  className={
                    character.known
                      ? "big-character-card"
                      : "big-character-card locked"
                  }
                >
                  <h3>{character.name}</h3>
                  <p>Humeur : {character.mood}</p>
                  <p>
                    Relation :{" "}
                    {character.relation !== null
                      ? `${character.relation}%`
                      : "Inconnue"}
                  </p>
                  <p>Téléphone : {character.phoneStatus}</p>
                </div>
              ))}
            </div>
          </div>
        );

      case "relations":
        return (
          <div className="content-card">
            <h2>❤️ Relations</h2>

            <div className="relations-page">
              {characters
                .filter((character) => character.relation !== null)
                .map((character) => (
                  <div className="relation-card" key={character.id}>
                    <div>
                      <h3>{character.name}</h3>
                      <p>{character.mood}</p>
                    </div>

                    <strong>{character.relation}%</strong>

                    <div className="relation-page-bar">
                      <div
                        style={{ width: `${character.relation}%` }}
                        className="relation-page-fill"
                      />
                    </div>
                  </div>
                ))}
            </div>
          </div>
        );

      case "timeline":
        return (
          <div className="content-card">
            <div className="section-title">
              <h2>🔍 Timeline</h2>
              <span className="notification-pill">Debug narratif</span>
            </div>

            <div className="timeline-list">
              {timelineEvents.map((event) => (
                <article
                  className={`timeline-event ${event.type}`}
                  key={event.id}
                >
                  <div className="timeline-time">{event.time}</div>

                  <div className="timeline-content">
                    <strong>{event.title}</strong>
                    <p>{event.description}</p>
                  </div>
                </article>
              ))}
            </div>
          </div>
        );

      case "journal":
        return (
          <div className="content-card">
            <h2>📚 Journal</h2>

            <ul className="journal-list">
              <li>Arrivée à Briar University</li>
              <li>Retrouvailles avec Beau</li>
              <li>Première rencontre avec Dean</li>
              <li>Dean peut maintenant envoyer des SMS à Elina</li>
            </ul>
          </div>
        );

      case "settings":
        return (
          <div className="content-card">
            <h2>⚙️ Paramètres</h2>

            <div className="settings-section">
              <div className="setting-row">
                <div>
                  <strong>Contenu NSFW</strong>

                  <p>
                    Autorise les scènes romantiques et sexuelles explicites
                    lorsque l'histoire y mène naturellement.
                  </p>
                </div>

                <label className="switch">
                  <input
                    type="checkbox"
                    checked={settings.nsfwEnabled}
                    readOnly
                  />

                  <span className="slider"></span>
                </label>
              </div>
            </div>
          </div>
        );

      default:
        return (
          <div className="content-card">
            <div className="scene-banner">
              <p>{currentScene.location}</p>
              <h2>{currentScene.title}</h2>
            </div>

            <div className="narration">{currentScene.narration}</div>

            {currentScene.dialogues.map((dialogue, index) => (
              <div key={index} className={`message ${dialogue.className}`}>
                <strong>{dialogue.speaker}</strong>
                <p>« {dialogue.text} »</p>
              </div>
            ))}
          </div>
        );
    }
  };

  return (
    <div className="app">
      <header className="topbar">
        <h1>Ink & Fate</h1>

        <div className="topbar-right">
          <span>{player.name}</span>

          {player.notifications.length > 0 && (
            <span className="notification-pill">
              🔔 {player.notifications.length}
            </span>
          )}

          <button>Save</button>
        </div>
      </header>

      <div className="main-layout">
        <aside className="navigation">
          <div className="player-card">
            <div className="player-avatar">{player.avatarInitials}</div>

            <div>
              <strong>{player.name}</strong>
              <p>Personnage actif</p>
            </div>

            {player.notifications.length > 0 && (
              <span className="player-notification">
                {player.notifications.length}
              </span>
            )}
          </div>
          <button
            onClick={() => setActiveView("player")}
            className={activeView === "player" ? "active" : ""}
          >
            ✨ Mon personnage
          </button>
          <button
            onClick={() => setActiveView("scene")}
            className={activeView === "scene" ? "active" : ""}
          >
            📖 Scène
          </button>

          <button
            onClick={() => setActiveView("phone")}
            className={activeView === "phone" ? "active" : ""}
          >
            📱 Téléphone
            {unreadTotal > 0 && (
              <span className="nav-badge">{unreadTotal}</span>
            )}
          </button>

          <button
            onClick={() => setActiveView("characters")}
            className={activeView === "characters" ? "active" : ""}
          >
            👤 Personnages
          </button>

          <button
            onClick={() => setActiveView("relations")}
            className={activeView === "relations" ? "active" : ""}
          >
            ❤️ Relations
          </button>

          <button
            onClick={() => setActiveView("timeline")}
            className={activeView === "timeline" ? "active" : ""}
          >
            🔍 Timeline
          </button>

          <button
            onClick={() => setActiveView("journal")}
            className={activeView === "journal" ? "active" : ""}
          >
            📚 Journal
          </button>

          <button
            onClick={() => setActiveView("settings")}
            className={activeView === "settings" ? "active" : ""}
          >
            ⚙️ Paramètres
          </button>
        </aside>

        <main className="main-content">{renderContent()}</main>
      </div>

      {activeView === "scene" && (
        <footer className="player-input">
          <input placeholder='Écrire une action ou une réplique... Exemple : *Je souris* "Salut."' />
          <button>Envoyer</button>
        </footer>
      )}
    </div>
  );
}

export default App;

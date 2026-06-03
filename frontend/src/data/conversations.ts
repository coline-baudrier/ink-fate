export type Conversation = {
  id: string;
  name: string;
  initials: string;
  canText: boolean;
  unreadCount: number;
  lockedReason?: string;
  preview: string;
  messages: {
    sender: "player" | "character";
    text: string;
  }[];
};

export const conversations: Conversation[] = [
  {
    id: "dean",
    name: "Dean",
    initials: "D",
    canText: true,
    unreadCount: 1,
    preview: "Hey Maxwell. Tu comptes survivre à ta première semaine ?",
    messages: [
      {
        sender: "character",
        text: "Hey Maxwell. Tu comptes survivre à ta première semaine ?",
      },
    ],
  },
  {
    id: "beau",
    name: "Beau",
    initials: "B",
    canText: true,
    unreadCount: 0,
    preview: "N'oublie pas qu'on mange ensemble ce soir.",
    messages: [
      {
        sender: "character",
        text: "N'oublie pas qu'on mange ensemble ce soir.",
      },
    ],
  },
  {
    id: "hannah",
    name: "Hannah",
    initials: "H",
    canText: false,
    unreadCount: 0,
    lockedReason: "Numéro non échangé",
    preview: "Conversation indisponible",
    messages: [],
  },
];

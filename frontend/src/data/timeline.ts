export type TimelineEventType =
  | "scene"
  | "memory"
  | "relationship"
  | "phone"
  | "warning";

export type TimelineEvent = {
  id: string;
  time: string;
  type: TimelineEventType;
  title: string;
  description: string;
};

export const timelineEvents: TimelineEvent[] = [
  {
    id: "event-1",
    time: "10:20",
    type: "scene",
    title: "Scène démarrée",
    description: "Elina arrive sur le campus de Briar University.",
  },
  {
    id: "event-2",
    time: "10:21",
    type: "relationship",
    title: "Relation initialisée",
    description: "Dean Di Laurentis est ajouté aux relations connues.",
  },
  {
    id: "event-3",
    time: "10:22",
    type: "memory",
    title: "Mémoire ajoutée",
    description: "Dean semble intrigué par Elina.",
  },
  {
    id: "event-4",
    time: "10:30",
    type: "phone",
    title: "Contact débloqué",
    description: "Dean peut désormais envoyer des SMS à Elina.",
  },
  {
    id: "event-5",
    time: "10:31",
    type: "warning",
    title: "Point à surveiller",
    description: "Vérifier que Dean ne devient pas trop familier trop vite.",
  },
];

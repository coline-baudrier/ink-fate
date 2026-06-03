export type Character = {
  id: string;
  name: string;
  mood: string;
  relation: number | null;
  phoneStatus: string;
  known: boolean;
};

export const characters: Character[] = [
  {
    id: "dean",
    name: "Dean Di Laurentis",
    mood: "Taquin",
    relation: 18,
    phoneStatus: "Numéro échangé",
    known: true,
  },
  {
    id: "beau",
    name: "Beau Maxwell",
    mood: "Protecteur",
    relation: 92,
    phoneStatus: "Numéro échangé",
    known: true,
  },
  {
    id: "hannah",
    name: "Hannah Wells",
    mood: "Inconnue",
    relation: null,
    phoneStatus: "Numéro non échangé",
    known: false,
  },
];

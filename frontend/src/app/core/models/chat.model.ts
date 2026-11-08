// Informations sur un document source
export interface Source {
  citation: string;
  document: string;
  reference: string;
  page: number;
  score: number;
}

// Réponse complète du système RAG
export interface AskResponse {
  question: string;
  answer: string;
  sources: Source[];
  strategy: string;
}

// Informations envoyées au backend
export interface AskRequest {
  question: string;
  top_k: number;
  strategy: string;
}
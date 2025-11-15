// ----------------------------
// Shared API Types
// ----------------------------

export interface QueryRequest {
  query: string;
  top_k?: number;
}

export interface RetrievedSource {
  id: string;
  source: string;
  chunk_index?: number;
  score?: number;
  page?: number;
}

export interface QueryResponse {
  answer: string;
  sources: RetrievedSource[];
}

// ----------------------------
// Documents API
// ----------------------------

export interface DocumentListResponse {
  documents: string[];
}

export interface ReindexResponse {
  indexed_chunks: number;
}

// ----------------------------
// Reranker Training
// ----------------------------

export interface TrainingSample {
  query: string;
  positive_passages: string[];
  negative_passages: string[];
}

export interface TrainRerankerRequest {
  samples: TrainingSample[];
  num_epochs: number;
  batch_size: number;
}

export interface TrainRerankerResponse {
  status: string;
  model_path: string;
}

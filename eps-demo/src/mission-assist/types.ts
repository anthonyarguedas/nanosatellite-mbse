export type RetrievalMethod = 'semantic-qwen' | 'lexical-tfidf';

export interface MissionSource {
  id: string;
  title: string;
  url: string;
  revision: string;
  location: string;
  retrievedAt: string;
  quotes: string[];
}

/** Interpretation and epoch are retained alongside the original source value. */
export interface MissionParameter<T> {
  value: T;
  sourceIds: string[];
  original: string;
  meaning: string;
}

export interface MissionRecord {
  id: string;
  name: string;
  identity: string;
  revision: string;
  description: string;
  descriptionSourceIds: string[];
  status: 'flown' | 'study';
  epoch: string;
  statusDetail: string;
  orbit: {
    altitudeKm: MissionParameter<number | [number, number]> | null;
    orbitType: MissionParameter<string> | null;
    inclinationDeg: MissionParameter<number> | null;
  };
  sources: MissionSource[];
  caveats: string[];
}

export interface MissionCatalogue {
  revision: string;
  missions: MissionRecord[];
}

export interface MissionAnalogue {
  mission: MissionRecord;
  score: number;
  method: RetrievalMethod;
  matchedTerms: string[];
  catalogueRevision: string;
}

/** Only produced after explicit acceptance of a sourced scalar altitude. */
export interface MissionMatch extends MissionAnalogue {
  altitudeKm: number;
  acceptedAt: string;
}

export interface MissionSearchResult {
  status: 'matches' | 'abstained';
  matches: MissionAnalogue[];
  reason: string;
  method: RetrievalMethod;
}

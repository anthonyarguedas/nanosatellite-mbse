import rawCatalog from './catalog.json';
import type { Catalog } from '../types';

/** Reviewed transcription of manufacturer data. Missing values remain explicit. */
export const catalog = rawCatalog as unknown as Catalog;

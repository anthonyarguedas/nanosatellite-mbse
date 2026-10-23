import { describe, expect, it } from 'vitest';
import { missionSearchIsCurrent } from './mission-session';

describe('query-bound mission presentation sessions',()=>{
  const context={query:'Same authored ConOps',generation:4,method:'lexical-tfidf' as const};
  it('retains query association across ordinary graph navigation',()=>{
    expect(missionSearchIsCurrent(context,context.query,4,'lexical-tfidf')).toBe(true);
  });
  it('invalidates the same query on workspace replacement',()=>{
    expect(missionSearchIsCurrent(context,context.query,5,'lexical-tfidf')).toBe(false);
  });
  it('rejects changed queries, methods and absent results',()=>{
    expect(missionSearchIsCurrent(context,'New query',4,'lexical-tfidf')).toBe(false);
    expect(missionSearchIsCurrent(context,context.query,4,'semantic-qwen')).toBe(false);
    expect(missionSearchIsCurrent(null,context.query,4,'lexical-tfidf')).toBe(false);
  });
});

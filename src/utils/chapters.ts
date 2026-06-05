import { getCollection, type CollectionEntry } from 'astro:content';

export type Chapter = CollectionEntry<'chapters'>;

/** Sort key: numbered chapters by their number, appendix (string chapter) last. */
function sortKey(entry: Chapter): number {
  const c = entry.data.chapter;
  if (typeof c === 'number') return c;
  // Any string chapter ("A") sorts after all numbered chapters.
  return 1000;
}

/** A human label for the chapter number column ("1".."13", "Appendix"). */
export function chapterLabel(entry: Chapter): string {
  const c = entry.data.chapter;
  if (typeof c === 'number') return String(c);
  return 'Appendix';
}

/** All chapters in reading order. */
export async function getOrderedChapters(): Promise<Chapter[]> {
  const all = await getCollection('chapters');
  return all.sort((a, b) => {
    const ka = sortKey(a);
    const kb = sortKey(b);
    if (ka !== kb) return ka - kb;
    // Stable fallback on id (filename) for deterministic order.
    return a.id.localeCompare(b.id);
  });
}

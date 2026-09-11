# Moosic Clustering Project — Session Report

**Case study:** Moosic — automating playlist creation from Spotify audio features
**Dataset:** 5000 songs, features: danceability, energy, acousticness, tempo, valence
**Algorithm:** K-Means (baseline for comparison against DBSCAN/Agglomerative, planned as future work)

---

## 1. Starting Question

The project began from a genuine point of confusion: with 5000 songs, a "fine" clustering
(many clusters) produces too many small, hard-to-use groups, while a coarse clustering
(few clusters) produces oversized, musically meaningless groups. This raised the question
of whether K-means-based playlist generation is a realistic technique or just a teaching
exercise.

**Conclusion reached:** it's a real technique, but it's a stepping stone, not a complete
solution on its own. Inertia and the silhouette score measure geometric structure — how
tight and how separated clusters are — but neither has any concept of what makes a good
*playlist*. This is precisely the tension the case study's "Aligning Clustering with
Business Goals" section addresses: mathematically clean clusters and musically meaningful
ones are not guaranteed to be the same thing. The rest of this session was spent building
a pipeline that treats the business constraint (a usable playlist size) as an explicit
input to the algorithm, rather than hoping it emerges from the metrics alone.

---

## 2. Auditing the Existing Sandbox

Before building anything new, the existing scripts (`moosic.py`, `scale.py`, `test.py`)
were reviewed and several concrete issues were found:

| Script | Issue | Cause |
|---|---|---|
| `moosic.py` | `KeyError` risk | Feature name typo: `'acoustiness'` instead of `'acousticness'` |
| `test.py` | Inconsistent path | Loaded `../data/songs.csv` while other scripts used `songs.csv` |
| `moosic.py` | k chosen inconsistently | Computed inertia/silhouette across k=2–9, then hardcoded `best_k=2` regardless of the analysis |
| `scale.py` | k chosen automatically | Picked k via `argmax(silhouette)` with no human judgement — exactly the anti-pattern the business-alignment lesson warns against |
| `test.py` | k chosen arbitrarily | Hardcoded `k=3`, no metric computed at all |

Each script used a different, uncoordinated philosophy for choosing k — this was the root
cause of inconsistent, hard-to-compare results across the sandbox.

---

## 3. Methodology Built

### 3.1 Baseline ("free") clustering

Following the elbow/silhouette method from the course notebooks, a baseline clustering was
run on the full 5000-song dataset with no target size imposed. The silhouette curve showed
a knee around **k=8**.

**Bug found and fixed — radar chart axis mismatch.** The first radar chart of the 8
clusters showed all curves nearly overlapping. Root cause: cluster centroids were
inverse-transformed back into original units (e.g. tempo in BPM) but plotted on an axis
hardcoded to `(0, 1)` — meant for scaled data. This silently clipped/distorted every value.
**Fix:** plot the *scaled* centroids (already 0–1 under `MinMaxScaler`) directly, and keep
the inverse-transformed values only for the printed reference table.

**Two indentation bugs found and fixed**, both of the same shape: a `for` loop meant to run
"once per cluster" was mistakenly un-indented to sit *outside* its parent loop, so it only
ran once total, using leftover data from the last cluster processed. This affected both the
terminal playlist printout and the generated Markdown report.

At k=8 (5000 songs), cluster sizes ranged roughly 380–1180 songs each — confirming the
"free" clustering, left alone, does not produce anything close to playlist-sized groups.

### 3.2 Business constraint: target playlist size

**Decision: target playlist size = 20–60 songs.**

This number is the single most important design choice in the whole pipeline — see the
parameter sensitivity results in Section 5.

### 3.3 Recursive splitting

Rather than forcing a single global k, clusters are split **recursively**: any cluster
larger than `TARGET_MAX` is re-clustered on just its own members (fresh local KMeans, small
k), and this repeats until every leaf is under the target size or hits a floor
(`MIN_SONGS_TO_SPLIT`).

Key design decision: all branches share **one global scaler**, fit once on the full
dataset — not a fresh scaler per branch — so centroids from different branches remain
comparable to each other later.

### 3.4 Global reassignment pass

Recursive splitting is *locally* greedy: a song can end up in a branch only because it was
the least-wrong option available at that point in the tree, even if a completely different,
already-finished branch would now be a better fit. **Fix:** after all leaves are
determined, take every leaf centroid together and run one flat nearest-centroid pass over
all 5000 songs, reassigning anything closer to a different leaf's centroid.

### 3.5 Merging undersized leaves

Because the stopping rule only checks the *upper* bound (`n <= TARGET_MAX`), tiny leaves
(sometimes 1–2 songs) are a near-guaranteed side effect of uneven splits — not a data
problem, a structural one. A merge step folds any leaf below `TARGET_MIN` into a
neighboring cluster.

This step went through **three bug-fix iterations**, documented here because the debugging
process itself is part of the learning record:

1. **Order-of-operations bug:** merging was originally done *before* the global
   reassignment pass, so reassignment silently discarded the merge and reintroduced tiny
   clusters. **Fix:** reassign first, then merge the *result* of reassignment, and do not
   reassign again afterward.
2. **Unbounded merge target bug:** the merge function had no upper-size check, so
   undersized leaves could snowball a single cluster to 100+ songs. **Fix:** prefer merge
   targets that stay under `TARGET_MAX`, falling back only if nothing fits.
3. **Fake "nearest neighbor" bug:** `pairwise_distances_argmin` was called but its result
   was never used — the merge target was actually just the first entry in an unsorted
   candidate list, not the true nearest cluster. This caused one specific cluster to
   repeatedly "win" merges by list position, producing a single cluster of ~2200 songs in
   one test run. **Fix:** compute real Euclidean distances between centroids, sort
   nearest-to-farthest, and walk that order for a valid merge target.

---

## 4. Experiment Sweeps — Parameter Sensitivity

Multiple sweeps were run varying `target_min`/`target_max`, `min_songs_to_split`, and
`max_k_per_split`, logged to a running CSV.

### Finding 1 — target range dominates every other parameter

| Range | Width | % in range |
|---|---|---|
| 12–20 | 8 | 61–70% |
| 15–25 | 10 | 65% |
| 30–40 | 10 | 24–35% |
| 15–30 | 15 | 79–85% |
| 20–40 | 20 | 81–87% |
| 30–60 | 30 | 84–87% |
| 20–60 | 40 | 96–98% |

Wider windows perform better, as expected — but **width alone doesn't fully explain the
results.** 15–25 and 30–40 are both 10 wide, yet 15–25 outperforms 30–40 by more than 2×.
This shows that the *position* of the target window relative to the data's natural leaf-size
distribution matters as much as its width — the recursive splitter naturally produces a lot
of leaves in the low-20s range, so windows that include that region perform much better than
windows that don't, independent of width.

### Finding 2 — `max_k_per_split` sensitivity scales with window narrowness

| Window width | Spread in % across `max_k_per_split` values |
|---|---|
| 8 | ~9 points |
| 15 | ~5.5 points |
| 20 | ~6 points |
| 40 | ~1.5 points |

On a wide target window there's enough slack that any reasonable branching factor works. On
a narrow window, there's much less room for error, so how coarsely each split branches
matters far more.

### Finding 3 — `min_songs_to_split` has **zero effect**, structurally

Confirmed identically across every sweep, including a direct retest at 5, 10, 15, 20 on the
same window: results were identical to the decimal. Root cause: the stopping condition is
`if n <= TARGET_MAX or n < MIN_SONGS_TO_SPLIT`. Since `TARGET_MAX` was larger than every
`MIN_SONGS_TO_SPLIT` value tested, the first condition always fires first as `n` shrinks —
the second condition is mathematically unreachable under these settings. This is not a
tuning result, it's a logical guarantee of the current code.

---

## 5. Case Study: Investigating the Largest Remaining Cluster

Even after the merge fix, one cluster consistently remained oversized relative to the
20–60 (and stricter) target windows. Rather than assuming this was still a bug, it was
investigated directly:

- **Feature comparison vs. dataset average:** danceability +0.21, energy +0.12, valence
  +0.14, tempo −9 BPM — a real, upbeat/danceable profile, not a "sits near the average of
  everything" generic bucket.
- **Within-cluster standard deviation:** tight across danceability, energy, and valence —
  confirming this is an internally coherent group, not a merge-artifact grab-bag.
- **Manual listen/inspection:** largely consistent with dance-pop/reggaeton
  ("Tusa," "Perfect Strangers," "Don't You Worry Child") — but **"Teenage Dirtbag"**, an
  alt-rock track, was also present, almost certainly grouped in on tempo/energy alone. This
  is a concrete, specific example of the case study's opening question — audio features
  cannot fully capture genre or "feel" the way a human listener does.
- **Language mixing:** English, Spanish, German, and Italian titles all appeared in the
  same cluster — expected, since none of the five chosen features encode language, a
  limitation the case study explicitly names.

**Conclusion:** this cluster is genuinely coherent by the numbers, just oversized relative
to a usable playlist length. Structural soundness and business-appropriate size are two
different properties, and this cluster is a clean, documented example of a case where they
diverge.

---

## 6. Recursive Re-Split of the Largest Cluster

The 97-song cluster above was tested for further splitting.

| k | Silhouette | Sizes |
|---|---|---|
| 2 | 0.413 | 21, 76 |
| 3 | 0.335 | 26, 20, 51 |
| 4 | 0.300 | 20, 21, 30, 26 |

Silhouette score decreases monotonically as k increases — **k=2 is the best-supported
split, not merely the simplest option.**

**Result at k=2:**
- Sub-cluster 0 (21 songs): tempo ~130 BPM, energy 0.79 — faster, driving tracks
- Sub-cluster 1 (76 songs): tempo ~104 BPM, valence 0.625, higher acousticness — slower,
  warmer tracks

**Notable correction:** based on the song list alone, this split initially looked like it
might follow a genre/language line (Latin/reggaeton vs. EDM/dance-pop). The actual feature
data shows the real separating axis is **tempo and energy** — language and apparent genre
cut across both sub-clusters. This is a useful, honest finding: even direct human inspection
of song titles reached for the wrong explanation until the underlying numbers were checked.

---

## 7. Summary of Bugs Found and Fixed

| # | Bug | Symptom | Fix |
|---|---|---|---|
| 1 | Feature name typo | `KeyError` on `'acoustiness'` | Corrected spelling |
| 2 | Inconsistent file paths | Script only worked from one specific working directory | Standardized relative paths |
| 3 | k chosen inconsistently across scripts | Non-comparable results | Adopted one documented target-range-driven method |
| 4 | Radar chart axis mismatch | All clusters appeared to overlap | Plot scaled centroids, not inverse-transformed ones |
| 5 | Indentation bug (×2) | Loops ran once instead of per-cluster | Correct indentation |
| 6 | Merge before reassignment | Merge silently undone, tiny clusters returned | Reassign first, merge the result |
| 7 | Unbounded merge target | One cluster could balloon past target size | Prefer merge targets under `TARGET_MAX` |
| 8 | Fake nearest-neighbor merge | `pairwise_distances_argmin` computed but unused; one cluster ballooned to ~2200 songs | Use real sorted distances for merge target selection |
| 9 | Log schema drift | Old and new CSV rows had different column counts, causing misleading duplicate-looking rows | Recommend a version/notes tag on future log rows |

---

## 8. Reflections — Aligning Clustering with Business Goals

The core lesson of this session, tied directly back to the course material: **inertia and
silhouette narrow down candidates, they don't make the final decision.** The actual
business constraint (a usable playlist length) had to be fed into the pipeline explicitly,
as a target range driving a recursive splitting/merging process — it never emerged on its
own from the metrics. Even after building that pipeline correctly, the "is this cluster
actually good" question still required direct inspection: feature-average comparisons,
within-cluster spread, and reading actual song titles. The metrics guided *where to look*;
they never replaced *looking*.

---

## 9. Known Limitations / Honest Gaps

- The re-split heuristic (`k = n // TARGET_MAX`, capped) is a simple rule, not an
  elbow/silhouette search at every branch — a deliberate simplification to avoid
  over-engineering, not a rigorously optimized choice.
- `MIN_SONGS_TO_SPLIT` is currently dead code under the tested configurations — a candidate
  for either removal or a redesigned stopping rule if pursued further.
- No listening/human-evaluation pass has been done at scale — only a handful of clusters
  have been spot-checked by title and feature averages, per the case study's own guidance
  that structure and meaningfulness are not the same thing.
- Only K-Means has been tested. DBSCAN and Agglomerative Clustering — explicitly asked for
  by the case study — have not yet been implemented or compared.

---

## 10. Next Steps

1. Compare K-Means against **DBSCAN** and **Agglomerative Clustering** on the same
   evaluation lens (size distribution, coherence, business-fit) — the case study's second
   open question, not yet addressed.
2. Decide whether to invest in a full parameter-sensitivity re-sweep now that the merge
   logic is fixed, versus treating the current findings as sufficient for the report.
3. Optional: a proper human-listening pass on a larger sample of final playlists, beyond
   the single deep-dive case study in Section 5–6.

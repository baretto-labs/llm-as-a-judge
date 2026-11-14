// Probes for batch_03 TypeScript examples: chunk() slice bug, and async in forEach.

// b03-001 candidate (buggy): slice(i, size) instead of slice(i, i + size)
function chunkBuggy<T>(items: T[], size: number): T[][] {
  const out: T[][] = [];
  for (let i = 0; i < items.length; i += size) {
    out.push(items.slice(i, size));
  }
  return out;
}

// b03-002 candidate (correct)
function chunkOk<T>(items: T[], size: number): T[][] {
  if (!Number.isInteger(size) || size <= 0) {
    throw new RangeError(`size doit être un entier positif, reçu ${size}`);
  }
  const out: T[][] = [];
  for (let i = 0; i < items.length; i += size) {
    out.push(items.slice(i, i + size));
  }
  return out;
}

console.log("chunkBuggy([1..7], 3) =", JSON.stringify(chunkBuggy([1, 2, 3, 4, 5, 6, 7], 3)));
console.log("chunkOk([1..7], 3)    =", JSON.stringify(chunkOk([1, 2, 3, 4, 5, 6, 7], 3)));
console.log("chunkOk([1,2], 5)     =", JSON.stringify(chunkOk([1, 2], 5)));
try {
  chunkOk([1, 2], 0);
} catch (e) {
  console.log("chunkOk([1,2], 0)     =", (e as Error).constructor.name + ": " + (e as Error).message);
}

// b03-003: await inside forEach does not block the caller
const saved: number[] = [];
async function save(n: number): Promise<void> {
  await new Promise((r) => setTimeout(r, 10 * (3 - n)));
  saved.push(n);
}

async function saveAllBroken(items: number[]): Promise<void> {
  items.forEach(async (item) => {
    await save(item);
  });
  console.log("  [broken] après forEach, saved =", JSON.stringify(saved));
}

async function saveAllOk(items: number[]): Promise<void> {
  await Promise.all(items.map((item) => save(item)));
  console.log("  [ok] après Promise.all, saved =", JSON.stringify(saved));
}

(async () => {
  console.log("b03-003:");
  saved.length = 0;
  await saveAllBroken([1, 2, 3]);
  await new Promise((r) => setTimeout(r, 100));
  console.log("  [broken] 100 ms plus tard, saved =", JSON.stringify(saved));
  saved.length = 0;
  await saveAllOk([1, 2, 3]);
})();

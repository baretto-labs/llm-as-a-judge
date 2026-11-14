// Fact-checks the TypeScript claims of batch_03.
//  - b03-003 : `await items.forEach(async …)` n'attend rien (le correctif proposé est inopérant)
//  - b03-010 : excess property check sur littéral frais, pas via une variable
// Le fichier doit compiler : les @ts-expect-error échouent si TypeScript n'émet PAS l'erreur attendue.

const saved: number[] = [];

async function save(n: number): Promise<void> {
  await new Promise((r) => setTimeout(r, 10 * (3 - n)));
  saved.push(n);
}

// Le « correctif » proposé par la réponse évaluée en b03-003
async function saveAllAwaitForEach(items: number[]): Promise<void> {
  await items.forEach(async (item) => {
    await save(item);
  });
}

// Le correctif réellement valide
async function saveAllPromiseAll(items: number[]): Promise<void> {
  await Promise.all(items.map((item) => save(item)));
}

// ── b03-010 : typage structurel et contrôle des propriétés excédentaires ─────
type Options = { retries: number };
function run(o: Options): number {
  return o.retries;
}

// @ts-expect-error : littéral frais, la propriété en trop est refusée
run({ retries: 3, verbose: true });

const opts = { retries: 3, verbose: true };
run(opts); // accepté : opts n'est plus un littéral frais

(async () => {
  saved.length = 0;
  await saveAllAwaitForEach([1, 2, 3]);
  console.log("b03-003 juste après `await forEach` :", JSON.stringify(saved),
    saved.length === 0 ? "(OK : rien n'est terminé, le correctif est inopérant)" : "(KO)");
  await new Promise((r) => setTimeout(r, 100));
  console.log("b03-003 100 ms plus tard              :", JSON.stringify(saved));

  saved.length = 0;
  await saveAllPromiseAll([1, 2, 3]);
  console.log("b03-003 après `await Promise.all`     :", JSON.stringify(saved),
    saved.length === 3 ? "(OK : tout est terminé)" : "(KO)");

  console.log("b03-010 compilation : les deux cas se comportent comme décrit (voir @ts-expect-error)");
})();

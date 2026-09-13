// Probes for batch_06 TS/JS: analyse des dates, clonage par JSON, structuredClone.

console.log("── analyse des chaînes de date");
const dateOnly = new Date("2026-03-01");
const dateTime = new Date("2026-03-01T00:00:00");
console.log("   new Date('2026-03-01')          ->", dateOnly.toISOString(), "| local:", dateOnly.toString().slice(0, 24));
console.log("   new Date('2026-03-01T00:00:00') ->", dateTime.toISOString(), "| local:", dateTime.toString().slice(0, 24));
console.log("   décalage local (min)            :", new Date("2026-03-01").getTimezoneOffset());
console.log("   getDate() sur la version UTC    :", dateOnly.getDate(), "| getUTCDate() :", dateOnly.getUTCDate());
console.log("   new Date('2026-02-30')          ->", new Date("2026-02-30").toString().slice(0, 15));
console.log("   Date.parse('01/03/2026')        ->", new Date("01/03/2026").toISOString().slice(0, 10), "(mois/jour aux US)");

console.log("── clonage par aller-retour JSON");
const source = {
  created: new Date("2026-03-01T12:00:00Z"),
  count: NaN,
  missing: undefined,
  big: 10n,
  nested: { tags: ["a"] },
  self: null as unknown,
};
const clone = JSON.parse(JSON.stringify({ ...source, big: undefined })) as Record<string, unknown>;
console.log("   Date       ->", typeof clone.created, JSON.stringify(clone.created));
console.log("   NaN        ->", JSON.stringify(clone.count));
console.log("   undefined  -> clé présente ?", "missing" in clone);
try {
  JSON.stringify({ big: 10n });
} catch (e) {
  console.log("   BigInt     ->", (e as Error).constructor.name + ": " + (e as Error).message);
}
const cyclic: Record<string, unknown> = {};
cyclic.self = cyclic;
try {
  JSON.stringify(cyclic);
} catch (e) {
  console.log("   cycle      ->", (e as Error).constructor.name);
}

console.log("── structuredClone");
const deep = structuredClone({ created: new Date("2026-03-01T12:00:00Z"), nested: { tags: ["a"] } });
console.log("   Date préservée ?", deep.created instanceof Date, "|", deep.created.toISOString());
const shared = { nested: { tags: ["a"] } };
const cloned = structuredClone(shared);
cloned.nested.tags.push("b");
console.log("   copie profonde ? source =", JSON.stringify(shared.nested.tags), "| clone =", JSON.stringify(cloned.nested.tags));

// Probes for batch_09 JS: fermetures dans les boucles, async dans reduce, égalité de dates.

console.log("── fermetures dans une boucle");
const avecVar = [];
for (var i = 0; i < 3; i++) {
  avecVar.push(() => i);
}
const avecLet = [];
for (let j = 0; j < 3; j++) {
  avecLet.push(() => j);
}
console.log("   var  -> ", JSON.stringify(avecVar.map((f) => f())));
console.log("   let  -> ", JSON.stringify(avecLet.map((f) => f())));

const avecIIFE = [];
for (var k = 0; k < 3; k++) {
  avecIIFE.push(((capture) => () => capture)(k));
}
console.log("   IIFE -> ", JSON.stringify(avecIIFE.map((f) => f())));

console.log("── reduce avec une fonction asynchrone");
const delai = (ms, v) => new Promise((r) => setTimeout(() => r(v), ms));

(async () => {
  const sansAwait = [1, 2, 3].reduce(async (acc, n) => {
    const total = await acc;
    return total + (await delai(5, n));
  }, Promise.resolve(0));
  console.log("   reduce avec accumulateur await -> ", await sansAwait);

  const naif = [1, 2, 3].reduce((acc, n) => acc + n, 0);
  console.log("   reduce synchrone               -> ", naif);

  const mauvais = [1, 2, 3].reduce(async (acc, n) => (await acc) + n, 0);
  console.log("   accumulateur initial 0 non promesse -> ", await mauvais, "(fonctionne car await 0 vaut 0)");

  console.log("── égalité de dates");
  const a = new Date("2026-03-01T00:00:00Z");
  const b = new Date("2026-03-01T00:00:00Z");
  console.log("   a === b            :", a === b);
  console.log("   a == b             :", a == b);
  console.log("   a.getTime() === b.getTime() :", a.getTime() === b.getTime());
  console.log("   +a === +b          :", +a === +b);
  console.log("   JSON.stringify égal :", JSON.stringify(a) === JSON.stringify(b));
  const set = new Set([a, b]);
  console.log("   new Set([a, b]).size :", set.size, "<- deux dates égales restent deux entrées");
})();

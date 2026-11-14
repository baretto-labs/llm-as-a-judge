// Probes for batch_04 TypeScript/JS candidates: `this` binding, sort default, JSON precision, ==.

class Counter {
  private count = 0;
  increment(): void {
    this.count += 1;
  }
  incrementArrow = (): void => {
    this.count += 1;
  };
  get value(): number {
    return this.count;
  }
}

console.log("── liaison de `this`");
const counter = new Counter();
const detached = counter.increment;
try {
  detached();
  console.log("   méthode détachée : aucun problème, value =", counter.value);
} catch (e) {
  console.log("   méthode détachée :", (e as Error).constructor.name + " — " + (e as Error).message);
}
const detachedArrow = counter.incrementArrow;
detachedArrow();
console.log("   champ fléché détaché : value =", counter.value);
const bound = counter.increment.bind(counter);
bound();
console.log("   après bind : value =", counter.value);

console.log("── tri par défaut");
console.log("   [10, 9, 1, 20].sort()              =", JSON.stringify([10, 9, 1, 20].sort()));
console.log("   avec comparateur (a, b) => a - b   =", JSON.stringify([10, 9, 1, 20].sort((a, b) => a - b)));
const original = [3, 1, 2];
const sorted = original.sort((a, b) => a - b);
console.log("   sort() trie en place ?", original === sorted, JSON.stringify(original));

console.log("── précision JSON");
const parsed = JSON.parse('{"id": 9007199254740993, "amount": 0.1}');
console.log("   id 9007199254740993 relu :", parsed.id, "| égal à l'original ?", parsed.id === 9007199254740993);
console.log("   Number.MAX_SAFE_INTEGER  :", Number.MAX_SAFE_INTEGER);
console.log("   0.1 + 0.2 === 0.3 ?", 0.1 + 0.2 === 0.3, "| valeur :", 0.1 + 0.2);

console.log("── coercition de l'égalité lâche");
const cases: Array<[string, boolean]> = [
  ['"" == 0', ("" as unknown as number) == 0],
  ['"0" == 0', ("0" as unknown as number) == 0],
  ['"" == "0"', ("" as string) == "0"],
  ["null == undefined", (null as unknown) == undefined],
  ["null == 0", (null as unknown as number) == 0],
  ["[] == false", ([] as unknown as boolean) == false],
];
for (const [label, result] of cases) {
  console.log(`   ${label.padEnd(20)} -> ${result}`);
}

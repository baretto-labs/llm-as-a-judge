// Probes for batch_08 JS: pollution de prototype, egalité NaN, Array.sort sur objets.

console.log("── fusion profonde naïve et pollution de prototype");

function fusionNaive(cible, source) {
  for (const cle of Object.keys(source)) {
    if (typeof source[cle] === "object" && source[cle] !== null) {
      cible[cle] = cible[cle] || {};
      fusionNaive(cible[cle], source[cle]);
    } else {
      cible[cle] = source[cle];
    }
  }
  return cible;
}

const charge = JSON.parse('{"__proto__": {"estAdmin": true}}');
console.log("   avant :", JSON.stringify({ estAdmin: {}.estAdmin }));
fusionNaive({}, charge);
console.log("   après fusion naïve : ({}).estAdmin =", JSON.stringify({}.estAdmin));
console.log("   un objet neuf hérite de la propriété :", JSON.stringify(Object.create(Object.prototype).estAdmin));
delete Object.prototype.estAdmin;

function fusionSure(cible, source) {
  for (const cle of Object.keys(source)) {
    if (cle === "__proto__" || cle === "constructor" || cle === "prototype") continue;
    if (typeof source[cle] === "object" && source[cle] !== null) {
      cible[cle] = fusionSure(cible[cle] ?? Object.create(null), source[cle]);
    } else {
      cible[cle] = source[cle];
    }
  }
  return cible;
}
fusionSure({}, JSON.parse('{"__proto__": {"estAdmin": true}}'));
console.log("   après fusion filtrée : ({}).estAdmin =", JSON.stringify({}.estAdmin));
console.log("   structuredClone du même JSON pollue ?",
  JSON.stringify((structuredClone(JSON.parse('{"__proto__":{"x":1}}')), {}.x)));

console.log("── égalité et NaN");
console.log("   NaN === NaN            :", NaN === NaN);
console.log("   [NaN].includes(NaN)    :", [NaN].includes(NaN));
console.log("   [NaN].indexOf(NaN)     :", [NaN].indexOf(NaN));
console.log("   Object.is(NaN, NaN)    :", Object.is(NaN, NaN));
console.log("   new Set([NaN, NaN]).size :", new Set([NaN, NaN]).size);
console.log("   Object.is(0, -0)       :", Object.is(0, -0), "| 0 === -0 :", 0 === -0);

console.log("── tri d'objets sans comparateur");
const items = [{ n: 10 }, { n: 9 }, { n: 1 }];
console.log("   [{n:10},{n:9},{n:1}].sort() :", JSON.stringify(items.sort()));
console.log("   String({n:1}) :", JSON.stringify(String({ n: 1 })));

// Probes for batch_10 TS: any contre unknown, satisfies, narrowing.
// Le fichier doit compiler : chaque @ts-expect-error échoue si TypeScript n'émet PAS l'erreur attendue.

declare function recevoir(): unknown;
declare function recevoirAny(): any;

// ── any désactive toute vérification
const viaAny = recevoirAny();
viaAny.methodeInexistante();          // accepté : any ne vérifie rien
const nombreDepuisAny: number = viaAny;  // accepté : any est assignable à tout

// ── unknown force le rétrécissement
const viaUnknown = recevoir();
// @ts-expect-error : on ne peut rien faire d'un unknown sans le rétrécir
viaUnknown.methodeInexistante();
// @ts-expect-error : unknown n'est assignable qu'à unknown et any
const nombreDepuisUnknown: number = viaUnknown;

if (typeof viaUnknown === "string") {
  console.log("   unknown rétréci en string, longueur :", viaUnknown.length);
}

// ── satisfies conserve le type littéral tout en vérifiant la forme
type Reglage = { hote: string; port: number };
const config = { hote: "localhost", port: 8080 } satisfies Reglage;
console.log("   satisfies : port reste littéral ?", config.port === 8080);

const configAnnotee: Reglage = { hote: "localhost", port: 8080 };
console.log("   annotation classique : port =", configAnnotee.port);

// ── le piège du catch
try {
  throw new Error("échec");
} catch (e) {
  // e est unknown par défaut depuis TS 4.4 avec useUnknownInCatchVariables
  // @ts-expect-error : accès direct interdit sur unknown
  console.log(e.message);
  if (e instanceof Error) {
    console.log("   catch rétréci via instanceof :", e.message);
  }
}

console.log("── compilation réussie : tous les @ts-expect-error étaient justifiés");

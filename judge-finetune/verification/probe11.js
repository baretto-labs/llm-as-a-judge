// Probes for batch_11 JS: parseInt et conversions, encodage d'URL, comparaison de chaînes.

console.log("── parseInt et conversions numériques");
const entrees = ["42", "08", "0x1f", "12px", " 7 ", "", "1e3", "Infinity", null, undefined, "1,5"];
for (const v of entrees) {
  const p = parseInt(v);
  const p10 = parseInt(v, 10);
  const n = Number(v);
  console.log(
    `   ${String(JSON.stringify(v)).padEnd(12)} parseInt=${String(p).padEnd(10)} parseInt(,10)=${String(p10).padEnd(10)} Number=${n}`
  );
}
console.log("   Number.parseInt === parseInt :", Number.parseInt === parseInt);
console.log("   Number('') vaut 0, parseInt('') vaut NaN :", Number(""), parseInt(""));

console.log("── encodeURI contre encodeURIComponent");
const valeur = "a&b=c/d?e f#g";
console.log("   valeur brute            :", JSON.stringify(valeur));
console.log("   encodeURI(valeur)       :", JSON.stringify(encodeURI(valeur)));
console.log("   encodeURIComponent      :", JSON.stringify(encodeURIComponent(valeur)));
const url = `https://api.example.com/recherche?q=${encodeURI(valeur)}`;
const urlOk = `https://api.example.com/recherche?q=${encodeURIComponent(valeur)}`;
console.log("   paramètre lu avec encodeURI       :", new URL(url).searchParams.get("q"));
console.log("   paramètre lu avec encodeURIComponent :", new URL(urlOk).searchParams.get("q"));
console.log("   URLSearchParams fait le travail   :",
  new URLSearchParams({ q: valeur }).toString());

console.log("── comparaison de chaînes et casse");
console.log("   'ADMIN'.toLowerCase() === 'admin' :", "ADMIN".toLowerCase() === "admin");
console.log("   'ADMİN'.toLowerCase() === 'admin' :", "ADMİN".toLowerCase() === "admin", "(I turc)");
console.log("   localeCompare accents  :", "é".localeCompare("e"), "| === :", "é" === "e");
console.log("   normalize NFC vs NFD   :",
  "é".normalize("NFC") === "é".normalize("NFD"),
  "| après normalisation commune :",
  "é".normalize("NFC") === "é".normalize("NFC"));
console.log("   longueur 'e\\u0301' :", "é".length, "| longueur 'é' :", "é".length);

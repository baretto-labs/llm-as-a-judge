// Probes for batch_07 JS/TS: ordre micro/macro-tâches, et innerHTML contre textContent (jsdom).

console.log("── ordre d'exécution");
const trace = [];
trace.push("1 synchrone");
setTimeout(() => {
  trace.push("5 setTimeout 0");
  console.log("   " + trace.join(" | "));
}, 0);
Promise.resolve().then(() => trace.push("3 microtâche .then"));
queueMicrotask(() => trace.push("4 queueMicrotask"));
trace.push("2 synchrone");

// ── XSS : innerHTML contre textContent
(async () => {
  let JSDOM;
  try {
    ({ JSDOM } = require("jsdom"));
  } catch {
    console.log("── jsdom absent : sonde XSS ignorée");
    return;
  }
  await new Promise((r) => setTimeout(r, 10));
  console.log("── innerHTML contre textContent");

  const dom = new JSDOM(`<!doctype html><body><div id="a"></div><div id="b"></div></body>`, {
    runScripts: "dangerously",
  });
  const { document } = dom.window;
  const charge = '<img src=x onerror="document.body.dataset.pwned=\'oui\'">';

  document.getElementById("a").innerHTML = charge;
  console.log("   innerHTML   -> balises créées :", document.querySelectorAll("#a img").length,
    "| attribut onerror présent :", !!document.querySelector("#a img")?.getAttribute("onerror"));
  console.log("   innerHTML   -> body.dataset.pwned =", JSON.stringify(document.body.dataset.pwned));

  document.getElementById("b").textContent = charge;
  console.log("   textContent -> balises créées :", document.querySelectorAll("#b img").length);
  console.log("   textContent -> contenu HTML échappé :",
    JSON.stringify(document.getElementById("b").innerHTML.slice(0, 60)));
})();

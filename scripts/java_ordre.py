"""Réplique exacte de l'ordre d'extraits produit par RagContextJudge :
String.hashCode -> java.util.Random -> Collections.shuffle -> jonction -> troncature 6000.
Vérifié en recalculant hintCoverage et en le comparant aux 180 valeurs stockées."""
M48 = (1 << 48) - 1
MUL, ADD = 0x5DEECE66D, 0xB

def java_hash(s):
    h = 0
    for c in s:
        h = (31 * h + ord(c)) & 0xFFFFFFFF
    return h - (1 << 32) if h >= (1 << 31) else h

class JavaRandom:
    def __init__(self, seed):
        self.s = (seed ^ MUL) & M48
    def _next(self, bits):
        self.s = (self.s * MUL + ADD) & M48
        v = self.s >> (48 - bits)
        return v - (1 << bits) if bits == 32 and v >= (1 << 31) else v
    def next_int(self, bound):
        if bound & (bound - 1) == 0:
            return (bound * self._next(31)) >> 31
        while True:
            bits = self._next(31)
            val = bits % bound
            if bits - val + (bound - 1) < (1 << 31):
                return val

def java_shuffle(lst, seed):
    out = list(lst)
    r = JavaRandom(seed)
    for i in range(len(out), 1, -1):
        j = r.next_int(i)
        out[i - 1], out[j] = out[j], out[i - 1]
    return out

def contexte_juge(question, chunks, plafond=6000):
    """plafond=None : aucune troncature (banc plafond du 2026-10-20). La valeur par défaut
    reste 6000 pour que les bancs déjà joués restent reproductibles à l'identique."""
    t = "\n---\n".join(java_shuffle(chunks, java_hash(question)))
    if plafond is None or len(t) <= plafond:
        return t
    return t[:plafond] + "\n[... truncated ...]"

def couverture(texte, hints):
    if not hints:
        return 1.0
    bas = texte.lower()
    return sum(h.lower() in bas for h in hints) / len(hints)

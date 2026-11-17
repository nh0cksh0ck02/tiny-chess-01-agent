# nh0cksh0ck02 tiny-chess-01 Engine v5
import base64, json, os, sys, urllib.request

ENV_URL = os.environ.get("MAKEFUN_ENV_URL") or sys.exit("MAKEFUN_ENV_URL is not set")
VALS = {"P": 100, "N": 320, "B": 330, "R": 500, "Q": 900, "K": 20000}
D, DG = (-10, 1, 10, -1), (-11, -9, 9, 11)
DIRS = {"P": (-10,-20,-11,-9), "N": (-21,-19,-12,-8,8,12,19,21), "B": DG, "R": D, "Q": D + DG, "K": D + DG}

# 32-entry PST per piece
PST = {p: [x - 50 for x in base64.b64decode("MjIyMjc8Ph43LSgyMjIyTjc3PlA8PkhSZGRkZDIyMjIAChQUCh4yNxQ3PkQUMkRIFDdESBQyPkQKHjIyAAoUFB4oKCgoNzIyKD4+PigyPj4oNzg+KDI4PigyMjIeKCgoRlI8MkZGMjIoHh4eHhQUChQKCgAUCgoAFAoKABQKCgA=")[i*32:(i+1)*32]] for i, p in enumerate("PNBK")}

rot = lambda b: [c.swapcase() for c in reversed(b)]
post = lambda p, b: json.load(urllib.request.urlopen(urllib.request.Request(ENV_URL + p, data=json.dumps(b).encode(), headers={"content-type": "application/json"})))

sq_to_i = lambda s: (10 - int(s[1])) * 10 + ord(s[0]) - 96
fen_to_board = lambda f: list(" "*20 + "".join(f" {''.join('.'*int(c) if c.isdigit() else c for c in r)} " for r in f.split()[0].split("/")) + " "*20)
pst = lambda p, sq: PST[p.upper()][(9 - sq // 10 if p.isupper() else sq // 10 - 2) * 4 + min(sq % 10 - 1, 8 - sq % 10)] if p.upper() in PST else 0
eval_pos = lambda b: sum(VALS[p] + pst(p, sq) if p.isupper() else -VALS[p.upper()] - pst(p, sq) for sq, p in enumerate(b) if p.upper() in VALS)
move_score = lambda b, i, j: (VALS[b[j].upper()] * 20 - VALS[b[i]]) if b[j].islower() else (1000 if b[i] == "P" and j // 10 == 2 else pst(b[i], j) - pst(b[i], i))

def gen_moves(b, caps=False):
  for i, p in enumerate(b):
    if not p.isupper(): continue
    if p == "P":
      if not caps and b[i - 10] == ".":
        yield (i, i - 10)
        if i // 10 == 8 and b[i - 20] == ".": yield (i, i - 20)
      for d in (-11, -9):
        if b[i + d].islower(): yield (i, i + d)
    elif p in DIRS:
      for d in DIRS[p]:
        j = i + d
        while True:
          t = b[j]
          if t == " " or t.isupper(): break
          if not caps or t.islower(): yield (i, j)
          if p in "NK" or t.islower(): break
          j += d

def make_move(b, i, j):
  nb, p = b[:], b[i]
  nb[i], nb[j] = ".", "Q" if p == "P" and j // 10 == 2 else p
  if p == "K" and abs(j - i) == 2:
    nb[96 if j == 97 else 94], nb[98 if j == 97 else 91] = nb[98 if j == 97 else 91], "."
  return nb

def search(b, depth, alpha, beta):
  if depth <= 0:
    sp = eval_pos(b)
    if sp >= beta: return beta
    alpha = max(alpha, sp)
    if depth <= -3: return alpha
  for i, j in sorted(gen_moves(b, depth <= 0), key=lambda m: move_score(b, m[0], m[1]), reverse=True):
    if b[j] == "k": return 19000 + max(0, depth)
    sc = -search(rot(make_move(b, i, j)), depth - 1, -beta, -alpha)
    if sc >= beta: return beta
    alpha = max(alpha, sc)
  return alpha

def choose(fen, legal, depth=4):
  w = fen.split()[1] == "w"
  b = rot(fen_to_board(fen)) if not w else fen_to_board(fen)
  pc = sum(1 for c in b if c.upper() in "NBRQ")
  d = depth + (2 if pc <= 3 else (1 if pc <= 6 else 0))
  sq = lambda s: 119 - sq_to_i(s) if not w else sq_to_i(s)
  parsed = sorted([(sq(m[:2]), sq(m[2:4]), m) for m in legal], key=lambda m: move_score(b, m[0], m[1]), reverse=True)
  best_m, best_s, alpha = legal[0], -1e9, -1e9
  for f, t, uci in parsed:
    if b[t] == "k": return uci
    sc = -search(rot(make_move(b, f, t)), d - 1, -1e9, -alpha)
    if sc > best_s: best_s, best_m = sc, uci
    alpha = max(alpha, sc)
  return best_m

while True:
  g = post("/game", {})
  if g.get("status") == "done": break
  while g.get("status") in ("your_move", "playing"):
    leg = g.get("legal_moves") or g.get("legal", [])
    if not leg: break
    g = post("/move", {"game": g.get("game") or g.get("game_id"), "move": choose(g["fen"], leg)})

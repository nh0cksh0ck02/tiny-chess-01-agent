# nh0cksh0ck02 tiny-chess-01 tactical engine (MIT)
import json, os, sys, urllib.error, urllib.request

ENV_URL = os.environ.get("MAKEFUN_ENV_URL") or sys.exit("MAKEFUN_ENV_URL is not set")
VALS = {"p": 100, "n": 320, "b": 330, "r": 500, "q": 900, "k": 20000}

def post(path, body):
    req = urllib.request.Request(ENV_URL + path, data=json.dumps(body).encode(), headers={"content-type": "application/json"})
    try:
        with urllib.request.urlopen(req) as res:
            return json.load(res)
    except urllib.error.HTTPError as e:
        sys.exit(f"{path}: HTTP {e.code} {e.read().decode(errors='replace')}")

def board_of(fen):
    board = {}
    for i, row in enumerate(fen.split()[0].split("/")):
        col = 0
        for c in row:
            if c.isdigit(): col += int(c)
            else:
                board["abcdefgh"[col] + str(8 - i)] = c
                col += 1
    return board

def center_dist(sq):
    f, r = ord(sq[0]) - ord("a"), int(sq[1]) - 1
    return 4 - max(abs(f - 3.5), abs(r - 3.5))

def attacked(sq, by_white, board):
    f, r = ord(sq[0]) - ord("a"), int(sq[1]) - 1
    pr, pc = (r - 1, "P") if by_white else (r + 1, "p")
    if 0 <= pr <= 7:
        for df in (-1, 1):
            if 0 <= f + df <= 7 and board.get(chr(ord("a") + f + df) + str(pr + 1)) == pc: return True
    nc = "N" if by_white else "n"
    for df, dr in [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]:
        if 0 <= f + df <= 7 and 0 <= r + dr <= 7 and board.get(chr(ord("a") + f + df) + str(r + dr + 1)) == nc: return True
    kc = "K" if by_white else "k"
    for df in (-1, 0, 1):
        for dr in (-1, 0, 1):
            if (df or dr) and 0 <= f + df <= 7 and 0 <= r + dr <= 7 and board.get(chr(ord("a") + f + df) + str(r + dr + 1)) == kc: return True
    dc = ("B", "Q") if by_white else ("b", "q")
    for df, dr in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
        cf, cr = f + df, r + dr
        while 0 <= cf <= 7 and 0 <= cr <= 7:
            p = board.get(chr(ord("a") + cf) + str(cr + 1))
            if p:
                if p in dc: return True
                break
            cf += df; cr += dr
    oc = ("R", "Q") if by_white else ("r", "q")
    for df, dr in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        cf, cr = f + df, r + dr
        while 0 <= cf <= 7 and 0 <= cr <= 7:
            p = board.get(chr(ord("a") + cf) + str(cr + 1))
            if p:
                if p in oc: return True
                break
            cf += df; cr += dr
    return False

def choose(fen, legal):
    board = board_of(fen)
    white_turn = fen.split()[1] == "w"
    opp = not white_turn

    def rank(move):
        f_sq, t_sq = move[:2], move[2:4]
        mover = board[f_sq]
        victim = board.get(t_sq) or (("p" if white_turn else "P") if mover.lower() == "p" and f_sq[0] != t_sq[0] else None)
        taken = VALS[victim.lower()] if victim else 0
        promo = VALS[move[4].lower()] if len(move) == 5 else 0
        mover_val = VALS[mover.lower()]
        pos_delta = int(center_dist(t_sq) * 8 - center_dist(f_sq) * 8)
        score = taken * 10 + promo * 10 + pos_delta
        if attacked(t_sq, opp, board):
            loss = mover_val - taken
            score -= (loss * 10 if loss > 0 else 50)
        if attacked(f_sq, opp, board) and not attacked(t_sq, opp, board):
            score += mover_val * 5
        return (-score, -promo, mover_val, move)

    return min(legal, key=rank)

while True:
    g = post("/game", {})
    if g["status"] == "done": break
    while g["status"] == "your_move":
        g = post("/move", {"game": g["game"], "move": choose(g["fen"], g["legal_moves"])})
    print(f"game {g['game']}: {g['outcome']} by {g['reason']}", file=sys.stderr)
print(f"done: {g.get('wins')} won, {g.get('draws')} drawn, {g.get('losses')} lost", file=sys.stderr)

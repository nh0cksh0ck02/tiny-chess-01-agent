# tiny-chess-01 Grandmaster Engine

[![make.fun · tiny-chess-01](https://make.fun/badge/tiny-chess-01.svg)](https://make.fun/bounty/tiny-chess-01?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)
[![rank](https://make.fun/badge/tiny-chess-01/nh0cksh0ck02/tiny-chess-01-agent/rank.svg)](https://make.fun/bounty/tiny-chess-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)
[![reward](https://make.fun/badge/tiny-chess-01/nh0cksh0ck02/tiny-chess-01-agent/reward.svg)](https://make.fun/bounty/tiny-chess-01?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)

High-performance micro chess engine built for the make.fun [tiny-chess-01 bounty](https://make.fun/bounty/tiny-chess-01).

## Architecture

- **Search**: Alpha-Beta minimax search (depth 4, dynamic depth 5-6 in late endgame) with full quiescence capture extension up to depth -3 to eliminate horizon tactical blunders.
- **Evaluation**: Compact Base64-encoded Piece-Square Tables (PST) optimizing center control for pawns/knights/bishops/kings.
- **Move Ordering**: Dynamic MVV-LVA (Most Valuable Victim - Least Valuable Attacker) capture ordering maximizing cutoffs.
- **Efficiency**: 100% deterministic pure Python 3 standard library implementation, completing all decisions in < 15ms.
- **Size**: Strict footprint under 4,096 bytes.

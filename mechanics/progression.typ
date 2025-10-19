== Save File Structure

Players may maintain multiple save files, each with independent progression tracking.

== Post-Match Rewards

Upon completion of a match (whether victory or defeat), players receive two primary reward currencies: Cheese and Experience Points (EXP).

*Cheese:* 
A currency utilized for "Gacha" system interactions. Each "Gacha" roll requires an expenditure of 10 Cheese.

*Experience Points:* 
Accumulated EXPcontributes to the player's Level, which serves as a prerequisite for unlocking new "Forges".

== Level Progression

Player Level advancement requires progressively increasing amounts of EXP. The EXP requirement for each level follows a linear scaling formula:

$ "EXP Required" = 100 + 10(N - 1) $

Where $N$ represents the current level.

\*Example Progression:\*
- Level 1 → 2: 100 EXP
- Level 2 → 3: 110 EXP
- Level 3 → 4: 120 EXP
- $dots.h.c$
- Level $N$ → $N+1$: $100 + 10(N - 1)$ EXP

== Reward Calculation

Both Cheese and EXP rewards are calculated dynamically based on match duration (measured in turns played) using the following formula:

$ y = floor(A (x / (x + B)) (1 - e^(-(x / C)^2))) $

Where:
- $x$ = number of turns played in the match
- $A$, $B$, $C$ = reward-specific constants

=== Victory Rewards

*Experience Points:*
- $A = 200$
- $B = 20$
- $C = 80$

*Cheese:*
- $A = 20$
- $B = 20$
- $C = 80$

=== Defeat Rewards

*Experience Points:*
- $A = 100$
- $B = 20$
- $C = 80$

*Cheese:*
- $A = 5$
- $B = 20$
- $C = 80$

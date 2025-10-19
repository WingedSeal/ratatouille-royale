== Pre-Match
A player can build and select a deck (Squeak Set) before entering a match. They can also pick the first 5 squeaks that'll be drawn into the hands. 

== Match
Each turns they are multiple types of action player can take which all cost "crumbs" (except End Turn).
+ Place Squeak
+ Move
+ Activate Skill
+ End Turn

=== Place Squeak
Most Rodent type Squeaks can only be placed on "Deployment Zone". While Trick type Squeaks have their own placing mechanism. Once a Squeak is placed, a new Squeak will be automatically drawn from the deck and the placed squeak will not go back to the deck. Only when the deck is completely empty while trying to draw a new Squeak, it'll be reset to its original state.

=== Move
Each tile has its own height. An entity can jump up to 1 high difference. A jump is automatically performed when moving. When a move is performed, 1 "Move Stamina" will be consumed. This stamina is unique to each entity and will reset at the end of the turn. Most entites cannot occupy the same tile.


=== Activate Skill
Entities in the game (including Rodents) may have abilities called skills (usually 0-3 skills). Player can choose to activate any ally or neutral entity's skill. Once it is activated, if the skill requires target(s) to be selected, the game will go into target selecting mode and let the player choose target(s). Most skills can be cancelled. (Some skills may go into target selecting mode more than once.)

Most skills requires direct line of sight (LOS) to its target. To calculate this LOS, the game will draw direct line from the entity to its target then interpolate that line into hexagonical line. (Note that when interpolating, the result hexagonical line will always be a shortest path to target.). Then compare the difference between the entity's tile height and target's tile height and the skill's "altitude" stats. If altitude is high enough then the skill has line of sight.

When a skill completed, 1 "Skill Stamina" will be consumed. This stamina is unique to each entity and will reset at the end of the turn.

=== End Turn
Forfeit the remaining crumbs and end the turn.

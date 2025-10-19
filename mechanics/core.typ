== Pre-Match Phase

Prior to entering a match, players must build and select a deck (referred to as a "Squeak Set"). Additionally, players may designate the initial sequence of 5 "Squeaks" that will be drawn into their starting hand.

== Match Phase

During each turn, players may execute multiple action types on any order, all of which consume "Crumbs" (with the exception of the "End Turn" action). The available actions are:

- Place Squeak
- Move
- Activate Skill
- End Turn

=== Place Squeak

*Deployment Restriction:*
Rodent-type Squeaks are restricted to placement within designated "Deployment Zones". Conversely, Trick-type Squeaks may utilize specialized placement mechanics unique to them.

*Squeak Draw Mechanism:* 
Upon placement of a Squeak, the system automatically draws a new Squeak from the deck. Placed Squeaks are permanently removed from the active deck cycle. When an attempt is made to draw from an empty deck, the deck resets to its original composition.

=== Move

*Terrain Navigation:*
Each tile possesses a distinct height value. Entities are capable of traversing elevation differences of up to 1 unit, with jumping automatically executed during movement when necessary.

*Movement Resource:*
Each movement action consumes one unit of "Move Stamina", a resource unique to each entity. This stamina pool fully regenerates at the end of each turn. Most entities are not allowed to occupy the same tile at once.

=== Activate Skill

*Skill Availability:* 
Game entities, including "Rodents", usually has between zero and three "Skills". Players may activate "Skills" belonging to any allied or neutral entity.

*Target Selection:* 
Upon "Skill" activation, if the "Skill" requires target selection, the game enters "Target Selection Mode", prompting the player to select the appropriate target(s). Most "Skills" may be cancelled during this process. Note that certain Skills may require multiple target selection phases.

*Line of Sight Calculation:* 
The majority of "Skills" require direct line of sight (LOS) to their designated target. LOS determination follows this algorithm:

+ A direct line is drawn from the activating entity to the target
+ This line is interpolated into a hexagonal grid path (always selecting the shortest possible path)
+ The system calculates the height differential between the entity's tile and the target's tile
+ This differential is compared against the Skill's "Altitude" stats
+ If the "Altitude" value meets or exceeds the height differential, "LOS" is confirmed

*Skill Resource:* 
Upon successful "Skill" completion, one unit of "Skill Stamina" is consumed. This resource is entity-specific and fully regenerates at the end of the turn.

=== End Turn

This action forfeits all remaining "Crumbs" and immediately concludes the player's current turn.

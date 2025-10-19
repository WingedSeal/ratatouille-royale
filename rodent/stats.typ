*HP (Hit Points):* 
Amount of damage an entity can take before being defeated.

*Speed:* 
The maximum number of tiles an entity can traverse per movement action. Any unused "Speed" value is forfeited cannot be carried over.

*Move Stamina:* 
The number of movement actions an entity may perform per turn. The standard value is 2 for most entities.

*Skill Stamina:*
The number of skill activation an entity may perform per turn.

*Move Cost:* 
The amount of crumbs required per 1 movement action.

*Defense:* 
Reduces incoming damage by a flat amount. Damage calculation follows the formula: `damage_taken = damage_received - defense`.

*Crumb Cost:* 
The amount of crumbs required to deploy the entity.

*Attack:* 
The base attack value from which skills' damage is derived.

*Height:* 
Entities may function as cover for enemy's line of sight calculations. This value is added to the tile's base height when determining cover effectiveness. Most entities have height of 0.

=== Skills

*Reach:* 
Defines the maximum tile distance a skill can reach its target.

*Altitude:* 
Specifies the maximum height differential that a skill can overcome. This value may be negative. For example, a skill with an altitude of 1 can target enemies positioned behind cover or on the tile that is 1 height unit above the activating entity.

*Crumb Cost:* 
The amount of crumbs required to activate the skill.

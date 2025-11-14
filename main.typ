#import "template.typ": *
#show: apply-style

#title-page(
  title: "Game Design Document",
  subtitle: "Ratatouille Royale",
  authors: (
    "Peepo TheGoat 1234", 
    "Pond CodingFrontEnd 777",
    "Cheewanont Chuleekorn 6522781846", 
    "Kamolpat Thananopavarn 6522790045", 
    "Aek Egg 12345"
  ),
)

#outline()

= Overview
#include "overview.typ"

= Game Theme
#include "theme.typ"

= Terminology
#include "terminology.typ"

= Game Mechanics
#include "mechanics/core.typ"

== Progression
#include "mechanics/progression.typ"

= Rodent
== Stats
#include "rodent/stats.typ"

== Classes
#include "rodent/class.typ"

= Rodent List
#include "rodent/rodents/vanguard.typ"
#include "rodent/rodents/tank.typ"
#include "rodent/rodents/duelist.typ"

= Trick List
#include "tricks/offense.typ"

= Gacha Pool
#include "progression/gacha_pool.typ"

= Forges
#include "progression/forges.typ"

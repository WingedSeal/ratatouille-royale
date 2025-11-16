#import "template.typ": *
#show: apply-style

#title-page(
  title: "Game Design Document",
  subtitle: "Ratatouille Royale",
  authors: (
    "Puwarit Khowean 6522781580", 
    "Nattapol Phanmadee 6522781994",
    "Cheewanont Chuleekorn 6522781846", 
    "Kamolpat Thananopavarn 6522790045", 
    "Aekkarin Yimyaem 6522772498"
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
#include "rodent/rodents/support.typ"
#include "rodent/rodents/specialist.typ"

= Trick List
#include "tricks/offense.typ"
#include "tricks/defense.typ"
#include "tricks/utility.typ"

= Common Effects
#include "effects.typ"

= Gacha Pool
#include "progression/gacha_pool.typ"

= Forges
#include "progression/forges.typ"

= UI
#grid(
  columns: (1fr,) * 2,
  gutter: 1em,
  ..range(1, 17).map(i => image("ui/" + str(i) + ".png"))
)

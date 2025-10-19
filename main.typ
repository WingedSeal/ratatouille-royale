#import "template.typ": *
#show: apply-style
// #import "@preview/charged-ieee:0.1.4": *
//
// #show: ieee.with(
//   title: [A typesetting system to untangle the scientific writing process],
//   abstract: [
//     The process of scientific writing is often tangled up with the intricacies of typesetting, leading to frustration and wasted time for researchers. In this paper, we introduce Typst, a new typesetting system designed specifically for scientific writing. Typst untangles the typesetting process, allowing researchers to compose papers faster. In a series of experiments we demonstrate that Typst offers several advantages, including faster document creation, simplified syntax, and increased ease-of-use.
//   ],
//   authors: (
//     (
//       name: "Martin Haug",
//       department: [Co-Founder],
//       organization: [Typst GmbH],
//       location: [Berlin, Germany],
//       email: "haug@typst.app"
//     ),
//     (
//       name: "Laurenz Mädje",
//       department: [Co-Founder],
//       organization: [Typst GmbH],
//       location: [Berlin, Germany],
//       email: "maedje@typst.app"
//     ),
//   ),
//   index-terms: ("Scientific writing", "Typesetting", "Document creation", "Syntax"),
// )


= Overview
#include "overview.typ"

= Game Theme
#include "theme.typ"

= Terminology
#include "terminology.typ"

= Game Mechanics
== Core
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

= Gacha Pool
#include "progression/gacha_pool.typ"

= Forges
#include "progression/forges.typ"

#let apply-style(body) = {
  let primary = rgb("#1e3a8a")
  let secondary = rgb("#312e81")
  let accent = rgb("#991b1b")
  let bold-color = rgb("#065f46")
  let text-color = rgb("#111827")
  let code-bg = rgb("#f3f4f6")
  
  set page(
    margin: (x: 1in, y: 0.8in),
    numbering: "1",
    number-align: center,
  )
  
  set text(
    font: "Times New Roman",
    size: 11pt,
    fill: text-color,
  )
  
  set par(
    justify: true,
    leading: 0.65em,
    spacing: 1em,
  )
  
  set heading(numbering: "1.1")
  
  show heading.where(level: 1): it => {
    pagebreak(weak: true)
    v(1.5em)
    block[
      #set text(size: 22pt, weight: "bold", fill: primary)
      #if it.numbering != none [
        #text(fill: secondary)[#counter(heading).display(it.numbering)]
        #h(0.5em)
      ]
      #it.body
    ]
    v(1em)
  }
  
  show heading.where(level: 2): it => {
    v(1em)
    block[
      #set text(size: 16pt, weight: "bold", fill: secondary)
      #if it.numbering != none [
        #counter(heading).display(it.numbering)
        #h(0.4em)
      ]
      #it.body
    ]
    v(0.6em)
  }
  
  show heading.where(level: 3): it => {
    v(0.8em)
    block[
      #set text(size: 13pt, weight: "bold", fill: accent)
      #if it.numbering != none [
        #counter(heading).display(it.numbering)
        #h(0.3em)
      ]
      #it.body
    ]
    v(0.4em)
  }
  
  show strong: it => text(fill: bold-color, weight: "bold")[#it]
  
  show emph: it => text(fill: rgb("#374151"), style: "italic")[#it]
  
  show raw.where(block: false): it => box(
    fill: code-bg,
    inset: (x: 3pt, y: 0pt),
    outset: (y: 3pt),
    radius: 2pt,
    text(fill: accent, font: "Courier New")[#it]
  )
  
  show raw.where(block: true): it => block(
    fill: code-bg,
    inset: 10pt,
    radius: 4pt,
    width: 100%,
    text(fill: text-color, font: "Courier New", size: 9.5pt)[#it]
  )
  
  set list(marker: text(fill: secondary)[•])
  set enum(numbering: n => text(fill: secondary)[#n.])
  
  show link: it => text(fill: secondary, underline: true)[#it]
  
  set table(
    stroke: (x, y) => if y == 0 {
      (bottom: 2pt + primary)
    } else {
      (bottom: 0.5pt + rgb("#e5e7eb"))
    },
    fill: (x, y) => if y == 0 {
      primary.lighten(90%)
    }
  )
  
  show quote: it => block(
    fill: code-bg,
    inset: (left: 15pt, rest: 10pt),
    radius: 4pt,
    stroke: (left: 3pt + secondary),
    width: 100%,
  )[#it]
  
  body
}
#let title-page(title: "", subtitle: "", authors: (), date: none) = {
  set page(numbering: none)
  
  v(2fr)
  
  align(center)[
    #text(size: 32pt, weight: "bold", fill: rgb("#1e3a8a"))[
      #title
    ]
    
    #v(0.5em)
    
    #if subtitle != "" [
      #text(size: 16pt, fill: rgb("#312e81"))[
        #subtitle
      ]
    ]
    
    #v(2em)
    
    #if authors != () [
      #align(center)[
        #context [
          #let max-name-width = 0pt
          #for author in authors {
            let parts = author.split(" ")
            if parts.len() != 3 {
              panic("Author must be in format: 'FirstName LastName ID'. Got: '" + author + "'")
            }
            let name = parts.slice(0, 2).join(" ")
            let name-width = measure(text(size: 14pt)[#name]).width
            max-name-width = calc.max(max-name-width, name-width)
          }
          
          #text(size: 14pt)[
            #show table: set table(
              stroke: none,
              fill: none,
            )
            #table(
              columns: (auto, auto),
              stroke: none,
              align: (left, left),
              column-gutter: 1em,
              ..authors.map(author => {
                let parts = author.split(" ")
                let name = parts.slice(0, 2).join(" ")
                let id = parts.at(2)
                (name, id)
              }).flatten()
            )
          ]
        ]
      ]
    ]
  ]
  
  v(3fr)
  
  pagebreak()
}

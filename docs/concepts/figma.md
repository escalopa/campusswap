# Figma basics

[Figma](https://www.figma.com) is the design tool used for the whole project. Everything the course asks for lives in [one Figma file](https://www.figma.com/design/FBkfowqM4rI8lcgZ8fuzQv).

## How our file is organized

| Section | Contents |
|---|---|
| **00 · Cover** | Title slide |
| **01 · UX Research** | A.1 Research plan · A.2 Interview guide · A.3 Survey · B Research report · B Competitive analysis · C Rough design |
| **02 · Lo-Fi Prototype** | A.1 Interview notes · A.2 Themes · A.3 Feature ideation · A.4 Prioritization · B.1 User flow · B.2 Crazy 8s · B.3 Lo-fi wireframes |
| **03 · Hi-Fi Prototype** | A.1 Idea brief · A.2 Usability study guide · A.3 User flow v2.0 · B.1 Moodboard · B.2 Style guide · B.3 Pattern library · B.4 Hi-fi mockups |
| **04 · Case Study** | The final presentation |

Frame names match the course rubric codes (A.1, B.2…), so the instructor can find each item during the file inspection.

## Terms

Frame
:   A container, like an artboard. Each phone screen and each document block is a frame.

Section
:   A large labeled area that groups frames. Our file has five.

Auto layout
:   Figma's way of stacking items with automatic spacing and padding, like CSS flexbox. Content reflows when text changes.

Component
:   A reusable master element, like *Button*. Change the component and every copy updates.

Instance
:   A copy of a component placed on a screen. You can change its text but it stays linked to the master.

Variant
:   One version of a component, grouped in a component set: *Button / Primary*, *Button / Secondary*, *Button / Ghost*.

Component property
:   An editable setting on a component, like the button label text, exposed in the right panel.

Variables and styles
:   Saved colors, text styles and effects reused across the file. Our colors are variables like `brand/green`.

Prototype (in Figma)
:   Links between frames ("on tap, go to Item details") that turn static screens into a clickable app.

Flow and Present mode
:   A flow is a named starting screen for a prototype. The ▶ **Present** button plays it.

Prototype link
:   Share → Copy prototype link gives a `figma.com/proto/…` URL that opens the prototype for anyone with access.

Dev Mode
:   A view for developers with measurements, colors and code snippets.

Local copy (.fig)
:   File → Save local copy downloads an offline `.fig` file. The final submission needs both the online link and the `.fig` file.

## Sharing checklist

- [ ] Share → anyone with the link → **can view**
- [ ] Copy the prototype link and test it in a private browser window
- [ ] File → Save local copy (`.fig`)

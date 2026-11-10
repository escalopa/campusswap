# Roadmap and tracker

Status as of 10 November 2026. The same tracker is in the [project guide PDF](../assets/campusswap-project-guide.pdf).

## What's built

| Deliverable | Status |
|---|---|
| Figma file: cover, research, lo-fi, hi-fi sections | :material-check-circle:{ style="color:#1E7B5C" } Mostly built |
| Research plan, interview guide, survey | :material-check-circle:{ style="color:#1E7B5C" } Done |
| Competitive analysis | :material-check-circle:{ style="color:#1E7B5C" } Done (desk research) |
| 15 feature ideas, value vs complexity matrix | :material-check-circle:{ style="color:#1E7B5C" } Draft, confirm after synthesis |
| User flows, Crazy 8s slots, 4 clickable lo-fi screens | :material-check-circle:{ style="color:#1E7B5C" } Done (sketches pending) |
| Idea brief, usability study guide, moodboard | :material-check-circle:{ style="color:#1E7B5C" } Done |
| Style guide and pattern library (components) | :material-check-circle:{ style="color:#1E7B5C" } Done |
| Hi-fi screens 1–7 and [clickable prototype](https://www.figma.com/proto/FBkfowqM4rI8lcgZ8fuzQv/CampusSwap?node-id=10-144&starting-point-node-id=10-144) | :material-check-circle:{ style="color:#1E7B5C" } Done |
| Case study section in Figma (links, QR code, slide outline) | :material-check-circle:{ style="color:#1E7B5C" } Done |
| Case study deck | :material-check-circle:{ style="color:#1E7B5C" } Draft with hi-fi screens and QR; research gaps marked |
| Telegram bot [@campusswap_bot](https://t.me/campusswap_bot) | :material-check-circle:{ style="color:#1E7B5C" } MVP done, profile set up, runs locally |
| Documentation site | :material-check-circle:{ style="color:#1E7B5C" } Done |

## Rubric coverage (exam: 28 November 2026)

Status of every graded item. **Ready** means built and needs nothing more; **needs data** means the frame or slide is built but must be filled from real interviews or tests.

| Assignment | Item | Status |
|---|---|---|
| UX Research | A Research plan, interview guide, survey | Ready |
| | B Research report (summary, ≥2 key findings, recommendations, appendix) | Needs data: interviews + survey (by 15 Nov) |
| | C Rough design with annotations | Ready; add a photo of a hand sketch and the research link |
| Lo-Fi | A.1 Interview notes · A.2 Themes and HMW | Needs data: interviews |
| | A.3 Feature ideation (15 ideas) · A.4 Prioritization | Ready; confirm the reasons after synthesis |
| | B.1 User flow · B.3 Lo-fi clickable wireframes | Ready |
| | B.2 Crazy 8s paper sketches | Needs you: draw and photograph |
| Hi-Fi | A.1 Idea brief · A.2 Usability study guide | Ready |
| | A.3 User flow v2.0 | Needs data: 2–5 usability tests (by 21 Nov) |
| | B.1 Moodboard | Needs screenshots pasted |
| | B.2 Style guide · B.3 Pattern library · B.4 7 hi-fi screens + prototype | Ready |
| Case study | Figma file (online + `.fig`) | Ready; share the link and save the `.fig` copy |
| | Presentation (Google Slides) | Ready except findings, test results, key learnings, About me |
| | Live demo of the full flow | Ready: Figma flow *Hi-Fi prototype*, plus the live Telegram bot |

## What's left

### Research

- [x] Write the forms script ([`research/forms`](https://github.com/escalopa/campusswap/tree/main/research))
- [ ] Run it once to create the screener, survey and research spreadsheet
- [ ] Post the recruiting message in dorm and course chats
- [ ] Run 5–6 interviews
- [ ] Collect 30+ survey responses
- [ ] Fill interview notes, themes, report and key findings in Figma
- [ ] Draw a hand sketch of one screen

### Lo-fi

- [ ] Draw Crazy 8s and paste them into Figma
- [ ] Adjust lo-fi screens to the findings

### Hi-fi

- [x] Finish hi-fi screens 5–7 and wire the hi-fi prototype
- [ ] Run 2–5 usability tests
- [ ] Update user flow v2.0 and screens from test results
- [ ] Paste moodboard screenshots

### Case study and submission

- [x] Import the deck into [Google Slides](https://docs.google.com/presentation/d/118UVpU_nEm3OP0KZgbS7O5V0DsFyDCYGhPjINbZ9dK4/edit?usp=sharing) and check the layout
- [ ] Fill findings, test results, key learnings, About me and timeline
- [x] Add hi-fi screenshots, prototype link and QR code
- [x] Link the deck in the Figma file (section 04)
- [ ] Share Figma and Slides as "Anyone with the link can view"; save a `.fig` copy; export the deck as PDF
- [ ] Rehearse: 25-minute run-through with a live prototype demo

### Telegram bot

- [x] Create a bot with @BotFather and run it locally
- [ ] Test with 3–5 students for a week and record usage numbers for the case study
- [x] Cloud Run + Firestore deployment code, tested against a real Firestore database
- [ ] Deploy with `bot/deploy/deploy.sh` (see [Deploy to Google Cloud](../bot/deploy.md))
- [ ] Later: "wanted" alerts, email verification by code

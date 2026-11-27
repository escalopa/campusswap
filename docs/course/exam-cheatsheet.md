# Exam cheat sheet — 28 November

## Tonight (about 2.5 hours, in this order)

1. **Sharing (10 min).** Figma → Share → *Anyone with the link* → *can view*. Google Slides → Share → *Anyone with the link* → *Viewer*. Open both links in a private window to check.
2. **Backups (10 min).** Figma → File → *Save local copy* (`.fig`). Slides → File → Download → PDF. Keep both on the desktop.
3. **Personal slides (20 min).** Slide 2: your real timeline. Slide 15: three key learnings in your own words. Slide 16: photo + one line about you.
4. **Research gap (choose one, 30–60 min).**
    - **A. Mini-study tonight (better).** Call or meet 3 dorm students, 10–15 minutes each, using questions 3, 6, 10, 11 and 13 of the interview guide. Ask 2 of them to try the prototype (tasks T1 and T2). Write down quotes. Replace slide 7 with 2–3 real findings, each with one quote, and say "n = 3, pilot".
    - **B. No interviews possible.** Retitle slide 7 to *"Research status: study designed, fieldwork next"* and present the plan, the competitor gap and the assumptions honestly (wording below). Never present invented findings.
5. **Rehearse twice (60 min)** with a timer, including the live prototype demo.
6. **Morning:** school ID, charger, camera, mic. Tabs: Slides, prototype, Figma file.

## Talk script (25 min)

| Min | Slide | Say |
|---|---|---|
| 0–1 | 1 Title | "CampusSwap helps students pass on dorm items to each other, free or cheap, with verified students and pickup built in." |
| 1–2 | 2 Overview | Role (research + UX/UI), platform (iOS), tools (Figma, FigJam, Google Forms), timeline. |
| 2–4 | 3 Problem | Usable items thrown away at move-out, newcomers buy new. Three assumed pains: posts get buried, strangers feel risky, pickup takes many messages. |
| 4–7 | 5 Methods | Three methods for three goals: interviews (why), survey (how many), competitive analysis (what's missing). Recruiting: dorm residents, givers and getters, no close friends (bias). |
| 7–9 | 6 Competitors | "Telegram chats have the right audience but the wrong format; Avito the right format but the wrong audience." Gap: verified campus audience + search + built-in pickup. |
| 9–11 | 7 Findings | Option A: real quotes from tonight. Option B: research status wording below. |
| 11–13 | 8 Synthesis | Sticky notes → themes → *How might we* → 15 ideas → value vs complexity → 7 MVP features (quick wins). |
| 13–15 | 10 User flow | Seven steps; pickup is the step no competitor has. Second flow: give away an item. |
| 15–17 | 11 Lo-fi | Crazy 8s → 4 grey screens, clickable. "Grey on purpose: feedback is about the flow, not colors." |
| 17–18 | 12 Testing | Four tasks with success criteria, think-aloud, SEQ 1–7. What changed (if you tested tonight). |
| 18–20 | 13 Visual | Green = trust and sustainability, yellow = warmth, coral only for alerts. Space Grotesk + DM Sans. WCAG: white on green 5.2:1. Components with variants. |
| 20–24 | 14 + demo | Switch to the prototype: sign up → home → desk lamp → request → pick 18:00 → confirm → rate. Then Post tab → post a kettle. Optionally show the real Telegram bot. |
| 24–25 | 15–17 | Key learnings, about me, thank you. Then open the Figma file: walk sections 01 → 04 left to right. |

## Honest wording if research isn't done (option B)

> "I designed the full study: research plan, interview guide with a rationale for every question, a 13-question survey, and the forms to collect it. The fieldwork is my next step. So far the design is built on the competitive analysis and on clearly labeled assumptions, and the usability test plan defines how I'll check them. The first thing I'd change after interviews is the prioritization: each selected feature has to be backed by a finding."

## Likely theory questions (short answers + link to your project)

| Question | Answer | In CampusSwap |
|---|---|---|
| UX vs UI? | UX = how easy and pleasant the whole experience is; UI = what the screens look like. | UX: the 7-step flow; UI: style guide and components. |
| Design thinking / double diamond? | Discover → define (right problem), develop → deliver (right solution); diverge then converge each time. | Research + synthesis = diamond 1; ideation, prototype, test = diamond 2. |
| Qualitative vs quantitative? | Qual explains *why* (few people, deep); quant measures *how many* (many people, shallow). Use both. | Interviews (5–6) + survey (30+). |
| How do you avoid bias in interviews? | Ask about past behavior, not hypotheticals; no leading questions; don't interview friends; let silence work. | "Tell me about the last time you got a used item…" |
| What is an affinity map? | Grouping sticky notes into themes to find patterns. | Notes per participant (one color each) → 4 themes. |
| What is a HMW question? | Turns a problem into an opportunity: broad enough for many ideas, narrow enough to focus. | "How might we make agreeing on pickup effortless?" |
| How did you prioritize? | Value vs complexity matrix: quick wins (high value, low effort) into the MVP. | 7 MVP features; ratings and alerts later. |
| Lo-fi vs hi-fi? | Lo-fi is cheap to change and tests the flow; hi-fi tests look, feel and details. | 4 grey screens → 7 hi-fi screens. |
| Why only 5 users in usability testing? | About 5 users find most usability problems; test in rounds, fix, test again (Nielsen). | 2–5 sessions, 4 tasks. |
| Moderated vs unmoderated? | Moderated: you're there and can ask why. Unmoderated: alone, scalable (Maze). | Moderated, think-aloud. |
| Gestalt principles? | Proximity, similarity, common region, continuity: people group what looks related. | Item cards: photo, title and building grouped in one card. |
| Fitts's law? | Bigger, closer targets are faster to hit. | Full-width primary button at the bottom (thumb zone). |
| Hick's law? | More choices = slower decisions. | 5 category chips, one primary action per screen. |
| Jakob's law? | Users expect your app to work like the apps they know. | Standard tab bar, back arrow, chat bubbles. |
| Accessibility? | WCAG AA: 4.5:1 contrast for text; don't rely on color alone; touch targets ≥ 44 px. | White on green 5.2:1; FREE tag has text, not just color. |
| Atomic design? | Atoms → molecules → organisms → templates → pages. | Colors/icons → buttons/chips → item card/tab bar → screens. |
| Components and variants? | A component is a reusable master; variants are its versions; instances update with the master. | Button: Primary/Secondary/Ghost; Chip: Default/Selected. |
| Design handoff? | Give developers specs, tokens, components and assets (Dev Mode). | Color variables + text styles + the working Telegram bot. |
| MVP? | Smallest product that solves the core problem so you can learn from real users. | The Telegram bot is a live MVP of the core flow. |
| How would you measure success? | Pick metrics tied to the goal: activation, task success, retention. | Items posted per week, % requests that end in a handover, rating average. |

## Questions about your project

- **Why this problem?** Personal: dorm move-in/move-out waste; a campus has a closed, trusted community.
- **Biggest risk?** Trust and no-shows → verified sign-up, ratings, pickup slots, cancel button.
- **What would you do next?** Run the full study, re-prioritize from findings, test v2 with 5 users, pilot the bot in one dorm and measure handovers.
- **Why a Telegram bot too?** Students already live in Telegram; it's the fastest way to test demand with real people.

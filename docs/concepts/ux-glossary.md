# UX/UI glossary

## Basics

UX (user experience)
:   How easy and pleasant the whole product is to use, from the first moment to the last. *In CampusSwap: the flow from finding an item to picking it up.*

UI (user interface)
:   What the screens look like: layout, colors, fonts, buttons. *In CampusSwap: the green buttons, item cards and tab bar.*

MVP (minimum viable product)
:   The smallest version of a product that solves the main problem, so you can learn from real users quickly. *In CampusSwap: 7 features — sign-up, post, search, building filter, free/swap/sell, chat, pickup scheduler.*

Value proposition
:   One statement of who the product is for, what it does, and why it's better than the alternatives. *See the [product overview](../product/index.md#value-proposition).*

Persona
:   A realistic description of a typical user, based on research. *In CampusSwap: "a newcomer who needs a desk lamp" and "a student moving out who wants their kettle to go to someone who needs it".*

## Research

Research plan
:   A document that says what you want to learn, from whom, and how. *[Research plan PDF](../assets/campusswap-research-plan.pdf).*

Research goals and questions
:   Goals are the big things you want to understand. Questions are the specific things you need answered to reach the goals.

Qualitative vs quantitative
:   Qualitative research explains *why* (interviews, observations, few people, deep). Quantitative research measures *how many* (surveys, analytics, many people, shallow). Good research uses both.

Semi-structured interview
:   A conversation with prepared questions, where you also follow up on interesting answers. Ask about real past events ("Tell me about the last time…"), not hypotheticals ("Would you use…?").

Interview guide (script)
:   The exact introduction, questions and closing you use in every interview, so interviews are comparable.

Rationale
:   The reason you ask each question, written next to it. The course rubric requires one for every interview and survey question.

Survey
:   A short online form many people fill in. It gives numbers, like "62% of respondents threw away an item someone else could have used".

Likert scale
:   A 1–5 (or 1–7) rating answer, from "very dissatisfied" to "very satisfied".

Recruiting criteria and screener
:   The rules for who can take part in your study, and the short questions that check them.

Bias
:   Anything that pushes answers away from the truth: interviewing friends, leading questions ("Don't you hate…?"), or only asking people who already agree.

Competitive analysis
:   Comparing the products people already use to find what's missing. *In CampusSwap: Telegram chats, Avito, VK groups and free shelves.*

Research report
:   A summary of what you learned: executive summary, background and goals, key findings with evidence, recommendations, and an appendix with the raw data.

Executive summary
:   Three or four sentences a busy person can read instead of the whole report.

Key finding
:   One important thing you learned, backed by evidence (quotes, counts, observations).

## Synthesis

Synthesis
:   Turning raw notes into clear insights you can design from.

Sticky notes (interview notes)
:   One idea per note, one color per participant, so you can see who said what and how many people said the same thing.

Affinity map (affinity diagram)
:   Moving sticky notes into groups of related ideas. Each group becomes a theme.

Theme
:   A pattern several people mentioned, like "trust and safety".

How Might We (HMW)
:   A way to turn a problem into an opportunity question: "How might we make agreeing on pickup effortless?" It's open enough for many ideas but focused on one problem.

Feature ideation
:   Brainstorming many possible features. Quantity first, judgment later. *In CampusSwap: 15 ideas.*

Feature prioritization
:   Choosing which features to build first.

Value vs complexity matrix
:   A 2×2 chart. High value and simple ("quick wins") go into the MVP; high value but complex ("big bets") come later; low value ideas wait or are dropped.

## Design

User flow
:   The steps a user takes to reach a goal, from start to finish. *In CampusSwap: onboard → discover → evaluate → request → pickup → handover → rate.*

Journey map
:   A user flow drawn as stages left to right, with the tasks (and sometimes feelings and pain points) under each stage.

Crazy 8s
:   Fold a sheet of paper into 8 boxes and sketch 8 ideas in 8 minutes. Speed beats beauty; the goal is many options.

Sketch
:   A quick hand drawing of a screen. The cheapest way to try an idea.

Wireframe
:   A screen made of grey boxes and plain text only, to plan layout and content. No colors or images.

Lo-fi (low fidelity)
:   Rough and simple: sketches or grey wireframes. Cheap to change, used to test whether the flow makes sense.

Hi-fi (high fidelity)
:   Looks like the finished app: final colors, fonts, icons and realistic content.

Mockup
:   A static picture of a hi-fi screen.

Prototype
:   Screens linked together so you can click or tap through them like a real app. Prototypes can be lo-fi or hi-fi.

Clickable prototype link
:   A Figma link (`figma.com/proto/…`) anyone can open to try the prototype. The final case study needs one, plus a QR code.

Moodboard
:   A collage of inspiration — other apps, colors, fonts, photos — that sets the feeling of the design.

Style guide
:   The visual rules: color palette, typography (fonts, sizes, weights), icons, imagery, corner radius, shadows.

Pattern library (UI kit)
:   The reusable building blocks of the interface: buttons, inputs, chips, cards, navigation.

Design system
:   Style guide + pattern library + usage rules, used together so every screen looks consistent.

Atomic design
:   Building interfaces from small to large: **atoms** (colors, fonts, icons) → **molecules** (a button, a search field) → **organisms** (an item card, a tab bar) → **templates** → **pages**.

Visual hierarchy
:   Making the most important thing on a screen the most noticeable, using size, weight, color and position.

Gestalt principles
:   How people group what they see: things that are **close** together, **similar**, or inside the same **container** look related.

Fitts's law
:   Bigger and closer targets are faster to tap. That's why the main button is full-width at the bottom, in the thumb zone.

Hick's law
:   More choices make decisions slower. Keep options few and clear.

Jakob's law
:   Users spend most of their time in other apps, so they expect yours to work the same way. Use familiar patterns (tab bars, back arrows).

Affordance
:   A visual clue that shows how something can be used: a button looks pressable, a field looks typeable.

Accessibility and WCAG
:   Designing so everyone can use the product, including people with low vision. WCAG is the standard; normal text needs a contrast ratio of at least 4.5:1 with its background.

Design handoff
:   Giving developers what they need to build the design: specs, spacing, colors, components and assets (Figma Dev Mode helps).

## Testing

Usability testing
:   Watching real people try your prototype to find where they get confused or stuck.

Moderated vs unmoderated
:   Moderated: you're with the participant (in person or on a call) and can ask follow-ups. Unmoderated: they do the tasks alone with a tool like Maze.

Usability study guide
:   The plan and script for a test: participants, setup, introduction, warm-up questions, tasks, wrap-up.

Opening ethnography
:   A few warm-up questions about the participant's real life before the tasks.

Task and success criteria
:   A realistic goal you ask the participant to complete ("Find a free desk lamp"), and what counts as success ("reaches item details in under 60 seconds").

Think-aloud
:   Participants say what they're looking at and thinking while they use the prototype.

SEQ (Single Ease Question)
:   "How easy was that, from 1 to 7?" asked after each task.

Why five users?
:   Research by the Nielsen Norman Group shows about five participants find most of the usability problems in a design. Testing more people in rounds (test, fix, test) beats testing many people once.

Iteration (v2.0)
:   Improving the design based on test results, then testing again.

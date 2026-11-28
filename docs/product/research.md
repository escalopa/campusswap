# Research

The full plan is in the [research plan PDF](../assets/campusswap-research-plan.pdf) and in the Figma file, section **01 · UX Research**.

## Goals

1. **Understand current behavior:** how students get rid of and get dorm items, and which channels they use.
2. **Find pain points:** what makes buying, selling or giving away items between students slow, frustrating or risky.
3. **Understand trust and handover:** what makes students trust another student, and what makes pickup easy or hard.

Out of scope: payments, delivery services, selling outside the university.

## Research questions

1. What items do students buy, sell or give away, and when (move-in, move-out, mid-semester)?
2. Which channels do they use today, and why?
3. What frustrates them most about these channels?
4. What information do they need before deciding to take an item?
5. What makes them trust or distrust another student?
6. How do they arrange the handover, and what goes wrong?
7. What motivates them to sell versus give items away for free?

## Methods

Interviews were scoped out to fit the course timeline. Research uses:

=== "Survey (primary)"

    - **Who:** students living in the dorms
    - **Format:** anonymous Google Form, 9 questions, about 3 minutes ([open the form](https://docs.google.com/forms/d/e/1FAIpQLSeZqgGGr42lQ_Ph2Kzji2QeW6nCwc-nRKMY6Zw-5VnyHHrCjA/viewform))
    - **Covers:** behavior (Q1–3), pain points (Q4–5), trust (Q6), value (Q7–8), open ideas (Q9)
    - **Status:** live. The first 22 submissions were test entries used to check the form and the analysis script, and are excluded from results.

=== "Competitive analysis"

    - **What:** Telegram dorm chats, Avito, VK groups, campus free shelves
    - **Criteria:** campus-only audience, search, visibility, trust, pickup, alerts, fees
    - **Result:** see the [competitive landscape](index.md#competitive-landscape)

=== "Usability test"

    - **What:** 4 tasks on the clickable hi-fi prototype, think-aloud, ease rated 1–7
    - **See:** [Design → Usability testing](design.md#usability-testing)

## Recruiting criteria

- **Must:** current student living in the dorms for at least one semester, who exchanged (or threw away) an item in the last 12 months
- **Mix:** 2+ mostly givers and 2+ mostly getters, different study years, at least one international and one local student
- **Exclude:** close friends and teammates (bias), anyone who has seen the concept

## Key findings

!!! warning "Waiting for real survey answers"
    This section will hold 2–3 key findings with the share of respondents behind each, plus a recommendation per finding. Test entries are not reported as findings.

| # | Finding | Evidence | Recommendation |
|---|---|---|---|
| 1 | *pending* | *% of respondents* | *pending* |
| 2 | *pending* | *% of respondents* | *pending* |
| 3 | *pending* | *% of respondents* | *pending* |

## Synthesis: from notes to features

```mermaid
flowchart LR
    N[Survey answers<br>+ competitor gaps] --> T[Themes<br>affinity map]
    T --> H[How might we…?<br>questions]
    H --> I[15 feature ideas]
    I --> P[Value vs complexity<br>matrix]
    P --> M[7 MVP features]
```

Draft themes and their opportunity questions (to be confirmed by the real notes):

| Theme | How might we… |
|---|---|
| Finding items | …help students quickly find the item they need on campus? |
| Posting and reach | …make posting an item fast and keep it visible? |
| Trust and safety | …help students feel safe exchanging with someone they don't know? |
| Handover | …make agreeing on pickup time and place effortless? |

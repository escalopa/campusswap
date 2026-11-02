# Design

All design work lives in the [Figma file](https://www.figma.com/design/FBkfowqM4rI8lcgZ8fuzQv), sections **02 · Lo-Fi Prototype** and **03 · Hi-Fi Prototype**.

## User flows

### Flow 1: get an item

| Step | Tasks |
|---|---|
| 1. Onboard | Sign up with university email · choose dorm building |
| 2. Discover | Browse "near you" · search or pick a category · filter free only |
| 3. Evaluate | Open item · check photos and condition · check giver profile and rating |
| 4. Request | Tap "Request item" · send a quick-reply message |
| 5. Arrange pickup | Pick one of the giver's time slots · see the pickup spot |
| 6. Handover | Meet at the spot · both confirm |
| 7. Rate | Rate the giver · item marked as given |

### Flow 2: give away an item

Tap **+** → add 1–4 photos → title and category → condition → Free, Swap or Sell → pickup spot and time slots → publish → accept a request → hand over → rate.

## Lo-fi prototype

**Lo-fi** means rough: grey boxes and plain text, so feedback is about the flow, not colors.

- **Crazy 8s:** eight paper sketches in eight minutes (home, search, item details, post, chat, pickup picker, handover, profile)
- **Wireframes:** four clickable screens in Figma — Home feed, Item details, Post an item, Chat and pickup
- **Prototype:** in Figma Present mode, flow *Lo-Fi prototype*

## Usability testing

A moderated test with 2–5 students, using the clickable prototype and the think-aloud method.

| Task | What the participant does | Success means |
|---|---|---|
| T1 | Find a free desk lamp in your building and open it | Item details in under 60 seconds |
| T2 | Request it and choose a pickup time | Time slot selected, confirmation seen |
| T3 | Confirm the handover and rate the giver | Rating submitted |
| T4 | Post your old kettle for free, pickup at your lobby | Published in under 90 seconds |

After each task: *"How easy was that, from 1 (very difficult) to 7 (very easy)?"* (Single Ease Question).

!!! warning "To fill after testing"
    Problems observed → changes made → user flow v2.0.

## Visual design

**Moodboard keywords:** friendly, trustworthy, fresh, campus-made, sustainable, quick.
**References:** Vinted (item cards), Too Good To Go (pickup windows, warm green), Depop (youthful tone), Airbnb (trust through reviews), Duolingo (friendly microcopy). Avito as the example of what to avoid.

### Colors

| | Name | Hex | Use |
|---|---|---|---|
| <span class="swatch" style="background:#1E7B5C"></span> | Green | `#1E7B5C` | Primary actions, active states |
| <span class="swatch" style="background:#145640"></span> | Green dark | `#145640` | Text on mint |
| <span class="swatch" style="background:#DDF1E8"></span> | Mint | `#DDF1E8` | FREE tag, success backgrounds |
| <span class="swatch" style="background:#FFC83D"></span> | Yellow | `#FFC83D` | Prices, highlights |
| <span class="swatch" style="background:#FF6B4A"></span> | Coral | `#FF6B4A` | Alerts and badges only |
| <span class="swatch" style="background:#14161A"></span> | Ink | `#14161A` | Text |
| <span class="swatch" style="background:#FAF8F2"></span> | Cream | `#FAF8F2` | App background |

White text on the primary green has a contrast ratio of 5.2:1, which passes WCAG AA.

### Typography

- **Space Grotesk** (Bold, Medium) for headings: friendly, a little techy
- **DM Sans** (Regular to Bold) for UI and body text: easy to read at small sizes
- App scale: Title 24 · Heading 17 · Body 15 · Button 16 · Caption 12

### Pattern library

Built as Figma components with variants (atomic design):

- **Icons:** 18 line icons, 24 px, 2 px stroke
- **Button:** Primary, Secondary, Ghost
- **Chip:** Default, Selected · **Tag:** Free, Price
- **Inputs:** Search field, Form field with label
- **Cards:** Item card (feed grid), Giver card (avatar, verified badge, rating)
- **Navigation:** Tab bar with a raised Post button, Header with back button

## Hi-fi screens

iPhone 14 size (390 × 844), built only from the style guide and pattern library:

1. Sign up (university email)
2. Home (free near you, categories)
3. Item details (photo, FREE tag, giver card, pickup info)
4. Chat and pickup (choose a time slot)
5. Pickup confirmed
6. Handover and rating
7. Post an item

**[Open the clickable prototype](https://www.figma.com/proto/FBkfowqM4rI8lcgZ8fuzQv/CampusSwap?node-id=10-144&starting-point-node-id=10-144)** (Figma flow *Hi-Fi prototype*): sign up → home → item details → chat and pickup → pickup confirmed → rating → home. The Post tab opens "Post an item".

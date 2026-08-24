---
name: itinerary-architecture
description: Sequence destinations and lock transport and lodging anchors. Use after intake, before writing day-by-day.
---

# Architecture (advisors call this the skeleton)

## 1. Filter destinations

Season, access time, whether interests cluster in one area, and whether stops connect without backtracking. Drop a stop that adds a full extra travel day unless it is a non-negotiable.

## 2. Anchors first

Lock in this order using live tools, not memory:

1. Long legs — `plan_leg` (and leaf transport tools if you need a specific mode).
2. Nights implied by those legs — `compare_stays` for the city and dates.
3. Timed tickets, permits, hard restaurant slots (ask the traveler; do not fake sold-out inventory).

Arrival night is for recovery if they flew overnight. Do not stack a peak experience after a red-eye.

## 3. Sequence stays

Prefer ending on the highlight stay when routing allows. If air or rail forces the wow stay into the middle, say so: what you wanted vs why it is this way.

## 4. Geography over excitement

Assign each day a zone (neighborhood or town). Do not zigzag across a city to hit “top sights” in rank order. Clustering cuts wasted transit.

## 5. Buffers

One buffer day per week of travel. First/last nights prefer refundable stays when flights can slip.

## 6. Tools

- `plan_leg` for each hop
- `compare_stays` (or lodging leaf tools) for each city block
- Present 2–3 options with one recommended pick and a one-line why

Do not book. Quote and wait for approval.

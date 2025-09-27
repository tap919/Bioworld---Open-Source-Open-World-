# Bioworld — Ultimate Playbook v1
Date: 2025-09-16

## A) Reworded prompt for a world‑class game developer
“Deliver a concise, low‑risk upgrade plan for **Bioworld** that improves player onboarding, readability, and systemic depth without scope creep. Provide 50 incremental improvements, a 90‑day implementation plan, and clear success metrics. Anticipate 50 common objections from developers and publishers, classify each as **KEEP** (part of our edge) or **IMPROVE** (we fix), and propose the minimal remedy where needed. Finish with 5 small moves that let Bioworld outperform GTA and Fallout on specific axes without aping them.”

---

## B) 50 low‑scope improvements
1. **First‑minute goal card** — Show a single objective on spawn. Reduce overwhelm.
2. **Context pings** — Press middle‑mouse to tag an object and see affordances.
3. **Diegetic hints** — NPC signs or field notes teach one system per area.
4. **Tooltips with verbs** — Items list what they *do*, not lore.
5. **Hold‑to‑confirm on destructive actions** — Prevent accidental deletes.
6. **Photo mode** — Drives sharing and tests readability.
7. **Quick‑place hotbar** — One‑tap place last three build pieces.
8. **Radial emote/wave** — Lightweight social signal in coop.
9. **Breadcrumb trail** — Toggle to highlight last 20 steps for backtracking.
10. **Pingable resources** — Scan pulse reveals nearby gatherables on cooldown.
11. **Crafting queue** — Fire‑and‑forget batch crafting to cut tedium.
12. **Ghost preview with snap** — Grid and angle snap with RVT‑aware blend.
13. **Undo last build** — Single‑step undo for placed pieces.
14. **Lightweight stamina** — Short sprints, no long‑term debuffs.
15. **Contextual prompts priority** — Avoid prompt spam by importance.
16. **Audio affordance palette** — Unique “clicks” for gather, craft, place.
17. **Minimal fall damage** — Forgiving traversal during prototype.
18. **Safe bed savepoint** — Clear save rules; no loss surprises.
19. **Discovery log** — Auto journal when you trigger a new interaction.
20. **Blueprint share code** — Copy a short code to spawn your build.
21. **Photo‑to‑blueprint** — Snapshot a build to auto‑create a plan.
22. **In‑world craft benches** — Few, readable tiers with silhouettes.
23. **Resource purity UI** — Simple bar with thresholds, not decimals.
24. **Day‑one remapping** — Full input remap, hold/toggle inversion.
25. **Color‑blind safe palette** — Modes for common deficiencies.
26. **Camera collision smoothing** — Avoid pop‑in on foliage.
27. **Dynamic FOV hint** — Slight widen when sprinting or falling.
28. **Footstep decals** — Read terrain moisture and direction.
29. **Wind lanes** — Visualize wind that affects seeds or smoke.
30. **Simple weather alerts** — Icons for approaching hazard fronts.
31. **Lightweight photo quests** — “Capture a chain reaction” tasks.
32. **Graceful coop drop‑in** — Spawn next to host, auto‑equip basics.
33. **Session recovery** — Rejoin within 5 minutes keeps inventory.
34. **Ping latency display** — Small number near nameplate.
35. **No hard hunger** — Energy as action budget, not failure state.
36. **One‑screen crafting** — No nested tabs; search bar.
37. **Inline tutorials** — One card per mechanic, dismissible forever.
38. **Explainer replays** — Tiny gifs in UI to show verbs.
39. **Collectible sets** — Small set bonuses nudge exploration.
40. **Waypoint sharing** — Paste a map pin to chat.
41. **Server browser filters** — Friends, low ping, empty, survival, creative.
42. **Ghost collision on join** — 10 seconds no‑clip to avoid spawn grief.
43. **Low‑end preset** — One click to reach 60 FPS on 1660S.
44. **Async shader warmup** — Splash‑screen compilation to cut hitches.
45. **Crash reporter with repro steps** — In‑game form to attach save.
46. **Playtest mode** — Console flag that logs task completions.
47. **Diegetic progress gates** — Tools and knowledge over XP.
48. **Weekly seed** — Featured world seed for community experiments.
49. **Patch notes in launcher** — Visual, short, linked to issues.
50. **Dev commentary nodes** — Optional hotspots explaining design.

**Success metric for B:** +15% time‑to‑first‑craft speed. −25% early churn. +3 average surprises logged per session.

---

## C) 90‑day implementation plan
**Weeks 1–2** — Onboarding pass (1,3,4,15,18,37). Metrics wire‑up.  
**Weeks 3–4** — Build UX (7,12,13,36). RVT snap prototype.  
**Weeks 5–6** — Discovery and logging (19,31,46,50).  
**Weeks 7–8** — Coop quality (8,32,33,41,42,34).  
**Weeks 9–10** — Readability and traversal (2,5,10,16,26,27,28,29).  
**Weeks 11–12** — Performance and stability (43,44,45,49).  
**Ongoing** — Accessibility and options (24,25,35,40,47,48).

**Owners**  
- Design: A, B lists and readability.  
- Engineering: UX systems, networking, performance.  
- Art/Audio: Affordance palette, decals, icons.  
- QA: Playtest scripts, repro capture.  
- Prod: Scope and exit gates.

**Exit criteria**  
- New user reaches first craft <7 minutes.  
- 90th percentile hitch <16 ms during slice.  
- Coop reconnect success >95%.

---

## D) 50 likely objections and our stance
| # | Objection | Stance | Action | Rationale |
|---|---|---|---|---|
|1|“Systems over scripts is risky.”|KEEP|Show slice videos proving fun loops.|Differentiator. Evidence based.|
|2|“No story campaign.”|KEEP|Optional lore notes only.|Focus on sandbox pillar.|
|3|“Too complex for casuals.”|IMPROVE|Onboarding cards and hints.|Reduce cognitive load.|
|4|“Coop adds scope.”|IMPROVE|Listen‑server only in v1.|Constrain topology.|
|5|“Open source invites forks.”|KEEP|GPL + contributor guide.|Community is a force multiplier.|
|6|“Mod safety.”|IMPROVE|Sandboxed hooks v0.3.|Security budgeted later.|
|7|“Performance with Lumen/Nanite.”|IMPROVE|Low‑end preset, early profiling.|Predictable budgets.|
|8|“No monetization.”|KEEP|Free core, optional cosmetic pack later.|Focus on reach first.|
|9|“Art style unclear.”|IMPROVE|Stylized guide, silhouettes.|Readability first.|
|10|“Networking desync risk.”|IMPROVE|Replication budget and tests.|Targeted replication only.|
|11|“Retention uncertain.”|IMPROVE|Weekly seed and photo quests.|Light goals.|
|12|“QA surface huge.”|IMPROVE|Test slices, crash reporter.|Focus on loops.|
|13|“Tooling heavy.”|IMPROVE|Simple importer rules.|Lower asset friction.|
|14|“Market crowded.”|KEEP|Unique ecology interactions.|USP is systemic reactivity.|
|15|“No PvP limits virality.”|KEEP|Coop creativity focus.|Avoid grief meta.|
|16|“Controller support costly.”|IMPROVE|Essential verbs only.|Pare bindings.|
|17|“Accessibility scope.”|IMPROVE|Top 4 features now.|High ROI, low cost.|
|18|“Localization later?”|IMPROVE|Text keys early.|Enable community loc.|
|19|“Save integrity.”|IMPROVE|Safe beds and autosaves.|Clear model.|
|20|“Griefing risk.”|IMPROVE|Ghost on join, pin tools.|Prevent collisions.|
|21|“Map empty without story.”|KEEP|Ecology provides goals.|System‑born challenges.|
|22|“Crafting grind.”|IMPROVE|Queue and batch.|Cut friction.|
|23|“Camera issues.”|IMPROVE|Collision smoothing.|Comfort.|
|24|“Hardcore expects hunger.”|KEEP|Energy budget instead.|Less punitive.|
|25|“No PvE bosses.”|KEEP|World as opponent.|Stay pillar‑true.|
|26|“Art bottleneck.”|IMPROVE|PCG dressing, kitbash.|Throughput.|
|27|“Long shaders.”|IMPROVE|Async warmup.|Reduce hitch.|
|28|“Foggy KPIs.”|IMPROVE|Define 3 metrics.|Guide decisions.|
|29|“Ambiguous target.”|IMPROVE|Audience statement.|Align cuts.|
|30|“Content scarcity.”|IMPROVE|Combos > items.|Depth over breadth.|
|31|“Input overload.”|IMPROVE|Hold‑to‑confirm, remap.|Fewer mistakes.|
|32|“Tutorial stigma.”|IMPROVE|Inline tips, dismissible.|Player respect.|
|33|“Cheating in coop.”|IMPROVE|Server authority minimal.|Integrity.|
|34|“Hosting headaches.”|IMPROVE|Browser filters.|Find good lobbies.|
|35|“No console.”|KEEP|PC first for speed.|Focus and cost.|
|36|“UI looks generic.”|IMPROVE|Iconography pass.|Readability.|
|37|“Physics bugs.”|IMPROVE|Record and repro tools.|Faster fixes.|
|38|“Analytics creep.”|KEEP|Opt‑in only, minimal.|Trust.|
|39|“Community toxicity.”|IMPROVE|Mute/report basics.|Safety.|
|40|“IP risk with mods.”|IMPROVE|Content policy.|Avoid takedowns.|
|41|“Legal for OSS.”|IMPROVE|CLA and license vet.|Compliance.|
|42|“Data privacy.”|IMPROVE|No PII, clear notice.|Compliance.|
|43|“Brand identity weak.”|IMPROVE|Name and logo pass.|Clarity.|
|44|“No achievements.”|IMPROVE|Small badges.|Soft goals.|
|45|“Patch churn.”|IMPROVE|Visual notes in launcher.|Player comms.|
|46|“No photo mode.”|IMPROVE|Add simple mode.|Shareability.|
|47|“No roadmap.”|IMPROVE|Public milestones.|Expectation mgmt.|
|48|“Hard to stream.”|IMPROVE|Streamer safe mode.|TOS friendly.|
|49|“Build grief.”|IMPROVE|Undo and locks.|Protection.|
|50|“Niche appeal only.”|KEEP|Depth over mass appeal.|Community core.|

---

## E) Five small plays to outperform GTA and Fallout on specific axes
1. **Shareable blueprints as social objects** — GTA/Fallout lack native build‑sharing loops. Make builds portable with short codes and leaderboards for “most remixed.”
2. **Reactive ecology chains** — Chain reactions that travel through wind, water, heat, and AI needs. Market the “unexpected.”
3. **Zero‑friction coop creation** — Join, place, and leave with state preserved per player. Content creators can collaborate fast.
4. **In‑game automation blocks** — Simple logic cubes enable farms and factories without mods. Streamer‑friendly engineering.
5. **Weekly world parameters** — A rotating seed with one rule tweak. Community experiments create news.

---

## F) Handoff notes
- This document aligns with the Preproduction Handoff Packet.  
- Implement sections B and C first. Use metrics listed.  
- Keep/Improve stances in section D are binding through prototype unless metrics say otherwise.

# The Fairway villa, Dubai Hills Estate: recreation brief

Source listing (read 2026-09-26):
https://www.propertyfinder.ae/en/plp/buy/villa-for-sale-dubai-dubai-hills-estate-the-fairway-141920484.html
Listed by fam Properties, ref PF-IvGx-VS-181490. AED 43,800,000.

The listing has **no floor plans, no dimensions and no elevations**. An exact
copy is not possible from it. This project recreates the villa from what the
listing publishes: its figures, its room list and 30 photographs. Everything
else is a design decision, labelled below as an assumption, and the validator
holds it to the Dubai Building Code the same way as the other villa.

The original design belongs to its architect and builder. This model is for
study and visualisation. It is not a set of drawings to build that house from.

## Facts from the listing (used as fixed inputs)

| Item | Listing | Model |
|---|---|---|
| Plot | 13,033.05 sq ft | 30.00 x 40.36 m = 1,210.8 m2 (shape assumed) |
| Built-up area | 12,600 sq ft (1,170.6 m2) | BRIEF_GFA; check 17 holds BUA to +/-10 % |
| Bedrooms | 5 + maid's | 5 en-suite bedrooms on FF, maid's room on GF |
| Bathrooms | 7 | 5 en-suites + maid's bath + driver's bath (plus powder room and spa shower, counted differently by agents) |
| Rooms | cinema, office/study | basement cinema; GF office |
| Features | private garden and pool, gym, jacuzzi, walk-in closets, study, pantry, maid's and driver's rooms, laundry and storage, balcony, open kitchen, wine cellar, BBQ area, steam room, covered parking and garage | all present |
| Community | The Fairway, Dubai Hills Estate; built by BCI; Vastu compliant; fully furnished | Dubai; Vastu not modelled (see open questions) |

## What the photographs show (the architecture being matched)

- **Massing:** a white rendered first-floor box cantilevered over a fully glazed
  ground floor on the garden side.
- **Screens and cladding:**
  - vertical timber louvres in front of the first-floor bedroom windows;
  - a projecting white roof "frame" over the first floor;
  - a dark grey stacked-stone feature wall on one flank.
- **Rear:**
  - a first-floor balcony with a glass balustrade;
  - a rectangular blue-mosaic pool with an in-water sun ledge and water jets;
  - pale stone paving next to the house and a timber deck with loungers;
  - hedged boundaries and palms.
- **Covered BBQ / dining terrace:**
  - composite timber deck and a timber soffit;
  - an outdoor kitchen against a stone wall, with a TV above.
- **Ground-floor interior:**
  - open living with veined travertine floors and feature walls, black slot-light tracks and floor-to-ceiling glass to the pool;
  - dining for 10 beside an open kitchen with a marble island;
  - a floating cantilevered stair with a glass balustrade against a walnut-shelved wall, and a timber-framed glass screen.
- **First floor:**
  - a landing with a glass balustrade over a double-height void;
  - a family lounge;
  - bedrooms with herringbone oak, walnut wardrobes and louvred glazing;
  - a child's bedroom.
- **Other rooms:**
  - a home cinema with two tiers of modular sofas, acoustic panelling and a ceiling projector, and no windows;
  - a garage with a polished-concrete floor and a glazed sectional door.
- **Street side:** white boxes, a dark vertical-slat gate, palms in front of the boundary wall.

## Evidence for the storeys (assumption A1)

The BUA (1,170.6 m2) is 97 % of the plot (1,210.8 m2). Two storeys would need a
585 m2 ground floor (48 % cover) and leave little room for the photographed
garden, pool, deck and BBQ terrace.

Comparable listings in The Fairway show **basement + G + 1 (+ roof)**, with the
cinema, gym, spa and wine cellar in the basement:

- [Provident Estate: 5-bed villa in The Fairway](https://providentestate.com/buy/5-bedroom-villa-for-sale-in-the-fairway-dubai-hills-estate-dubai30281/)
  says "G+1+Roof+basement", 12,500 sq ft BUA on 10,791 sq ft;
- [Henley & Partners: Dubai Hills Estate, The Fairway](https://www.henleyglobal.com/residence-investment/united-arab-emirates/real-estate/dubai-hills-estate-fairway-dubai-united-arab-emirates)
  describes four levels with a basement.

So this villa is modelled as B1 + GF + FF, with a flat roof that is not accessible.

## Assumptions (each can be changed in villa_design.py)

| # | Assumption | Why |
|---|---|---|
| A1 | Basement (cinema, media lounge and bar, gym, spa with steam and jacuzzi, wine cellar, play room, laundry, plant, stores) | see above |
| A2 | Rectangular plot 30.00 x 40.36 m; street north, golf course / garden south | typical Fairway plot proportions; the builders' street-north convention |
| A3 | Setbacks 6 m front, 3 m sides and rear | DBC K-SB-02 default (3 m); a deeper front for the forecourt. The Dubai Hills DCR was not available |
| A4 | GF +200 above the road; forecourt rises to it at <= 4 % | parking slope K-PARK-02; photographed level thresholds to the deck |
| A5 | Ground floor 3.6 m clear, first floor 3.2 m, basement 3.5 m | photographed floor-to-ceiling glazing; tiered cinema |
| A6 | Straight floating feature stair GF-FF (24 risers of 170.8, treads 280); enclosed service stair B1-GF (23 risers of 173.9) | photographs; DBC K-BSMT-04 (an enclosed basement stair) |
| A7 | Five bedroom suites on FF; the GF has living, dining, open kitchen and pantry, office, sitting room, powder room, maid's and driver's rooms and a 2-car garage | photographs of bedrooms behind the FF louvres |
| A8 | Pool 4.5 x 9.0 m running from the house towards the garden; 1.1-1.5 m deep; the sun ledge (300 deep) modelled as a bench | photographs; DBC K-POOL-02/03 (see open questions) |
| A9 | Basement rooms are non-habitable recreation/service rooms, mechanically ventilated | DBC K-BSMT-03 requires daylight for HABITABLE basement rooms; see open questions |
| A10 | Materials: white render, dark stacked stone (east flank, BBQ wall), timber louvres/soffits/deck, black aluminium frames, limestone paving, blue mosaic pool | photographs |

## Open questions for the owner

1. **Floor plans.** With the agent's floor plans (fam Properties, ref
   PF-IvGx-VS-181490), rooms and dimensions can be matched exactly. Everything
   in A1-A9 would then be replaced by the real figures.
2. **The sun ledge.** It is photographed at about 300 mm deep. DBC K-POOL-03
   wants the shallowest designed depth to be 850-1,200 mm. The model treats the
   ledge as a bench, not as floor. An authority may not accept that.
3. **Basement recreation rooms.** Are they habitable? If Dubai Municipality
   classes the media lounge or gym as habitable, K-BSMT-03 needs daylight.
   That means a lightwell or sunken court, which is not in the photographs.
4. **Vastu.** The listing says "Vastu compliant". Vastu rules (entrance
   direction, kitchen in the south-east, master bedroom in the south-west) are
   not modelled. The model's orientation (street north) is assumed.
5. **Roof.** Comparable villas have a roof terrace. The photographs show none,
   so the roof is not accessible.

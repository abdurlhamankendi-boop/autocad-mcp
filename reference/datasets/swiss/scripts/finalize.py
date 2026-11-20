import json, os, sys
mined = json.load(open(sys.argv[1], encoding='utf-8'))
OUT = r"C:\Users\lsire\autocad-mcp\reference\datasets\swiss_stats.json"
ZIP = r"C:\Users\lsire\autocad-mcp\reference\datasets\swiss\swiss-dwellings-v3.0.0_geometries.zip"

meta = {
    'purpose': 'TYPICALITY WARNINGS for villa_design.py (not hard rules). Swiss multi-family apartments, not Gulf villas: '
               'flag a villa value only as "unusual vs Swiss dwelling stock" when it falls outside p5..p95; never block on it.',
    'generated': '2026-09-26',
    'units': 'metres / square metres; areas are net polygon areas of the annotated spaces (inside walls)',
    'source': {
        'title': 'Swiss Dwellings: A large dataset of apartment models including aggregated geolocation-based simulation results '
                 'covering viewshed, natural light, traffic noise, centrality and geometric analysis',
        'version': '3.0.0 (changelog date 2023-03-31; Zenodo publication_date field 2022-09-20)',
        'zenodo_record_requested': 'https://zenodo.org/records/7070951 (concept record; the API resolves it to the latest version)',
        'zenodo_record_resolved': 'https://zenodo.org/records/7788422',
        'doi': '10.5281/zenodo.7788422', 'concept_doi': '10.5281/zenodo.7070951',
        'creators': 'Matthias Standfest; Michael Franzen; Yvonne Schröder; Luis Gonzalez Medina; Yarilo Villanueva Hernandez; '
                    'Jan Hendrik Buck; Yen-Ling Tan; Milena Niedzwiecka; Rachele Colmegna (Archilyse AG)',
        'licence': {
            'id': 'cc-by-4.0', 'name': 'Creative Commons Attribution 4.0 International',
            'url': 'https://creativecommons.org/licenses/by/4.0/legalcode',
            'verified_how': 'Zenodo API https://zenodo.org/api/records/7070951 -> metadata.license.id == "cc-by-4.0"; '
                            'Zenodo licence vocabulary: re-distribution and re-use allowed on condition that the creator is appropriately credited',
            'attribution_to_use': 'Standfest, M. et al., Swiss Dwellings v3.0.0, Zenodo, doi:10.5281/zenodo.7788422, CC BY 4.0. '
                                  'Statistics derived (aggregated) by this pipeline; not endorsed by the authors.',
        },
        'data_origin_per_record': 'Plans of commercial clients of Archilyse AG, digitised and manually QA-ed (<=5% area deviation, median 1.2%).',
    },
    'download': {
        'archive_on_zenodo': {'key': 'swiss-dwellings-v3.0.0.zip', 'bytes': 931868205,
                              'published_checksum': 'md5:3b7915ecd5bf8e492a3e78c598b74123'},
        'what_was_fetched': 'Only the geometries.csv member, via one HTTP Range request (bytes 85-291005590 of the archive = local header + '
                            'deflate stream, 291,005,506 bytes). A central directory was appended locally so the file is a normal zip.',
        'local_file': ZIP, 'local_file_bytes': os.path.getsize(ZIP),
        'integrity': 'CRC-32 0x1be5b7b9 and uncompressed size 1,093,732,415 bytes of geometries.csv match the original archive\'s central directory. '
                     'The whole-archive md5 could not be checked because the whole archive was not downloaded. '
                     'md5 of extracted geometries.csv (computed locally): d8017c3499940b9fc77bf24554761eb0',
        'skipped_members': {
            'swiss-dwellings-v3.0.0/simulations.csv': '639,072,043 B compressed / 1,594,839,853 B raw: per-area view/sun/noise/centrality simulations '
                                                     '(+ layout_* columns such as number_of_doors that could cross-check ours); not needed for geometry statistics',
            'swiss-dwellings-v3.0.0/locations.csv': '1,768,834 B / 5,551,909 B: site climate and points of interest; not needed',
            'swiss-dwellings-v3.0.0/location_ratings.csv': '20,797 B / 87,232 B: location ratings; not needed',
        },
    },
    'method': {
        'dwelling_key': 'site_id + apartment_id (the record states apartment_id is only unique per site)',
        'dwelling_filter': 'unit_usage RESIDENTIAL only; dwellings with <2 valid areas or <15 m2 indoor net area dropped',
        'deduplication': 'Floors that reuse the same plan give identical apartments (same area_ids). Each distinct layout (set of area_ids) is counted ONCE; '
                         'n_apartment_instances shows how many real apartments the layouts stand for',
        'label_schemes': 'Annotations use either explicit labels (BEDROOM / LIVING_ROOM / LIVING_DINING) or a generic ROOM label. '
                         'If LIVING_* is present and BEDROOM is not, ROOM = bedroom. If BEDROOM is also present, ROOM = study. '
                         'Layouts with ONLY generic ROOM labels ("--R", about 23%) have no reliable living/bedroom split, so they are EXCLUDED from all groups '
                         '(see sensitivity_generic_room_scheme)',
        'bathroom_split': 'Swiss BATHROOM areas are split by fixtures: shower or bathtub -> bathroom (full); toilet without shower/bath -> wc; '
                          'no fixtures -> sanitary_nofixture',
        'shape': 'short/long side and aspect ratio = minimum rotated rectangle of the room polygon (plans are often rotated). rectangularity = area / that rectangle; '
                 'near_rectangular_subset (rectangularity >= 0.9) is the fairest comparison for the villa\'s rectangular rooms',
        'doors': 'Doors carry no room id in the data, so they are matched geometrically: a DOOR / ENTRANCE_DOOR polygon within 5 cm of a room whose boundary runs '
                 '>= 0.20 m along it; the 2 best rooms are kept. doors_per_room counts DOOR + ENTRANCE_DOOR. See qa.opening_matching_counts: '
                 '~98.6% of interior doors match exactly 2 rooms',
        'open_connections': 'Two rooms <= 2 cm apart sharing >= 0.5 m of boundary (annotator "area splitter", no wall between them), e.g. an open kitchen to living',
        'shares_wall_or_boundary': 'rooms <= 0.6 m apart whose 0.3 m buffers overlap along >= 1.0 m (i.e. back-to-back across a wall), plus all door/open links',
        'connection_probabilities': 'connections.<kind>[t1][t2] = share of t1 rooms with >= 1 link to a t2 room. ENTRANCE = dwelling entrance door, '
                                    'EXTERNAL = door to a space outside the dwelling other than the entrance. link_pair_share = share of all links by room-type pair',
        'swiss_room_count': 'n_rooms_swiss = number of ROOM + BEDROOM + LIVING_ROOM + LIVING_DINING areas (Swiss "Zimmer" count, half-rooms ignored). '
                            'rooms_ge4 therefore mostly = 3 bedrooms + living',
        'circulation': 'corridor/hall (CORRIDOR, CORRIDORS_AND_HALLS, LOBBY, FOYER) + STAIRCASE areas inside the dwelling / indoor net area '
                       '(indoor = all non-outdoor, non-technical areas). Circulation inside open-plan living rooms is not counted',
        'derived_types': {
            'bedroom_master_proxy': 'largest bedroom of a dwelling with >= 2 bedrooms',
            'bedroom_secondary': 'the other bedrooms of such dwellings',
            'bathroom_ensuite': 'full bathroom with a direct door/open link to a bedroom',
            'bathroom_shared': 'full bathroom without such a link',
            'hall_entrance': 'corridor that holds the dwelling entrance door',
            'corridor_internal': 'other corridors',
        },
        'percentiles': 'linear-interpolated percentiles over rooms (room stats) or dwellings (dwelling stats), one weight per unique layout',
        'code': r'C:\Users\lsire\autocad-mcp\reference\datasets\swiss\scripts: zipdir.py (list zip members from a range-fetched tail), '
                'fixzip.py (append central directory, verify CRC), stage.py (stream CSV -> SQLite, walls dropped), mine.py (statistics), '
                'finalize.py (provenance + caveats). Python 3.13, shapely 2.1.2, numpy 2.5.2',
    },
    'type_mapping_swiss_to_canonical': {
        'living': ['LIVING_ROOM', 'LIVING_DINING', 'ROOM (only in generic-label sensitivity block: largest ROOM)'],
        'dining': ['DINING'],
        'kitchen': ['KITCHEN', 'KITCHEN_DINING'],
        'bedroom': ['BEDROOM', 'ROOM (when LIVING_* is labelled and BEDROOM is not)'],
        'study': ['ROOM (when BEDROOM and LIVING_* are both labelled)', 'OFFICE', 'OFFICE_SPACE', 'STUDIO'],
        'bathroom': ['BATHROOM with SHOWER or BATHTUB fixture'],
        'wc': ['BATHROOM with TOILET but no SHOWER/BATHTUB'],
        'sanitary_nofixture': ['BATHROOM with no sanitary fixtures drawn'],
        'corridor': ['CORRIDOR', 'CORRIDORS_AND_HALLS', 'LOBBY', 'FOYER'],
        'stair': ['STAIRCASE (area inside the dwelling; rare, see dwelling.internal_stair_fixture)'],
        'storage': ['STOREROOM', 'CLOAKROOM'],
        'balcony_terrace': ['BALCONY', 'LOGGIA', 'TERRACE', 'WINTERGARTEN', 'PATIO'],
        'garden': ['GARDEN'],
        'laundry': ['WASH_AND_DRY_ROOM (never inside a dwelling in this data, see dwelling.in_unit_washing_machine)'],
        'excluded_technical': ['SHAFT', 'ELEVATOR', 'VOID', 'LIGHTWELL', 'OUTDOOR_VOID', 'TECHNICAL_AREA', 'HEATING', 'NOT_DEFINED', 'etc.'],
        'excluded_not_indoor': ['BASEMENT_COMPARTMENT', 'BASEMENT'],
    },
    'villa_role_hints': {
        'note': 'Which statistics to compare each villa_design.py ROLE against. The recommended group is rooms_ge4 (as the task asked); '
                'bedrooms_ge4 is closer in family size but smaller; multi_floor is the only source for stairs.',
        'family_living': 'rooms.living', 'majlis': 'rooms.living (weak proxy: no Swiss equivalent of a formal reception room)',
        'formal_dining': 'rooms.dining (small n; Swiss dining is mostly part of LIVING_DINING)',
        'kitchen': 'rooms.kitchen', 'prep_kitchen': 'none (no Swiss equivalent)', 'pantry': 'none (storage is the nearest)',
        'master_bedroom': 'rooms_derived.bedroom_master_proxy', 'bedroom': 'rooms_derived.bedroom_secondary (or rooms.bedroom)',
        'ensuite': 'rooms_derived.bathroom_ensuite (n is small: en-suites are rare in Swiss flats)',
        'guest_wc': 'rooms.wc', 'hall': 'rooms_derived.hall_entrance', 'corridor': 'rooms_derived.corridor_internal / rooms.corridor',
        'landing': 'rooms.corridor in multi_floor', 'study': 'rooms.study',
        'store': 'rooms.storage', 'laundry': 'dwelling.in_unit_washing_machine (no in-unit laundry rooms in the data)',
        'maid_room': 'none (no Swiss equivalent)', 'maid_bath': 'rooms.bathroom (shower rooms) / rooms.wc', 'driver_room': 'none', 'driver_bath': 'none',
        'plant': 'none (technical areas excluded)',
        'stair': 'groups.multi_floor.dwelling.internal_stair_fixture',
        'bathrooms_per_bedroom': 'groups.<g>.dwelling.multi_bedroom',
        'circulation_share': 'groups.<g>.dwelling.circulation_share_of_indoor_area',
    },
}

caveats = [
    'Apartments, not villas: Swiss multi-family flats (median indoor net area about 84 m2 overall, about 106 m2 for rooms_ge4) are much smaller than a Gulf 4-bedroom villa. '
    'Room SIZES in a villa will often sit at or above the Swiss p75-p95; treat high-side deviations as informative, not as errors.',
    'Regional and cultural bias: Swiss (mostly German-speaking-region) housing from Archilyse clients, i.e. institutional and investor stock, not a random sample. '
    'No majlis, maid, driver or prep-kitchen rooms; laundry is communal in the basement; en-suite bathrooms are rare (about 8% of dwellings, 11% for rooms_ge4) '
    'and the bathrooms-per-bedroom ratio (median 0.5) is far below Gulf villa practice (usually >= 1). A villa exceeding the Swiss p95 on sanitary ratio is normal.',
    'Generic-label layouts (about 23% of unique layouts, only ROOM labels) are excluded from all groups; the sensitivity block shows their bedroom and bathroom areas are similar '
    'but heuristic "living" rooms are smaller, so living-room stats describe explicitly labelled (more recent) plans.',
    'Door and adjacency relations are recovered geometrically (doors have no room id in the data); about 1.3% of interior doors and about 9% of entrance doors could not be '
    'matched within 5 cm, so door counts are slight undercounts.',
    'Open-plan circulation is invisible: circulation_share counts only labelled corridor/hall/stair areas, so open-plan layouts show lower shares.',
    'Internal STAIRCASE areas are rare (maisonettes draw stairs as a fixture inside a corridor or living area). Stair footprints come from merged fixtures per floor and may '
    'describe only the part of a flight drawn on that floor.',
    'Shorter side and aspect ratio use the minimum rotated rectangle; for L-shaped or irregular rooms this overstates the usable width. Use near_rectangular_subset when '
    'checking rectangular villa rooms.',
    'Floor repetition is removed (one count per unique layout). n_apartment_instances gives the undeduplicated apartment count.',
    'Licence CC BY 4.0: any redistribution of these derived statistics must credit the dataset authors (see source.licence.attribution_to_use).',
]

final = {**meta, **mined, 'caveats': caveats}
# order: meta first, then groups, sensitivity, raw, qa, caveats
json.dump(final, open(OUT, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print('wrote', OUT, os.path.getsize(OUT))

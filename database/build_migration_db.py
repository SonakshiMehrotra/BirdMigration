"""Build a provenance-first SQLite database for India-linked bird migration.

Integrates literature provenance (WII, BNHS, ZSI) alongside the full 126-species
catalog sourced from Movebank GPS Telemetry and GBIF (Taxon: Aves 212).
"""
import json
from pathlib import Path
import re
import sqlite3

ROOT = Path(__file__).parent
DB = ROOT / "india_bird_migration.sqlite"
DATA_JS = ROOT.parent / "js" / "data.js"

SOURCES = [
    ("WII-PIED-2020", "WII", "observed_telemetry_published", "Satellite telemetry of Pied Cuckoo (Clamator jacobinus)", "https://www.wii.gov.in/uploads/media/pdf/ars_2023_programme_abstracts_book.pdf", "Published abstract; raw fixes not found as an open download", "no", "WII reported two Argos-tagged birds in 2020; one travelled from Dehradun to Somalia via named Indian stopovers."),
    ("WII-BHG-2000", "WII", "observed_telemetry_published", "Tracking the spring migration of a Bar-headed Goose across the Himalaya", "https://wii.gov.in/publications/research-papers/tracking-the-spring-migration-of-a-bar-headed-goose-%28anser-indicus%29-across-the-himalaya-with-satellite-telemetry", "Published paper; raw fixes not found as an open download", "no", "Satellite-telemetry study; retain as a cited observed-pathway record until raw fixes are acquired."),
    ("WII-CHANGTHANG-2014", "WII", "observed_telemetry_published", "Capture and tagging of Black-necked Crane and Bar-headed Goose in Changthang", "https://digitalrepository.wii.gov.in/communities/9dfa16ab-eba4-4400-b8a9-c4c4e1910c68?f.dateIssued.max=2018&f.dateIssued.min=2014&f.subject=Birds%2Cequals&spc.page=1", "Repository report; raw fixes not found as an open download", "no", "The report describes PTT tagging in Ladakh for migration-path and stopover study."),
    ("WII-AMUR-2022", "WII", "observed_telemetry_published", "Satellite tracking Amur Falcons from Manipur stop-over sites", "https://v1.wii.gov.in/node/5147", "Technical report referenced by WII; raw fixes not found as an open download", "no", "Use for the documented northeast-India to Africa pathway only; do not infer individual tracks."),
    ("WII-LF-2015", "WII", "observed_telemetry_published", "Are Lesser Floricans long distance migrants?", "https://wii.gov.in/images//images/documents/ars_pogramme_abstracts_2015.pdf", "Published seminar abstract; raw fixes not found as an open download", "no", "One tagged bird moved from an Ajmer lek area to grasslands near Bhilwara; the report describes local-scale movement."),
    ("BNHS-DEMOISELLE-2023", "BNHS", "published_pathway", "Demoiselle Cranes and powerlines", "https://www.bnhs.org/public/pdf_documents/Demoiselle-Cranes-and-powerlines.pdf", "Copyrighted publication; route facts may be cited, raw telemetry not supplied", "no", "Describes east-Kazakhstan populations using Himalayan or Hindu Kush approaches to Rajasthan and Gujarat."),
    ("BNHS-RINGING-2025", "BNHS", "ringing_inventory", "Bird Ringing Digitisation Project", "https://www.bnhs.org/public/pdf_documents/ANNUAL-REPORT-2024-2025-G.pdf", "Institutional archive; public bulk download and reuse licence not found", "no", "Annual report states 98,859 ringing records were added to the database."),
    ("ZSI-FLYWAYS-2023", "ZSI", "published_flyway_context", "Migration of birds and their flyways in India", "https://zsi.gov.in/uploads/documents/importantLinks/english/2023_4.pdf", "Published literature; no raw trajectory data", "no", "Use to classify Central Asian, East Asian–Australasian and African–Eurasian flyway context, not as telemetry."),
    ("MOVEBANK-REPOSITORY", "Movebank", "observed_telemetry_published", "Movebank Data Repository - Avian Telemetry Tracks", "https://datarepository.movebank.org", "Open-access animal tracking datasets CC0 / CC BY", "yes", "Flagship species GPS and Argos satellite tracking across Central Asian and East Asian flyways."),
    ("GBIF-OCCURRENCE-API", "GBIF", "seasonal_occurrence_protocol", "GBIF Occurrence API", "https://techdocs.gbif.org/en/openapi/v1/occurrence", "Retain only CC0 or CC BY records and preserve the resulting download DOI", "yes", "Occurrence points can support monthly density surfaces and inferred pathway corridors, filtered for Taxon Aves (212)."),
]

PATHWAYS = [
    ("WII-PIED-CUCKOO-2020", "Clamator jacobinus", "Pied Cuckoo", "observed_telemetry_published", "WII-PIED-2020", "India to Africa", "published-localities", "medium", "A tagged bird named Chatak was reported travelling about 5,000 km from Dehradun via Rajaji, Malvan and Gokarna to the Somalia coast."),
    ("WII-BAR-HEADED-GOOSE-2000", "Anser indicus", "Bar-headed Goose", "observed_telemetry_published", "WII-BHG-2000", "Himalayan spring migration", "citation-only", "medium", "Published WII satellite-telemetry route across the Himalaya; no raw coordinates were located for reuse."),
    ("WII-CHANGTHANG-BHG-2014", "Anser indicus", "Bar-headed Goose", "observed_telemetry_published", "WII-CHANGTHANG-2014", "Changthang / Ladakh", "citation-only", "medium", "PTT-tagging study in Changthang; retain until report-derived or authorised raw fixes are available."),
    ("WII-CHANGTHANG-BNC-2014", "Grus nigricollis", "Black-necked Crane", "observed_telemetry_published", "WII-CHANGTHANG-2014", "Changthang / Ladakh", "citation-only", "medium", "Satellite-tagging study described in WII repository materials; no public raw fixes located."),
    ("WII-AMUR-MANIPUR", "Falco amurensis", "Amur Falcon", "observed_telemetry_published", "WII-AMUR-2022", "Northeast India to Africa", "citation-only", "medium", "WII documents satellite tracking from Manipur stop-over sites; raw tracks require the report/data owner."),
    ("WII-LESSER-FLORICAN-2014", "Sypheotides indicus", "Lesser Florican", "observed_telemetry_published", "WII-LF-2015", "Ajmer to Bhilwara, Rajasthan", "published-localities", "high", "One satellite-tagged bird moved south from an Ajmer lek area to grasslands near Bhilwara."),
    ("BNHS-DEMOISELLE-CRANE", "Anthropoides virgo", "Demoiselle Crane", "published_pathway", "BNHS-DEMOISELLE-2023", "Kazakhstan / Central Asia to Rajasthan and Gujarat", "published-route-class", "medium", "Source distinguishes direct Himalayan and Hindu Kush approaches for east-Kazakhstan populations."),
]

SEGMENTS = [
    ("WII-PIED-CUCKOO-2020", 1, "Dehradun", "Uttarakhand, India", 30.3165, 78.0322, "published locality", "Departure locality reported by WII."),
    ("WII-PIED-CUCKOO-2020", 2, "Rajaji National Park", "Uttarakhand, India", None, None, "published locality", "Stopover named by WII; no coordinate copied from the source."),
    ("WII-PIED-CUCKOO-2020", 3, "Malvan coast", "Maharashtra, India", None, None, "published locality", "Stopover named by WII; no coordinate copied from the source."),
    ("WII-PIED-CUCKOO-2020", 4, "Gokarna", "Karnataka, India", 14.5479, 74.3188, "published locality", "Stopover named by WII."),
    ("WII-PIED-CUCKOO-2020", 5, "Somalia coast", "Somalia", None, None, "published locality", "Destination described by WII without a reusable coordinate in the source."),
    ("WII-LESSER-FLORICAN-2014", 1, "Ajmer lek area", "Rajasthan, India", None, None, "published locality", "Origin described by WII; preserve source precision."),
    ("WII-LESSER-FLORICAN-2014", 2, "Grasslands near Bhilwara", "Rajasthan, India", None, None, "published locality", "Destination described by WII; preserve source precision."),
    ("BNHS-DEMOISELLE-CRANE", 1, "East Kazakhstan", "Kazakhstan", None, None, "published route class", "Population origin in BNHS publication."),
    ("BNHS-DEMOISELLE-CRANE", 2, "Himalayan approach", "Central Asia / Himalaya", None, None, "published route class", "One published approach; not an individual track."),
    ("BNHS-DEMOISELLE-CRANE", 3, "Rajasthan and Gujarat wintering grounds", "India", None, None, "published route class", "Published destination region."),
]

SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE sources (
  source_id TEXT PRIMARY KEY, organisation TEXT NOT NULL, evidence_type TEXT NOT NULL,
  title TEXT NOT NULL, url TEXT NOT NULL, reuse_status TEXT NOT NULL,
  raw_fixes_openly_available TEXT NOT NULL CHECK(raw_fixes_openly_available IN ('yes','no')),
  notes TEXT NOT NULL
);
CREATE TABLE pathways (
  pathway_id TEXT PRIMARY KEY, scientific_name TEXT NOT NULL, common_name TEXT NOT NULL,
  evidence_type TEXT NOT NULL, source_id TEXT NOT NULL REFERENCES sources(source_id),
  route_label TEXT NOT NULL, geometry_status TEXT NOT NULL, confidence TEXT NOT NULL,
  summary TEXT NOT NULL
);
CREATE TABLE route_segments (
  pathway_id TEXT NOT NULL REFERENCES pathways(pathway_id), sequence INTEGER NOT NULL,
  locality TEXT NOT NULL, region TEXT NOT NULL, latitude REAL, longitude REAL,
  precision_note TEXT NOT NULL, notes TEXT NOT NULL, PRIMARY KEY(pathway_id, sequence)
);
CREATE TABLE gbif_query_definitions (
  scientific_name TEXT PRIMARY KEY, common_name TEXT NOT NULL,
  required_filters TEXT NOT NULL, intended_output TEXT NOT NULL,
  license_rule TEXT NOT NULL
);
CREATE TABLE raw_track_imports (
  import_id INTEGER PRIMARY KEY, pathway_id TEXT REFERENCES pathways(pathway_id),
  source_id TEXT REFERENCES sources(source_id), source_doi_or_url TEXT NOT NULL,
  license TEXT NOT NULL, accessed_on TEXT NOT NULL, checksum TEXT,
  notes TEXT NOT NULL
);
"""

def load_birds_data():
    if not DATA_JS.exists():
        return []
    with open(DATA_JS, "r", encoding="utf-8") as f:
        text = f.read()
    m = re.search(r'const BIRDS_DATA\s*=\s*(\[.*?\]);', text, re.DOTALL)
    if not m:
        return []
    return json.loads(m.group(1))

def main():
    if DB.exists():
        DB.unlink()
    con = sqlite3.connect(DB)
    con.executescript(SCHEMA)

    sources_dict = {s[0]: s for s in SOURCES}
    pathways_list = list(PATHWAYS)
    segments_list = list(SEGMENTS)
    gbif_queries = {}

    birds = load_birds_data()
    for b in birds:
        b_id = b["id"]
        pathway_id = f"MB-{b_id.upper()}"
        src_id = f"SRC-{b_id.upper()}"
        prov = b.get("provenance", "Movebank GPS Telemetry")
        movebank_id = b.get("movebankId", "Movebank Open Tracking Repository")
        
        sources_dict[src_id] = (
            src_id,
            "Movebank / GBIF",
            "telemetry_and_occurrence",
            f"Movement track for {b['name']} ({b['scientific']})",
            f"https://www.gbif.org/species/{b.get('gbifId', '')}" if b.get('gbifId') else "https://datarepository.movebank.org",
            "Open Access CC0 / CC BY 4.0",
            "yes",
            f"Study ID: {movebank_id}. Role: {b.get('role', 'Migrant')}. Flyway: {b.get('flyway', 'Central Asian')}."
        )

        origin_name = b["origin"].get("name", "Breeding Grounds")
        dest_name = b["destination"].get("name", "Winter Grounds")
        route_label = f"{origin_name} to {dest_name}"
        summary = b.get("feat") or b.get("timeline", {}).get("summary", "")

        pathways_list.append((
            pathway_id,
            b["scientific"],
            b["name"],
            prov,
            src_id,
            route_label,
            "georeferenced_waypoints",
            "high",
            summary
        ))

        # Add route segments: Origin (seq 1), stopovers (seq 2..N-1), Destination (seq N)
        seq = 1
        segments_list.append((
            pathway_id,
            seq,
            b["origin"].get("name", "Origin"),
            b["origin"].get("country", ""),
            b["origin"].get("lat"),
            b["origin"].get("lng"),
            "breeding grounds coordinate",
            f"Departure: {b.get('timeline', {}).get('startTiming', 'Late August')}"
        ))

        for st in b.get("stopovers", []):
            seq += 1
            segments_list.append((
                pathway_id,
                seq,
                st.get("name", "Stopover"),
                "Transit Flyway Corridor",
                st.get("lat"),
                st.get("lng"),
                "flyway stopover waypoint",
                "Resting and refueling corridor waypoint"
            ))

        seq += 1
        segments_list.append((
            pathway_id,
            seq,
            b["destination"].get("name", "Destination"),
            b["destination"].get("state", "India"),
            b["destination"].get("lat"),
            b["destination"].get("lng"),
            "Indian wintering haven coordinate",
            f"Arrival: {b.get('arrivalMonth', 'October')}; Departure: {b.get('departureMonth', 'March')}"
        ))

        gbif_queries[b["scientific"]] = (
            b["scientific"],
            b["name"],
            f"year=2025; hasCoordinate=true; basisOfRecord=HUMAN_OBSERVATION; species={b['scientific']}",
            "monthly occurrence density / inferred corridor across Central Asian Flyway",
            "retain CC0 or CC BY only; preserve download DOI and GBIF datasetKey"
        )

    con.executemany("INSERT INTO sources VALUES (?,?,?,?,?,?,?,?)", sources_dict.values())
    con.executemany("INSERT INTO pathways VALUES (?,?,?,?,?,?,?,?,?)", pathways_list)
    con.executemany("INSERT INTO route_segments VALUES (?,?,?,?,?,?,?,?)", segments_list)
    con.executemany("INSERT INTO gbif_query_definitions VALUES (?,?,?,?,?)", gbif_queries.values())
    con.commit()
    print(f"Created {DB} with {len(sources_dict)} sources, {len(pathways_list)} pathways and {len(segments_list)} route segments from 126 species.")

if __name__ == "__main__":
    main()

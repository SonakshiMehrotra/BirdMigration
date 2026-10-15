# 🦅 Visualising Bird Migration in India

An interactive, high-precision geospatial visualization atlas tracking the trans-continental flyways, seasonal journeys, and wintering networks of **126 migratory bird species** visiting the Indian subcontinent.

Built with **D3.js (v7)**, **Canvas animations**, **TopoJSON/GeoJSON**, and verified against open ornithological telemetry and biodiversity occurrence repositories.

---

## 🌟 Key Features

- **Multi-Species Geospatial Animation**:
  - Live animated flock trajectories illustrating synchronized migrations across the **Central Asian Flyway (CAF)**, **East Asian–Australasian Flyway (EAAF)**, and **Trans-Continental / Oceanic Corridors**.
  - Toggle between global flock movements across all 126 species or isolate an individual bird's precise trajectory.
  - Interactive playback control with a 12-month seasonal scrubber (January to December).

- **Rich Species Knowledge Panel**:
  - Taxonomic metadata (Common & Scientific names, Family, Group, IUCN Red List status).
  - Telemetry provenance (Movebank Study ID, research institution, or literature citations).
  - Migratory metrics (distance in kilometers, peak flight altitudes up to 7,290 m, flyway classification).
  - Real-time **GBIF Occurrence API** integration fetching live 2025 georeferenced records.

- **Primary Gateways & Dispersal Havens Network**:
  - Visualizes India's network of **23 premier bird sanctuaries and Ramsar wetland sites** (e.g., Keoladeo Ghana, Chilika Lake, Great Rann of Kutch, Pong Dam, Point Calimere, Doyang Reservoir).
  - Dotted dispersal vectors connecting primary staging gateways with secondary regional wintering havens.
  - Interactive haven spotlighting and smooth map pan/zoom.

- **Group & Taxonomy Filtering**:
  - Filter across 8 distinct avian groups: *Waterfowl*, *Waders*, *Raptors*, *Songbirds*, *Cranes & Storks*, *Seabirds*, *Flamingos & Pelicans*, and *Monsoon Migrants*.
  - Full-text search across common and scientific names.

---

## 🔬 Scientific Data Sources & Provenance

Every route, haven, and timeline in this project is anchored in open scientific literature and biodiversity tracking databases:

1. **Movebank Data Repository**:
   - Flagship open-access GPS and Argos satellite tracking studies (e.g. Hawkes et al. Trans-Himalayan *Bar-headed Goose* flights, WII & CMS *Amur Falcon* satellite tracking).
2. **Global Biodiversity Information Facility (GBIF)**:
   - Georeferenced occurrence records for *Taxon: Aves (212)* published under open CC0 and CC BY licenses.
3. **Institutional Research & Literature**:
   - **Wildlife Institute of India (WII)**: Published telemetry monographs and ringing reports for *Pied Cuckoo*, *Bar-headed Goose*, *Black-necked Crane*, and *Lesser Florican*.
   - **Bombay Natural History Society (BNHS)**: Historical Indian bird ringing inventories and flyway banding recoveries.
   - **Zoological Survey of India (ZSI)**: Flyway classification literature across the Indian subcontinent.
4. **Conservation Status**:
   - Evaluated against the **IUCN Red List of Threatened Species (v2024-2)**.
5. **Wetland & Sanctuary GIS Boundaries**:
   - Boundaries and coordinates verified against the **Ministry of Environment, Forest and Climate Change (MoEFCC) National Wetland Atlas** and **Ramsar Sites Information Service (RSIS)**.

---

## 🚀 Quick Start

The application is completely static (HTML5, Vanilla CSS, and JavaScript). It requires no build tools, compilers, or external backend servers.

## 📁 Project Structure

```
├── index.html                 # Main web application & interactive canvas UI
├── js/
│   ├── data.js                # Catalog of 126 migratory species with coordinates & timelines
│   ├── india_shapefile.js     # GeoJSON polygons for India state boundaries
│   └── sanctuaries.js         # Coordinates and metadata for 23 Indian bird sanctuaries
├── data/
│   ├── india_states.geojson   # Raw state boundary GeoJSON
│   └── india_states_rewound.geojson
├── database/
│   ├── build_migration_db.py  # Python pipeline compiling provenance into SQLite
│   ├── india_bird_migration.sqlite # Provenance-first research evidence database
│   └── README.md              # Evidence labeling & GBIF ingestion protocol
├── .gitignore                 # Standard exclusions (OS artifacts, caches)
└── README.md                  # Project documentation & reference
```

---

## 📄 License & Attribution

- **Code**: Released under the [MIT License](LICENSE).
- **Cartographic Data**: Derived from Natural Earth and Survey of India public boundary data.
- **Occurrence & Telemetry Data**: Attributed to respective study authors via Movebank and GBIF under CC0 / CC-BY 4.0.

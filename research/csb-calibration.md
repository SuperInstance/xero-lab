# CSB calibration — crowdsourced bathymetry trust practice (brief)

*Xero Research Library · 2026-10-12 · Brief by design — deep bathy
work lives in the OpenSky Terrain / Z-lane, not here.*
*Addition-layer framing: a borrowed practice Zero may call on —
the practice is not part of Zero.*

## What this backs

Casey's trust ladder (see `nuggets.md`): data is ranked by how well
you know its calibration — live reading from your own calibrated
sounder > your own recorded marks > fleet-shared soundings > official
vector chart (ENC) > static raster chart. IHO crowdsourced
bathymetry (CSB) practice is the institutional version of the same
idea, and it has a guidance document: **IHO Publication B-12,
Guidance on Crowdsourced Bathymetry** (Ed. 2.0.0, 2019; a newer
edition is in preparation).

## The B-12 model in five points

1. **Trusted Nodes are the unit of trust.** Individual mariners don't
   feed the archive directly; data flows through vetted Trusted
   Nodes to the IHO Data Centre for Digital Bathymetry (DCDB,
   hosted by NOAA NCEI). A Trusted Node is onboarded deliberately:
   sample file reviewed, formats agreed, credentials issued.
2. **Provenance is mandatory metadata.** Contributors get a uniqueID
   (contributor prefix + UUID, normally one per vessel). Mandatory
   metadata from Trusted Nodes covers vessel and **sensor
   configuration** — including the transducer's position/offset
   relative to the GNSS antenna and the waterline. A sounding without
   its geometry is worth less, and B-12 says so structurally.
3. **Uncertainty is a first-class section** (B-12 §4): depth data
   must carry an understanding of its error budget — sensor,
   installation offsets, water level, motion — rather than a bare
   number.
4. **Trusted Nodes calibrate the fleet.** Per the IHO CSB Cookbook,
   nodes can cross-check datasets against each other and against
   authoritative surveys, estimate and remove biases, **cross-
   calibrate one vessel's data using a well-calibrated vessel in the
   same area**, establish per-collector calibration and uncertainty
   histories (which also reveal instrument changes over time), and
   work with harbour authorities to establish known-depth areas
   where individual sounders can be calibrated.
5. **Trust is earned and tracked per source**, not granted to the
   dataset as a whole: a collector's history becomes part of the
   metadata that downstream users rely on.

Sources:
- IHO CSB Cookbook / guidance (Trusted Node uncertainty, cross-calibration): https://iho.int/mtg_docs/com_wg/CSBWG/CSBWG_Misc/CSB-Guidance_Document-Edition_1.0.0-Clean.pdf
- B-12 Ed. 2.0.2 (2019) full text: https://legacy.iho.int/iho_pubs/bathy/B_12_Ed2.0.2_2019.pdf
- B-12 current-edition preview (structure, DCDB, Trusted Nodes): https://metanorma.github.io/mn-samples-iho/documents/b12/document.html

## Mapping to the zero-agent trust ladder

| Casey | IHO analogue |
|---|---|
| Know your own sounder's calibration | Sensor-configuration metadata; known-depth calibration areas |
| Fleet marks trusted less than your own | Per-collector calibration/uncertainty history at the Trusted Node |
| Someone else's weird sounder day poisons their marks | Cross-checks between datasets; bias detection by the node |
| Static raster = dead language, for naming | Authoritative chart = reference frame, not live truth |

The pattern worth stealing: **never strip provenance to make data
uniform.** The offset, the instrument, the day, and the source's
track record travel with the sounding — because the trust decision
happens at read time, per user, per purpose.

## Open questions

- Should a Xero fleet treat its coordinator as a Trusted Node in the
  B-12 sense (vetting, cross-calibration, per-source histories), or
  is that over-formalizing a three-boat fleet?
- B-12's newer edition (in preparation as of the 2025 working-group
  materials): what changes for small contributors? UNVERIFIED — check
  iho.int before relying on edition-specific clauses.

*Status: brief, high confidence on the model; edition details move.*

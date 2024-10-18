# AVAIL Road Network Resilience Analysis (Technical Documentation)

## Network Centrality - AADT Comparison

### Process

1. OSM extracts

   1. Geographic Region (e.g. Albany County)
   1. Road Network
   1. Using [osmosis](https://github.com/openstreetmap/osmosis/blob/main/doc/detailed-usage.adoc)
      1. https://github.com/openstreetmap/osmosis
      1. https://wiki.openstreetmap.org/wiki/Osmosis

1. OSM Extract fed to OSRM

   1. https://github.com/Project-OSRM/osrm-backend?tab=readme-ov-file#using-docker
   1. https://github.com/project-osrm/osrm-backend/pkgs/container/osrm-backend

1. OSM Road Network

   1. https://pyrosm.readthedocs.io/en/latest/basics.html?highlight=osmnx#export-to-networkx-osmnx

1. NYSDOT RIS LRSN Milepoint Network LRSN_Milepoints Layer

   1. Route geometry sent to OSRM Matching.

1. OSRM Matching results enhanced by JOINing with OSM NetworkX [MutliDiGraph](https://networkx.org/documentation/stable/reference/classes/multidigraph.html)

   1. This enables further higher-level deductions in deciding map matchings.
      1. As the network analysis capabilities of this network analysis system are enhanced,
         those same capabilities can be used to improve map matching.

1. OSMnx Simplified Network.

   1. https://osmnx.readthedocs.io/en/stable/user-reference.html#osmnx.simplification.simplify_graph
   1. https://github.com/gboeing/osmnx-examples

1. RIS Route attributes joined to OSMnx Simplified Network

1. NetworkX Edge Betweenness Centrality calculated on OSMnx Simplified Network using enhanced OSRM Matching results.

   1. https://m.youtube.com/watch?v=0CCrq62TF7U
   1. https://en.wikipedia.org/wiki/Betweenness_centrality
   1. https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.centrality.edge_betweenness_centrality.html#networkx.algorithms.centrality.edge_betweenness_centrality

1. Results output to GPKG and CSV.
   1. https://geopandas.org/en/stable/docs/user_guide/io.html

## Concerns with using Network Centrality to identify critical road segments.

1. Sensitive to partitioning.

   1. Computing network centrality is very time expensive.
   1. Reducing the problem size involves partitioning the road network.
   1. Partitions introduce artificial dead ends (even where interstates meet the partition boundary).
      1. The network centrality of a dead end is zero.

1. Network flow capacity?

   1. How to model edge flow capacity?
      1. This is what is really important.
         1. How effectively can traffic flow through the network edge?
      1. AADT is observed network flow.

1. Ports and Railroad terminals.

   1. These are critical locations in the transportation network.
      1. Simple road network analysis will treat them as dead ends.
   1. Hypothesis: Truck AADT will show the importance of the roads to/from these locations.

## Concerns with AADT

1. Not all roads have AADT measure.

   1. The existence of AADT measures indicate that the roadway is considered important by DOT planners.

      1. A decision was made to allocate resources to collecting traffic counts.

         1. Not all roadways are allocated such resources.

      1. Using AADT to determine network importance introduces a bit of circularity:
         A roadway must first be deemed important to get the data that "impartial" analysis uses to determine importance.

   1. There may exist routes of unplanned network importance.
      1. Do we want to account for this phenomenon?
      1. Network Analysis Tools (especially routing engines) can discover such unplanned, high centrality, routes.
      1. Planned vs Emergent route hierarchy
         1. https://www.thedrive.com/news/communities-are-telling-waze-to-stop-sending-traffic-through-them
         1. https://www.streetlightdata.com/waze-traffic-effect-4-steps-for-neighborhoods-cities-to-fight-back/
         1. https://www.quora.com/How-do-I-stop-Waze-from-routing-in-my-neighborhood
         1. https://support.google.com/waze/thread/209392463/how-do-i-get-waze-to-remove-shortcut-through-my-neighborhood?hl=en
         1. https://www.govtech.com/fs/la-considers-legal-action-to-stop-waze-from-routing-commuters-through-neighborhoods.html

## "Bridge Edges" are not captured in Network Centrality nor AADT

1. Relative importance to community

   1. What if removing network edge(s) completely isolates a village community?

      1. Consider a village connected to the larger road network by a minor collector.

         1. Further consider that the minor collector crosses waterways on the outskirts of the village.
         1. A flood may completely isolate the village.

      1. If that village is smaller, the edge may have low relative AADT but the residents will be completely isolated.
         1. The potential for complete isolation of smaller communities must be considered.

   1. Possible network analysis approach:
      1. Look for "Bridge Edges" where if the edge is removed, you get isolated components.
         1. https://en.wikipedia.org/wiki/Bridge_(graph_theory)
         1. https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.connectivity.cuts.minimum_edge_cut.html

## Map Matching (Conflation of OSM and NYSDOT Roadway Inventory System)

Hidden Markov Map Matching is the gold standard algorithm used by nearly all tools:

1. https://www.microsoft.com/en-us/research/publication/hidden-markov-map-matching-noise-sparseness/

From [Open source map matching with Markov decision processes: A new method and a detailed benchmark with existing approaches by Adrian Wöltche](https://onlinelibrary.wiley.com/doi/epdf/10.1111/tgis.13107)

> The research field of map matching for addressing this issue has a long and
> comprehensive history. Early approaches from around 1994 to 2005 used simple
> point-to-curve and curve-to-curve (Bernstein & Kornhauser, 1996;White et al., 2000)
> map matching algorithms. Also, Discrete Fréchet Distance (Eiter & Mannila, 1994)
> and FreeSpace Diagrams (Alt et al., 2003) were applied in geometric
> curve-to-curve matching (Brakatsoulas et al., 2005). Amajor issue of these
> historic approaches is that outliers (i.e., measurement errors) and the typical
> noise of GNSS-recorded tracks cannot be resolved accurately. The matches
> therefore were mostly inaccurate, except when the GNSS track fitted the
> underlying road network very precisely already. The lack of accuracy is also one
> of the conclusions of the most prominent map matching survey of that decade in
> Quddus et al. (2007), which gives a good overview of the historic map matching
> approaches. At that time, new technologies were demanded to address these
> inaccuracies.
>
> Shortly thereafter, a major breakthrough was achieved in Newson and Krumm(2009)
> by applying a stochastic method based on Hidden Markov Models (HMMs) and the
> Viterbi algorithm (Forney, 1973; Viterbi, 1967)in the domain of map matching. It
> was inspired by Krumm et al. (2007) and Hummel (2006). The basic idea was that
> each GNSS measurement represents an observation in the HMM and that for each
> observation there exist multiple potential road positions, the hidden states.
> “Hidden,” since the real position is unknown. Each pair of hidden state and
> observation has an observation probability calculated from the distance
> between the measurement and the road position. In addition, each pair of adjacent
> hidden states has a transition probability calculated from the routing distance
> between the assigned road positions. The Viterbi algorithms a dynamic
> programming algorithm that finds an optimal sequence of hidden states (i.e.,
> road positions) by maximizing over the multiplication of all observation and
> transition probabilities. This approach is able to deal with the uncertainty of
> map matching as it weights and compares various alternating paths before it
> select the final match.To date, it is the state-of-the-art in map matching,
> which can be seen in all the following current open source tools all originally
> based on Newson and Krumm (2009), sometimes with further enhancements, for
> example,Barefoot (https://github.com/bmwcarit/barefoot) (Louail et al., 2014),
> Fast map matching (https://github.com/cyang -kth/fmm) (FMM) (Yang & Gidófalvi,
> 2018), Map Matching based on GraphHopper
> (https://github.com/graphhopper/graphhopper#map-matching), Open Source Routing
> Machine (https://github.com/Project-OSRM/osrm- backend) (OSRM) (Luxen & Vetter,
> 2011), Valhalla (https://github.com/valhalla/valhalla), and pgMapMatch
> (https://github.com/amillb/pgMapMatch) (Millard-Ball et al., 2019). A notable exception
> in FMM is that it also implements an earlier method called ST-Match (Lou et al., 2009)
> which is a simpler stochastic model compared toHMMs for faster matching of
> large tracks.
>
> Barefoot, FMM, and pgMapMatch are three tools explicitly designed for map
> matching, whereasGraphHopper, OSRM, and Valhalla are designed as general-purpose
> routing frameworks with a map matching implementation as an additional algorithm
> on top. There are also differences in the used programming languages and
> interfaces. Table 1 gives an overview of these state-of-the-art OSS tools and
> our own novel implementation“Map Matching 2”.F I G U R E 3 Didactic example of a
> correctly matched track. The red recorded measurements are matched to the most
> probable road positions (i.e., candidates, marked by green cross-marks). This
> leads to the lightblue line showing the correctly matched route.

### OSRM

We are currently use OSRM Matching.

1. https://ieeexplore.ieee.org/abstract/document/9333085
1. https://project-osrm.org/docs/v5.22.0/api/#match-service
1. https://github.com/Telenav/open-source-spec/tree/master/osrm
   1. https://github.com/Telenav/open-source-spec/blob/master/osrm/doc/osrm_mapmatching.md

This is an aside. We may be able to use the OSRM travel time matrix or tileset to improve
edge weighting when calculating road network node or edge centrality.

1. https://typeset.io/questions/what-is-the-osrm-open-source-routing-machine-algorithm-used-2s8a1twfrg

### Map Matching Alternatives

These all appear to primarily use Hidden Markov Models Matching, so I wouldn't expect to see much difference in results.

1. https://github.com/bmwcarit/barefoot
1. https://github.com/graphhopper/graphhopper
1. https://valhalla.github.io/valhalla/meili/overview/
   1. https://valhalla.github.io/valhalla/meili/algorithms/
1. https://github.com/cyang-kth/fmm
   1. https://fmm-wiki.github.io/
   1. https://www.tandfonline.com/doi/abs/10.1080/13658816.2017.1400548?journalCode=tgis20
   1. https://dl.acm.org/doi/abs/10.1145/1653771.1653820
1. https://github.com/amillb/pgMapMatch

### Data Documentation

1. Road Class
   1. https://download.tomtom.com/open/banners/openlr-whitepaper_v1.5.pdf
   1. https://openlr-python.readthedocs.io/en/latest/reference.html
   1. https://github.com/Mappy/PyLR/tree/master
   1. https://github.com/sharedstreets/sharedstreets-builder/blob/a554983e96010d32b71d7d23504fa88c6fbbad10/src/main/java/io/sharedstreets/tools/builder/osm/model/Way.java

### Currently using these OSM Libraries

1. [osmosis](https://github.com/openstreetmap/osmosis/blob/main/doc/detailed-usage.adoc)

   Used for extracting subnetworks from OSM

   - Geographic Regions
   - Roadway Only Network (no footpaths, etc)

   1. https://github.com/openstreetmap/osmosis
   1. https://wiki.openstreetmap.org/wiki/Osmosis

1. [Pyrosm](https://pyrosm.readthedocs.io/en/latest/index.html)

   > Pyrosm is a Python library for reading OpenStreetMap from Protocol buffer Binary
   > Format -files (\*.osm.pbf) into Geopandas GeoDataFrames. Pyrosm makes it easy to
   > extract various datasets from OpenStreetMap pbf-dumps including e.g. road
   > networks, buildings, Points of Interest (POI), landuse, natural elements,
   > administrative boundaries and much more. Fully customized queries are supported
   > which makes it possible to parse any kind of data from OSM, even with more
   > specific filters.
   >
   > Pyrosm is easy to use and it provides a somewhat similar user interface as
   > OSMnx. The main difference between pyrosm and OSMnx is that OSMnx reads the data
   > using an OverPass API, whereas pyrosm reads the data from local OSM data dumps
   > that are downloaded from the PBF data providers (Geofabrik, BBBike). This makes
   > it possible to parse OSM data faster and make it more feasible to extract data
   > covering large regions.

1. [OSMnx](https://osmnx.readthedocs.io/en/stable/index.html)

   > OSMnx is a Python package to easily download, model, analyze, and visualize
   > street networks and other geospatial features from OpenStreetMap. You can
   > download and model walking, driving, or biking networks with a single line of
   > code then analyze and visualize them. You can just as easily work with urban
   > amenities/points of interest, building footprints, transit stops, elevation
   > data, street orientations, speed/travel time, and routing.

1. https://osmcode.org/pyosmium/

   1. https://github.com/osmcode/pyosmium

### Further Road Network Analysis

#### OSM

1. https://github.com/nilsnolde/routingpy/

   > One lib to route them all - routingpy is a Python 3 client for several popular routing webservices.
   >
   > Inspired by geopy and its great community of contributors, routingpy enables
   > easy and consistent access to third-party spatial webservices to request route
   > directions, isochrones or time-distance matrices.
   >
   > routingpy currently includes support for the following services:
   >
   > - Mapbox, OSRM
   > - Openrouteservice
   > - Here Maps
   > - Google Maps
   > - Graphhopper
   > - OpenTripPlannerV2
   > - Local Valhalla
   > - Local OSRM

#### Graph Databases

These may become necessary as we scale up our analysis and replicate existing research.

1. https://age.apache.org/

   1. https://github.com/apache/age

1. https://pgrouting.org/

1. https://kuzudb.com/

   1. https://github.com/kuzudb/kuzu

1. https://neo4j.com/

#### GTFS

1. https://gtfs.org/resources/gtfs/

1. https://mrcagney.github.io/gtfs_kit_docs/index.html#

   1. https://github.com/mrcagney/gtfs_kit

1. https://gtfs.org/documentation/realtime/language-bindings/python/

   1. https://github.com/MobilityData/gtfs-realtime-bindings

1. https://medium.com/analytics-vidhya/the-hitchhikers-guide-to-gtfs-with-python-e9790090952a

### The Case for Reimplemting Map Conflation Within This Project

Coupling this project with the AVAIL's map conflation work has multiple benefits.

Firstly, it is a stated goal of the larger Road Network Reliability proposal
to contribute a research tool to disaster and transportation planning communities.
Providing a single tool that will enable end-to-end processing from source GIS files,
through geospatial and network theory algorithms, to exploratory tools and generated
reports will make for a much more valuable community contribution. A single
interface with fully automated processes is preferable to multiple interfaces
requiring human orchestration of their respective processes.

Additionally, the previous AVAIL Map Conflation project hit a wall with
higher-level graph analysis. The previous version was written in JavaScript (JS).
The JS community has very limited spatial and graph analysis tools. In JS, we
needed to implement the most basic geospatial and network analysis algorithms
from scratch. This contributed greatly to project complexity and made
implementing even relatively simple algorithms prohibitively costly, thus
reducing the quality of the conflation output.

The greater ease and simplicity gained from a rich ecosystem of existing tooling
will translate into a final product of much greater value to researchers outside
AVAIL. The final product will be much more reliable as it will be built upon
battle-tested and widely-used research community standard tools. Reimplementing
existing tools isolates projects and thereby forsakes the value belonging to
communities adds. Furthermore, maximizing the degree to which we build upon
tools with established reputations will allow outside researchers to use our
contribution with greater confidence. Plainly, as much as possible, we must
embed our work within existing community works and maximize the
[Network Effect](https://en.wikipedia.org/wiki/Network_effect).

Code is liability, whereas well-established and heavily supported community
projects are assets. Joining this project to the rich Python geospatial and
graph analysis ecosystem has already enabled us to replace thousands of lines of
code in the previous JS implementation with a single line library function call.
The difference in ease of use and simplicity is incomparable and cannot be
overstated. A sample of the Python community's spatial and graph analysis tools
are listed throughout this document.

I cannot stress enough that we've just scratched the surface here. I am certain
that going forward we will make dramatic improvements over previous conflation
results. Hidden Markov Map Matching (HMMM) uses relatively low-level
deductions, focusing on a single sequence of coordinates at a time. With more
sophisticated graph analysis tools, we can model how routes connect into
higher-level network structures and then use these models to improve the
individual HMMM results. Ultimately, map matching is a decision making problem,
data science yields better decisions, and Python is the programming language for
data science.

#### Utility for other AVAIL road network analysis code that uses Python

Two existing AVAIL Road Network analysis projects use Python.
They should be able to leverage this codebase as it is further implemented.

1. [excessive_delay](https://github.com/availabs/avail-falcor/tree/master/tasks/excessive_delay)
1. [avl-modeler3](https://github.com/availabs/avl-modeler3/tree/master/server)

### Interesting

1. https://udst.github.io/pandana/

   1. https://github.com/UDST/pandana

1. https://networkx.org/documentation/stable/auto_examples/geospatial/plot_lines.html#graphs-from-a-set-of-lines

1. https://docs.momepy.org/en/stable/

   > Momepy is a library for quantitative analysis of urban form - urban
   > morphometrics. It is part of PySAL (Python Spatial Analysis Library) and is
   > built on top of GeoPandas, other PySAL modules and networkX.

1. https://pysal.org/

   1. https://www.routledge.com/Geographic-Data-Science-with-Python/Rey-Arribas-Bel-Wolf/p/book/9781032445953

1. https://pytorch.org/blog/geospatial-deep-learning-with-torchgeo/

1. https://github.com/conveyal/r5

   > Developed to power Conveyal's web-based interface for scenario planning and
   > land-use/transport accessibility analysis, R5 is our routing engine for
   > multimodal (transit/bike/walk/car) networks with a particular focus on public
   > transit.

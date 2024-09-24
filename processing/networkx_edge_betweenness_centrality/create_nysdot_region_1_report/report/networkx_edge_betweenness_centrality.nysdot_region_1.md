# NetworkX Edge Betweenness Centrality (NYSDOT Region 1)

The following visualizations show the effect of partitioning the road network before running edge betweenness centrality metrics. Road network partitions essentially create artificial boundaries through which no traffic flows, in effect turning all roads at a boundary into dead ends. Therefore, any divide and conquer strategy to reduce the metric computational costs must consider the distortive effects of partitioning the network prior to computation.

Furthermore, when comparing edge betweenness centrality to AADT, it becomes evident that this network metric is not an adequate proxy for actual road network use.

## Albany County

### Tract-Level Edge Betweenness Centrality

#### Census Tracts (Albany County)

![./census_tracts.albany_county.png](./images/census_tracts.albany_county.png)

#### Betweenness Centrality (Albany County, Census Tract-Level)

![./tract_level_centrality.albany_county.png](./images/tract_level_centrality.albany_county.png)

---

### County Subdivision-Level Edge Betweenness Centrality

#### County Subdivisions (Albany County)

![./county_subdivisions.albany_county.png](./images/county_subdivisions.albany_county.png)

#### Betweenness Centrality (Albany County, County Subdivision-Level)

![./county_subdivision_level_centrality.albany_county.png](./images/county_subdivision_level_centrality.albany_county.png)

### County Level Edge Betweenness Centrality

#### Betweenness Centrality (Albany County, County Level)

![./county_level_centrality.albany_county.png](./images/county_level_centrality.albany_county.png)

#### NYSDOT RIS AADT (Albany County)

![./nysdot_ris_aadt.albany_county.png](./images/nysdot_ris_aadt.albany_county.png)

---

## NYSDOT Region 1

### County Subdivision-Level Edge Betweenness Centrality

#### County Subdivisions (NYSDOT Region 1)

![./county_subdivisions.nysdot_region_1.png](./images//county_subdivisions.nysdot_region_1.png)

#### Betweenness Centrality (NYSDOT Region 1, County Subdivision-Level)

![./county_subdivision_level_centrality.nysdot_region_1.png](./images/county_subdivision_level_centrality.nysdot_region_1.png)

### County Level Edge Betweenness Centrality

#### Counties (NYSDOT Region 1)

![./nysdot_region_1_counties.png](./images/nysdot_region_1_counties.png)

#### Betweenness Centrality (NYSDOT Region 1, County Level)

![./county_level_centrality.nysdot_region_1.png](./images/county_level_centrality.nysdot_region_1.png)

#### NYSDOT RIS AADT (NYSDOT Region 1)

![./nysdot_ris_aadt.nysdot_region_1.png](./images/nysdot_ris_aadt.nysdot_region_1.png)

---

## NYS

### State-Level Edge Betweenness Centrality

![./state_level_centrality.png](./images/state_level_centrality.png)

#### NYSDOT RIS AADT (NYS)

![./state_level_nysdot_ris_aadt.png](./images/state_level_nysdot_ris_aadt.png)

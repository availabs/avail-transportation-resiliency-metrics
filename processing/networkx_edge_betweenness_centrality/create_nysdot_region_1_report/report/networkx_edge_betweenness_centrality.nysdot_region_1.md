# NetworkX Edge Betweenness Centrality (NYSDOT Region 1)

## Edge Betweenness Centrality Computational Complexity

The computation time for betweenness centrality does not scale linearly with the road network size. The [computational complexity](https://en.wikipedia.org/wiki/Time_complexity) of this metric is `O(nm + n² log n)` where `n` is the number of nodes and `m` is the number of edges.

Roughly speaking, doubling the size of a network quadruples compututation time, and increasing the network size by a factor of ten consequentially increases run time by at least a factor of a hundred.

### Observed Computation Times vs Theoretical Time Complexity:

![Actual Computation Time](./images/actual_computation_time.png)
![Theoretical Computation Time](./images/theoretical_computation_time.png)

(Note: The road network with observed computation time of 50 hours was Erie County).

Resources:

- [NetworkX Edge Betweenness Centrality](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.centrality.edge_betweenness_centrality.html#rc3df3f41cd0d-1)
- A Faster Algorithm for Betweenness Centrality. Ulrik Brandes, Journal of Mathematical Sociology 25(2):163-177, 2001. https://doi.org/10.1080/0022250X.2001.9990249

### Problems with divide and conquer road network partitioning

Computing betweenness centrality at scale presents the challenge that partitioning the network to run the measure on manageably sized subnetworks dramatically affects the results. Intuitively, road network partitions essentially introduce impassable artificial barriers, in effect turning all roads at partition boundaries into dead ends.

Therefore, any divide and conquer strategy employed to reduce the betweenness centrality metric's computational cost must consider the severe distortive effects of partitioning the network prior to computation.

A viable option for reducing the network work size for large areas is to drop lower level roads. For example, dropping all residential and service roads reduces the state-wide network's size enough to make computation faster than computing the metric for all roads within some larger counties.

It is worth mentioning that, when comparing edge betweenness centrality to AADT, it becomes evident that betweenness centrality metric computed using speedlimits alone is not an adequate proxy for actual road network use even when betweenness centrality is computed for the state-wide network.

The following visualizations show the effect of partitioning the road network to reduce betweenness centrality metric computation costs.

### Albany County

#### Tract Level Edge Betweenness Centrality

##### Census Tracts (Albany County)

![./census_tracts.albany_county.png](./images/census_tracts.albany_county.png)

##### Betweenness Centrality (Albany County, Census Tract Level)

![./tract_level_centrality.albany_county.png](./images/tract_level_centrality.albany_county.png)

---

#### County Subdivision Level Edge Betweenness Centrality

##### County Subdivisions (Albany County)

![./county_subdivisions.albany_county.png](./images/county_subdivisions.albany_county.png)

##### Betweenness Centrality (Albany County, County Subdivision Level)

![./county_subdivision_level_centrality.albany_county.png](./images/county_subdivision_level_centrality.albany_county.png)

#### County Level Edge Betweenness Centrality

##### Betweenness Centrality (Albany County, County Level)

![./county_level_centrality.albany_county.png](./images/county_level_centrality.albany_county.png)

##### NYSDOT RIS AADT (Albany County)

![./nysdot_ris_aadt.albany_county.png](./images/nysdot_ris_aadt.albany_county.png)

---

### NYSDOT Region 1

#### County Subdivision Level Edge Betweenness Centrality

##### County Subdivisions (NYSDOT Region 1)

![./county_subdivisions.nysdot_region_1.png](./images//county_subdivisions.nysdot_region_1.png)

##### Betweenness Centrality (NYSDOT Region 1, County Subdivision Level)

![./county_subdivision_level_centrality.nysdot_region_1.png](./images/county_subdivision_level_centrality.nysdot_region_1.png)

#### County Level Edge Betweenness Centrality

##### Counties (NYSDOT Region 1)

![./nysdot_region_1_counties.png](./images/nysdot_region_1_counties.png)

##### Betweenness Centrality (NYSDOT Region 1, County Level)

![./county_level_centrality.nysdot_region_1.png](./images/county_level_centrality.nysdot_region_1.png)

##### NYSDOT RIS AADT (NYSDOT Region 1)

![./nysdot_ris_aadt.nysdot_region_1.png](./images/nysdot_ris_aadt.nysdot_region_1.png)

---

### NYS

#### State Level Edge Betweenness Centrality (Interstates through Tertiary Roads ONLY)

![./state_level_centrality.png](./images/state_level_centrality.png)

##### NYSDOT RIS AADT (NYS)

![./state_level_nysdot_ris_aadt.png](./images/state_level_nysdot_ris_aadt.png)

### US Northeast (CT, MA, ME, NH, NJ, NY, PA, RI;)

####  Interstates through Primary Roads ONLY

![US Northeast Edge Betweenness Centrality](./images//us_northeast.motorway-to-primary-roadways.png)

####  Interstates through Secondary Roads ONLY

![US Northeast Edge Betweenness Centrality](./images//us_northeast.motorway-to-secondary-roadways.png)

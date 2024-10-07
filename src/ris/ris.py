"""RIS Milepoint Dataset Wrapper

Should implement
    * JOINing RIS Dataset Layers
        * AADT
        * Oneway
        * Bridges
        * Large Culverts
        * Road Class
    * OSM Conflation
        * Send features to OSRMMatcher
        * Handle the logic of choosing best matches
            * Induced OSM subnets
            * Higher Level Deductions
    * Enriching OSM with RIS Metadata such as AADT
        * NetworkX MultiDiGraph Edges
        * OSMnx Simplified MultiDiGraph
"""

import pandas as pd
import geopandas as gpd

# https://geopandas.org/en/latest/docs/user_guide/fiona_to_pyogrio.html
gpd.options.io_engine = "pyogrio"


class RISMilepoint:
    def __init__(
        self,
        filepath,
        rows=None,
        columns=['ROUTE_ID', 'ROUTE_NUMBER', 'ROADWAY_TYPE', 'DIRECTION', 'DOT_ID', 'COUNTY_ORDER']
    ):
        self.filename = filepath

        self.gdf = gpd.read_file(
            filepath,
            rows=rows,
            layer='LRSN_Milepoint',
            columns=columns,
            force_2d=True
        )

        self.gdf.set_index('ROUTE_ID', verify_integrity=True, inplace=True)

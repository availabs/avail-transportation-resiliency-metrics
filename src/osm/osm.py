import pyrosm
import networkx as nx
import osmnx as ox

class PyrosmOSM:
    def __init__(self, osm_filepath: str):
        self.filename = osm_filepath
        osm = pyrosm.OSM(self.filename)

        # From https://pyrosm.readthedocs.io/en/latest/basics.html?highlight=osmnx#export-to-networkx-osmnx
        nodes_gdf,edges_gdf = osm.get_network(nodes=True, network_type='driving+service')

        self.osm = osm
        self.nodes_gdf = nodes_gdf
        self.edges_gdf = edges_gdf

class NetworkXOSM:
    def __init__(self, pyrosm_osm: PyrosmOSM):
        self.G = pyrosm_osm.osm.to_graph(
            pyrosm_osm.nodes_gdf,
            pyrosm_osm.edges_gdf,
            graph_type="networkx",
            retain_all=True,
            osmnx_compatible=True
        )

class OSMnxOSM:
    def __init__(self, nx_osm: NetworkXOSM):
        self.sG = ox.simplify_graph(self.nx.G, track_merged=True)

class OSM:
    def __init__(self, osm_filepath):
        self.filename = osm_filepath

        self.pyrosm = None
        self.nx = None
        self.ox = None

    def init_pyrosm(self):
        if self.pyrosm:
            return

        self.pyrosm = PyrosmOSM(self.filename)


    def init_nx(self):
        if self.nx:
            return

        self.init_pyrosm()

        self.nx = NetworkXOSM(self.pyrosm)


    def init_ox(self):
        if self.ox:
            return

        self.init_nx()

        self.ox = OSMnxOSM(self.nx)
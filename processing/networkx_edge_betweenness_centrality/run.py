import sys
import os
from glob import glob 
from enum import Enum
import pickle
import functools

import networkx as nx
import pyrosm
import osmnx as ox

# Allow for outputing simplified network GPKG without centralities because
#   simplified network will be useful to load into database for analysis
#   and calculating centralities takes a long time.
WITH_CENTRALITIES = os.getenv("WITH_CENTRALITIES", 'True').lower() in ('true', '1', 't')

print(WITH_CENTRALITIES)

# The work_dir is the single positional argument.
work_dir = os.path.abspath(sys.argv[1])
intermediate_output_dir = os.path.join(work_dir, 'intermediate_output')

# Create the intermediate output directory if it does not exist.
os.makedirs(intermediate_output_dir, exist_ok=True)

### Workflow Orchestration Helpers ###

class WorkflowPipelineStages(Enum):
    NETWORKX = "networkx"
    OSMNX = "osmnx"
    EDGE_BETWEENNESS_CENTRALITY = "edge_betweenness_centrality"
    GPKG = 'gpkg'
    GPKG_WITHOUT_CENTRALITIES = "gpkg_without_centralities"


workflow_stage_output_file_paths: dict[WorkflowPipelineStages: str] = {
   WorkflowPipelineStages.NETWORKX: os.path.join(intermediate_output_dir, 'networkx.pkl'),
   WorkflowPipelineStages.OSMNX: os.path.join(intermediate_output_dir, 'osmnx.pkl'),
   WorkflowPipelineStages.EDGE_BETWEENNESS_CENTRALITY: os.path.join(intermediate_output_dir, 'edge_betweenness_centrality.pkl'),
   WorkflowPipelineStages.GPKG: os.path.join(work_dir, 'network.gpkg'),
   WorkflowPipelineStages.GPKG_WITHOUT_CENTRALITIES: os.path.join(work_dir, 'network.without_centralities.gpkg'),
}

def workflow_stage_output_file_exists(stage: WorkflowPipelineStages):
    return os.path.isfile(workflow_stage_output_file_paths[stage])

def get_workflow_stage_output(stage: WorkflowPipelineStages):
    with open(workflow_stage_output_file_paths[stage], 'rb') as f:
        return pickle.load(f)

def save_workflow_stage_output(stage, output):
    with open(workflow_stage_output_file_paths[stage], 'wb') as f:
        return pickle.dump(output, f)

# Get the osm.pbf file path
def get_osm_pbf_file():
    pbf_files = glob(f"{work_dir}/**/*.osm.pbf", recursive=True)

    # Verify that there is a single osm.pbf file in the work_dir.
    if len(pbf_files) != 1:
        raise Exception(f'There must be exactly 1 osm.pbf file in the work directory {work_dir}. Found {len(pbf_files)}')

    return pbf_files[0]

def create_networkx_graph():
    stage = WorkflowPipelineStages.NETWORKX

    if workflow_stage_output_file_exists(stage):
        print('Retrieving NetworkX Graph from intermediate work directory')
        return get_workflow_stage_output(stage)

    print('Creating NetworkX Graph from OSM PBF file')

    # From https://pyrosm.readthedocs.io/en/latest/basics.html?highlight=osmnx#export-to-networkx-osmnx
    osm = pyrosm.OSM(get_osm_pbf_file())
    nodes, edges = osm.get_network(nodes=True, network_type='driving+service')

    # Export the nodes and edges to NetworkX graph
    G = osm.to_graph(nodes, edges, graph_type="networkx", retain_all=True, osmnx_compatible=True)

    print('Persisting NetworkX Graph to intermediate work directory')
    save_workflow_stage_output(stage, G)

    return G

def flatten(k, v):
    v = v[k] if isinstance(v[k], list) else [v[k]]
    v = [x for x in v if isinstance(x, str)]

    return v[0] if v else None

@functools.cache
def create_osmnx_simplified_graph():
    stage = WorkflowPipelineStages.OSMNX

    if workflow_stage_output_file_exists(stage):
        print('Retrieving OSMnx simplified Graph from intermediate work directory')
        return get_workflow_stage_output(stage)


    G = create_networkx_graph()

    print('Creating OSMnx simplified Graph from NetworkX Graph')
    g = ox.simplify_graph(G)

    # WARNING: Reindexing and exporting to GPKG throws the following error:
    #            ValueError: cannot insert osmid, already exists
    #
    # The following workaround is suggested by the library's author:
    #   https://github.com/gboeing/osmnx/issues/638#issuecomment-756948363
    for node, data in g.nodes(data=True):
        if 'osmid' in data:
            data['osmid_original'] = data.pop('osmid')

    # NOTE: add_edge_speeds crashes without the following work around
    for e in list(g.edges(data=True)):
        if not (isinstance(e[2]['maxspeed'], str) or e[2]['maxspeed'] == None):
            e[2]['maxspeed'] = flatten('maxspeed', e[2])

    # https://osmnx.readthedocs.io/en/stable/user-reference.html#osmnx.routing.add_edge_speeds
    ox.add_edge_speeds(g)

    # https://osmnx.readthedocs.io/en/stable/user-reference.html#osmnx.routing.add_edge_travel_times
    ox.add_edge_travel_times(g)

    print('Persisting OSMnx simplified Graph to intermediate work directory')
    save_workflow_stage_output(stage, g)

    return g

def compute_edge_betweenness_centrality():
    stage = WorkflowPipelineStages.EDGE_BETWEENNESS_CENTRALITY

    if workflow_stage_output_file_exists(stage):
        print('Retrieving Edge Betweenness Centrality from intermediate work directory')
        return get_workflow_stage_output(stage)

    g = create_osmnx_simplified_graph()

    print('Computing Edge Betweenness Centrality')

    # Note: took 5h30m to run for Albany County
    edge_betweenness_centrality = nx.edge_betweenness_centrality(g, weight='travel_time')

    print('Persisting Edge Betweenness Centrality from intermediate work directory')
    save_workflow_stage_output(stage, edge_betweenness_centrality)

    return edge_betweenness_centrality

def create_gpkg(with_centralities=True):
    stage = WorkflowPipelineStages.GPKG if with_centralities else WorkflowPipelineStages.GPKG_WITHOUT_CENTRALITIES

    gpkg_path = workflow_stage_output_file_paths[stage]

    if workflow_stage_output_file_exists(stage):
        print(f'GPKG already exists at {gpkg_path}')
        return

    g = create_osmnx_simplified_graph()
    
    if with_centralities:
        edge_betweenness_centrality = compute_edge_betweenness_centrality()

        print('Adding Edge Betweenness Centrality to Simplified Graph')

        for edge in list(g.edges(data=True)):
            edge[2]['centrality'] = edge_betweenness_centrality[(edge[0],edge[1], 0)]

    gdf_nodes, gdf_relationships = ox.graph_to_gdfs(g)

    print(f'Writing GPKG to {gpkg_path}')

    try:
        gdf_nodes.to_file(gpkg_path, layer='intersections', driver='GPKG')
        gdf_relationships.to_file(gpkg_path, layer='roadways', driver='GPKG')
    except:
        print('Error writing GPKG.', file=sys.stderr)
        os.remove(gpkg_path)
        raise 


def main():
   create_gpkg(WITH_CENTRALITIES) 

if __name__ == '__main__':
    main()

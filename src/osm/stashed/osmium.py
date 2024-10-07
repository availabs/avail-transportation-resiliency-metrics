import osmium

# NOTE: The following import breaks running module in VSCode with the ▶ button.
from ...common import BrokenInvariantError

"""Might be useful later"""
def analyse_osm_ways(osm_filepath: str, osm_G: nx.MultiDiGraph):
    # CONSIDER: This information could be added directly to osm_G

    kept_osm_way_ids = set([way_id for u,v,way_id in osm_G.edges.data('osmid')])

    osm_nodes_to_ways_info = dict()
    osm_ways_meta = dict()

    num_ways = 0
    for o in osmium.FileProcessor(osm_filepath, osmium.osm.WAY):
        way_id = o.id

        if not way_id in kept_osm_way_ids:
            continue

        num_ways += 1

        # https://wiki.openstreetmap.org/wiki/Key:oneway#Implied_oneway_restriction
        highway = o.tags['highway'] if 'highway' in o.tags else None
        junction = o.tags['junction'] if 'junction' in o.tags else None
        oneway = o.tags['oneway'] if 'oneway' in o.tags else None

        # https://wiki.openstreetmap.org/wiki/Tag:highway%3Dmotorway#How_to_map
        if oneway is None and highway == 'motorway':
            oneway = 'yes'

        # https://wiki.openstreetmap.org/wiki/Tag:junction%3Droundabout#The_roundabout_itself
        if junction == 'roundabout':
            oneway = 'yes'

        osm_ways_meta[way_id] = {
            'highway': highway,
            'junction': junction,
            'oneway': oneway
        }

        # Forward direction across Nodes path
        if oneway not in ['reverse', '-1']: # See: https://wiki.openstreetmap.org/wiki/Key:oneway#List_of_values
            nodes_list = [n.ref for n in list(o.nodes)]

            if not nx.is_path(osm_G, nodes_list):
                raise BrokenInvariantError("OSM Way's Forward Nodes path does not exist in NetworkX graph")

            length_along = 0
            predecessor_u = None

            osm_ways_meta['fwd_nodes'] = nodes_list

            for i, (u, v) in enumerate(zip(nodes_list[:-1], nodes_list[1:])):
                edges_data = osm_G.get_edge_data(u, v)

            if not edges_data:
                raise BrokenInvariantError('OSM Way Node Pair not found.')

            ## TODO: Figure out why sometimes an multi-edge is missing for a OSM Way. (NOTE: Applies also for reverse direction below.)
            # osm_way_edges = [d for d in edges_data.values() if d['osmid'] == way_id]
            #
            # if len(osm_way_edges) > 1:
            # raise BrokenInvariantError('OSM Node Pair occurs more than once for Way.')

            length = list(edges_data.values())[0]['length']

            if (u,v) not in osm_nodes_to_ways_info:
                osm_nodes_to_ways_info[(u,v)] = { way_id: { 'fwd': {} } }
            elif way_id not in osm_nodes_to_ways_info[(u,v)]:
                osm_nodes_to_ways_info[(u,v)][way_id] = { 'fwd': {} }

            osm_nodes_to_ways_info[(u,v)][way_id]['fwd'][i] = {
                'u': u,
                'v': v,
                'way_node_idx': i,
                'length_along': length_along,
                'length': length,
                'predecessor_u': predecessor_u,
                'successor_v': None
            }

            if i:
                osm_nodes_to_ways_info[(predecessor_u, u)][way_id]['fwd'][i-1]['successor_v'] = v

            length_along += length
            predecessor_u = u

        # Reverse direction across Node Path
        if oneway not in ['yes', '1']: # See: https://wiki.openstreetmap.org/wiki/Key:oneway#List_of_values
            nodes_list = [n.ref for n in list(o.nodes)]
            nodes_list.reverse()

            if not nx.is_path(osm_G, nodes_list):
                raise BrokenInvariantError("OSM Way's Reverse Nodes path does not exist in NetworkX graph")

            osm_ways_meta['bwd_nodes'] = nodes_list

            for i, (u, v) in enumerate(zip(nodes_list[:-1], nodes_list[1:])):
                edges_data = osm_G.get_edge_data(u, v)

            if not edges_data:
                raise BrokenInvariantError('OSM Way Node Pair not found.')

            length = list(edges_data.values())[0]['length']

            if (u,v) not in osm_nodes_to_ways_info:
                osm_nodes_to_ways_info[(u,v)] = { way_id: { 'bwd': {} } }
            elif way_id not in osm_nodes_to_ways_info[(u,v)]:
                osm_nodes_to_ways_info[(u,v)][way_id] = { 'bwd': {} }
            elif 'bwd' not in osm_nodes_to_ways_info[(u,v)][way_id]:
                osm_nodes_to_ways_info[(u,v)][way_id]['bwd'] = dict()

            osm_nodes_to_ways_info[(u,v)][way_id]['bwd'][i] = {
                'u': u,
                'v': v,
                'way_node_idx': i,
                'length_along': length_along,
                'length': length,
                'predecessor_u': predecessor_u,
                'successor_v': None
            }

            if i:
                osm_nodes_to_ways_info[(predecessor_u, u)][way_id]['bwd'][i-1]['successor_v'] = v

            length_along += length
            predecessor_u = u


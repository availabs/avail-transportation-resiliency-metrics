import itertools
import json
import urllib.request

from typing import TypedDict, Annotated

import networkx as nx
import pandas as pd
import shapely

from ..common import BrokenInvariantError

class OSRMMatchingResponseMatchingsLegAnnotationMetadata (TypedDict):
    datasource_names: list[str]

class OSRMMatchingResponseMatchingsLegAnnotation (TypedDict):
    metadata: OSRMMatchingResponseMatchingsLegAnnotationMetadata
    datasources: list[int]
    weight: list[float]
    nodes: list[int]
    distance: list[float]
    duration: list[float]
    speed: list[float]

class OSRMMatchingResponseMatchingsLeg (TypedDict):
    steps: list
    summary: str
    weight: float
    duration: float
    annotation: OSRMMatchingResponseMatchingsLegAnnotation
    distance: float

class OSRMMatchingResponseMatchings (TypedDict):
    confidence: float
    distance: float
    duration: float
    geometry: str
    legs: list[OSRMMatchingResponseMatchingsLeg]

class OSRMMatchingResponseTracepoint (TypedDict):
    alternatives_count: int
    distance: float
    hint: str
    location: Annotated[list[float], 2]
    matchings_index: int
    name: str
    waypoint_index: int

class OSRMMatchingResponse (TypedDict):
    code: int
    matchings: list[OSRMMatchingResponseMatchings]
    tracepoints: list[OSRMMatchingResponseTracepoint]

class OSRMMatchMetadata (TypedDict):
    feature_id: str | int
    feature_properies: dict
    reversed: bool
    osm_subnet_name: str
    matched_coordinates_sequence: list[Annotated[list[float], 2]]
    url: str
    matching_response: OSRMMatchingResponse


class OSRM:
    def __init__(self, host: str, osm_subnet_name: str) -> None:
        self.host = host
        self.osm_subnet_name = osm_subnet_name

    def match(self, feature: shapely.LineString | shapely.MultiLineString, reverse=False) -> OSRMMatchMetadata:
        coords = feature['geometry']['coordinates']
        flattened  = list(itertools.chain.from_iterable(coords))

        if reverse:
            flattened.reverse()

        # Make it immutable
        flattened_coordinates_sequence = tuple(flattened)

        coords_str = ';'.join([f'{lat},{lon}' for lat, lon in flattened_coordinates_sequence])

        url =  f'{self.host}/match/v1/{self.osm_subnet_name}/{coords_str}?annotations=true&overview=full'

        contents = urllib.request.urlopen(url).read()

        osrm_matching_response = json.loads(contents)

        return {
            'feature_id': feature['id'],
            'feature_props': feature['properties'],
            'reversed': reverse,
            'osm_subnet_name': self.osm_subnet_name,
            'matched_coordinates_sequence': flattened_coordinates_sequence,
            'matching_response': osrm_matching_response
        }


def extract_osm_node_chain(osrm_match_response: OSRMMatchingResponse) -> list[int]:
   matchings = osrm_match_response['matchings']
   nodes_chain = []

   for matching in matchings:
       legs = matching['legs']

       for leg in legs:
           nodes = leg['annotation']['nodes']

           # https://www.geeksforgeeks.org/python-merge-overlapping-part-of-lists/
           tmp1 = (i for i in range(len(nodes), 0, -1) if nodes[:i] == nodes_chain[-i:])
           tmp2 = next(tmp1, 0)

           nodes_chain.extend(nodes[tmp2:])

   return nodes_chain

def get_tracepoints_linestrings(match_meta: OSRMMatchMetadata) -> list[shapely.LineString]:
    feature_coords = match_meta['matched_coordinates_sequence']
    locations = [d['location'] for d in match_meta['matching_response']['tracepoints']]

    if len(feature_coords) != len(locations):
        raise BrokenInvariantError(f'len(feature_coords) = {len(feature_coords)}, len(locations) = {len(locations)}')

    return [shapely.LineString([f, t]) for f,t in zip(feature_coords, locations)]

def get_tracepoints_multipolygon(match_meta: OSRMMatchMetadata) -> list[shapely.LineString]:
    f_coords = match_meta['matched_coordinates_sequence']
    t_coords  = [d['location'] for d in match_meta['matching_response']['tracepoints']]

    if len(f_coords) != len(t_coords):
        raise BrokenInvariantError(f'len(feature_coords) = {len(f_coords)}, len(locations) = {len(t_coords)}')

    f_pairs = [(o,d) for o,d in zip(f_coords[:-1], f_coords[1:])]
    t_pairs = [(o,d) for o,d in zip(t_coords[:-1], t_coords[1:])]

    polys = [
        shapely.MultiPoint([
            shapely.Point(f[0]),
            shapely.Point(f[1]),
            shapely.Point(t[0]),
            shapely.Point(t[1]),
        ]).convex_hull for f, t in zip(f_pairs, t_pairs)
    ]

    return shapely.unary_union(polys)

"""TODO: break down summary stats by OSM Way for deciding which RIS Segment to OSM Way to choose from alternatives."""
def get_tracepoints_distances_summary(match_meta: OSRMMatchMetadata) -> dict:
    distances = [d['distance'] for d in match_meta['matching_response']['tracepoints']]

    return pd.Series(distances).describe()

"""This hypothesis FAILS. Matchings lengths can be significantly greater than 1."""
def assert_matchings_length_is_one(match_meta: OSRMMatchMetadata):
   count = len(match_meta['matching_response']['matchings'])

   if count != 1:
       raise BrokenInvariantError(f'len(matchings) = {count}')


"""This hypothesis fails. Flattened feature coords length DOES NOT determine matching legs length.
The number of flattened feature coords does correspond to tracepoints, however some tracepoints may be None.

For all observations in Albany County RIS,
  if there is a single matchings entry,
  the number of its legs does equal the number of of non-None a tracepoint.
"""
def assert_matching_legs_coorespond_to_feature_coords_pairs(match_meta: OSRMMatchMetadata):
    assert_matchings_length_is_one(match_meta)

    f_coords = match_meta['matched_coordinates_sequence']
    matching = match_meta['matching_response']['matchings'][0]
    legs = matching['legs']

    if (len(f_coords) - len(legs)) != 1:
       raise BrokenInvariantError(f'len(f_coords) = {len(f_coords)}; len(legs) = {len(legs)}')

"""This is was true for all of Albany County RIS."""
def assert_matching_legs_coorespond_to_nonnone_tracings_length(match_meta: OSRMMatchMetadata):
    """Filter out where tracing is None."""
    num_nonnone_tracings = len([t for t in match_meta['matching_response']['tracepoints'] if t])

    num_matchings = len(match_meta['matching_response']['matchings'])

    num_legs = 0
    for m in match_meta['matching_response']['matchings']:
        num_legs += len(m['legs'])

    if (num_nonnone_tracings - num_matchings) != num_legs:
       raise BrokenInvariantError(
           f'num_nonone_tracings={num_nonnone_tracings}, num_matchings={num_matchings}, num_legs={num_legs}'
       )

"""This hypothesis FAILS. There can be gaps in the OSM Nodes Chain."""
def assert_osrm_matching_node_chain_is_a_connected_path(G: nx.MultiDiGraph, match_meta: OSRMMatchMetadata) -> list:
   nodes_chain = extract_osm_node_chain(match_meta['matching_response'])

   for u,v in zip(nodes_chain[:-1], nodes_chain[1:]):
       if not G.has_edge(u=u, v=v):
           raise BrokenInvariantError(f'Nodes u={u} and v={v} are not connected in the graph; len(nodes_chain) = {len(nodes_chain)}')


# def assert_osrm_matching_node_chain_is_a_connectable_path(G: nx.MultiDiGraph, match_meta: OSRMMatchMetadata):
def assert_osrm_matching_node_chain_is_a_connectable_path(G: nx.MultiDiGraph, match_meta: OSRMMatchMetadata):
    nodes_chain = extract_osm_node_chain(match_meta['matching_response'])

    for u,v in zip(nodes_chain[:-1], nodes_chain[1:]):
        if not G.has_edge(u=u, v=v):
            try:
                path = nx.shortest_path(G, source=u, target=v)
                print(
                    f'id={match_meta["feature_id"]}, dir={match_meta["feature_properies"]["DIRECTION"]}, reversed={match_meta["reversed"]}, u={u}, v={v}, chain gap length={len(path)}'
                )
            except:
                raise BrokenInvariantError(f'NO PATH: id={match_meta["feature_id"]}, reversed={match_meta["reversed"]}, u={u}, v={v}')


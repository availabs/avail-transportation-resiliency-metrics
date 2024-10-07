# OSRM

## 🔑🔑🔑 [Explanation of OSRM Map-Matching Algorithm and API Response](https://github.com/Project-OSRM/osrm-backend/issues/2933#issuecomment-249068441) 🔑🔑🔑

> @wiva-koikoi It sounds like you are misunderstanding the API response and how
> the map-matching algorithm works.
>
> The elements of matchings are not connected - if your trace matches without
> error, then matchings array should only have 1 entry. The fact that you've got 4
> means that OSRM split your coordinates into 4 partial matches with gaps between.
> The matching algorithm is probabilistic and your GPS data is noisy - it's not
> going to give you a perfect result every time.
>
> For coordinate [16], you've supplied a radius of 15m. OSRM will search for up to
> 3x that distance for a road to snap to, and will give up if it can't find one.
>
> Here's that point highlighted:
> http://bl.ocks.org/d/a69a9c1a98f28a4cc69ada4cfdd58e8e
>
> You've specified a bearing of 74 +/- 120 for this coordinate. The nearest road
> that matches that is about 65m away. This coordinate is failing to snap to
> anything and is being discarded, causing a break in your trace.
>
> You should not draw the matchings geometries as connected - they are not, they
> represent partial matches from your original sequence of coordinates.
>
> The tracepoints array are your original points, and the the matching_index and
> waypoint_index properties tell you which partial match each tracepoint was
> included in. If your trace is clean and matches well, then they will all have
> matching_index: 0.
>
> Given how far from the road your coordinate [16] is, it sounds like you need to
> check your GPS accuracy reading - it was much worse than 15m. Either that, or
> there's a road that's not on the map, in which case we wouldn't want to snap to
> the wrong road anyway.
>
> You can try iteratively removing these failed points yourself - if you get a
> null response, drop that point and re-try the request, see if the matches get
> connected. Note that there's a ~500m max distance between points before traces
> get split.
>
> The map-matching algorithm was tuned based on GPS data from a car arriving at
> about 10 second intervals, with ~5m accuracy. It works quite well for coarser
> and finer data than that, but if you drift too far from the expected model,
> you'll start to see more splits.

[Improving Results](https://github.com/Project-OSRM/osrm-backend/issues/2933#issuecomment-248899775)

> If you are looking to improve your results, you could adjust GPS precision
> (see https://github.com/Project-OSRM/osrm-backend/blob/master/docs/http.md#request-4).

## Resources

- [Rerouting because of a blocked path](https://github.com/Project-OSRM/osrm-backend/issues/5346)
- [Traffic](https://github.com/Project-OSRM/osrm-backend/wiki/Traffic)
- [OSRM Map Matching Output explanation](https://gis.stackexchange.com/questions/271071/osrm-map-matching-output-explanation)
- [Match service results explanation](https://github.com/Project-OSRM/osrm-backend/issues/2949)
- [Non correct drawing of route segments with waypoints which was dropped by matching service.](https://github.com/Project-OSRM/osrm-backend/issues/2933#issuecomment-249068441_)
- [How to request / force more alternative routes?](https://github.com/Project-OSRM/osrm-backend/issues/5663)
- [Matching breaks the route into separate routes ! #5136](https://github.com/Project-OSRM/osrm-backend/issues/5136)
- [How to use OSRM's match service](https://stackoverflow.com/questions/50698754/how-to-use-osrms-match-service)
- [Match service results explanation #2949](https://github.com/Project-OSRM/osrm-backend/issues/2949)

[OSRM Tile service](https://project-osrm.org/docs/v5.5.1/api/#tile-service)

> This service generates Mapbox Vector Tiles that can be viewed with a
> vector-tile capable slippy-map viewer. The tiles contain road geometries and
> metadata that can be used to examine the routing graph. The tiles are generated
> directly from the data in-memory, so are in sync with actual routing results,
> and let you examine which roads are actually routable, and what weights they
> have applied.

- [Mapbox Vector Tile](https://github.com/tilezen/mapbox-vector-tile)
  > Python package for encoding & decoding Mapbox Vector Tiles
- https://www.geopackage.org/extensions.html
- https://gitlab.com/imagemattersllc/ogc-vtp2/-/blob/master/extensions/1-vte.adoc
- https://gitlab.com/imagemattersllc/ogc-vtp2/-/blob/master/extensions/2-mvte.adoc

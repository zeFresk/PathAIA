# coding: utf8
"""Useful functions for visualizing patches in WSIs."""

import numpy
from skimage.morphology import binary_dilation, disk
import openslide
from typing import Sequence, Tuple, Optional
from ..util.types import NDByteImage, Patch, Coord


def preview_from_queries(
    slide: openslide.OpenSlide,
    queries: Sequence[Patch],
    min_res: int = 512,
    color: Tuple[int, int, int] = (255, 255, 0),
    thickness: int = 2,
    cell_size: int = 20,
    size_0: Optional[Coord] = None,
) -> NDByteImage:
    """
    Give thumbnail with patches displayed.

    Args:
        slide: openslide object
        queries: patch objects to preview from
        min_res: minimum size for the smallest side of the thumbnail (usually the width)
        color: rgb color for patch boundaries
        thickness: thickness of patch boundaries
        cell_size: size of a cell representing a patch in the grid
        psize: size of a patch at level 0

    Returns:
        Thumbnail image with patches displayed.

    """
    # get thumbnail first
    slide_size = Coord(slide.dimensions)
    if size_0 is None:
        size_0 = Coord(queries[0].size_0)
    thickness = 2 * (thickness // 2) + 1
    res = slide_size / size_0 * (thickness + cell_size) + thickness
    thumb_w = max(min_res, res.x)
    thumb_h = max(min_res, res.y)
    image = slide.get_thumbnail((thumb_w, thumb_h))
    thumb_size = Coord(image.size)
    dsr = slide_size[0] / thumb_size[0]
    image = numpy.array(image)[:, :, 0:3]
    # get grid
    grid = 255 * numpy.ones((thumb_size.y, thumb_size.x), numpy.uint8)
    for query in queries:
        # position in queries are absolute
        x, y = query.position / dsr
        dx, dy = query.size_0 / dsr
        startx = min(x, thumb_size.x - 1)
        starty = min(y, thumb_size.y - 1)
        endx = min(x + dx, thumb_size.x - 1)
        endy = min(y + dy, thumb_size.y - 1)
        # horizontal segments
        grid[starty, startx:endx] = 0
        grid[endy, startx:endx] = 0
        # vertical segments
        grid[starty:endy, startx] = 0
        grid[starty:endy, endx] = 0
    grid = grid < 255
    d = disk(thickness//2)
    grid = binary_dilation(grid, d)
    image[grid] = color
    return image

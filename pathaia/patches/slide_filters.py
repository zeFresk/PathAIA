import cv2
import numpy as np
from skimage.morphology import remove_small_objects
from ..util.types import NDBoolMask, NDImage


def filter_remove_small_objects(
    in_mask: NDBoolMask,
    avoid_overmask: bool = True,
    overmask_thresh: float = 10,
    min_size_fac: float = 1,
) -> NDBoolMask:
    """
    Removes small objects from a binary mask. Can recursively lowers its minimum
    accepted size if too much tissue is erased.

    Args:
        in_mask: input binary mask (must be boolean).
        avoid_overmask: if True recursively call itself if too much tissue is
            erased.
        overmask_thresh: if avoid_overmask and more than overmask_thresh% of
            the input mask is erased, calls the function recursively with lower minimum
            accepted size.
        min_size_fac: multiplier for overmask_thresh used to compute minimum
            accepted size. Mainly for internal use in recursive call.

    Returns:
        Output binary mask with small objects removed.
    """
    min_size = int(min_size_fac * in_mask.sum() * overmask_thresh / 100)
    out_mask = remove_small_objects(in_mask, min_size=min_size)
    mask_percentage = 100 - out_mask.sum() / in_mask.sum() * 100
    if (
        (mask_percentage >= overmask_thresh)
        and (min_size >= 1)
        and (avoid_overmask is True)
    ):
        min_size_fac *= 0.8
        out_mask = filter_remove_small_objects(
            in_mask, avoid_overmask, overmask_thresh, min_size_fac
        )
    return out_mask


def filter_thumbnail(x: NDImage) -> NDBoolMask:
    """
    Computes a tissue mask from a slide thumbnail. Filters background, red pen, blue pen
    using La*b* space.

    Args:
        x: input thumbnail as a numpy byte array.

    Returns:
        Numpy binary mask where usable tissue is marked as True.
    """
    x = cv2.cvtColor(x.astype(np.float32) / 255, cv2.COLOR_RGB2Lab)
    l, a, b = x.transpose(2, 0, 1)
    mask = (
        ((a > 10) | ((a > 5) & (b > 0)) & (l > 40))
        & ((a < 50) | (b < 90))
        & (l < 95)
        & (l > 10)
    )
    return filter_remove_small_objects(mask)

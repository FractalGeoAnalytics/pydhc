import numpy as np
import pandas as pd
from numpy.typing import NDArray



def _enclosed(
    fr: NDArray, to: NDArray, samplefrom: NDArray, sampleto: NDArray
) -> NDArray[np.bool]:
    """
    calculates the intervals that are totally covered by the from and to depths
    """
    # the first step is to do the basic check of the intervals
    idx_from: NDArray[
        np.bool
    ]  # idx of the array less than the from depth of the composite
    idx_to: NDArray[
        np.bool
    ]  # idx of the array less than the from depth of the composite
    idx_full: NDArray[np.bool]
    idx_from = samplefrom > fr
    idx_to = sampleto < to
    idx_full = idx_from & idx_to
    return idx_full


def _boundary(
    fr: NDArray, to: NDArray, samplefrom: NDArray, sampleto: NDArray
) -> NDArray[np.bool]:
    """
    returns the index of the samples intersecting the boundary
    """
    # the first step is to do the basic check of the intervals
    idx_from: NDArray[
        np.bool
    ]  # idx of the array less than the from depth of the composite
    idx_to: NDArray[
        np.bool
    ]  # idx of the array less than the from depth of the composite
    idx_partial: NDArray[np.bool]
    idx_from = samplefrom <= to
    idx_to = sampleto >= fr
    idx_partial = idx_from & idx_to
    return idx_partial


def _contact(idx_partial, idx_enclosed):
    return np.logical_xor(idx_partial, idx_enclosed)

def _sample_weight():
    pass

def composite(cfrom: NDArray, cto: NDArray, samplefrom: NDArray, sampleto: NDArray, array: NDArray,method:str='soft') -> NDArray:
    """
    Simple function to composite drill hole data to a set of intervals:
    Handles compositing of data to intervals for both the hard and soft boundary conditions.
    Hard boundary data (assays, some stratigraphic contacts) does not allow for the intervals to be broken. and best effort intervals are taken.
    Soft boundary data (most geophysics, hylogger, though practically it can be ignored in most cases) does allow for the breaking of data at interval boundaries

    Args:
        cfrom (NDArray): the from depths that you would like to composite to
        cto (NDArray): the to depths that you would like to composite to
        samplefrom (NDArray): the from depth of the input array
        sampleto (NDArray): the from depth of the input array
        array (NDArray): the numpy array that you would like to have composited
    Returns:

    Examples:
    """
    # first step is to confirm that the input data is consistent
    assert cfrom.shape[0] == cto.shape[0], "Composite from to are not the same size"

    assert samplefrom.shape[0] == sampleto.shape[0], "Sample from to are not the same size"

    # all we are doing now is to loop over each of the from and to intervals

    n_composites: int = cfrom.shape[0]
    n_columns: int = array.shape[1]
    output: NDArray = np.zeros((n_composites, n_columns))*np.nan
    fr: float
    to: float
    accumulated_array:NDArray
    total_weight:NDArray

    coverage:float

    sample_length = sampleto-samplefrom
    # validate sample length always positive
    # if it is 0 or negative this will cause issues with the weighted sum
    idx_sample_fail = sample_length<=0
    method='soft'
    if method == 'soft':
        cutoff = 0
    else:
        cutoff = 1
    for i in range(n_composites):
        # extract the from and to of the desired interval
        fr = cfrom[i]
        to = cto[i]
        # this is the fast and simple way 
        # to calculate if a sample interval is covered by 
        # a composite interval rather calculating each of the states of coverage.
        coverage = np.fmin(sampleto,to) - np.fmax(samplefrom,fr)
        # coverage will return a negative value if the sample is not insite the composite interval
        # the soft boundary case is the simplest to calculate 
        # in this case we can have weights for a sample less than 1 and greater than 0
        # if we wanted the hard boundary case we would only accept weights of 1
        coverage[coverage<cutoff] = 0 # changing the 0 here 
        # the matrix multiply is quite slow when applying this to a very large array
        # in the case when there are no intersections we can speed up the calculation
        # quite significantly by carrying on the calculation if there are any samples
        # with a positive weight
        if np.any(coverage)>0:
            # we only calculate a length weighted average
            weights = coverage/sample_length
            # if the sample length is 0 or negative that will cause issues
            # use the validation index to set that weight to 0
            weights[idx_sample_fail] = 0
            total_weight = np.sum(weights)
            # once we have an array of normalised weights
            # it is simple to multiple the sample array by the weights
            weight_array = weights.reshape(-1,1)/total_weight
            # we can speed up the calculation even more by selecting indicies 
            # from the array that we are going to multiply
            idx_inside = weight_array>0
            # then we sum the array 
            accumulated_array = np.nansum(array[idx_inside,:]*weight_array[idx_inside],0)
            # and insert into the output
        else:
            accumulated_array = 0
        output[i,:] = accumulated_array
    return output

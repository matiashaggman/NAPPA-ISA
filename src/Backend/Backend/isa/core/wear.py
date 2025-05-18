import pandas as pd
import numpy as np
from scipy.signal import spectrogram


#NOTE: Warning, this approach is largely not validated and is based on heuristics.
def detect_wear(
    feature: pd.Series,
    threshold: float = 0.009,
    seg_len: int = 120,
    overlap: int = 119,
    min_nonwear_duration: int = 1800,
) -> pd.Series:
    """
    Identify timepoints when the wearable is *on-body* based on the activity
    feature.

    The signal is split into overlapping windows, a spectrogram is computed,
    and a simple power-threshold heuristic marks each window as wear / non-wear.
    The resulting mask is re-indexed to the original 30-s grid and short
    non-wear gaps ( < *min_nonwear_duration* ) are filled.

    Parameters
    ----------
    feature : pd.Series
        Activity feature, indexed at **30-second frequency**.
    threshold : float, default 0.009
        Heuristic power threshold applied to each spectrogram window.
    seg_len : int, default 120
        Window length (*nperseg*) in samples (120 x 30 s = 1 h).
    overlap : int, default 119
        Window overlap in samples (119 gives 30-s hop).
    min_nonwear_duration : int, default 1800
        Shorter non-wear runs (in seconds) are treated as *wear*
        to suppress false negatives.

    Returns
    -------
    pd.Series[bool]
        Boolean mask on the original index - **True = wearable is worn**.
    """
    f, t, Sxx = spectrogram(
        feature.to_numpy(),
        fs=1/30, #features are 30s epochs -> 1/30 Hz
        nperseg=seg_len,
        noverlap=overlap,
    )
    # Heuristic for wear detection. *Might* need improvements in the future
    threshold_fn = (10 * np.log10(np.max(Sxx, axis=0) + 1e-10) / 1e4) + 0.01

    wear_idx = threshold_fn > threshold

    time_index = [feature.index[0] + pd.Timedelta(seconds=int(x)) for x in t] #type: ignore

    wear_df = pd.DataFrame(wear_idx, index=time_index, columns=['wear'])

    aligned_wear = wear_df.reindex(feature.index, method='nearest')

    aligned_wear = aligned_wear.resample('30s').mean().ffill().astype(bool)

    # Remove false negatives by thresholding the number of consecutive nonwear time points
    nonwear_blocks = (aligned_wear['wear'] == False).astype(int).groupby(aligned_wear['wear'].ne(aligned_wear['wear'].shift()).cumsum()).cumsum()
    aligned_wear.loc[nonwear_blocks < (min_nonwear_duration / 30), 'wear'] = True

    return aligned_wear['wear'] # return pandas series instead of df for simplicity.


def detect_wear_blocks(
    wear_idx: pd.Series,
    threshold_length: pd.Timedelta = pd.Timedelta(hours=4), #type: ignore
    buffer_length:    pd.Timedelta = pd.Timedelta(minutes=30), #type: ignore
) -> list[tuple[str, str]]:
    """
    Collapse the per-epoch wear mask into coarse *wear blocks*.

    A block is emitted when the device is worn continuously for at least
    *threshold_length*.  Each block is then expanded by ±*buffer_length* so
    that the classifier has context at the edges.

    Parameters
    ----------
    wear_idx : pd.Series[bool]
        Boolean wear mask indexed by datetime (same as the feature index).
    threshold_length : pd.Timedelta, default 4 h
        Minimum uninterrupted wear duration required to create a block.
    buffer_length : pd.Timedelta, default 30 min
        Extra time added before the start and after the end of each block.

    Returns
    -------
    list[tuple[str, str]]
        List of ``(start, end)`` strings in the format
        ``"YYYY-MM-DD HH:MM:SS"`` suitable for JSON serialisation.
    """

    wearTime = wear_idx  # wear_idx is a Series of booleans indexed by time
    wearBlocks = []
    current_block = []

    # Iterate over the Series
    for index, row in wearTime.items():
        if row:
            current_block.append(index)
        else:
            if current_block:
                if (current_block[-1] - current_block[0]) >= threshold_length:
                    # if we are creating the first block, don't subtract buffer_length (might go over the start time)
                    if len(wearBlocks) == 0:
                        wearBlocks.append((
                            current_block[0],
                            current_block[-1] + buffer_length,
                        ))
                    else:
                        wearBlocks.append((
                            current_block[0] - buffer_length,
                            current_block[-1] + buffer_length,
                        ))
                current_block = []

    # Check last block
    if current_block:
        if (current_block[-1] - current_block[0]) >= threshold_length:
            wearBlocks.append((
                current_block[0] - buffer_length,
                current_block[-1],
            ))

    wearBlocks = [(start.strftime("%Y-%m-%d %H:%M:%S"), end.strftime("%Y-%m-%d %H:%M:%S")) for start, end in wearBlocks]
    
    return wearBlocks


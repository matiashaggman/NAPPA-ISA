import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from scipy.signal import medfilt
from matplotlib.patches import Circle


color_palette = sns.color_palette('Set2')
coolwarm_palette = sns.color_palette(palette='coolwarm')

def init_plot_style():
    """
    Initialize the global plot style once at the start of the script.
    """
    sns.set_theme()  # Or any other style you want
    plt.rcParams.update({
        'font.size': 14,
        'axes.titlesize': 16,
        'axes.labelsize': 14,
        'xtick.labelsize': 12,
        'ytick.labelsize': 12,
        'legend.fontsize': 12,
        'figure.autolayout': True
    })
    return 


def plot_segments(ax, x, y, mask, color, step=False):
    """
    Plot segments of data on the given axes.

    Parameters:
    ax : matplotlib.axes.Axes
        The axes to plot on.
    x : array-like
        The x data.
    y : array-like
        The y data.
    mask : array-like of bool
        A boolean mask indicating which segments to plot.
    color : str
        The color to use for the plotted segments.
    step : bool
        Use step function over plot for discrete data.
    """
    # Convert bool to int to find transitions
    mask_int = mask.astype(int)
    transitions = np.diff(mask_int)
    start_pts = np.where(transitions == 1)[0] + 1
    end_pts = np.where(transitions == -1)[0] + 1

    # If the mask starts True at index 0
    if mask_int.iloc[0] == 1:
        start_pts = np.insert(start_pts, 0, 0)
    # If the mask ends True at last index
    if mask_int.iloc[-1] == 1:
        end_pts = np.append(end_pts, len(mask_int))

    if not step:
        for s, e in zip(start_pts, end_pts):
            ax.plot(x[s:e], y[s:e], color=color, linewidth=1)
    else:
        for s, e in zip(start_pts, end_pts):
            ax.step(x[s:e], y[s:e], color=color, linewidth=1)
    return


def plot_CI_segments(ax, x, CI, mask, color):
    """
    Plot confidence intervals on the given axes.

    Parameters:
    ax : matplotlib.axes.Axes
        The axes to plot on.
    x : array-like
        The x data.
    CI : tuple of array-like
        The lower and upper bounds of the confidence interval.
    mask : array-like of bool
        A boolean mask indicating which segments to plot.
    color : str
        The color to use for the plotted segments.
    """
    # Convert bool to int to find transitions
    mask_int = mask.astype(int)
    transitions = np.diff(mask_int)
    start_pts = np.where(transitions == 1)[0] + 1
    end_pts = np.where(transitions == -1)[0] + 1

    # If the mask starts True at index 0
    if mask_int.iloc[0] == 1:
        start_pts = np.insert(start_pts, 0, 0)
    # If the mask ends True at last index
    if mask_int.iloc[-1] == 1:
        end_pts = np.append(end_pts, len(mask_int))

    for s, e in zip(start_pts, end_pts):
        ax.fill_between(x[s:e], CI[0][s:e], CI[1][s:e], color=color, alpha=0.3)
    return


def make_donut_fig(recording, wear_idx):
    """
    Create a donut plot for sleep stage distribution.

    Parameters:
    recording : SleepRecording
        The sleep recording object containing labels.
    wear_idx : array-like of bool
        A boolean mask indicating the wear time indexes.

    Returns:
    fig : matplotlib.figure.Figure
        The created figure.
    ax : matplotlib.axes.Axes
        The axes of the created figure.
    """
    sleep_df = recording.labels[wear_idx]

    stage_counts = sleep_df['sleep_stage'].value_counts()
    stage_proportions = stage_counts / stage_counts.sum()

    sns.set_theme()
    fig, ax = plt.subplots(figsize=(6, 6))

    # Create the donut plot
    colors = sns.color_palette(palette='coolwarm')
    color_mapping = {'deep': colors[0], 'light': colors[1], 'wake': colors[2]}
    stage_colors = [color_mapping[stage] for stage in stage_proportions.index]

    wedges, texts, autotexts = ax.pie(
        stage_proportions,
        labels=stage_proportions.index,
        autopct='%1.0f%%',
        startangle=90,
        colors=stage_colors,
        wedgeprops={'width': 0.3},
        textprops={'color': 'black', 'fontsize': 12}
    )

    center_circle = Circle((0, 0), 0.5, color='white', zorder=10)
    ax.add_artist(center_circle)

    ax.set_title("Sleep Stage Distribution")

    return fig, ax


def make_bar_fig(recording, wear_idx, settings):
    """
    Generates a bar plot figure showing the distribution of sleep stages over time.
    Parameters:
    recording (object): The recording object containing sleep stage data.
    wear_idx (int): The index of the wearable device data to be used.
    settings (dict): A dictionary containing settings for the plot. 
                    Expected key is 'date_format' with values:
                    0 - '%d.%m.'
                    1 - '%d/%m'
                    2 - '%d.%m.%y'
                    3 - '%d/%m/%y'
    Returns:
    matplotlib.axes._subplots.AxesSubplot: The Axes object with the bar plot.
    """

    match settings['report']['quality']['date_format']:
        case 0:
            dateFmt = '%d.%m.'
        case 1:
            dateFmt = '%d/%m'
        case 2:
            dateFmt = '%d.%m.%y'
        case 3:
            dateFmt = '%d/%m/%y'
        case _:
           dateFmt =  '%d.%m.'

    df = recording.labels[wear_idx]

    dates_df = pd.to_datetime(pd.Series(df.index.date, name='date')).dt.strftime(dateFmt)
    dates_df.index = df.index

    df = pd.concat([df, dates_df], axis=1)
    df = df.drop(columns=['p(deep)', 'p(light)', 'p(wake)'])

    df_counts = df.groupby(['date', 'sleep_stage']).size().unstack(fill_value=0)

    sns.set_theme()
    ax = df_counts.plot(kind='bar', stacked=True, figsize=(10, 5), color=coolwarm_palette)

    ax.set_title('Sleep stages distribution over time')
    plt.xticks(rotation=0)

    y_labels = ax.get_yticks()
    # ax.set_yticklabels([f"{int(y*30/(60*60))}" for y in y_labels])
    y_vals   = np.arange(0, ax.get_ylim()[1] + 1, 30*60)   # 30-min grid
    y_labels = [f"{int(t/3600)}" for t in y_vals]          # hours
    ax.set_yticks(y_vals)
    ax.set_yticklabels(y_labels)
    ax.set_ylabel('Hours')

    plt.legend(title='Sleep stages', bbox_to_anchor=(0.7, -0.1), ncols=3, frameon=False)

    plt.xlabel('')
    plt.tight_layout()

    return ax


def make_violin_fig(recording, wear_idx, settings):
    """
    Generates a violin plot figure to visualize sleep stage distribution over time.
    Parameters:
    recording (object): The recording object containing sleep data.
    wear_idx (int): The index of the wear period to be analyzed.
    settings (dict): A dictionary containing settings for the plot. 
                    Expected key is 'date_format' with possible values:
                    0 - '%d.%m.'
                    1 - '%d/%m'
                    2 - '%d.%m.%y'
                    3 - '%d/%m/%y'
    Returns:
    matplotlib.axes._subplots.AxesSubplot: The Axes object with the violin plot.
    """

    match settings['report']['quality']['date_format']:
        case 0:
            dateFmt = '%d.%m.'
        case 1:
            dateFmt = '%d/%m'
        case 2:
            dateFmt = '%d.%m.%y'
        case 3:
            dateFmt = '%d/%m/%y'
        case _:
           dateFmt =  '%d.%m.'

    df = recording.labels[wear_idx]

    dates_df = pd.to_datetime(pd.Series(df.index.date, name='date')).dt.strftime(dateFmt)
    dates_df.index = df.index

    df = pd.concat([df, dates_df], axis=1)

    fig, ax = plt.subplots(figsize=(10, 5))

    sns.violinplot(
        data=df, x='date',
        y='sdt', inner=None,
        ax=ax, zorder=2,
        color=coolwarm_palette[0]
    )

    ax.axhline(y=1.5, color='black', linestyle='--', zorder=3, alpha=1, linewidth=1)
    ax.axhline(y=2.5, color='black', linestyle='--', zorder=3, alpha=1, linewidth=1)

    ax.set_title('Sleep Stage Distribution Over Time')
    plt.yticks([1,2,3], ['Deep', 'Light', 'Wake'])
    plt.xlabel('')
    plt.ylabel('')
    plt.tight_layout()

    return ax


def make_main_fig(recording, wear_idx, settings, isMainPage):
    """
    Build the composite timeline figure for either the main page or a
    sub-page.

    Parameters
    ----------
    recording : SleepRecording
        Slice of data to plot (features + labels already attached).
    wear_idx  : pd.Series[bool]
        Boolean mask (same index as *recording*) marking wear periods.
    settings  : dict
        The full settings tree; reads visualisation + filtering keys.
    isMainPage : bool
        True → use the main-page visualisation options.
        False → use subsequent-page options.

    Returns
    -------
    fig : matplotlib.figure.Figure
    axes : list[matplotlib.axes.Axes]
        One Axes per panel; length depends on which sub-plots are enabled.
    """

    time = recording.timestamps
    features = recording.features
    sdt = recording.labels.loc[:, 'sdt']
    sdt_lower = recording.labels.loc[:, 'sdt_ci_lower']
    sdt_upper = recording.labels.loc[:, 'sdt_ci_upper']

    hypnogram = recording.labels.loc[:, 'sleep_stage'].replace({'wake':2, 'light':1, 'deep':0}).infer_objects(copy=False)

    if settings['report']['filtering']['median_filter']:
        window_size = settings['report']['filtering']['window_size'] * 2
        if window_size % 2 == 0:
            window_size += 1
        sdt = medfilt(sdt, kernel_size=window_size)
        sdt_lower = medfilt(sdt_lower, kernel_size=window_size)
        sdt_upper = medfilt(sdt_upper, kernel_size=window_size)

    sdt_plot = False # If sdt_plot = false, then we make a discrete hypnogram.
    sdt_ci = False
    activity_plot = False
    respiration_rate_plot = False
    position_plot = False

    if isMainPage:
        sdt_plot = settings['visualization']['main_page']['sdt']
        sdt_ci = settings['visualization']['main_page']['sdt_ci']
        activity_plot = settings['visualization']['main_page']['activity']
        respiration_rate_plot = settings['visualization']['main_page']['respiration_rate']
        position_plot = settings['visualization']['main_page']['position']
    else:
        sdt_plot = settings['visualization']['subsequent_pages']['sdt']
        sdt_ci = settings['visualization']['subsequent_pages']['sdt_ci']
        activity_plot = settings['visualization']['subsequent_pages']['activity']
        respiration_rate_plot = settings['visualization']['subsequent_pages']['respiration_rate']
        position_plot = settings['visualization']['subsequent_pages']['position']


    height_ratios = [4, 2 if activity_plot else 0, 2 if respiration_rate_plot else 0, 1 if position_plot else 0]
    height_ratios = [ratio for ratio in height_ratios if ratio > 0]

    if len(height_ratios) == 0:
        raise ValueError("No plots selected. Please select at least one plot to display.")

    fig, axes = plt.subplots(
        figsize=(12, 8),
        nrows=len(height_ratios),
        ncols=1, sharex=True,
        gridspec_kw={"height_ratios": height_ratios}
    )

    if len(height_ratios) == 1:
        axes = [axes]

    plot_idx = 0

    # PLOT #1: Sleep Depth or discrete hypnogram
    if sdt_plot:  # Plot SDT
        if settings['report']['filtering']['nonwear']:
            plot_segments(ax=axes[plot_idx], x=time, y=sdt, mask=wear_idx, color=coolwarm_palette[0])
            plot_segments(ax=axes[plot_idx], x=time, y=sdt, mask=~wear_idx, color=color_palette[-1])
            if sdt_ci:
                plot_CI_segments(ax=axes[plot_idx], x=time, CI=(sdt_lower, sdt_upper), mask=wear_idx, color=coolwarm_palette[-1])
                plot_CI_segments(ax=axes[plot_idx], x=time, CI=(sdt_lower, sdt_upper), mask=~wear_idx, color=color_palette[-1])
        else:
            axes[plot_idx].plot(time, sdt, color=coolwarm_palette[0])
            if sdt_ci:
                axes[plot_idx].fill_between(time, sdt_lower, sdt_upper, color=coolwarm_palette[-1], alpha=0.3)

        axes[plot_idx].axhline(y=1.5, color='black', linestyle='--', zorder=1, alpha=1, linewidth=1)
        axes[plot_idx].axhline(y=2.5, color='black', linestyle='--', zorder=1, alpha=1, linewidth=1)
        axes[plot_idx].set_ylim(0.5, 3.5)
        axes[plot_idx].set_yticks([1, 2, 3])
    else:  # Plot a discrete hypnogram instead
        if settings['report']['filtering']['nonwear']:
            plot_segments(ax=axes[plot_idx], x=time, y=hypnogram, mask=wear_idx, color=coolwarm_palette[0])
            plot_segments(ax=axes[plot_idx], x=time, y=hypnogram, mask=~wear_idx, color=color_palette[-1])
        else:
            axes[plot_idx].step(time, hypnogram, color=coolwarm_palette[0])
        axes[plot_idx].set_yticks([0, 1, 2])

    axes[plot_idx].set_yticklabels(["Deep", "Light", "Wake"])
    axes[plot_idx].set_title("Sleep depth")
    plot_idx += 1

    # PLOT #2: Activity
    if activity_plot:
        if settings['report']['filtering']['median_filter']:
            window_size = settings['report']['filtering']['window_size'] * 2
            if window_size % 2 == 0:
                window_size += 1
            activity_feature = medfilt(features.loc[:, 'activity'], kernel_size=window_size)
        else:
            activity_feature = features.loc[:, 'activity']

        if settings['report']['quality']['log_scale']:
            activity_feature = np.log10(np.abs(activity_feature))

        if settings['report']['filtering']['nonwear']:
            plot_segments(ax=axes[plot_idx], x=time, y=activity_feature, mask=wear_idx, color=coolwarm_palette[0])
            plot_segments(ax=axes[plot_idx], x=time, y=activity_feature, mask=~wear_idx, color=color_palette[-1])
        else:
            axes[plot_idx].plot(time, activity_feature, color=coolwarm_palette[0])

        axes[plot_idx].set_yticks([])
        axes[plot_idx].set_ylabel("Activity", rotation=90)
        plot_idx += 1

    # PLOT #3: Respiration rate
    if respiration_rate_plot:
        if settings['report']['filtering']['median_filter']:
            window_size = settings['report']['filtering']['window_size'] * 2
            if window_size % 2 == 0:
                window_size += 1
            respiration_rate_feature = medfilt(features.loc[:, 'resp_rate_y'], kernel_size=window_size)
        else:
            respiration_rate_feature = features.loc[:, 'resp_rate_y']

        if settings['report']['filtering']['nonwear']:
            plot_segments(ax=axes[plot_idx], x=time, y=respiration_rate_feature, mask=wear_idx, color=coolwarm_palette[0])
            plot_segments(ax=axes[plot_idx], x=time, y=respiration_rate_feature, mask=~wear_idx, color=color_palette[-1])
        else:
            axes[plot_idx].plot(time, respiration_rate_feature, color=coolwarm_palette[0])

        axes[plot_idx].set_yticks([])
        axes[plot_idx].set_ylabel("Respiration rate", rotation=90)
        plot_idx += 1  

    # PLOT #4: Body Position
    if position_plot:
        pos = features.loc[:, 'body_pos']
        axes[plot_idx].fill_between(time, 0, 1, where=(pos == 1), color=color_palette[0],
                                    transform=axes[plot_idx].get_xaxis_transform(), interpolate=True, label='Prone')
        axes[plot_idx].fill_between(time, 0, 1, where=(pos == 2), color=color_palette[3],
                                    transform=axes[plot_idx].get_xaxis_transform(), interpolate=True, label='Supine')
        axes[plot_idx].fill_between(time, 0, 1, where=(pos == 3), color=color_palette[2],
                                    transform=axes[plot_idx].get_xaxis_transform(), interpolate=True, label='Right side')
        axes[plot_idx].fill_between(time, 0, 1, where=(pos == 4), color="#a1c9f4",
                                    transform=axes[plot_idx].get_xaxis_transform(), interpolate=True, label='Left side')
        axes[plot_idx].fill_between(time, 0, 1, where=(pos == 5), color="#d0bbff",
                                    transform=axes[plot_idx].get_xaxis_transform(), interpolate=True, label='Head down')
        axes[plot_idx].fill_between(time, 0, 1, where=(pos == 6), color=color_palette[6],
                                    transform=axes[plot_idx].get_xaxis_transform(), interpolate=True, label='Head up')

        if settings['report']['filtering']['nonwear']:
            axes[plot_idx].fill_between(time, 0, 1, where=~wear_idx, color=color_palette[-1],
                                        transform=axes[plot_idx].get_xaxis_transform(), interpolate=True, label='Nonwear')

        axes[plot_idx].legend(loc='upper center', bbox_to_anchor=(0.5, -0.5), ncol=7, frameon=False)
        axes[plot_idx].set_yticks([])
        axes[plot_idx].set_ylabel("Posture", rotation=90)

    # X-axis formatting

    match settings['report']['quality']['date_format']:
        case 0:
            date_fmt = mdates.DateFormatter('%d.%m. %H')
        case 1:
            date_fmt = mdates.DateFormatter('%d/%m %H')
        case 2:
            date_fmt = mdates.DateFormatter('%d.%m.%y %H')
        case 3:
            date_fmt = mdates.DateFormatter('%d/%m/%y %H')
        case 4:
            date_fmt = mdates.DateFormatter('%H:%M')
        case _:
            date_fmt = mdates.DateFormatter('%H:%M')

    # if recording.duration <= pd.Timedelta(days=1):
    #     # If total duration is less than a day, show only hours and minutes
    #     date_fmt = mdates.DateFormatter('%H:%M')
    #     plt.locator_params(axis='x', nbins=12) 
    # else:
    #     #locator = mdates.AutoDateLocator(minticks=settings['report']['quality']['x_axis_ticks'], maxticks=settings['report']['quality']['x_axis_ticks'])
    #     locator = plt.gca().xaxis.get_major_locator()
    #     locator.set_params(nbins=settings['report']['quality']['x_axis_ticks'])  
    #     #plt.locator_params(axis='x', nbins=settings['report']['quality']['x_axis_ticks'])
    ax = plt.gca()
    if recording.duration <= pd.Timedelta(days=1):
        ax.xaxis.set_major_locator(
            mdates.AutoDateLocator(minticks=12, maxticks=12))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    else:
        nt = settings['report']['quality']['x_axis_ticks']
        ax.xaxis.set_major_locator(
            mdates.AutoDateLocator(minticks=nt, maxticks=nt))
        #axes[-1].xaxis.set_major_locator(locator)
        axes[-1].xaxis.set_major_formatter(date_fmt)

    #plt.tight_layout()
    return fig, axes
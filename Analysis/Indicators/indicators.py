def BollingerBands(df, window=20, std_dev=2):
    """
    Calculates Bollinger Bands for a given DataFrame.

    Args:
        df: A pandas DataFrame with a 'Close' column.
        window: The window size for the SMA.
        std_dev: The number of standard deviations for the bands.

    Returns:
        A DataFrame with columns for the SMA, upper band, and lower band.
    """

    df['SMA'] = df['c'].rolling(window=window).mean()
    df['STD'] = df['c'].rolling(window=window).std(ddof=0)

    df['UpperBand'] = round(df['SMA'] + (df['STD'] * std_dev), 5)
    df['LowerBand'] = round(df['SMA'] - (df['STD'] * std_dev), 5)

    return df


def RSI(df, period=14):
    """
    Calculates the Relative Strength Index (RSI) for a given DataFrame.

    Args:
        df: A pandas DataFrame with a 'Close' column.
        period: The period for calculating RSI.

    Returns:
        A pandas Series containing the RSI values.
    """

    delta = df['c'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    exponentially_smoothed_gain = gain.ewm(com=period - 1, adjust=False).mean()
    exponentially_smoothed_loss = loss.ewm(com=period - 1, adjust=False).mean()
    RS = exponentially_smoothed_gain / exponentially_smoothed_loss
    RSI = round(100.0 - (100.0 / (1.0 + RS)), 4)
    return RSI

def StochasticRSI(df, rsi_period = 14, stoch_period = 14, k_period = 3, d_period = 3):
    """
    Calculates the Stochastic RSI for a given DataFrame.

    Args:
        df: A pandas DataFrame with a 'Close' column.
        period: The period for calculating the Stochastic Oscillator.
        smooth_window: The window for smoothing the %K line.

    Returns:
        A pandas DataFrame with the Stochastic RSI values.
    """

    df['RSI'] = RSI(df, rsi_period)
    #
    # # Calculate %K
    # df['%K'] = round((df['RSI'] - df['RSI'].rolling(window=period).min()) / (
    #             df['RSI'].rolling(window=period).max() - df['RSI'].rolling(window=period).min()) * 100, 4)
    #
    # # Calculate %D (Smooth %K)
    # df['%D'] = df['%K'].rolling(window=smooth_window).mean()

    # Calculate StochRSI
    min_rsi = df['RSI'].rolling(window=stoch_period, min_periods=stoch_period).min()
    max_rsi = df['RSI'].rolling(window=stoch_period, min_periods=stoch_period).max()
    stoch_rsi = (df['RSI'] - min_rsi) / (max_rsi - min_rsi)

    # Calculate %K
    df['%K'] = round(stoch_rsi.rolling(window=k_period, min_periods=k_period).mean(), 4) * 100

    # Calculate %D
    df['%D'] = round(df['%K'].rolling(window=d_period, min_periods=d_period).mean(), 4)

    return df
import logging
import datetime

import pandas
import pandas_datareader

LOG = logging.getLogger(__name__)

PORTFOLIO_TICKERS = [
    'AAPL',
    'MSFT',
    'AMZN',
    'TSLA',
]


def prev_date(lookback: int) -> pandas.Timestamp:
    """Return a previous date from now"""
    return (pandas.Timestamp('now') - datetime.timedelta(lookback)).normalize()


def positions() -> pandas.DataFrame:
    """Return a fixture dataframe holding position quantities"""
    data = [
        [PORTFOLIO_TICKERS[0], prev_date(23), 'L', 37],
        [PORTFOLIO_TICKERS[1], prev_date(36), 'L', 65],
        [PORTFOLIO_TICKERS[2], prev_date(87), 'L', 5],
        [PORTFOLIO_TICKERS[3], prev_date(27), 'S', 34],
    ]

    df = pandas.DataFrame.from_records(data, columns=['ticker', 'purchase_date', 'position', 'quantity'])
    assert len(df) == len(PORTFOLIO_TICKERS), 'Not every ticker in portfolio has data'

    return df


def extract_price_yahoo(ticker: str) -> pandas.DataFrame:
    """Extract a historical timeseries of price for a specific ticker"""
    LOG.info(f'Extracting price time series for ticker - {ticker}')
    df = pandas_datareader.get_data_yahoo(ticker)

    df = df.reset_index()\
        .sort_values('Date', ascending=True)\
        .reset_index(drop=True)

    df.columns = [i.lower().replace(' ', '_') for i in df.columns]
    df['date'] = pandas.to_datetime(df['date'])

    return df


def portfolio() -> pandas.DataFrame:
    """Generate a dataframe containing key portfolio data (dummy data)"""
    def _load_prices(df):
        for ticker in df['ticker'].unique():
            prices = extract_price_yahoo(ticker)
            prices['ticker'] = ticker
            yield prices

    def _get_price(ticker, date):
        # Get a 'near enough' price to date provided
        df = prices[(prices['ticker'] == ticker) & (prices['date'] <= date)]\
            .sort_values('date', ascending=False)\
            .reset_index(drop=True)

        return df.iloc[0].close

    def _has_returns(row):
        if row['pct_change'] > 0 and row['position'] == 'L':
            return True
        elif row['pct_change'] < 0 and row['position'] == 'S':
            return True

        return False

    def _cash_return(row):
        # Return actual money made - handler for shorts
        if row['cash_diff'] < 0 and row['position'] == 'S':
            return abs(row['cash_diff'])
        elif row['cash_diff'] > 0 and row['position'] == 'S':
            return row['cash_diff'] * -1

        return row['cash_diff']

    df = positions()
    prices = pandas.concat(_load_prices(df))

    df['current_date'] = pandas.pandas.Timestamp('now').normalize()

    df = df.assign(
        current_price=df.apply(lambda row: _get_price(row['ticker'], row['current_date']), axis=1),
        purchase_price=df.apply(lambda row: _get_price(row['ticker'], row['purchase_date']), axis=1),
    )

    df['pct_change'] = ((df['purchase_price'] - df['current_price']) / df['current_price']) * 100

    df = df.assign(
        has_returns=df.apply(_has_returns, axis=1),
        purchase_value=(df['purchase_price'] * df['quantity']),
        current_value=(df['current_price'] * df['quantity']),
    )

    df['cash_diff'] = df['purchase_value'] - df['current_value']
    df['cash_return'] = df.apply(_cash_return, axis=1)

    return df

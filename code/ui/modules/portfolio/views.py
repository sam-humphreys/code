import random

import pandas
import flask

from code.ui import app
import code.ui.modules.portfolio.data


@app.route('/portfolio/live', methods=['GET'])
def portfolio_live():
    """Display live portfolio monitoring tools for the dummy portfolio"""
    df = code.ui.modules.portfolio.data.portfolio()

    df_objects = [row for row in df.itertuples(index=False)]
    df_html = df.set_index('ticker')\
        .drop('has_returns', axis=1)\
        .to_html(classes=["table-striped", "table", "table-hover", "table-bordered", "table-sm"])

    position_split = df.groupby('position').size().to_frame('count').reset_index().to_dict('records')
    value_data = df[['ticker', 'purchase_value', 'current_value']].to_dict('records')

    return flask.render_template(
        template_name_or_list='portfolio/live.html',
        df_objects=df_objects,
        table_data=df_html,
        position_split=position_split,
        value_data=value_data,
    )


@app.route('/portfolio/historical_prices', methods=['GET'])
def portfolio_historical_prices():
    """Display historical close price time series for a specific ticker"""
    ticker = flask.request.args.get('ticker', default=None, type=str)
    if not ticker:
        # Randomly choose a ticker if one has not been specified
        ticker = random.choice(code.ui.modules.portfolio.data.PORTFOLIO_TICKERS)

    df = code.ui.modules.portfolio.data.extract_price_yahoo(ticker)
    df['date'] = df['date'].dt.strftime('%Y-%m-%d')  # Amcharts uses string date

    df_html = df.set_index('date').to_html(classes=["table-striped", "table", "table-hover", "table-bordered", "table-sm"])
    df_dict = df[['date', 'close']].to_dict('records')

    return flask.render_template(
        template_name_or_list='portfolio/historical_price.html',
        table_data=df_html,
        chart_data=df_dict,
        selected_ticker=ticker,
        tickers=code.ui.modules.portfolio.data.PORTFOLIO_TICKERS,
    )


@app.route('/portfolio/price_download/<string:ticker>')
def download_price_csv(ticker):
    """Download pricing for a selected ticker"""
    name = pandas.Timestamp('now').strftime('%Y%m%d-%H%M%S')
    df = code.ui.modules.portfolio.data.extract_price_yahoo(ticker)

    # Make response
    response = flask.make_response(df.to_csv(index=False))
    response.headers["Content-Disposition"] = f"attachment; filename={name}-{ticker}-prices.csv"
    response.headers["Content-Type"] = "text/csv"

    return response

from flask import Flask, render_template, request
import numpy as np
import pandas as pd
import seaborn as sb
import plotly
import plotly.graph_objs as go
# Data dari flask di kirim ke browser dalam bentuk json
import json
from joblib import dump, load

app = Flask(__name__)

# Sumber data
idx = pd.read_csv('idx_findata_ratios.csv')
idx = idx.head(100)

@app.route('/')
def home():
    return render_template('home.html')

# Render Picture
# @app.route('/static/<path:x>')
# def gal(x):
#     return send_from_directory("static",x)

# Render About page
@app.route('/about')
def about():
    return render_template('about.html')

# # # # # # # # # #
# HISTOGRAM & BOX #
# # # # # # # # # #

def category_plot(cat_plot = 'histplot', cat_x = 'SECTOR', cat_y = 'PER', estimator = 'count', hue = 'YEAR'):
    
    idx = pd.read_csv('idx_findata_ratios.csv')

    if cat_plot == 'histplot':

        data = []

        for val in idx[hue].unique():
            hist = go.Histogram(
                x=idx[idx[hue] == val][cat_x], # Series
                y=idx[idx[hue] == val][cat_y],
                histfunc= estimator,
                name = val
            )
            
            data.append(hist)

            title = 'Histogram'

    elif cat_plot == 'boxplot':
        data = []

        for val in idx[hue].unique():
            box = go.Box(
                x=idx[idx[hue] == val][cat_x], # Series
                y=idx[idx[hue] == val][cat_y],
                name = val
            )
            
            data.append(box)

            title = 'Box'
    
    layout = go.Layout(
        title=title,
        xaxis=dict(title=cat_x),
        yaxis=dict(title=cat_y),
        boxmode='group'
    )

    res = {"data" : data, "layout" : layout}

    graphJSON = json.dumps(res,cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON

@app.route('/')
def index():
    plot = category_plot()

    # Dropdown Menu
    list_plot = [('histplot', 'Histogram' ), ('boxplot', 'Box')]
    list_x = [('SECTOR', 'Sector'), ('SUBSECTOR', 'SubSector'), ('YEAR', 'Year'), ('Category', 'Category')]
    list_y = [('ASSETS', 'Assets'), ('LIABILITIES', 'Liabilities'), ('EQUITY', 'Equity'), ('SALES', 'Sales'), ('EBT', 'EBT'), ('PROFIT_FOR_THE_PERIOD', 'EAT'), ('EPS', 'EPS'), ('BOOK_VALUE', 'BookValue'), ('PER', 'PER'), ('PBV', 'PBV'), ('DER', 'DER'), ('ROA', 'ROA'), ('ROE', 'ROE'), ('NPM', 'NPM')]
    list_est = [('count', 'Count'), ('sum', 'Sum'),('avg','Average'), ('min', 'Minimum'), ('max', 'Maximum')]
    list_hue = [('SECTOR', 'Sector'), ('SUBSECTOR', 'SubSector'), ('YEAR', 'Year'), ('Category', 'Category')]
    return render_template(
        'category.html', 
        plot=plot, 
        focus_plot='histplot', 
        focus_x='SECTOR',
        focus_y='PER',
        focus_estimator='count',
        focus_hue = 'YEAR',
        drop_plot = list_plot,
        drop_x = list_x,
        drop_y = list_y,
        drop_estimator = list_est,
        drop_hue = list_hue)

@app.route('/cat_fn/<nav>')
def cat_fn(nav):
    
    if nav == 'True': # Saat klik menu navigasi
        cat_plot = 'histplot'
        cat_x = 'SECTOR'
        cat_y = 'PER'
        estimator = 'count'
        hue = 'YEAR'

    else : # Saat memilih value dari form
        cat_plot = request.args.get('cat_plot')
        cat_x = request.args.get('cat_x')
        cat_y = request.args.get('cat_y')
        estimator = request.args.get('estimator')
        hue = request.args.get('hue')

    # Dari boxplot ke histogram akan None
    if estimator == None:
        estimator = 'count'

    # Saat estimator count, dropdown menu sumbu Y menjadi disabled dan memberikan nilai None 
    if cat_y == None:
        cat_y = 'PER'

    # Dropdown Menu
    list_plot = [('histplot', 'Histogram' ), ('boxplot', 'Box')]
    list_x = [('SECTOR', 'Sector'), ('SUBSECTOR', 'SubSector'), ('YEAR', 'Year'), ('Category', 'Category')]
    list_y = [('ASSETS', 'Assets'), ('LIABILITIES', 'Liabilities'), ('EQUITY', 'Equity'), ('SALES', 'Sales'), ('EBT', 'EBT'), ('PROFIT_FOR_THE_PERIOD', 'EAT'), ('EPS', 'EPS'), ('BOOK_VALUE', 'BookValue'), ('PER', 'PER'), ('PBV', 'PBV'), ('DER', 'DER'), ('ROA', 'ROA'), ('ROE', 'ROE'), ('NPM', 'NPM')]
    list_est = [('count', 'Count'), ('sum', 'Sum'),('avg','Average'), ('min', 'Minimum'), ('max', 'Maximum')]
    list_hue = [('SECTOR', 'Sector'), ('SUBSECTOR', 'SubSector'), ('YEAR', 'Year'), ('Category', 'Category')]

    plot = category_plot(cat_plot, cat_x, cat_y, estimator, hue)
    return render_template(
        'category.html', 
        plot=plot, 
        focus_plot=cat_plot, 
        focus_x=cat_x, 
        focus_y=cat_y, 
        focus_estimator=estimator,
        focus_hue = hue,
        drop_plot = list_plot,
        drop_x = list_x,
        drop_y = list_y,
        drop_estimator = list_est,
        drop_hue = list_hue
    )

# # # # # #
# SCATTER # 
# # # # # #

def scatter_plot(cat_x, cat_y , hue):

    idx = pd.read_csv('idx_findata_ratios.csv')

    data = []

    for val in idx[hue].unique():
        scatt = go.Scatter(
            x = idx[idx[hue] == val][cat_x],
            y = idx[idx[hue] == val][cat_y],
            mode = 'markers',
            name = val
        )
    
        data.append(scatt)

    layout = go.Layout(
        title='Scatter',
        title_x=0.5,
        xaxis=dict(title=cat_x),
        yaxis=dict(title=cat_y)
    )

    res = {"data" : data, "layout" : layout}

    graphJSON = json.dumps(res,cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON

@app.route('/scatt_fn')
def scatt_fn():
    cat_x = request.args.get('cat_x')
    cat_y = request.args.get('cat_y')
    hue = request.args.get('hue')

    if cat_x == None and cat_y == None and hue == None:
        cat_x = 'SALES'
        cat_y = 'PROFIT_FOR_THE_PERIOD'
        hue = 'YEAR'

    # Dropdown Menu
    list_x = [('ASSETS', 'Assets'), ('LIABILITIES', 'Liabilities'), ('EQUITY', 'Equity'), ('SALES', 'Sales'), ('EBT', 'EBT'), ('PROFIT_FOR_THE_PERIOD', 'EAT'), ('EPS', 'EPS'), ('BOOK_VALUE', 'BookValue'), ('PER', 'PER'), ('PBV', 'PBV'), ('DER', 'DER'), ('ROA', 'ROA'), ('ROE', 'ROE'), ('NPM', 'NPM')]
    list_y = [('ASSETS', 'Assets'), ('LIABILITIES', 'Liabilities'), ('EQUITY', 'Equity'), ('SALES', 'Sales'), ('EBT', 'EBT'), ('PROFIT_FOR_THE_PERIOD', 'EAT'), ('EPS', 'EPS'), ('BOOK_VALUE', 'BookValue'), ('PER', 'PER'), ('PBV', 'PBV'), ('DER', 'DER'), ('ROA', 'ROA'), ('ROE', 'ROE'), ('NPM', 'NPM')]
    list_hue = [('SECTOR', 'Sector'), ('SUBSECTOR', 'SubSector'), ('YEAR', 'Year'), ('Category', 'Category')]

    plot = scatter_plot(cat_x, cat_y, hue)   

    return render_template(
        'scatter.html', 
        plot=plot, 
        focus_x=cat_x, 
        focus_y=cat_y,
        focus_hue = hue,
        drop_x = list_x,
        drop_y = list_y,
        drop_hue = list_hue
    )


# # # #
# PIE #
# # # #

def pie_plot(hue = 'Category'):
    
    idx = pd.read_csv('idx_findata_ratios.csv')

    vcounts = idx[hue].value_counts()

    labels = []
    values = []

    for item in vcounts.iteritems():
        labels.append(item[0])
        values.append(item[1])

    data = [
        go.Pie(
            labels=labels,
            values=values
        )
    ]

    layout = go.Layout(title='Pie', title_x = 0.48)

    res = {"data" : data, "layout" : layout}

    graphJSON = json.dumps(res,cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON


@app.route('/pie_fn')
def pie_fn():
    hue = request.args.get('hue')

    if hue == None:
        hue = 'Category'

    # Dropdown Menu
    list_hue = [('SECTOR', 'Sector'), ('SUBSECTOR', 'SubSector'), ('YEAR', 'Year'), ('Category', 'Category')]

    plot = pie_plot(hue)
    return render_template('pie.html', plot=plot, focus_hue=hue, drop_hue = list_hue)

# Prediction Page
@app.route('/predict')
def predict():
    return render_template('predict.html')

# Result Page
@app.route('/Stocks_Valuation_Result', methods=["POST", "GET"])
def idx_Loan_predict():
    if request.method == "POST":
        input = request.form
        sales = int(request.form['SALES'])
        profit = int(request.form['PROFIT_FOR_THE_PERIOD'])
        bookvalue = int(request.form['BOOK_VALUE'])
        PER = float(request.form['PER'])
        ROA = float(request.form['ROA'])
        ROE = float(request.form['ROE'])
        Sector = request.form['SECTOR']
        SectorCode=0
        if Sector == 'AGRICULTURE':
            SectorCode=0
        elif Sector == 'BASIC INDUSTRY AND CHEMICALS':
            SectorCode=1
        elif Sector == 'CONSUMER GOODS INDUSTRY':
            SectorCode=2
        elif Sector == 'FINANCE':
            SectorCode=3
        elif Sector == 'INFRASTRUCTURE, UTILITIES AND TRANSPORTATION':
            SectorCode=4
        elif Sector == 'MINING':
            SectorCode=5
        elif Sector == 'MISCELLANEOUS INDUSTRY':
            SectorCode=6
        elif Sector == 'PROPERTY, REAL ESTATE AND BUILDING CONSTRUCTION':
            SectorCode=7
        elif Sector == 'TRADE, SERVICES & INVESTMENT':
            SectorCode=8
# Term, NewExist, GrAppv, SBA_Appv, RevLineCr, Lowdoc, NAICS_11
        pred = best.predict(pd.DataFrame([sales, profit, bookvalue, PER, ROA, ROE, SectorCode]).transpose())[0]
        
        pred_and_proba = f"{'Overvalued' if pred == 1 else 'Not Overvalued'}"

        return render_template('result.html',
        data=input, prediction=pred_and_proba, sales=sales,
        profit=profit, bookvalue=bookvalue,
        PER=PER, ROA=ROA,
        ROE=ROE, Sector=Sector)

if __name__ == '__main__':
    best = load('best_tpot.joblib')
    app.run(debug=True, port=4000)
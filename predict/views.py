# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render,HttpResponseRedirect
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg
from django.http import HttpResponse
import pandas as pd
import matplotlib as mpl
mpl.use('Agg') # Required to redirect locally
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import quandl
import cStringIO
import fbprophet

ticker = ' '

def history(request):
    return render(request,'history.html')

def stock(request):
    return render(request,'predict.html')

def contrast(request):
    return render(request,'form3.html')

def show_graph(request):
    quandl.ApiConfig.api_key = 'hSBzwas1PTzHyjs58m3G'
    print "here in show_graph"
    ticker = request.POST.get('ticker')
    tesla = quandl.get('WIKI/'+ticker)
    plt.plot(tesla.index, tesla['Adj. Close'], 'r')
    plt.title(ticker +' Stock Price')
    plt.ylabel('Price ($)');
    f = cStringIO.StringIO()
    plt.savefig(f, format="png", facecolor=(0.95,0.95,0.95))
    plt.clf()
    return HttpResponse(f.getvalue(), content_type="image/png")

def home_page(request):
	return render(request,'home.html')

def contrast_caps(request):
    quandl.ApiConfig.api_key = 'hSBzwas1PTzHyjs58m3G'
    ticker1 = request.POST.get('ticker1')
    ticker2 = request.POST.get('ticker2')
    print ticker1
    print ticker2
    tesla = quandl.get('WIKI/'+ticker1)
    gm = quandl.get('WIKI/'+ticker2)
    tesla = tesla["2010":]
    gm = gm["2010":]
    # Yearly average number of shares outstanding for Tesla and GM
    tesla_shares = {2018: 168e6, 2017: 162e6, 2016: 144e6, 2015: 128e6, 2014: 125e6, 
    2013: 119e6, 2012: 107e6, 2011: 100e6, 2010: 51e6}

    gm_shares = {2018: 1.42e9, 2017: 1.50e9, 2016: 1.54e9, 2015: 1.59e9, 2014: 1.61e9, 
    2013: 1.39e9, 2012: 1.57e9, 2011: 1.54e9, 2010: 1.50e9}
    
    apple_shares = {2018: 4.927e9, 2017: 5.252e9, 2016: 5.5e9, 2015: 5.793e9, 2014: 6.123e9, 
                2013: 6.522e9, 2012: 6.617e9, 2011: 6.557e9, 2010: 6.473e9}

    company1_shares = {}
    company2_shares = {}
    if ticker1 == 'TSLA':
        company1_shares = tesla_shares
    elif ticker1 == 'GM':
        company1_shares = gm_shares
    else:
        company1_shares = apple_shares

    if ticker2 == 'TSLA':
        company2_shares = tesla_shares
    elif ticker2 == 'GM':
        company2_shares = gm_shares
    else:
        company2_shares = apple_shares 

    # Create a year column 
    tesla['Year'] = tesla.index.year

    # Take Dates from index and move to Date column 
    tesla.reset_index(inplace = True)
    tesla['cap'] = 0

    # Calculate market cap for all years
    for i, year in enumerate(tesla['Year']):
        # Retrieve the shares for the year
        shares = company1_shares.get(year)
        
        # Update the cap column to shares times the price
        tesla.ix[i, 'cap'] = shares * tesla.ix[i, 'Adj. Close']
    
    	# Create a year column 
    gm['Year'] = gm.index.year
    
    # Take Dates from index and move to Date column 
    gm.reset_index(inplace = True)
    gm['cap'] = 0
    
    for i, year in enumerate(gm['Year']):
        # Retrieve the shares for the year
        shares = company2_shares.get(year)
        
        # Update the cap column to shares times the price
        gm.ix[i, 'cap'] = shares * gm.ix[i, 'Adj. Close']
    
	# Merge the two datasets and rename the columns
    cars = gm.merge(tesla, how='inner', on='Date')
    cars.rename(columns={'cap_x': 'gm_cap', 'cap_y': 'tesla_cap'}, inplace=True)
    	# Select only the relevant columns
    cars = cars.ix[:, ['Date', 'gm_cap', 'tesla_cap']]

    # Divide to get market cap in billions of dollars
    cars['gm_cap'] = cars['gm_cap'] / 1e9
    cars['tesla_cap'] = cars['tesla_cap'] / 1e9

    plt.figure(figsize=(10, 8))
    plt.plot(cars['Date'], cars['gm_cap'], 'b-', label = ticker2)
    plt.plot(cars['Date'], cars['tesla_cap'], 'r-', label = ticker1)
    plt.xlabel('Date'); plt.ylabel('Market Cap (Billions $)'); plt.title('Market Cap of ' + ticker2 + 'and ' + ticker1)
    plt.legend()
    
    f = cStringIO.StringIO()
    plt.savefig(f, format="png", facecolor=(0.95,0.95,0.95))
    plt.clf()
    return HttpResponse(f.getvalue(), content_type="image/png")

def predict_caps(request):
    plt.clf()
    quandl.ApiConfig.api_key = 'hSBzwas1PTzHyjs58m3G'
    ticker2 = request.POST.get('ticker2')
    gm = quandl.get('WIKI/'+ticker2)
    gm = gm["2010":]
    
    # Yearly average number of shares outstanding for Tesla and GM
    tesla_shares = {2018: 168e6, 2017: 162e6, 2016: 144e6, 2015: 128e6, 2014: 125e6, 
    2013: 119e6, 2012: 107e6, 2011: 100e6, 2010: 51e6}

    gm_shares = {2018: 1.42e9, 2017: 1.50e9, 2016: 1.54e9, 2015: 1.59e9, 2014: 1.61e9, 
    2013: 1.39e9, 2012: 1.57e9, 2011: 1.54e9, 2010: 1.50e9}

    apple_shares = {2018: 4.927e9, 2017: 5.252e9, 2016: 5.5e9, 2015: 5.793e9, 2014: 6.123e9, 
                2013: 6.522e9, 2012: 6.617e9, 2011: 6.557e9, 2010: 6.473e9}
    
    company_shares = {}

    if ticker2 == 'TSLA':
        company_shares = tesla_shares
    elif ticker2 == 'GM':
        company_shares = gm_shares
    else:
        company_shares = apple_shares
    # Create a year column 
    gm['Year'] = gm.index.year
    
    # Take Dates from index and move to Date column 
    gm.reset_index(inplace = True)

    gm['cap'] = 0
    
    for i, year in enumerate(gm['Year']):
        # Retrieve the shares for the year
        shares = company_shares.get(year)
        
        # Update the cap column to shares times the price
        gm.ix[i, 'cap'] = shares * gm.ix[i, 'Adj. Close']
    
    # Prophet requires columns ds (Date) and y (value)
    gm = gm.rename(columns={'Date': 'ds', 'cap': 'y'})
    # Put market cap in billions
    gm['y'] = gm['y'] / 1e9

    # Make the prophet models and fit on the data
    # changepoint_prior_scale can be changed to achieve a better fit
    gm_prophet = fbprophet.Prophet(changepoint_prior_scale=0.05)
    gm_prophet.fit(gm)

    # Make a future dataframe for 2 years
    gm_forecast = gm_prophet.make_future_dataframe(periods=365 * 2, freq='D')
    # Make predictions
    gm_forecast = gm_prophet.predict(gm_forecast)
    gm_prophet.plot(gm_forecast, xlabel = 'Date', ylabel = 'Market Cap (billions $)')

    plt.title('Market Cap of '+ ticker2);
    fi = cStringIO.StringIO()
    plt.savefig(fi, format="png", facecolor=(0.95,0.95,0.95))
    plt.clf()
    return HttpResponse(fi.getvalue(), content_type="image/png")
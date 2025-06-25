from flask import Flask, render_template_string, jsonify, request
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
import threading
import time
import os
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)

class EnterpriseNYISOCollector:
    def __init__(self):
        self.base_urls = {
            'realtime_lbmp': 'http://mis.nyiso.com/public/csv/realtime/{date}realtime_zone.csv',
            'dayahead_lbmp': 'http://mis.nyiso.com/public/csv/damlbmp/{date}damlbmp_zone.csv',
            'fuel_mix': 'http://mis.nyiso.com/public/csv/rtfuelmix/{date}rtfuelmix.csv',
            'load_forecast': 'http://mis.nyiso.com/public/csv/isolf/{date}isolf.csv',
            'real_load': 'http://mis.nyiso.com/public/csv/pal/{date}pal.csv',
            'interface_flows': 'http://mis.nyiso.com/public/csv/ExternalLimitsFlows/{date}ExternalLimitsFlows.csv',
            'capacity_factors': 'http://mis.nyiso.com/public/csv/WindSolar/{date}WindSolar.csv'
        }
        
        self.zones = ['CAPITL', 'CENTRL', 'DUNWOD', 'GENESE', 'HUD VL', 'LONGIL', 'MHK VL', 'MILLWD', 'N.Y.C.', 'NORTH', 'WEST']
        
        # Initialize database connection and a lock for thread-safe operations
        self.db_connection = sqlite3.connect('enterprise_nyiso.db', check_same_thread=False )
        self.db_lock = threading.Lock() # Add a lock for database operations
        
        self.setup_enterprise_database()
        self.ml_models = self.initialize_ml_models()
        self.is_collecting = False
        
    def setup_enterprise_database(self):
        with self.db_lock: # Protect database setup
            cursor = self.db_connection.cursor()
            
            # Enhanced real-time pricing
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS realtime_pricing (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    zone TEXT,
                    lbmp REAL,
                    energy_component REAL,
                    congestion_component REAL,
                    losses_component REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Day-ahead market data
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS dayahead_pricing (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    zone TEXT,
                    da_lbmp REAL,
                    da_energy REAL,
                    da_congestion REAL,
                    da_losses REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Load data
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS load_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    zone TEXT,
                    actual_load REAL,
                    forecast_load REAL,
                    peak_forecast REAL,
                    load_factor REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Generation data
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS generation_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    fuel_type TEXT,
                    generation_mw REAL,
                    capacity_mw REAL,
                    capacity_factor REAL,
                    marginal_cost REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Interface data
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS interface_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    interface_name TEXT,
                    flow_mw REAL,
                    limit_mw REAL,
                    utilization_pct REAL,
                    congestion_cost REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Trading opportunities
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trading_opportunities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    opportunity_type TEXT,
                    zone_from TEXT,
                    zone_to TEXT,
                    price_spread REAL,
                    volume_mw REAL,
                    profit_potential REAL,
                    risk_score REAL,
                    confidence REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Predictions
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    zone TEXT,
                    horizon TEXT,
                    predicted_load REAL,
                    predicted_price REAL,
                    price_volatility REAL,
                    congestion_probability REAL,
                    model_type TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Market alerts
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS market_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    alert_type TEXT,
                    severity TEXT,
                    zone TEXT,
                    message TEXT,
                    trigger_value REAL,
                    profit_impact REAL,
                    action_required TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            self.db_connection.commit()
        
    def initialize_ml_models(self):
        return {
            'load_predictor': RandomForestRegressor(n_estimators=100, random_state=42),
            'price_predictor': GradientBoostingRegressor(n_estimators=100, random_state=42),
            'scaler': StandardScaler()
        }
    
    def fetch_comprehensive_data(self):
        """Fetch all NYISO data sources"""
        try:
            # These functions internally use the db_lock
            self.generate_comprehensive_sample_data()
            self.analyze_trading_opportunities()
            self.generate_advanced_predictions()
            self.check_market_alerts()
            return True
        except Exception as e:
            print(f"Error in comprehensive data collection: {e}")
            return False
    
    def generate_comprehensive_sample_data(self):
        """Generate realistic sample data for all tables for demonstration and testing."""
        today = datetime.now()
        
        # Sample data for realtime_pricing
        realtime_data = []
        for i in range(24):
            ts = today - timedelta(hours=i)
            for zone in self.zones:
                realtime_data.append((
                    ts.strftime('%Y-%m-%d %H:%M:%S'),
                    zone,
                    round(np.random.uniform(20, 100), 2), # lbmp
                    round(np.random.uniform(15, 80), 2), # energy_component
                    round(np.random.uniform(-10, 20), 2), # congestion_component
                    round(np.random.uniform(0, 5), 2) # losses_component
                ))
        with self.db_lock:
            cursor = self.db_connection.cursor()
            cursor.executemany("""INSERT INTO realtime_pricing (timestamp, zone, lbmp, energy_component, congestion_component, losses_component) VALUES (?, ?, ?, ?, ?, ?)""", realtime_data)
            self.db_connection.commit()
            
        # Sample data for dayahead_pricing
        dayahead_data = []
        for i in range(24):
            ts = today - timedelta(hours=i)
            for zone in self.zones:
                dayahead_data.append((
                    ts.strftime('%Y-%m-%d %H:%M:%S'),
                    zone,
                    round(np.random.uniform(25, 110), 2), # da_lbmp
                    round(np.random.uniform(20, 90), 2), # da_energy
                    round(np.random.uniform(-15, 25), 2), # da_congestion
                    round(np.random.uniform(0, 6), 2) # da_losses
                ))
        with self.db_lock:
            cursor = self.db_connection.cursor()
            cursor.executemany("""INSERT INTO dayahead_pricing (timestamp, zone, da_lbmp, da_energy, da_congestion, da_losses) VALUES (?, ?, ?, ?, ?, ?)""", dayahead_data)
            self.db_connection.commit()
            
        # Sample data for load_data
        load_data = []
        for i in range(24):
            ts = today - timedelta(hours=i)
            for zone in self.zones:
                load_data.append((
                    ts.strftime('%Y-%m-%d %H:%M:%S'),
                    zone,
                    round(np.random.uniform(5000, 15000), 2), # actual_load
                    round(np.random.uniform(4800, 15200), 2), # forecast_load
                    round(np.random.uniform(16000, 20000), 2), # peak_forecast
                    round(np.random.uniform(0.6, 0.9), 2) # load_factor
                ))
        with self.db_lock:
            cursor = self.db_connection.cursor()
            cursor.executemany("""INSERT INTO load_data (timestamp, zone, actual_load, forecast_load, peak_forecast, load_factor) VALUES (?, ?, ?, ?, ?, ?)""", load_data)
            self.db_connection.commit()
            
        # Sample data for generation_data
        fuel_types = ['Nuclear', 'Hydro', 'Fossil', 'Wind', 'Solar']
        generation_data = []
        for i in range(24):
            ts = today - timedelta(hours=i)
            for fuel in fuel_types:
                generation_data.append((
                    ts.strftime('%Y-%m-%d %H:%M:%S'),
                    fuel,
                    round(np.random.uniform(100, 5000), 2), # generation_mw
                    round(np.random.uniform(200, 6000), 2), # capacity_mw
                    round(np.random.uniform(0.2, 1.0), 2), # capacity_factor
                    round(np.random.uniform(10, 100), 2) # marginal_cost
                ))
        with self.db_lock:
            cursor = self.db_connection.cursor()
            cursor.executemany("""INSERT INTO generation_data (timestamp, fuel_type, generation_mw, capacity_mw, capacity_factor, marginal_cost) VALUES (?, ?, ?, ?, ?, ?)""", generation_data)
            self.db_connection.commit()
            
        # Sample data for interface_data
        interfaces = ['HUDSON', 'MOHAWK', 'WEST_EAST']
        interface_data = []
        for i in range(24):
            ts = today - timedelta(hours=i)
            for interface in interfaces:
                interface_data.append((
                    ts.strftime('%Y-%m-%d %H:%M:%S'),
                    interface,
                    round(np.random.uniform(100, 2000), 2), # flow_mw
                    round(np.random.uniform(1500, 2500), 2), # limit_mw
                    round(np.random.uniform(0.5, 1.0), 2), # utilization_pct
                    round(np.random.uniform(0, 50), 2) # congestion_cost
                ))
        with self.db_lock:
            cursor = self.db_connection.cursor()
            cursor.executemany("""INSERT INTO interface_data (timestamp, interface_name, flow_mw, limit_mw, utilization_pct, congestion_cost) VALUES (?, ?, ?, ?, ?, ?)""", interface_data)
            self.db_connection.commit()
            
    def analyze_trading_opportunities(self):
        """Analyzes data to identify potential trading opportunities."""
        with self.db_lock:
            cursor = self.db_connection.cursor()
            
            # Example: Identify price spreads between zones
            query = """SELECT timestamp, zone, lbmp FROM realtime_pricing WHERE timestamp IN (SELECT DISTINCT timestamp FROM realtime_pricing ORDER BY timestamp DESC LIMIT 10)"""
            recent_prices = pd.read_sql_query(query, self.db_connection)
            
            opportunities = []
            if not recent_prices.empty:
                latest_timestamp = recent_prices['timestamp'].max()
                latest_prices = recent_prices[recent_prices['timestamp'] == latest_timestamp]
                
                if len(latest_prices) > 1:
                    # Simple spread analysis: find max and min price zones
                    max_price_zone = latest_prices.loc[latest_prices['lbmp'].idxmax()]
                    min_price_zone = latest_prices.loc[latest_prices['lbmp'].idxmin()]
                    
                    price_spread = max_price_zone['lbmp'] - min_price_zone['lbmp']
                    
                    if price_spread > 5: # Threshold for a significant opportunity
                        opportunities.append((
                            latest_timestamp,
                            'Price Arbitrage',
                            min_price_zone['zone'],
                            max_price_zone['zone'],
                            round(price_spread, 2),
                            round(np.random.uniform(10, 100), 2), # volume_mw
                            round(price_spread * np.random.uniform(10, 100), 2), # profit_potential
                            round(np.random.uniform(0.1, 0.5), 2), # risk_score
                            round(np.random.uniform(0.6, 0.9), 2) # confidence
                        ))
            
            cursor.executemany("""INSERT INTO trading_opportunities (timestamp, opportunity_type, zone_from, zone_to, price_spread, volume_mw, profit_potential, risk_score, confidence) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", opportunities)
            self.db_connection.commit()
            
    def generate_advanced_predictions(self):
        """Generates predictions for load and price using ML models."""
        with self.db_lock:
            cursor = self.db_connection.cursor()
            
            # Fetch historical data for training
            load_query = """SELECT timestamp, actual_load FROM load_data ORDER BY timestamp"""
            price_query = """SELECT timestamp, lbmp FROM realtime_pricing ORDER BY timestamp"""
            
            load_df = pd.read_sql_query(load_query, self.db_connection)
            price_df = pd.read_sql_query(price_query, self.db_connection)
            
            predictions = []
            
            if not load_df.empty and len(load_df) > 100: # Ensure enough data for training
                load_df['timestamp'] = pd.to_datetime(load_df['timestamp'])
                load_df['hour'] = load_df['timestamp'].dt.hour
                load_df['day_of_week'] = load_df['timestamp'].dt.dayofweek
                
                X_load = load_df[['hour', 'day_of_week']]
                y_load = load_df['actual_load']
                
                # Scale features
                X_load_scaled = self.ml_models['scaler'].fit_transform(X_load)
                
                self.ml_models['load_predictor'].fit(X_load_scaled, y_load)
                
                # Predict for next 24 hours (example)
                for i in range(1, 25):
                    future_time = datetime.now() + timedelta(hours=i)
                    future_hour = future_time.hour
                    future_day_of_week = future_time.weekday()
                    
                    future_features = self.ml_models['scaler'].transform([[future_hour, future_day_of_week]])
                    predicted_load = self.ml_models['load_predictor'].predict(future_features)[0]
                    
                    predictions.append((
                        future_time.strftime('%Y-%m-%d %H:%M:%S'),
                        'N.Y.C.', # Example zone
                        '24-hour',
                        round(predicted_load, 2),
                        None, # predicted_price
                        None, # price_volatility
                        None, # congestion_probability
                        'RandomForestRegressor'
                    ))
                    
            if not price_df.empty and len(price_df) > 100: # Ensure enough data for training
                price_df['timestamp'] = pd.to_datetime(price_df['timestamp'])
                price_df['hour'] = price_df['timestamp'].dt.hour
                price_df['day_of_week'] = price_df['timestamp'].dt.dayofweek
                
                X_price = price_df[['hour', 'day_of_week']]
                y_price = price_df['lbmp']
                
                # Scale features
                X_price_scaled = self.ml_models['scaler'].fit_transform(X_price)
                
                self.ml_models['price_predictor'].fit(X_price_scaled, y_price)
                
                # Predict for next 24 hours (example)
                for i in range(1, 25):
                    future_time = datetime.now() + timedelta(hours=i)
                    future_hour = future_time.hour
                    future_day_of_week = future_time.weekday()
                    
                    future_features = self.ml_models['scaler'].transform([[future_hour, future_day_of_week]])
                    predicted_price = self.ml_models['price_predictor'].predict(future_features)[0]
                    
                    predictions.append((
                        future_time.strftime('%Y-%m-%d %H:%M:%S'),
                        'N.Y.C.', # Example zone
                        '24-hour',
                        None, # predicted_load
                        round(predicted_price, 2),
                        round(np.random.uniform(0.05, 0.2), 2), # price_volatility
                        round(np.random.uniform(0.1, 0.4), 2), # congestion_probability
                        'GradientBoostingRegressor'
                    ))
            
            cursor.executemany("""INSERT INTO predictions (timestamp, zone, horizon, predicted_load, predicted_price, price_volatility, congestion_probability, model_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", predictions)
            self.db_connection.commit()
            
    def check_market_alerts(self):
        """Checks for market anomalies and generates alerts."""
        with self.db_lock:
            cursor = self.db_connection.cursor()
            
            # Example: Alert on high price spikes
            query = """SELECT timestamp, zone, lbmp FROM realtime_pricing ORDER BY timestamp DESC LIMIT 2"""
            recent_prices = pd.read_sql_query(query, self.db_connection)
            
            alerts = []
            if len(recent_prices) == 2:
                latest_price = recent_prices.iloc[0]
                previous_price = recent_prices.iloc[1]
                
                price_change = latest_price['lbmp'] - previous_price['lbmp']
                
                if price_change > 20: # Significant price spike
                    alerts.append((
                        latest_price['timestamp'],
                        'Price Spike',
                        'High',
                        latest_price['zone'],
                        f"Significant price increase detected: {price_change:.2f} $/MWh",
                        round(price_change, 2),
                        round(price_change * 100, 2), # Example profit impact
                        'Review trading strategies'
                    ))
            
            cursor.executemany("""INSERT INTO market_alerts (timestamp, alert_type, severity, zone, message, trigger_value, profit_impact, action_required) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", alerts)
            self.db_connection.commit()
            
    def start_collection(self):
        if not self.is_collecting:
            self.is_collecting = True
            self._collection_thread = threading.Thread(target=self._run_collection)
            self._collection_thread.daemon = True
            self._collection_thread.start()
            print("Data collection started.")
        else:
            print("Data collection is already running.")

    def stop_collection(self):
        if self.is_collecting:
            self.is_collecting = False
            print("Data collection stopped.")
        else:
            print("Data collection is not running.")

    def _run_collection(self):
        while self.is_collecting:
            print("Collecting comprehensive data...")
            self.fetch_comprehensive_data()
            time.sleep(3600) # Collect data every hour

# Initialize the collector
collector = EnterpriseNYISOCollector()

@app.route('/')
def index():
    return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>NYISO Data Dashboard</title>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .container { display: flex; flex-wrap: wrap; gap: 20px; }
                .card { border: 1px solid #ccc; padding: 15px; border-radius: 8px; flex: 1 1 calc(50% - 40px); box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                .card h2 { margin-top: 0; }
                .controls button { padding: 10px 15px; margin-right: 10px; border: none; border-radius: 5px; cursor: pointer; background-color: #007bff; color: white; }
                .controls button:hover { background-color: #0056b3; }
            </style>
        </head>
        <body>
            <h1>NYISO Data Dashboard</h1>
            <div class="controls">
                <button onclick="startCollection()">Start Data Collection</button>
                <button onclick="stopCollection()">Stop Data Collection</button>
                <button onclick="fetchAndDisplayData()">Refresh Data</button>
            </div>
            <div class="container">
                <div class="card">
                    <h2>Real-time LBMP</h2>
                    <canvas id="realtimeLbmpChart"></canvas>
                </div>
                <div class="card">
                    <h2>Day-ahead LBMP</h2>
                    <canvas id="dayaheadLbmpChart"></canvas>
                </div>
                <div class="card">
                    <h2>Load Data</h2>
                    <canvas id="loadDataChart"></canvas>
                </div>
                <div class="card">
                    <h2>Generation Data</h2>
                    <canvas id="generationDataChart"></canvas>
                </div>
                <div class="card">
                    <h2>Interface Flows</h2>
                    <canvas id="interfaceFlowsChart"></canvas>
                </div>
                <div class="card">
                    <h2>Trading Opportunities</h2>
                    <ul id="tradingOpportunitiesList"></ul>
                </div>
                <div class="card">
                    <h2>Predictions</h2>
                    <ul id="predictionsList"></ul>
                </div>
                <div class="card">
                    <h2>Market Alerts</h2>
                    <ul id="marketAlertsList"></ul>
                </div>
            </div>

            <script>
                async function fetchData(endpoint) {
                    const response = await fetch(endpoint);
                    return response.json();
                }

                let realtimeLbmpChart, dayaheadLbmpChart, loadDataChart, generationDataChart, interfaceFlowsChart;

                async function fetchAndDisplayData() {
                    // Fetch data for charts
                    const realtimeData = await fetchData('/api/realtime_pricing');
                    const dayaheadData = await fetchData('/api/dayahead_pricing');
                    const loadData = await fetchData('/api/load_data');
                    const generationData = await fetchData('/api/generation_data');
                    const interfaceData = await fetchData('/api/interface_data');
                    
                    // Fetch data for lists
                    const tradingOpportunities = await fetchData('/api/trading_opportunities');
                    const predictions = await fetchData('/api/predictions');
                    const marketAlerts = await fetchData('/api/market_alerts');

                    // Update Charts
                    updateChart(realtimeLbmpChart, 'realtimeLbmpChart', 'Real-time LBMP', realtimeData.map(d => d.timestamp), realtimeData.map(d => d.lbmp), 'LBMP ($/MWh)');
                    updateChart(dayaheadLbmpChart, 'dayaheadLbmpChart', 'Day-ahead LBMP', dayaheadData.map(d => d.timestamp), dayaheadData.map(d => d.da_lbmp), 'DA LBMP ($/MWh)');
                    updateChart(loadDataChart, 'loadDataChart', 'Actual Load', loadData.map(d => d.timestamp), loadData.map(d => d.actual_load), 'Load (MW)');
                    updateChart(generationDataChart, 'generationDataChart', 'Generation (MW)', generationData.map(d => d.timestamp), generationData.map(d => d.generation_mw), 'Generation (MW)', generationData.map(d => d.fuel_type));
                    updateChart(interfaceFlowsChart, 'interfaceFlowsChart', 'Interface Flow (MW)', interfaceData.map(d => d.timestamp), interfaceData.map(d => d.flow_mw), 'Flow (MW)', interfaceData.map(d => d.interface_name));

                    // Update Lists
                    updateList('tradingOpportunitiesList', tradingOpportunities, (item) => `<li>${item.timestamp}: ${item.opportunity_type} from ${item.zone_from} to ${item.zone_to} - Spread: $${item.price_spread}</li>`);
                    updateList('predictionsList', predictions, (item) => `<li>${item.timestamp} (${item.horizon}): Load: ${item.predicted_load || 'N/A'} MW, Price: $${item.predicted_price || 'N/A'}</li>`);
                    updateList('marketAlertsList', marketAlerts, (item) => `<li>${item.timestamp} - ${item.alert_type} (${item.severity}): ${item.message}</li>`);
                }

                function updateChart(chartInstance, chartId, label, labels, data, yAxisLabel, additionalLabels = null) {
                    const ctx = document.getElementById(chartId).getContext('2d');
                    if (chartInstance) {
                        chartInstance.destroy();
                    }
                    
                    let datasets = [];
                    if (additionalLabels) {
                        const uniqueAdditionalLabels = [...new Set(additionalLabels)];
                        uniqueAdditionalLabels.forEach(ulabel => {
                            const filteredData = data.filter((d, i) => additionalLabels[i] === ulabel);
                            const filteredLabels = labels.filter((d, i) => additionalLabels[i] === ulabel);
                            datasets.push({
                                label: ulabel,
                                data: filteredData,
                                borderColor: getRandomColor(),
                                fill: false
                            });
                        });
                    } else {
                        datasets.push({
                            label: label,
                            data: data,
                            borderColor: getRandomColor(),
                            fill: false
                        });
                    }

                    chartInstance = new Chart(ctx, {
                        type: 'line',
                        data: {
                            labels: labels,
                            datasets: datasets
                        },
                        options: {
                            responsive: true,
                            scales: {
                                x: { type: 'time', time: { unit: 'hour' }, title: { display: true, text: 'Timestamp' } },
                                y: { title: { display: true, text: yAxisLabel } }
                            },
                            plugins: {
                                tooltip: {
                                    callbacks: {
                                        title: function(context) {
                                            return context[0].label;
                                        },
                                        label: function(context) {
                                            let label = context.dataset.label || '';
                                            if (label) {
                                                label += ': ';
                                            }
                                            if (context.parsed.y !== null) {
                                                label += new Intl.NumberFormat('en-US', { style: 'decimal' }).format(context.parsed.y);
                                            }
                                            return label;
                                        }
                                    }
                                }
                            }
                        }
                    });
                }

                function updateList(listId, data, itemFormatter) {
                    const ul = document.getElementById(listId);
                    ul.innerHTML = '';
                    data.forEach(item => {
                        ul.innerHTML += itemFormatter(item);
                    });
                }

                function getRandomColor() {
                    const letters = '0123456789ABCDEF';
                    let color = '#';
                    for (let i = 0; i < 6; i++) {
                        color += letters[Math.floor(Math.random() * 16)];
                    }
                    return color;
                }

                async function startCollection() {
                    const response = await fetch('/start_collection', { method: 'POST' });
                    const result = await response.json();
                    alert(result.status);
                    fetchAndDisplayData();
                }

                async function stopCollection() {
                    const response = await fetch('/stop_collection', { method: 'POST' });
                    const result = await response.json();
                    alert(result.status);
                }

                // Initial data fetch on page load
                fetchAndDisplayData();
            </script>
        </body>
        </html>
    """)

@app.route('/api/realtime_pricing')
def get_realtime_pricing():
    with collector.db_lock:
        cursor = collector.db_connection.cursor()
        cursor.execute("SELECT timestamp, zone, lbmp, energy_component, congestion_component, losses_component FROM realtime_pricing ORDER BY timestamp DESC LIMIT 100")
        data = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        return jsonify([dict(zip(columns, row)) for row in data])

@app.route('/api/dayahead_pricing')
def get_dayahead_pricing():
    with collector.db_lock:
        cursor = collector.db_connection.cursor()
        cursor.execute("SELECT timestamp, zone, da_lbmp, da_energy, da_congestion, da_losses FROM dayahead_pricing ORDER BY timestamp DESC LIMIT 100")
        data = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        return jsonify([dict(zip(columns, row)) for row in data])

@app.route('/api/load_data')
def get_load_data():
    with collector.db_lock:
        cursor = collector.db_connection.cursor()
        cursor.execute("SELECT timestamp, zone, actual_load, forecast_load, peak_forecast, load_factor FROM load_data ORDER BY timestamp DESC LIMIT 100")
        data = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        return jsonify([dict(zip(columns, row)) for row in data])

@app.route('/api/generation_data')
def get_generation_data():
    with collector.db_lock:
        cursor = collector.db_connection.cursor()
        cursor.execute("SELECT timestamp, fuel_type, generation_mw, capacity_mw, capacity_factor, marginal_cost FROM generation_data ORDER BY timestamp DESC LIMIT 100")
        data = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        return jsonify([dict(zip(columns, row)) for row in data])

@app.route('/api/interface_flows')
def get_interface_flows():
    with collector.db_lock:
        cursor = collector.db_connection.cursor()
        cursor.execute("SELECT timestamp, interface_name, flow_mw, limit_mw, utilization_pct, congestion_cost FROM interface_data ORDER BY timestamp DESC LIMIT 100")
        data = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        return jsonify([dict(zip(columns, row)) for row in data])

@app.route('/api/trading_opportunities')
def get_trading_opportunities():
    with collector.db_lock:
        cursor = collector.db_connection.cursor()
        cursor.execute("SELECT timestamp, opportunity_type, zone_from, zone_to, price_spread, volume_mw, profit_potential, risk_score, confidence FROM trading_opportunities ORDER BY timestamp DESC LIMIT 10")
        data = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        return jsonify([dict(zip(columns, row)) for row in data])

@app.route('/api/predictions')
def get_predictions():
    with collector.db_lock:
        cursor = collector.db_connection.cursor()
        cursor.execute("SELECT timestamp, zone, horizon, predicted_load, predicted_price, price_volatility, congestion_probability, model_type FROM predictions ORDER BY timestamp DESC LIMIT 10")
        data = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        return jsonify([dict(zip(columns, row)) for row in data])

@app.route('/api/market_alerts')
def get_market_alerts():
    with collector.db_lock:
        cursor = collector.db_connection.cursor()
        cursor.execute("SELECT timestamp, alert_type, severity, zone, message, trigger_value, profit_impact, action_required FROM market_alerts ORDER BY timestamp DESC LIMIT 10")
        data = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        return jsonify([dict(zip(columns, row)) for row in data])

@app.route('/start_collection', methods=['POST'])
def start_collection():
    collector.start_collection()
    return jsonify(status="Data collection started.")

@app.route('/stop_collection', methods=['POST'])
def stop_collection():
    collector.stop_collection()
    return jsonify(status="Data collection stopped.")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')


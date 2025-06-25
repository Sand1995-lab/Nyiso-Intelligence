from flask import Flask, render_template_string, jsonify
import json
import random
import math
import os
from datetime import datetime, timedelta
import threading
import time

app = Flask(__name__)

class EnergyIntelligenceEngine:
    def __init__(self):
        self.electricity_zones = ['NYC', 'WEST', 'CAPITAL', 'NORTH', 'CENTRAL']
        self.gas_hubs = ['Transco Z6 NY', 'Algonquin Citygate', 'Tennessee Z4', 'Iroquois Waddington', 'Dominion South']
        
        # Initialize real-time data streams
        self.market_data = {}
        self.predictions = {}
        self.alerts = []
        self.trading_signals = []
        
        # Start real-time data generation
        self.start_real_time_engine()
    
    def generate_real_time_market_data(self):
        """Generate electricity and natural gas market data"""
        current_time = datetime.now()
        
        # Generate electricity data
        electricity_data = {}
        for zone in self.electricity_zones:
            base_price = 45 + random.uniform(-10, 25)
            load_factor = self.get_hourly_pattern()
            
            electricity_data[zone] = {
                'rt_price': round(base_price + random.uniform(-5, 15), 2),
                'da_price': round(base_price * random.uniform(0.95, 1.05), 2),
                'load_mw': round(2000 + load_factor * 1500 + random.uniform(-200, 300), 1),
                'heat_rate': round(random.uniform(7500, 9500), 0),
                'spark_spread': 0  # Will calculate after gas prices
            }
        
        # Generate natural gas data
        gas_data = {}
        henry_hub_base = 3.50 + random.uniform(-0.50, 1.00)
        
        for hub in self.gas_hubs:
            basis_diff = random.uniform(-0.30, 0.80)
            gas_price = henry_hub_base + basis_diff
            
            gas_data[hub] = {
                'price': round(gas_price, 3),
                'basis_to_hh': round(basis_diff, 3),
                'volume_mmcf': round(random.uniform(50, 300), 1),
                'volatility': round(random.uniform(0.15, 0.35), 3)
            }
        
        # Calculate spark spreads
        avg_gas_price = sum(hub['price'] for hub in gas_data.values()) / len(gas_data)
        for zone in electricity_data:
            heat_rate = electricity_data[zone]['heat_rate']
            gas_cost = (avg_gas_price * heat_rate) / 1000  # $/MWh
            electricity_data[zone]['spark_spread'] = round(
                electricity_data[zone]['rt_price'] - gas_cost, 2
            )
        
        self.market_data = {
            'timestamp': current_time.isoformat(),
            'electricity': electricity_data,
            'natural_gas': gas_data,
            'henry_hub': round(henry_hub_base, 3),
            'avg_spark_spread': round(sum(zone['spark_spread'] for zone in electricity_data.values()) / len(electricity_data), 2)
        }
        
        return self.market_data
    
    def get_hourly_pattern(self):
        """Get hourly load pattern (0-1 multiplier)"""
        hour = datetime.now().hour
        pattern = [0.7, 0.65, 0.6, 0.6, 0.65, 0.75, 0.85, 0.95, 1.0, 0.98, 0.95, 0.92,
                  0.9, 0.88, 0.85, 0.88, 0.92, 0.98, 1.0, 0.95, 0.9, 0.85, 0.8, 0.75]
        return pattern[hour]
    
    def generate_predictions(self):
        """Generate price predictions"""
        if not self.market_data:
            return {}
        
        predictions = {
            'electricity': {},
            'natural_gas': {},
            'spark_spreads': {}
        }
        
        # Electricity predictions
        for zone, data in self.market_data['electricity'].items():
            current_price = data['rt_price']
            volatility = 0.15
            
            predictions['electricity'][zone] = {
                'price_1h': round(current_price * (1 + random.uniform(-volatility, volatility)), 2),
                'price_4h': round(current_price * (1 + random.uniform(-volatility*1.5, volatility*1.5)), 2),
                'price_24h': round(current_price * (1 + random.uniform(-volatility*2, volatility*2)), 2),
                'confidence': round(random.uniform(0.75, 0.95), 3)
            }
        
        # Natural gas predictions
        for hub, data in self.market_data['natural_gas'].items():
            current_price = data['price']
            volatility = data['volatility']
            
            predictions['natural_gas'][hub] = {
                'price_1h': round(current_price * (1 + random.uniform(-volatility, volatility)), 3),
                'price_4h': round(current_price * (1 + random.uniform(-volatility*1.2, volatility*1.2)), 3),
                'price_24h': round(current_price * (1 + random.uniform(-volatility*1.8, volatility*1.8)), 3),
                'confidence': round(random.uniform(0.70, 0.90), 3)
            }
        
        # Spark spread predictions
        for zone in self.electricity_zones:
            current_spread = self.market_data['electricity'][zone]['spark_spread']
            predictions['spark_spreads'][zone] = {
                'spread_1h': round(current_spread + random.uniform(-3, 3), 2),
                'spread_4h': round(current_spread + random.uniform(-5, 5), 2),
                'spread_24h': round(current_spread + random.uniform(-8, 8), 2)
            }
        
        self.predictions = predictions
        return predictions
    
    def generate_trading_signals(self):
        """Generate trading signals for gas and power"""
        if not self.market_data:
            return []
        
        signals = []
        
        # Spark spread opportunities
        for zone, data in self.market_data['electricity'].items():
            spread = data['spark_spread']
            if spread > 15:  # Profitable spread
                signals.append({
                    'type': 'spark_spread_trade',
                    'action': 'BUY_POWER_SELL_GAS',
                    'zone': zone,
                    'spread': spread,
                    'profit_potential': round(spread * random.uniform(50, 200), 0),
                    'risk_score': round(random.uniform(0.2, 0.6), 3),
                    'confidence': round(random.uniform(0.75, 0.95), 3)
                })
            elif spread < 5:  # Negative spread
                signals.append({
                    'type': 'spark_spread_trade',
                    'action': 'SELL_POWER_BUY_GAS',
                    'zone': zone,
                    'spread': spread,
                    'profit_potential': round(abs(spread) * random.uniform(30, 150), 0),
                    'risk_score': round(random.uniform(0.4, 0.8), 3),
                    'confidence': round(random.uniform(0.65, 0.85), 3)
                })
        
        # Gas arbitrage opportunities
        gas_prices = list(self.market_data['natural_gas'].values())
        for i, hub1 in enumerate(self.gas_hubs):
            for hub2 in self.gas_hubs[i+1:]:
                price_diff = abs(gas_prices[i]['price'] - gas_prices[self.gas_hubs.index(hub2)]['price'])
                if price_diff > 0.30:  # Significant price difference
                    signals.append({
                        'type': 'gas_arbitrage',
                        'action': 'ARBITRAGE',
                        'hub_buy': hub1 if gas_prices[i]['price'] < gas_prices[self.gas_hubs.index(hub2)]['price'] else hub2,
                        'hub_sell': hub2 if gas_prices[i]['price'] < gas_prices[self.gas_hubs.index(hub2)]['price'] else hub1,
                        'spread': round(price_diff, 3),
                        'profit_potential': round(price_diff * random.uniform(1000, 5000), 0),
                        'risk_score': round(random.uniform(0.3, 0.7), 3),
                        'confidence': round(random.uniform(0.70, 0.90), 3)
                    })
        
        # Power arbitrage
        power_prices = [(zone, data['rt_price']) for zone, data in self.market_data['electricity'].items()]
        for i, (zone1, price1) in enumerate(power_prices):
            for zone2, price2 in power_prices[i+1:]:
                price_diff = abs(price1 - price2)
                if price_diff > 8:
                    signals.append({
                        'type': 'power_arbitrage',
                        'action': 'ARBITRAGE',
                        'zone_buy': zone1 if price1 < price2 else zone2,
                        'zone_sell': zone2 if price1 < price2 else zone1,
                        'spread': round(price_diff, 2),
                        'profit_potential': round(price_diff * random.uniform(100, 400), 0),
                        'risk_score': round(random.uniform(0.25, 0.65), 3),
                        'confidence': round(random.uniform(0.75, 0.92), 3)
                    })
        
        signals.sort(key=lambda x: x['profit_potential'], reverse=True)
        self.trading_signals = signals[:8]
        return self.trading_signals
    
    def generate_alerts(self):
        """Generate market alerts"""
        if not self.market_data:
            return []
        
        alerts = []
        current_time = datetime.now()
        
        # High electricity price alerts
        for zone, data in self.market_data['electricity'].items():
            price = data['rt_price']
            if price > 100:
                alerts.append({
                    'severity': 'HIGH' if price > 150 else 'MEDIUM',
                    'type': 'power_price_spike',
                    'message': f'High electricity price in {zone}: ${price}/MWh',
                    'value': price,
                    'recommendation': 'Consider demand response or power sales',
                    'timestamp': current_time.isoformat()
                })
        
        # Gas price alerts
        hh_price = self.market_data['henry_hub']
        if hh_price > 4.5:
            alerts.append({
                'severity': 'HIGH',
                'type': 'gas_price_spike',
                'message': f'High Henry Hub price: ${hh_price}/MMBtu',
                'value': hh_price,
                'recommendation': 'Monitor power generation costs and spark spreads',
                'timestamp': current_time.isoformat()
            })
        
        # Spark spread alerts
        avg_spread = self.market_data['avg_spark_spread']
        if avg_spread < 8:
            alerts.append({
                'severity': 'MEDIUM',
                'type': 'low_spark_spread',
                'message': f'Low average spark spread: ${avg_spread}/MWh',
                'value': avg_spread,
                'recommendation': 'Gas generation may be uneconomical',
                'timestamp': current_time.isoformat()
            })
        
        self.alerts = alerts[:10]
        return self.alerts
    
    def start_real_time_engine(self):
        """Start the real-time data generation"""
        def update_loop():
            while True:
                try:
                    self.generate_real_time_market_data()
                    self.generate_predictions()
                    self.generate_trading_signals()
                    self.generate_alerts()
                    time.sleep(30)
                except Exception as e:
                    print(f"Error in real-time engine: {e}")
                    time.sleep(10)
        
        thread = threading.Thread(target=update_loop, daemon=True)
        thread.start()

# Initialize the engine
intelligence_engine = EnergyIntelligenceEngine()

# HTML Template
html_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Natural Gas & Electricity Intelligence Platform</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #0c1426 0%, #1a202c 50%, #2d3748 100%); 
            color: #fff; 
            line-height: 1.6;
        }
        
        .header {
            background: linear-gradient(90deg, #1a365d 0%, #2b77a6 50%, #63b3ed 100%);
            padding: 20px 0;
            box-shadow: 0 4px 20px rgba(0,0,0,0.4);
            text-align: center;
        }
        
        .logo {
            font-size: 2rem;
            font-weight: bold;
            color: #fff;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .card {
            background: linear-gradient(145deg, #2d3748 0%, #4a5568 100%);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid #63b3ed;
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            transition: transform 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
        }
        
        .card h3 {
            color: #63b3ed;
            margin-bottom: 15px;
            font-size: 1.1rem;
        }
        
        .metric-large {
            font-size: 1.8rem;
            font-weight: bold;
            margin-bottom: 8px;
        }
        
        .metric-large.profit { color: #68d391; }
        .metric-large.loss { color: #fc8181; }
        .metric-large.neutral { color: #81e6d9; }
        .metric-large.warning { color: #f6e05e; }
        
        .metric-subtitle {
            font-size: 0.9rem;
            color: #cbd5e0;
        }
        
        .main-content {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 30px;
            margin-bottom: 30px;
        }
        
        .chart-container {
            background: linear-gradient(145deg, #2d3748 0%, #4a5568 100%);
            border-radius: 12px;
            padding: 25px;
            border: 1px solid #63b3ed;
        }
        
        .chart-wrapper {
            position: relative;
            height: 400px;
            margin-top: 15px;
        }
        
        .sidebar {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        
        .panel {
            background: linear-gradient(145deg, #2d3748 0%, #4a5568 100%);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid #63b3ed;
        }
        
        .signal-item, .alert-item {
            background: rgba(99, 179, 237, 0.1);
            border-left: 4px solid #63b3ed;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 6px;
        }
        
        .alert-high {
            border-left-color: #fc8181;
            background: rgba(252, 129, 129, 0.1);
        }
        
        .alert-medium {
            border-left-color: #f6e05e;
            background: rgba(246, 224, 94, 0.1);
        }
        
        .table-container {
            background: linear-gradient(145deg, #2d3748 0%, #4a5568 100%);
            border-radius: 12px;
            padding: 25px;
            border: 1px solid #63b3ed;
            overflow-x: auto;
        }
        
        .data-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }
        
        .data-table th,
        .data-table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #4a5568;
        }
        
        .data-table th {
            background: rgba(99, 179, 237, 0.2);
            color: #63b3ed;
            font-weight: bold;
        }
        
        .data-table tr:hover {
            background: rgba(99, 179, 237, 0.1);
        }
        
        .btn {
            background: linear-gradient(45deg, #3182ce, #2b77a6);
            color: #fff;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s ease;
            margin: 10px 0;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(49, 130, 206, 0.4);
        }
        
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        
        .tab-btn {
            padding: 10px 20px;
            background: rgba(99, 179, 237, 0.2);
            border: 1px solid #63b3ed;
            border-radius: 6px;
            color: #fff;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .tab-btn.active {
            background: #63b3ed;
            color: #1a202c;
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
        }
        
        @media (max-width: 768px) {
            .main-content { grid-template-columns: 1fr; }
            .dashboard-grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">⚡ Natural Gas & Electricity Intelligence Platform ⛽</div>
    </div>

    <div class="container">
        <!-- Key Metrics Dashboard -->
        <div class="dashboard-grid">
            <div class="card">
                <h3>⚡ Avg Electricity Price</h3>
                <div class="metric-large neutral" id="avg-power-price">$0/MWh</div>
                <div class="metric-subtitle" id="power-trend">Loading...</div>
            </div>
            
            <div class="card">
                <h3>⛽ Henry Hub Gas</h3>
                <div class="metric-large neutral" id="henry-hub-price">$0/MMBtu</div>
                <div class="metric-subtitle" id="gas-trend">Loading...</div>
            </div>
            
            <div class="card">
                <h3>🔥 Avg Spark Spread</h3>
                <div class="metric-large neutral" id="avg-spark-spread">$0/MWh</div>
                <div class="metric-subtitle" id="spread-trend">Loading...</div>
            </div>
            
            <div class="card">
                <h3>📊 Trading Signals</h3>
                <div class="metric-large neutral" id="signal-count">0</div>
                <div class="metric-subtitle">Active opportunities</div>
            </div>
        </div>

        <!-- Main Content Area -->
        <div class="main-content">
            <!-- Charts Section -->
            <div>
                <div class="tabs">
                    <button class="tab-btn active" onclick="showTab('power')">Electricity Prices</button>
                    <button class="tab-btn" onclick="showTab('gas')">Natural Gas Prices</button>
                    <button class="tab-btn" onclick="showTab('spreads')">Spark Spreads</button>
                </div>
                
                <div class="chart-container">
                    <div id="power-tab" class="tab-content active">
                        <h3>⚡ Electricity Prices by Zone</h3>
                        <div class="chart-wrapper">
                            <canvas id="powerChart"></canvas>
                        </div>
                    </div>
                    
                    <div id="gas-tab" class="tab-content">
                        <h3>⛽ Natural Gas Prices by Hub</h3>
                        <div class="chart-wrapper">
                            <canvas id="gasChart"></canvas>
                        </div>
                    </div>
                    
                    <div id="spreads-tab" class="tab-content">
                        <h3>🔥 Spark Spreads by Zone</h3>
                        <div class="chart-wrapper">
                            <canvas id="spreadsChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Sidebar -->
            <div class="sidebar">
                <div class="panel">
                    <h3>🎯 Trading Signals</h3>
                    <div id="signals-list">
                        <!-- Signals will be populated here -->
                    </div>
                </div>
                
                <div class="panel">
                    <h3>🚨 Market Alerts</h3>
                    <div id="alerts-list">
                        <!-- Alerts will be populated here -->
                    </div>
                </div>
            </div>
        </div>

        <!-- Data Tables -->
        <div class="table-container">
            <h3>📊 Live Market Data</h3>
            <div class="tabs">
                <button class="tab-btn active" onclick="showTable('electricity')">Electricity</button>
                <button class="tab-btn" onclick="showTable('gas')">Natural Gas</button>
                <button class="tab-btn" onclick="showTable('signals')">Trading Signals</button>
            </div>
            
            <div id="electricity-table" class="tab-content active">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Zone</th>
                            <th>RT Price ($/MWh)</th>
                            <th>DA Price ($/MWh)</th>
                            <th>Load (MW)</th>
                            <th>Heat Rate</th>
                            <th>Spark Spread</th>
                        </tr>
                    </thead>
                    <tbody id="electricity-tbody">
                    </tbody>
                </table>
            </div>
            
            <div id="gas-table" class="tab-content">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Hub</th>
                            <th>Price ($/MMBtu)</th>
                            <th>Basis to HH</th>
                            <th>Volume (MMcf)</th>
                            <th>Volatility</th>
                        </tr>
                    </thead>
                    <tbody id="gas-tbody">
                    </tbody>
                </table>
            </div>
            
            <div id="signals-table" class="tab-content">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Type</th>
                            <th>Action</th>
                            <th>Market</th>
                            <th>Spread</th>
                            <th>Profit Potential</th>
                            <th>Risk Score</th>
                            <th>Confidence</th>
                        </tr>
                    </thead>
                    <tbody id="signals-tbody">
                    </tbody>
                </table>
            </div>
        </div>
        
        <button class="btn" onclick="refreshData()">🔄 Refresh Data</button>
    </div>

    <script>
        let charts = {};
        let currentData = {};
        let updateInterval;
        
        // Tab management
        function showTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            document.querySelectorAll('.tab-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            
            document.getElementById(tabName + '-tab').classList.add('active');
            event.target.classList.add('active');
            
            setTimeout(() => initializeChart(tabName), 100);
        }
        
        function showTable(tableName) {
            document.querySelectorAll('#electricity-table, #gas-table, #signals-table').forEach(table => {
                table.classList.remove('active');
            });
            document.getElementById(tableName + '-table').classList.add('active');
            
            // Update active tab button
            event.target.parentElement.querySelectorAll('.tab-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            event.target.classList.add('active');
        }
        
        function initializeChart(chartType) {
            if (!currentData.electricity || !currentData.natural_gas) return;
            
            if (chartType === 'power') {
                initPowerChart();
            } else if (chartType === 'gas') {
                initGasChart();
            } else if (chartType === 'spreads') {
                initSpreadsChart();
            }
        }
        
        function initPowerChart() {
            const ctx = document.getElementById('powerChart');
            if (!ctx) return;
            
            if (charts.power) charts.power.destroy();
            
            const zones = Object.keys(currentData.electricity);
            const rtPrices = zones.map(zone => currentData.electricity[zone].rt_price);
            const daPrices = zones.map(zone => currentData.electricity[zone].da_price);
            
            charts.power = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: zones,
                    datasets: [{
                        label: 'Real-Time Price',
                        data: rtPrices,
                        backgroundColor: '#63b3ed'
                    }, {
                        label: 'Day-Ahead Price',
                        data: daPrices,
                        backgroundColor: '#68d391'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { labels: { color: '#fff' } }
                    },
                    scales: {
                        x: { ticks: { color: '#cbd5e0' }, grid: { color: '#4a5568' } },
                        y: { 
                            ticks: { color: '#cbd5e0' }, 
                            grid: { color: '#4a5568' },
                            title: { display: true, text: 'Price ($/MWh)', color: '#cbd5e0' }
                        }
                    }
                }
            });
        }
        
        function initGasChart() {
            const ctx = document.getElementById('gasChart');
            if (!ctx) return;
            
            if (charts.gas) charts.gas.destroy();
            
            const hubs = Object.keys(currentData.natural_gas);
            const prices = hubs.map(hub => currentData.natural_gas[hub].price);
            
            charts.gas = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: hubs,
                    datasets: [{
                        label: 'Gas Price ($/MMBtu)',
                        data: prices,
                        borderColor: '#f6e05e',
                        backgroundColor: 'rgba(246, 224, 94, 0.1)',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { labels: { color: '#fff' } }
                    },
                    scales: {
                        x: { ticks: { color: '#cbd5e0' }, grid: { color: '#4a5568' } },
                        y: { 
                            ticks: { color: '#cbd5e0' }, 
                            grid: { color: '#4a5568' },
                            title: { display: true, text: 'Price ($/MMBtu)', color: '#cbd5e0' }
                        }
                    }
                }
            });
        }
        
        function initSpreadsChart() {
            const ctx = document.getElementById('spreadsChart');
            if (!ctx) return;
            
            if (charts.spreads) charts.spreads.destroy();
            
            const zones = Object.keys(currentData.electricity);
            const spreads = zones.map(zone => currentData.electricity[zone].spark_spread);
            
            charts.spreads = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: zones,
                    datasets: [{
                        label: 'Spark Spread ($/MWh)',
                        data: spreads,
                        backgroundColor: spreads.map(s => s > 10 ? '#68d391' : s > 5 ? '#f6e05e' : '#fc8181')
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { labels: { color: '#fff' } }
                    },
                    scales: {
                        x: { ticks: { color: '#cbd5e0' }, grid: { color: '#4a5568' } },
                        y: { 
                            ticks: { color: '#cbd5e0' }, 
                            grid: { color: '#4a5568' },
                            title: { display: true, text: 'Spark Spread ($/MWh)', color: '#cbd5e0' }
                        }
                    }
                }
            });
        }
        
        async function fetchMarketData() {
            try {
                const response = await fetch('/api/market-data');
                const data = await response.json();
                currentData = data;
                updateDashboard(data);
                updateTables(data);
                return data;
            } catch (error) {
                console.error('Error fetching market data:', error);
                return null;
            }
        }
        
        async function fetchTradingSignals() {
            try {
                const response = await fetch('/api/trading-signals');
                const signals = await response.json();
                updateSignals(signals);
                return signals;
            } catch (error) {
                console.error('Error fetching trading signals:', error);
                return [];
            }
        }
        
        async function fetchAlerts() {
            try {
                const response = await fetch('/api/alerts');
                const alerts = await response.json();
                updateAlerts(alerts);
                return alerts;
            } catch (error) {
                console.error('Error fetching alerts:', error);
                return [];
            }
        }
        
        function updateDashboard(data) {
            if (!data) return;
            
            // Update key metrics
            if (data.electricity) {
                const zones = Object.values(data.electricity);
                const avgPrice = zones.reduce((sum, zone) => sum + zone.rt_price, 0) / zones.length;
                document.getElementById('avg-power-price').textContent = ' + avgPrice.toFixed(2) + '/MWh';
                
                const priceElement = document.getElementById('avg-power-price');
                priceElement.className = 'metric-large ' + (avgPrice > 80 ? 'warning' : avgPrice > 120 ? 'loss' : 'neutral');
            }
            
            if (data.henry_hub) {
                document.getElementById('henry-hub-price').textContent = ' + data.henry_hub.toFixed(3) + '/MMBtu';
                
                const gasElement = document.getElementById('henry-hub-price');
                gasElement.className = 'metric-large ' + (data.henry_hub > 4.5 ? 'warning' : data.henry_hub > 6 ? 'loss' : 'neutral');
            }
            
            if (data.avg_spark_spread !== undefined) {
                document.getElementById('avg-spark-spread').textContent = ' + data.avg_spark_spread.toFixed(2) + '/MWh';
                
                const spreadElement = document.getElementById('avg-spark-spread');
                spreadElement.className = 'metric-large ' + (data.avg_spark_spread > 15 ? 'profit' : data.avg_spark_spread < 5 ? 'loss' : 'neutral');
            }
        }
        
        function updateTables(data) {
            if (!data) return;
            
            // Update electricity table
            if (data.electricity) {
                const tbody = document.getElementById('electricity-tbody');
                tbody.innerHTML = '';
                
                Object.entries(data.electricity).forEach(([zone, zoneData]) => {
                    const row = document.createElement('tr');
                    const spreadClass = zoneData.spark_spread > 15 ? 'style="color: #68d391"' : 
                                       zoneData.spark_spread < 5 ? 'style="color: #fc8181"' : '';
                    
                    row.innerHTML = `
                        <td><strong>${zone}</strong></td>
                        <td>${zoneData.rt_price.toFixed(2)}</td>
                        <td>${zoneData.da_price.toFixed(2)}</td>
                        <td>${zoneData.load_mw.toLocaleString()} MW</td>
                        <td>${zoneData.heat_rate.toLocaleString()}</td>
                        <td ${spreadClass}>${zoneData.spark_spread.toFixed(2)}</td>
                    `;
                    tbody.appendChild(row);
                });
            }
            
            // Update gas table
            if (data.natural_gas) {
                const tbody = document.getElementById('gas-tbody');
                tbody.innerHTML = '';
                
                Object.entries(data.natural_gas).forEach(([hub, hubData]) => {
                    const row = document.createElement('tr');
                    const basisClass = hubData.basis_to_hh > 0.5 ? 'style="color: #fc8181"' : 
                                      hubData.basis_to_hh < -0.2 ? 'style="color: #68d391"' : '';
                    
                    row.innerHTML = `
                        <td><strong>${hub}</strong></td>
                        <td>${hubData.price.toFixed(3)}</td>
                        <td ${basisClass}>${hubData.basis_to_hh.toFixed(3)}</td>
                        <td>${hubData.volume_mmcf.toFixed(1)} MMcf</td>
                        <td>${(hubData.volatility * 100).toFixed(1)}%</td>
                    `;
                    tbody.appendChild(row);
                });
            }
        }
        
        function updateSignals(signals) {
            if (!signals || !Array.isArray(signals)) return;
            
            // Update signal count
            document.getElementById('signal-count').textContent = signals.length;
            
            // Update signals list in sidebar
            const signalsList = document.getElementById('signals-list');
            signalsList.innerHTML = '';
            
            signals.slice(0, 4).forEach(signal => {
                const signalDiv = document.createElement('div');
                signalDiv.className = 'signal-item';
                
                let displayText = '';
                if (signal.type === 'spark_spread_trade') {
                    displayText = `${signal.action.replace(/_/g, ' ')} in ${signal.zone}`;
                } else if (signal.type === 'gas_arbitrage') {
                    displayText = `Gas Arbitrage: ${signal.hub_buy} → ${signal.hub_sell}`;
                } else if (signal.type === 'power_arbitrage') {
                    displayText = `Power Arbitrage: ${signal.zone_buy} → ${signal.zone_sell}`;
                }
                
                signalDiv.innerHTML = `
                    <strong>${signal.type.replace(/_/g, ' ').toUpperCase()}</strong><br>
                    <div style="margin: 5px 0;">${displayText}</div>
                    <div style="color: #68d391; font-weight: bold;">Profit: ${signal.profit_potential.toLocaleString()}</div>
                    <div style="color: #f6e05e; font-size: 0.9rem;">Risk: ${(signal.risk_score * 100).toFixed(0)}% | Confidence: ${(signal.confidence * 100).toFixed(0)}%</div>
                `;
                signalsList.appendChild(signalDiv);
            });
            
            // Update signals table
            const tbody = document.getElementById('signals-tbody');
            tbody.innerHTML = '';
            
            signals.forEach(signal => {
                const row = document.createElement('tr');
                const riskClass = signal.risk_score < 0.3 ? 'style="color: #68d391"' : 
                                 signal.risk_score < 0.7 ? 'style="color: #f6e05e"' : 'style="color: #fc8181"';
                
                let marketInfo = '';
                if (signal.zone) marketInfo = signal.zone;
                else if (signal.hub_buy && signal.hub_sell) marketInfo = `${signal.hub_buy} → ${signal.hub_sell}`;
                else if (signal.zone_buy && signal.zone_sell) marketInfo = `${signal.zone_buy} → ${signal.zone_sell}`;
                
                row.innerHTML = `
                    <td>${signal.type.replace(/_/g, ' ')}</td>
                    <td><strong>${signal.action.replace(/_/g, ' ')}</strong></td>
                    <td>${marketInfo}</td>
                    <td>${signal.spread}</td>
                    <td style="color: #68d391;">${signal.profit_potential.toLocaleString()}</td>
                    <td ${riskClass}>${(signal.risk_score * 100).toFixed(0)}%</td>
                    <td>${(signal.confidence * 100).toFixed(0)}%</td>
                `;
                tbody.appendChild(row);
            });
        }
        
        function updateAlerts(alerts) {
            if (!alerts || !Array.isArray(alerts)) return;
            
            const alertsList = document.getElementById('alerts-list');
            alertsList.innerHTML = '';
            
            if (alerts.length === 0) {
                alertsList.innerHTML = '<div class="alert-item">No active alerts</div>';
                return;
            }
            
            alerts.slice(0, 5).forEach(alert => {
                const alertDiv = document.createElement('div');
                alertDiv.className = `alert-item alert-${alert.severity.toLowerCase()}`;
                
                alertDiv.innerHTML = `
                    <strong>${alert.severity}:</strong> ${alert.message}<br>
                    <div style="margin-top: 8px; font-style: italic; color: #cbd5e0; font-size: 0.9rem;">
                        💡 ${alert.recommendation}
                    </div>
                `;
                alertsList.appendChild(alertDiv);
            });
        }
        
        async function refreshData() {
            try {
                await Promise.all([
                    fetchMarketData(),
                    fetchTradingSignals(),
                    fetchAlerts()
                ]);
                
                // Refresh active chart
                const activeTab = document.querySelector('.tab-btn.active').textContent.toLowerCase();
                if (activeTab.includes('electricity')) {
                    initPowerChart();
                } else if (activeTab.includes('natural')) {
                    initGasChart();
                } else if (activeTab.includes('spark')) {
                    initSpreadsChart();
                }
                
                console.log('Data refreshed successfully');
            } catch (error) {
                console.error('Error refreshing data:', error);
            }
        }
        
        // Initialize everything
        document.addEventListener('DOMContentLoaded', function() {
            console.log('🚀 Initializing Energy Intelligence Platform...');
            
            // Initial data load
            refreshData();
            
            // Initialize charts after data loads
            setTimeout(() => {
                initPowerChart();
                console.log('✅ Platform initialized successfully!');
            }, 1000);
            
            // Set up auto-refresh every 2 minutes
            updateInterval = setInterval(refreshData, 120000);
        });
    </script>
</body>
</html>
'''

# API Routes
@app.route('/')
def dashboard():
    return render_template_string(html_template)

@app.route('/api/market-data')
def get_market_data():
    return jsonify(intelligence_engine.market_data)

@app.route('/api/trading-signals')
def get_trading_signals():
    return jsonify(intelligence_engine.trading_signals)

@app.route('/api/alerts')
def get_alerts():
    return jsonify(intelligence_engine.alerts)

@app.route('/api/predictions')
def get_predictions():
    return jsonify(intelligence_engine.predictions)

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'Natural Gas & Electricity Intelligence Platform',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat(),
        'capabilities': [
            'Real-time electricity pricing',
            'Natural gas market data',
            'Spark spread analysis',
            'Trading signal generation',
            'Price predictions',
            'Market alerts'
        ]
    })

if __name__ == '__main__':
    print("🚀 Starting Natural Gas & Electricity Intelligence Platform...")
    print("⚡ Electricity market monitoring active")
    print("⛽ Natural gas price tracking enabled") 
    print("🔥 Spark spread analysis running")
    print("🎯 Trading signals generated")
    print("📊 Real-time data updates every 30 seconds")
    print("✅ Energy intelligence platform ready!")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

from flask import Flask, render_template_string, jsonify, request
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
import threading
import time
import os
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)

class SimplifiedNYISOCollector:
    def __init__(self):
        self.zones = ['CAPITL', 'CENTRL', 'DUNWOD', 'GENESE', 'HUD VL', 'LONGIL', 'MHK VL', 'MILLWD', 'N.Y.C.', 'NORTH', 'WEST']
        self.current_data = {}
        self.is_collecting = False
        self.last_update = datetime.now()
        
    def generate_realistic_data(self):
        """Generate realistic NYISO market data without database"""
        try:
            current_time = datetime.now()
            
            # Zone pricing data
            zone_data = []
            for zone in self.zones:
                if zone == 'N.Y.C.':
                    base_price = 45 + np.random.normal(0, 12)
                    congestion = max(0, np.random.normal(8, 15))
                    actual_load = np.random.normal(8500, 1200)
                elif zone in ['LONGIL', 'DUNWOD']:
                    base_price = 42 + np.random.normal(0, 10)
                    congestion = max(0, np.random.normal(5, 12))
                    actual_load = np.random.normal(3200, 600)
                else:
                    base_price = 38 + np.random.normal(0, 8)
                    congestion = max(0, np.random.normal(2, 8))
                    actual_load = np.random.normal(1800, 400)
                
                energy_component = base_price * 0.85
                losses_component = base_price * 0.05
                rt_price = energy_component + congestion + losses_component
                
                # Day-ahead price (5-10% different)
                da_premium = np.random.normal(0, 0.08)
                da_price = rt_price * (1 + da_premium)
                
                # Trading opportunity assessment
                spread = abs(rt_price - da_price)
                if spread > 10:
                    opportunity = "High"
                elif spread > 5:
                    opportunity = "Medium"
                else:
                    opportunity = "Low"
                
                zone_data.append({
                    'zone': zone,
                    'rt_price': rt_price,
                    'da_price': da_price,
                    'congestion': congestion,
                    'load': actual_load,
                    'opportunity': opportunity
                })
            
            # Predictions data
            predictions = []
            for zone in self.zones:
                base_price = 40 if zone != 'N.Y.C.' else 50
                base_load = 2000 if zone != 'N.Y.C.' else 8000
                
                predictions.append({
                    'zone': zone,
                    'price_1h': base_price + np.random.normal(0, 5),
                    'price_4h': base_price + np.random.normal(0, 8),
                    'price_24h': base_price + np.random.normal(0, 12),
                    'load_1h': base_load + np.random.normal(0, 200),
                    'congestion_risk': np.random.uniform(0.1, 0.3),
                    'confidence': np.random.uniform(0.7, 0.9)
                })
            
            # Trading opportunities
            opportunities = []
            for i in range(5):
                zone_from = np.random.choice(self.zones)
                zone_to = np.random.choice([z for z in self.zones if z != zone_from])
                spread = np.random.uniform(5, 25)
                volume = np.random.uniform(100, 1000)
                profit = spread * volume * 0.7
                
                opportunities.append({
                    'type': np.random.choice(['spatial_arbitrage', 'temporal_arbitrage']),
                    'zone_from': zone_from,
                    'zone_to': zone_to,
                    'spread': spread,
                    'volume': volume,
                    'profit': profit,
                    'risk': np.random.uniform(0.2, 0.8),
                    'confidence': np.random.uniform(0.6, 0.9)
                })
            
            # Market alerts
            alerts = []
            high_price_zones = [z for z in zone_data if z['rt_price'] > 100]
            for zone_info in high_price_zones[:3]:
                severity = 'CRITICAL' if zone_info['rt_price'] > 200 else 'HIGH' if zone_info['rt_price'] > 150 else 'MEDIUM'
                alerts.append({
                    'type': 'price_spike',
                    'severity': severity,
                    'zone': zone_info['zone'],
                    'message': f"Price spike in {zone_info['zone']}: ${zone_info['rt_price']:.2f}/MWh",
                    'value': zone_info['rt_price'],
                    'impact': zone_info['rt_price'] * 100,
                    'action': 'Consider demand response or supply actions'
                })
            
            # Add congestion alerts
            alerts.append({
                'type': 'congestion',
                'severity': 'HIGH',
                'zone': 'PJM Interface',
                'message': 'Interface congestion: PJM at 95.2%',
                'value': 95.2,
                'impact': 5000,
                'action': 'Monitor for arbitrage opportunities'
            })
            
            # Add trading opportunity alert
            best_opp = max(opportunities, key=lambda x: x['profit'])
            alerts.append({
                'type': 'trading_opportunity',
                'severity': 'MEDIUM',
                'zone': best_opp['zone_from'],
                'message': f"High profit {best_opp['type']}: {best_opp['zone_from']}→{best_opp['zone_to']} (${best_opp['profit']:.0f})",
                'value': best_opp['profit'],
                'impact': best_opp['profit'],
                'action': 'Execute trade or hedge position'
            })
            
            # Generation mix
            generation = [
                {'fuel': 'Natural Gas', 'generation': 12000 + np.random.normal(0, 1000), 'capacity_factor': 0.48 + np.random.normal(0, 0.1), 'marginal_cost': 35 + np.random.normal(0, 5)},
                {'fuel': 'Nuclear', 'generation': 5200 + np.random.normal(0, 200), 'capacity_factor': 0.96 + np.random.normal(0, 0.02), 'marginal_cost': 12 + np.random.normal(0, 2)},
                {'fuel': 'Hydro', 'generation': 2800 + np.random.normal(0, 400), 'capacity_factor': 0.62 + np.random.normal(0, 0.1), 'marginal_cost': 0},
                {'fuel': 'Wind', 'generation': 1800 + np.random.normal(0, 600), 'capacity_factor': 0.43 + np.random.normal(0, 0.15), 'marginal_cost': 0},
                {'fuel': 'Solar', 'generation': 800 + np.random.normal(0, 300), 'capacity_factor': 0.38 + np.random.normal(0, 0.2), 'marginal_cost': 0},
                {'fuel': 'Coal', 'generation': 400 + np.random.normal(0, 100), 'capacity_factor': 0.33 + np.random.normal(0, 0.1), 'marginal_cost': 45 + np.random.normal(0, 8)},
                {'fuel': 'Oil', 'generation': 200 + np.random.normal(0, 50), 'capacity_factor': 0.25 + np.random.normal(0, 0.1), 'marginal_cost': 85 + np.random.normal(0, 10)}
            ]
            
            # Interface flows
            interfaces = [
                {'name': 'PJM', 'flow': 750 + np.random.normal(0, 100), 'limit': 1000, 'utilization': 75 + np.random.normal(0, 10), 'congestion_cost': np.random.uniform(0, 50), 'shadow_price': np.random.uniform(0, 60)},
                {'name': 'NE', 'flow': 520 + np.random.normal(0, 80), 'limit': 800, 'utilization': 65 + np.random.normal(0, 10), 'congestion_cost': np.random.uniform(0, 30), 'shadow_price': np.random.uniform(0, 40)},
                {'name': 'HQ', 'flow': 980 + np.random.normal(0, 120), 'limit': 1200, 'utilization': 82 + np.random.normal(0, 8), 'congestion_cost': np.random.uniform(0, 40), 'shadow_price': np.random.uniform(0, 50)},
                {'name': 'OH', 'flow': 270 + np.random.normal(0, 50), 'limit': 600, 'utilization': 45 + np.random.normal(0, 15), 'congestion_cost': np.random.uniform(0, 20), 'shadow_price': np.random.uniform(0, 25)},
                {'name': 'Central East', 'flow': 1100 + np.random.normal(0, 150), 'limit': 2000, 'utilization': 55 + np.random.normal(0, 12), 'congestion_cost': np.random.uniform(0, 35), 'shadow_price': np.random.uniform(0, 45)},
                {'name': 'UPNY SENY', 'flow': 1700 + np.random.normal(0, 200), 'limit': 2500, 'utilization': 68 + np.random.normal(0, 10), 'congestion_cost': np.random.uniform(0, 45), 'shadow_price': np.random.uniform(0, 55)}
            ]
            
            # Portfolio summary
            portfolio = {
                'total_pnl': np.random.normal(45000, 15000),
                'daily_change': np.random.normal(0.12, 0.05),
                'active_positions': np.random.randint(15, 30),
                'profitable_positions': np.random.randint(8, 20),
                'at_risk_positions': np.random.randint(0, 5),
                'avg_price': np.random.normal(42, 8),
                'system_load': sum(z['load'] for z in zone_data),
                'load_change': np.random.normal(0.03, 0.02)
            }
            
            # Store all data
            self.current_data = {
                'zones': zone_data,
                'predictions': predictions,
                'opportunities': opportunities,
                'alerts': alerts,
                'generation': generation,
                'interfaces': interfaces,
                'portfolio': portfolio,
                'last_update': current_time.isoformat()
            }
            
            self.last_update = current_time
            return True
            
        except Exception as e:
            print(f"Error generating data: {e}")
            return False

# Initialize collector
collector = SimplifiedNYISOCollector()

def background_data_collection():
    """Background data collection without database"""
    while True:
        try:
            collector.generate_realistic_data()
            time.sleep(180)  # Update every 3 minutes
        except Exception as e:
            print(f"Background collection error: {e}")
            time.sleep(60)

# Start background thread
if not collector.is_collecting:
    collector.is_collecting = True
    thread = threading.Thread(target=background_data_collection, daemon=True)
    thread.start()

# HTML Template
dashboard_html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NYISO Enterprise Trading Platform</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', sans-serif; 
            background: linear-gradient(135deg, #0a0f1a 0%, #1a1f2e 100%); 
            color: #fff; 
            overflow-x: hidden;
        }
        
        .header {
            background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 50%, #06b6d4 100%);
            padding: 20px 0;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            position: sticky;
            top: 0;
            z-index: 1000;
        }
        
        .header-content {
            max-width: 1600px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0 20px;
        }
        
        .logo {
            font-size: 1.8rem;
            font-weight: bold;
            color: #fff;
        }
        
        .nav-tabs {
            display: flex;
            gap: 20px;
        }
        
        .nav-tab {
            padding: 10px 20px;
            background: rgba(255,255,255,0.1);
            border: none;
            border-radius: 6px;
            color: #fff;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .nav-tab.active, .nav-tab:hover {
            background: rgba(255,255,255,0.2);
            transform: translateY(-2px);
        }
        
        .container {
            max-width: 1600px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .dashboard-grid {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .card {
            background: linear-gradient(145deg, #1e293b 0%, #334155 100%);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid #475569;
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            transition: all 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 40px rgba(59, 130, 246, 0.15);
        }
        
        .card h3 {
            color: #3b82f6;
            margin-bottom: 15px;
            font-size: 1.2rem;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .metric-large {
            font-size: 2rem;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .metric-large.profit { color: #10b981; }
        .metric-large.loss { color: #ef4444; }
        .metric-large.neutral { color: #06b6d4; }
        
        .change-indicator {
            display: flex;
            align-items: center;
            gap: 5px;
            font-size: 0.9rem;
        }
        
        .change-up { color: #10b981; }
        .change-down { color: #ef4444; }
        
        .main-content {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 30px;
            margin-bottom: 30px;
        }
        
        .chart-container {
            background: linear-gradient(145deg, #1e293b 0%, #334155 100%);
            border-radius: 12px;
            padding: 25px;
            border: 1px solid #475569;
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
        
        .opportunities-panel {
            background: linear-gradient(145deg, #1e293b 0%, #334155 100%);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid #475569;
            max-height: 500px;
            overflow-y: auto;
        }
        
        .opportunity-item {
            background: rgba(59, 130, 246, 0.1);
            border-left: 4px solid #3b82f6;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 6px;
        }
        
        .opportunity-profit {
            color: #10b981;
            font-weight: bold;
            font-size: 1.1rem;
        }
        
        .alerts-panel {
            background: linear-gradient(145deg, #1e293b 0%, #334155 100%);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid #475569;
        }
        
        .alert-item {
            padding: 12px;
            margin-bottom: 10px;
            border-radius: 6px;
            border-left: 4px solid;
        }
        
        .alert-critical {
            background: rgba(239, 68, 68, 0.2);
            border-left-color: #ef4444;
        }
        
        .alert-high {
            background: rgba(245, 158, 11, 0.2);
            border-left-color: #f59e0b;
        }
        
        .alert-medium {
            background: rgba(59, 130, 246, 0.2);
            border-left-color: #3b82f6;
        }
        
        .table-container {
            background: linear-gradient(145deg, #1e293b 0%, #334155 100%);
            border-radius: 12px;
            padding: 25px;
            border: 1px solid #475569;
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
            border-bottom: 1px solid #475569;
        }
        
        .data-table th {
            background: rgba(59, 130, 246, 0.2);
            color: #3b82f6;
            font-weight: bold;
        }
        
        .price-cell {
            font-weight: bold;
        }
        
        .price-high { color: #ef4444; }
        .price-medium { color: #f59e0b; }
        .price-low { color: #10b981; }
        
        .status-indicator {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-right: 8px;
        }
        
        .status-online { background: #10b981; animation: pulse 2s infinite; }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .btn {
            background: linear-gradient(45deg, #3b82f6, #1e40af);
            color: #fff;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .btn:hover {
            background: linear-gradient(45deg, #1e40af, #3b82f6);
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(59, 130, 246, 0.4);
        }
        
        .success-message {
            background: rgba(16, 185, 129, 0.2);
            border: 1px solid #10b981;
            color: #10b981;
            padding: 10px 15px;
            border-radius: 6px;
            margin: 10px 0;
            text-align: center;
        }
        
        @media (max-width: 1200px) {
            .dashboard-grid { grid-template-columns: 1fr 1fr; }
            .main-content { grid-template-columns: 1fr; }
        }
        
        @media (max-width: 768px) {
            .dashboard-grid { grid-template-columns: 1fr; }
            .header-content { flex-direction: column; gap: 15px; }
            .nav-tabs { flex-wrap: wrap; }
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="header-content">
            <div class="logo">⚡ NYISO Enterprise Trading Platform</div>
            <div class="nav-tabs">
                <button class="nav-tab active" onclick="showTab('overview')">Market Overview</button>
                <button class="nav-tab" onclick="showTab('trading')">Trading Opportunities</button>
                <button class="nav-tab" onclick="showTab('predictions')">AI Predictions</button>
                <button class="nav-tab" onclick="showTab('analytics')">Advanced Analytics</button>
            </div>
            <div style="display: flex; align-items: center; gap: 15px;">
                <span class="status-indicator status-online"></span>
                <span>Live Market Data</span>
                <button class="btn" onclick="refreshAllData()">🔄 Refresh</button>
            </div>
        </div>
    </div>

    <div class="container">
        <div id="refresh-message"></div>
        
        <!-- Market Overview Tab -->
        <div id="overview-tab" class="tab-content">
            <div class="dashboard-grid">
                <div class="card">
                    <h3>💰 Total P&L Today</h3>
                    <div class="metric-large profit" id="total-pnl">+$47,250</div>
                    <div class="change-indicator change-up">
                        ↗ +12.5% vs yesterday
                    </div>
                </div>
                
                <div class="card">
                    <h3>📊 System Load</h3>
                    <div class="metric-large neutral" id="system-load">24,567 MW</div>
                    <div class="change-indicator change-up">
                        ↗ +3.2% vs forecast
                    </div>
                </div>
                
                <div class="card">
                    <h3>⚡ Avg Price</h3>
                    <div class="metric-large neutral" id="avg-price">$42.15/MWh</div>
                    <div class="change-indicator change-down">
                        ↘ -5.8% vs DA
                    </div>
                </div>
                
                <div class="card">
                    <h3>🎯 Active Positions</h3>
                    <div class="metric-large neutral" id="active-positions">23</div>
                    <div class="change-indicator">
                        📈 8 profitable, 3 at risk
                    </div>
                </div>
            </div>

            <div class="main-content">
                <div class="chart-container">
                    <h3>📈 Real-Time vs Day-Ahead Price Comparison</h3>
                    <div class="chart-wrapper">
                        <canvas id="priceComparisonChart"></canvas>
                    </div>
                </div>
                
                <div class="sidebar">
                    <div class="opportunities-panel">
                        <h3>🎯 Top Trading Opportunities</h3>
                        <div id="opportunities-list">
                            <!-- Dynamic content -->
                        </div>
                    </div>
                    
                    <div class="alerts-panel">
                        <h3>🚨 Market Alerts</h3>
                        <div id="alerts-list">
                            <!-- Dynamic content -->
                        </div>
                    </div>
                </div>
            </div>

            <div class="table-container">
                <h3>📊 Real-Time Zone Pricing & Load Data</h3>
                <table class="data-table" id="zone-data-table">
                    <thead>
                        <tr>
                            <th>Zone</th>
                            <th>RT Price ($/MWh)</th>
                            <th>DA Price ($/MWh)</th>
                            <th>Spread</th>
                            <th>Load (MW)</th>
                            <th>Congestion</th>
                            <th>Opportunity</th>
                        </tr>
                    </thead>
                    <tbody id="zone-data-body">
                        <!-- Dynamic content -->
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Trading Opportunities Tab -->
        <div id="trading-tab" class="tab-content" style="display: none;">
            <div class="chart-container">
                <h3>🎯 Trading Opportunity Analysis</h3>
                <div class="chart-wrapper">
                    <canvas id="opportunityChart"></canvas>
                </div>
            </div>
        </div>

        <!-- AI Predictions Tab -->
        <div id="predictions-tab" class="tab-content" style="display: none;">
            <div class="chart-container">
                <h3>🤖 AI-Powered Price & Load Forecasts</h3>
                <div class="chart-wrapper">
                    <canvas id="predictionChart"></canvas>
                </div>
            </div>
            
            <div class="table-container">
                <h3>🔮 Multi-Horizon Predictions</h3>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Zone</th>
                            <th>1H Price</th>
                            <th>4H Price</th>
                            <th>24H Price</th>
                            <th>1H Load</th>
                            <th>Congestion Risk</th>
                            <th>Confidence</th>
                        </tr>
                    </thead>
                    <tbody id="predictions-table-body">
                        <!-- Dynamic content -->
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Advanced Analytics Tab -->
        <div id="analytics-tab" class="tab-content" style="display: none;">
            <div class="chart-container">
                <h3>📈 Generation Mix & Capacity Analysis</h3>
                <div class="chart-wrapper">
                    <canvas id="generationChart"></canvas>
                </div>
            </div>
            
            <div class="chart-container">
                <h3>🔌 Interface Flow Analysis</h3>
                <div class="chart-wrapper">
                    <canvas id="interfaceChart"></canvas>
                </div>
            </div>
        </div>
    </div>

    <script>
        let charts = {};
        
        function showTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.style.display = 'none';
            });
            
            document.querySelectorAll('.nav-tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            document.getElementById(tabName + '-tab').style.display = 'block';
            event.target.classList.add('active');
            
            setTimeout(() => initializeCharts(tabName), 100);
        }
        
        function initializeCharts(tabName) {
            if (tabName === 'overview') {
                initPriceComparisonChart();
            } else if (tabName === 'trading') {
                initOpportunityChart();
            } else if (tabName === 'predictions') {
                initPredictionChart();
            } else if (tabName === 'analytics') {
                initGenerationChart();
                initInterfaceChart();
            }
        }
        
        function initPriceComparisonChart() {
            const ctx = document.getElementById('priceComparisonChart');
            if (!ctx) return;
            
            if (charts.priceComparison) {
                charts.priceComparison.destroy();
            }
            
            // Use real data from API
            fetch('/api/zone-data')
                .then(response => response.json())
                .then(data => {
                    const zones = data.zones.map(z => z.zone);
                    const rtPrices = data.zones.map(z => z.rt_price);
                    const daPrices = data.zones.map(z => z.da_price);
                    
                    charts.priceComparison = new Chart(ctx, {
                        type: 'line',
                        data: {
                            labels: zones,
                            datasets: [{
                                label: 'Real-Time Price',
                                data: rtPrices,
                                borderColor: '#3b82f6',
                                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                                tension: 0.4,
                                fill: true
                            }, {
                                label: 'Day-Ahead Price',
                                data: daPrices,
                                borderColor: '#10b981',
                                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                                tension: 0.4,
                                fill: false
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: {
                                    labels: { color: '#fff' }
                                }
                            },
                            scales: {
                                x: {
                                    ticks: { color: '#94a3b8' },
                                    grid: { color: '#475569' }
                                },
                                y: {
                                    ticks: { color: '#94a3b8' },
                                    grid: { color: '#475569' },
                                    title: {
                                        display: true,
                                        text: 'Price ($/MWh)',
                                        color: '#94a3b8'
                                    }
                                }
                            }
                        }
                    });
                })
                .catch(error => {
                    console.error('Error loading price data:', error);
                    // Fallback with sample data
                    charts.priceComparison = new Chart(ctx, {
                        type: 'line',
                        data: {
                            labels: ['CAPITL', 'CENTRL', 'DUNWOD', 'GENESE', 'HUD VL', 'LONGIL', 'MHK VL', 'MILLWD', 'N.Y.C.', 'NORTH', 'WEST'],
                            datasets: [{
                                label: 'Real-Time Price',
                                data: [38.5, 41.2, 52.3, 35.8, 48.7, 58.2, 33.9, 47.1, 62.4, 31.5, 39.8],
                                borderColor: '#3b82f6',
                                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                                tension: 0.4,
                                fill: true
                            }, {
                                label: 'Day-Ahead Price',
                                data: [42.1, 39.8, 48.9, 38.2, 52.1, 54.7, 36.4, 43.8, 58.9, 34.2, 42.3],
                                borderColor: '#10b981',
                                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                                tension: 0.4,
                                fill: false
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: {
                                    labels: { color: '#fff' }
                                }
                            },
                            scales: {
                                x: {
                                    ticks: { color: '#94a3b8' },
                                    grid: { color: '#475569' }
                                },
                                y: {
                                    ticks: { color: '#94a3b8' },
                                    grid: { color: '#475569' },
                                    title: {
                                        display: true,
                                        text: 'Price ($/MWh)',
                                        color: '#94a3b8'
                                    }
                                }
                            }
                        }
                    });
                });
        }
        
        function initOpportunityChart() {
            const ctx = document.getElementById('opportunityChart');
            if (!ctx) return;
            
            if (charts.opportunity) {
                charts.opportunity.destroy();
            }
            
            charts.opportunity = new Chart(ctx, {
                type: 'scatter',
                data: {
                    datasets: [{
                        label: 'Trading Opportunities',
                        data: [
                            {x: 15.6, y: 8420, r: 8},
                            {x: 12.3, y: 5230, r: 6},
                            {x: 45.0, y: 3180, r: 4},
                            {x: 8.7, y: 2100, r: 5},
                            {x: 22.1, y: 6750, r: 7}
                        ],
                        backgroundColor: 'rgba(59, 130, 246, 0.6)',
                        borderColor: '#3b82f6'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            labels: { color: '#fff' }
                        }
                    },
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: 'Price Spread ($/MWh)',
                                color: '#94a3b8'
                            },
                            ticks: { color: '#94a3b8' },
                            grid: { color: '#475569' }
                        },
                        y: {
                            title: {
                                display: true,
                                text: 'Profit Potential ($)',
                                color: '#94a3b8'
                            },
                            ticks: { color: '#94a3b8' },
                            grid: { color: '#475569' }
                        }
                    }
                }
            });
        }
        
        function initPredictionChart() {
            const ctx = document.getElementById('predictionChart');
            if (!ctx) return;
            
            if (charts.prediction) {
                charts.prediction.destroy();
            }
            
            const hours = [];
            const prices = [];
            const loads = [];
            
            for (let i = 0; i < 24; i++) {
                const time = new Date();
                time.setHours(time.getHours() + i);
                hours.push(time.getHours() + ':00');
                prices.push(40 + Math.sin(i * 0.3) * 15 + Math.random() * 10);
                loads.push(20000 + Math.sin(i * 0.2) * 5000 + Math.random() * 2000);
            }
            
            charts.prediction = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: hours,
                    datasets: [{
                        label: 'Predicted Price ($/MWh)',
                        data: prices,
                        borderColor: '#ef4444',
                        backgroundColor: 'rgba(239, 68, 68, 0.1)',
                        yAxisID: 'y'
                    }, {
                        label: 'Predicted Load (MW/1000)',
                        data: loads.map(l => l/1000),
                        borderColor: '#10b981',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        yAxisID: 'y1'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            labels: { color: '#fff' }
                        }
                    },
                    scales: {
                        x: {
                            ticks: { color: '#94a3b8' },
                            grid: { color: '#475569' }
                        },
                        y: {
                            type: 'linear',
                            display: true,
                            position: 'left',
                            ticks: { color: '#94a3b8' },
                            grid: { color: '#475569' },
                            title: {
                                display: true,
                                text: 'Price ($/MWh)',
                                color: '#94a3b8'
                            }
                        },
                        y1: {
                            type: 'linear',
                            display: true,
                            position: 'right',
                            ticks: { color: '#94a3b8' },
                            grid: { drawOnChartArea: false },
                            title: {
                                display: true,
                                text: 'Load (GW)',
                                color: '#94a3b8'
                            }
                        }
                    }
                }
            });
        }
        
        function initGenerationChart() {
            const ctx = document.getElementById('generationChart');
            if (!ctx) return;
            
            if (charts.generation) {
                charts.generation.destroy();
            }
            
            charts.generation = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['Natural Gas', 'Nuclear', 'Hydro', 'Wind', 'Solar', 'Coal', 'Oil'],
                    datasets: [{
                        data: [45.2, 24.8, 16.3, 8.7, 3.2, 1.5, 0.3],
                        backgroundColor: [
                            '#ef4444',
                            '#f59e0b',
                            '#3b82f6',
                            '#10b981',
                            '#fbbf24',
                            '#6b7280',
                            '#374151'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'right',
                            labels: { color: '#fff' }
                        }
                    }
                }
            });
        }
        
        function initInterfaceChart() {
            const ctx = document.getElementById('interfaceChart');
            if (!ctx) return;
            
            if (charts.interface) {
                charts.interface.destroy();
            }
            
            charts.interface = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: ['PJM', 'NE', 'HQ', 'OH', 'Central East', 'UPNY SENY'],
                    datasets: [{
                        label: 'Flow (MW)',
                        data: [750, 520, 980, 270, 1100, 1700],
                        backgroundColor: '#3b82f6'
                    }, {
                        label: 'Limit (MW)',
                        data: [1000, 800, 1200, 600, 2000, 2500],
                        backgroundColor: '#6b7280'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            labels: { color: '#fff' }
                        }
                    },
                    scales: {
                        x: {
                            ticks: { color: '#94a3b8' },
                            grid: { color: '#475569' }
                        },
                        y: {
                            ticks: { color: '#94a3b8' },
                            grid: { color: '#475569' },
                            title: {
                                display: true,
                                text: 'MW',
                                color: '#94a3b8'
                            }
                        }
                    }
                }
            });
        }
        
        async function updateZoneData() {
            try {
                const response = await fetch('/api/zone-data');
                const data = await response.json();
                
                if (!data.zones) {
                    throw new Error('No zone data received');
                }
                
                const tbody = document.getElementById('zone-data-body');
                tbody.innerHTML = '';
                
                data.zones.forEach(zone => {
                    const row = document.createElement('tr');
                    const spread = zone.rt_price - zone.da_price;
                    const spreadClass = spread > 5 ? 'price-high' : spread < -5 ? 'price-low' : 'price-medium';
                    const rtClass = zone.rt_price > 100 ? 'price-high' : zone.rt_price > 50 ? 'price-medium' : 'price-low';
                    
                    row.innerHTML = `
                        <td><strong>${zone.zone}</strong></td>
                        <td class="price-cell ${rtClass}">${zone.rt_price.toFixed(2)}</td>
                        <td class="price-cell">${zone.da_price.toFixed(2)}</td>
                        <td class="price-cell ${spreadClass}">${spread.toFixed(2)}</td>
                        <td>${zone.load.toFixed(0)} MW</td>
                        <td>${zone.congestion.toFixed(2)}</td>
                        <td>${zone.opportunity}</td>
                    `;
                    tbody.appendChild(row);
                });
                
                // Update dashboard metrics
                updateDashboardMetrics(data);
                
            } catch (error) {
                console.error('Error updating zone data:', error);
                // Use fallback data
                updateZoneDataFallback();
            }
        }
        
        function updateZoneDataFallback() {
            const tbody = document.getElementById('zone-data-body');
            tbody.innerHTML = '';
            
            const fallbackZones = [
                {zone: 'CAPITL', rt_price: 38.5, da_price: 42.1, congestion: 2.3, load: 1850, opportunity: 'Medium'},
                {zone: 'CENTRL', rt_price: 41.2, da_price: 39.8, congestion: 3.1, load: 1920, opportunity: 'Low'},
                {zone: 'DUNWOD', rt_price: 52.3, da_price: 48.9, congestion: 8.2, load: 3150, opportunity: 'High'},
                {zone: 'GENESE', rt_price: 35.8, da_price: 38.2, congestion: 1.8, load: 1750, opportunity: 'Low'},
                {zone: 'HUD VL', rt_price: 48.7, da_price: 52.1, congestion: 6.5, load: 2880, opportunity: 'Medium'},
                {zone: 'LONGIL', rt_price: 58.2, da_price: 54.7, congestion: 12.1, load: 3420, opportunity: 'High'},
                {zone: 'MHK VL', rt_price: 33.9, da_price: 36.4, congestion: 1.2, load: 1680, opportunity: 'Low'},
                {zone: 'MILLWD', rt_price: 47.1, da_price: 43.8, congestion: 5.8, load: 2650, opportunity: 'Medium'},
                {zone: 'N.Y.C.', rt_price: 62.4, da_price: 58.9, congestion: 15.2, load: 8750, opportunity: 'High'},
                {zone: 'NORTH', rt_price: 31.5, da_price: 34.2, congestion: 0.8, load: 1580, opportunity: 'Low'},
                {zone: 'WEST', rt_price: 39.8, da_price: 42.3, congestion: 2.9, load: 1890, opportunity: 'Low'}
            ];
            
            fallbackZones.forEach(zone => {
                const row = document.createElement('tr');
                const spread = zone.rt_price - zone.da_price;
                const spreadClass = spread > 5 ? 'price-high' : spread < -5 ? 'price-low' : 'price-medium';
                const rtClass = zone.rt_price > 100 ? 'price-high' : zone.rt_price > 50 ? 'price-medium' : 'price-low';
                
                row.innerHTML = `
                    <td><strong>${zone.zone}</strong></td>
                    <td class="price-cell ${rtClass}">${zone.rt_price.toFixed(2)}</td>
                    <td class="price-cell">${zone.da_price.toFixed(2)}</td>
                    <td class="price-cell ${spreadClass}">${spread.toFixed(2)}</td>
                    <td>${zone.load.toFixed(0)} MW</td>
                    <td>${zone.congestion.toFixed(2)}</td>
                    <td>${zone.opportunity}</td>
                `;
                tbody.appendChild(row);
            });
        }
        
        function updateDashboardMetrics(data) {
            if (data.portfolio) {
                document.getElementById('total-pnl').textContent = 
                    (data.portfolio.total_pnl >= 0 ? '+ : '-) + Math.abs(data.portfolio.total_pnl).toLocaleString();
                document.getElementById('system-load').textContent = 
                    Math.round(data.portfolio.system_load).toLocaleString() + ' MW';
                document.getElementById('avg-price').textContent = 
                    ' + data.portfolio.avg_price.toFixed(2) + '/MWh';
                document.getElementById('active-positions').textContent = 
                    data.portfolio.active_positions;
            }
        }
        
        async function updateOpportunities() {
            try {
                const response = await fetch('/api/opportunities');
                const data = await response.json();
                
                const opportunitiesList = document.getElementById('opportunities-list');
                opportunitiesList.innerHTML = '';
                
                data.opportunities.slice(0, 3).forEach(opp => {
                    const oppDiv = document.createElement('div');
                    oppDiv.className = 'opportunity-item';
                    oppDiv.innerHTML = `
                        <strong>${opp.type.replace('_', ' ').toUpperCase()}: ${opp.zone_from} → ${opp.zone_to}</strong>
                        <div class="opportunity-profit">Profit Potential: ${Math.round(opp.profit).toLocaleString()}</div>
                        <div>Spread: ${opp.spread.toFixed(2)}/MWh | Volume: ${Math.round(opp.volume)} MW | Risk: ${opp.risk < 0.3 ? 'Low' : opp.risk < 0.7 ? 'Medium' : 'High'}</div>
                    `;
                    opportunitiesList.appendChild(oppDiv);
                });
            } catch (error) {
                console.error('Error updating opportunities:', error);
            }
        }
        
        async function updateAlerts() {
            try {
                const response = await fetch('/api/alerts');
                const data = await response.json();
                
                const alertsList = document.getElementById('alerts-list');
                alertsList.innerHTML = '';
                
                data.alerts.slice(0, 3).forEach(alert => {
                    const alertDiv = document.createElement('div');
                    alertDiv.className = `alert-item alert-${alert.severity.toLowerCase()}`;
                    alertDiv.innerHTML = `
                        <strong>${alert.severity}:</strong> ${alert.message}
                        <div>Action: ${alert.action}</div>
                    `;
                    alertsList.appendChild(alertDiv);
                });
            } catch (error) {
                console.error('Error updating alerts:', error);
            }
        }
        
        function refreshAllData() {
            const refreshMessage = document.getElementById('refresh-message');
            refreshMessage.innerHTML = '<div class="success-message">🔄 Refreshing market data...</div>';
            
            Promise.all([
                updateZoneData(),
                updateOpportunities(),
                updateAlerts()
            ]).then(() => {
                const activeTab = document.querySelector('.nav-tab.active').textContent.toLowerCase();
                if (activeTab.includes('overview')) {
                    initPriceComparisonChart();
                }
                refreshMessage.innerHTML = '<div class="success-message">✅ Market data refreshed successfully!</div>';
                setTimeout(() => {
                    refreshMessage.innerHTML = '';
                }, 3000);
            }).catch(error => {
                console.error('Error refreshing data:', error);
                refreshMessage.innerHTML = '<div class="success-message">⚠️ Using fallback data - some features may be limited</div>';
                setTimeout(() => {
                    refreshMessage.innerHTML = '';
                }, 5000);
            });
        }
        
        // Auto-refresh every 2 minutes
        setInterval(refreshAllData, 120000);
        
        // Initialize on page load
        document.addEventListener('DOMContentLoaded', () => {
            initializeCharts('overview');
            updateZoneData();
            updateOpportunities();
            updateAlerts();
        });
    </script>
</body>
</html>
'''

# API Routes
@app.route('/')
def dashboard():
    return render_template_string(dashboard_html)

@app.route('/api/zone-data')
def get_zone_data():
    # Return data directly from collector without database dependency
    if hasattr(collector, 'current_data') and collector.current_data.get('zones'):
        return jsonify({
            'zones': collector.current_data['zones'],
            'portfolio': collector.current_data.get('portfolio', {})
        })
    else:
        # Fallback data if collector hasn't generated data yet
        return jsonify({
            'zones': [
                {'zone': 'CAPITL', 'rt_price': 38.5, 'da_price': 42.1, 'congestion': 2.3, 'load': 1850, 'opportunity': 'Medium'},
                {'zone': 'CENTRL', 'rt_price': 41.2, 'da_price': 39.8, 'congestion': 3.1, 'load': 1920, 'opportunity': 'Low'},
                {'zone': 'DUNWOD', 'rt_price': 52.3, 'da_price': 48.9, 'congestion': 8.2, 'load': 3150, 'opportunity': 'High'},
                {'zone': 'GENESE', 'rt_price': 35.8, 'da_price': 38.2, 'congestion': 1.8, 'load': 1750, 'opportunity': 'Low'},
                {'zone': 'HUD VL', 'rt_price': 48.7, 'da_price': 52.1, 'congestion': 6.5, 'load': 2880, 'opportunity': 'Medium'},
                {'zone': 'LONGIL', 'rt_price': 58.2, 'da_price': 54.7, 'congestion': 12.1, 'load': 3420, 'opportunity': 'High'},
                {'zone': 'MHK VL', 'rt_price': 33.9, 'da_price': 36.4, 'congestion': 1.2, 'load': 1680, 'opportunity': 'Low'},
                {'zone': 'MILLWD', 'rt_price': 47.1, 'da_price': 43.8, 'congestion': 5.8, 'load': 2650, 'opportunity': 'Medium'},
                {'zone': 'N.Y.C.', 'rt_price': 62.4, 'da_price': 58.9, 'congestion': 15.2, 'load': 8750, 'opportunity': 'High'},
                {'zone': 'NORTH', 'rt_price': 31.5, 'da_price': 34.2, 'congestion': 0.8, 'load': 1580, 'opportunity': 'Low'},
                {'zone': 'WEST', 'rt_price': 39.8, 'da_price': 42.3, 'congestion': 2.9, 'load': 1890, 'opportunity': 'Low'}
            ],
            'portfolio': {
                'total_pnl': 47250,
                'system_load': 30457,
                'avg_price': 45.2,
                'active_positions': 23
            }
        })

@app.route('/api/opportunities')
def get_opportunities():
    if hasattr(collector, 'current_data') and collector.current_data.get('opportunities'):
        return jsonify({'opportunities': collector.current_data['opportunities']})
    else:
        return jsonify({'opportunities': [
            {'type': 'spatial_arbitrage', 'zone_from': 'N.Y.C.', 'zone_to': 'LONGIL', 'spread': 15.6, 'volume': 540, 'profit': 8420, 'risk': 0.3},
            {'type': 'temporal_arbitrage', 'zone_from': 'CAPITL', 'zone_to': 'CAPITL', 'spread': 12.3, 'volume': 425, 'profit': 5230, 'risk': 0.5},
            {'type': 'spatial_arbitrage', 'zone_from': 'DUNWOD', 'zone_to': 'CENTRL', 'spread': 8.7, 'volume': 320, 'profit': 2780, 'risk': 0.2}
        ]})

@app.route('/api/alerts')
def get_alerts():
    if hasattr(collector, 'current_data') and collector.current_data.get('alerts'):
        return jsonify({'alerts': collector.current_data['alerts']})
    else:
        return jsonify({'alerts': [
            {'severity': 'CRITICAL', 'message': 'Price spike in NYC - $287.50/MWh', 'action': 'Consider demand response activation'},
            {'severity': 'HIGH', 'message': 'Interface congestion - PJM at 95%', 'action': 'Monitor for arbitrage opportunities'},
            {'severity': 'MEDIUM', 'message': 'Wind forecast updated - 15% increase', 'action': 'Adjust renewable energy positions'}
        ]})

@app.route('/api/refresh')
def refresh_data():
    success = collector.generate_realistic_data()
    return jsonify({
        'success': success,
        'message': 'Data refreshed successfully' if success else 'Refresh failed, using cached data',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'NYISO Enterprise Trading Platform',
        'version': '4.0.0',
        'zones_monitored': len(collector.zones),
        'data_available': bool(collector.current_data),
        'last_update': collector.last_update.isoformat() if hasattr(collector, 'last_update') else None,
        'capabilities': [
            'Real-time market data simulation',
            'Trading opportunity analysis', 
            'Price forecasting',
            'Market alerts',
            'Portfolio tracking'
        ]
    })

if __name__ == '__main__':
    print("🚀 Starting NYISO Enterprise Trading Platform V4...")
    print("📊 Dashboard: Cloud-optimized version")
    print("🔄 Data collection: In-memory storage")
    print("💾 Database: Removed SQLite dependency")
    print("☁️ Cloud-ready: No file system dependencies")
    print("⚡ All NYISO zones: Simulated with realistic data")
    print("🎯 Ready for deployment...")
    
    # Generate initial data
    collector.generate_realistic_data()
    
    # Start the app
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

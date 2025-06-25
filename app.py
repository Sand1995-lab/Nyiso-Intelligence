from flask import Flask, render_template_string, jsonify
import json
import random
import time
from datetime import datetime
import os

app = Flask(__name__)

class StandaloneNYISOData:
    def __init__(self):
        self.zones = ['CAPITL', 'CENTRL', 'DUNWOD', 'GENESE', 'HUD VL', 'LONGIL', 'MHK VL', 'MILLWD', 'N.Y.C.', 'NORTH', 'WEST']
        
    def generate_zone_data(self):
        zone_data = []
        total_load = 0
        total_price = 0
        
        for zone in self.zones:
            if zone == 'N.Y.C.':
                base_price = random.uniform(55, 75)
                load = random.uniform(7500, 9500)
                congestion = random.uniform(10, 20)
            elif zone in ['LONGIL', 'DUNWOD']:
                base_price = random.uniform(45, 65)
                load = random.uniform(2800, 3800)
                congestion = random.uniform(5, 15)
            else:
                base_price = random.uniform(35, 55)
                load = random.uniform(1500, 2500)
                congestion = random.uniform(1, 8)
            
            da_price = base_price * random.uniform(0.92, 1.08)
            opportunity = "High" if abs(base_price - da_price) > 8 else "Medium" if abs(base_price - da_price) > 3 else "Low"
            
            zone_data.append({
                'zone': zone,
                'rt_price': round(base_price, 2),
                'da_price': round(da_price, 2),
                'congestion': round(congestion, 2),
                'load': round(load, 0),
                'opportunity': opportunity
            })
            
            total_load += load
            total_price += base_price
        
        avg_price = total_price / len(self.zones)
        
        return {
            'zones': zone_data,
            'portfolio': {
                'total_pnl': random.randint(25000, 85000),
                'system_load': round(total_load, 0),
                'avg_price': round(avg_price, 2),
                'active_positions': random.randint(18, 28)
            }
        }
    
    def generate_opportunities(self):
        opportunities = []
        
        opportunity_types = [
            ('spatial_arbitrage', 'N.Y.C.', 'CENTRL', random.uniform(8, 20), random.uniform(300, 800)),
            ('temporal_arbitrage', 'LONGIL', 'LONGIL', random.uniform(5, 15), random.uniform(200, 600)),
            ('spatial_arbitrage', 'DUNWOD', 'NORTH', random.uniform(10, 25), random.uniform(150, 500)),
            ('congestion_play', 'CAPITL', 'GENESE', random.uniform(12, 18), random.uniform(250, 650))
        ]
        
        for opp_type, zone_from, zone_to, spread, volume in opportunity_types:
            profit = spread * volume * random.uniform(0.6, 0.9)
            risk = random.uniform(0.2, 0.8)
            
            opportunities.append({
                'type': opp_type,
                'zone_from': zone_from,
                'zone_to': zone_to,
                'spread': round(spread, 2),
                'volume': round(volume, 0),
                'profit': round(profit, 0),
                'risk': round(risk, 2)
            })
        
        return sorted(opportunities, key=lambda x: x['profit'], reverse=True)
    
    def generate_alerts(self):
        alerts = []
        
        alert_templates = [
            ('CRITICAL', 'Price spike in {zone} - ${price:.2f}/MWh', 'Consider demand response activation'),
            ('HIGH', 'Interface congestion - {interface} at {util:.0f}%', 'Monitor for arbitrage opportunities'),
            ('MEDIUM', 'Wind forecast updated - {change:+.0f}% change', 'Adjust renewable energy positions'),
            ('HIGH', 'Load forecast deviation in {zone} - {deviation:+.1f}%', 'Review generation commitments'),
            ('MEDIUM', 'Virtual trading opportunity in {zone}', 'Execute hedge positions')
        ]
        
        for severity, message_template, action in alert_templates[:3]:  # Show 3 alerts
            if 'zone' in message_template:
                zone = random.choice(self.zones)
                if 'price' in message_template:
                    price = random.uniform(150, 300)
                    message = message_template.format(zone=zone, price=price)
                elif 'deviation' in message_template:
                    deviation = random.uniform(-15, 20)
                    message = message_template.format(zone=zone, deviation=deviation)
                else:
                    message = message_template.format(zone=zone)
            elif 'interface' in message_template:
                interface = random.choice(['PJM', 'NE', 'HQ', 'OH'])
                util = random.uniform(85, 98)
                message = message_template.format(interface=interface, util=util)
            elif 'change' in message_template:
                change = random.uniform(-25, 35)
                message = message_template.format(change=change)
            else:
                message = message_template
            
            alerts.append({
                'severity': severity,
                'message': message,
                'action': action
            })
        
        return alerts

# Initialize data generator
data_generator = StandaloneNYISOData()

# HTML Template - Complete standalone version
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
            padding: 10px;
            border-radius: 6px;
            margin: 10px 0;
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
                <button class="btn" onclick="refreshAllData()">🔄 REFRESH</button>
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
        let currentData = {
            zones: [],
            opportunities: [],
            alerts: [],
            portfolio: {}
        };
        
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
            
            const rtPrices = currentData.zones.map(zone => zone.rt_price);
            const daPrices = currentData.zones.map(zone => zone.da_price);
            const labels = currentData.zones.map(zone => zone.zone);
            
            charts.priceComparison = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
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
        }
        
        function initOpportunityChart() {
            const ctx = document.getElementById('opportunityChart');
            if (!ctx) return;
            
            if (charts.opportunity) {
                charts.opportunity.destroy();
            }
            
            const opportunityData = currentData.opportunities.map(opp => ({
                x: opp.spread,
                y: opp.profit,
                r: Math.max(4, Math.min(15, opp.volume / 100))
            }));
            
            charts.opportunity = new Chart(ctx, {
                type: 'scatter',
                data: {
                    datasets: [{
                        label: 'Trading Opportunities',
                        data: opportunityData,
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
                
                currentData.zones = data.zones;
                currentData.portfolio = data.portfolio;
                
                const tbody = document.getElementById('zone-data-body');
                tbody.innerHTML = '';
                
                data.zones.forEach(zone => {
                    const row = document.createElement('tr');
                    const spread = zone.rt_price - zone.da_price;
                    const spreadClass = spread > 5 ? 'price-high' : spread < -5 ? 'price-low' : 'price-medium';
                    const rtClass = zone.rt_price > 60 ? 'price-high' : zone.rt_price > 45 ? 'price-medium' : 'price-low';
                    
                    row.innerHTML = `
                        <td><strong>${zone.zone}</strong></td>
                        <td class="price-cell ${rtClass}">${zone.rt_price.toFixed(2)}</td>
                        <td class="price-cell">${zone.da_price.toFixed(2)}</td>
                        <td class="price-cell ${spreadClass}">${spread.toFixed(2)}</td>
                        <td>${zone.load.toLocaleString()} MW</td>
                        <td>${zone.congestion.toFixed(2)}</td>
                        <td><span class="opportunity-${zone.opportunity.toLowerCase()}">${zone.opportunity}</span></td>
                    `;
                    tbody.appendChild(row);
                });
                
                // Update dashboard metrics
                updateDashboardMetrics(data.portfolio);
                
                return true;
            } catch (error) {
                console.error('Error updating zone data:', error);
                return false;
            }
        }
        
        function updateDashboardMetrics(portfolio) {
            if (portfolio) {
                const pnlElement = document.getElementById('total-pnl');
                const pnl = portfolio.total_pnl;
                pnlElement.textContent = (pnl >= 0 ? '+
                 : '-
                ) + Math.abs(pnl).toLocaleString();
                pnlElement.className = 'metric-large ' + (pnl >= 0 ? 'profit' : 'loss');
                
                document.getElementById('system-load').textContent = Math.round(portfolio.system_load).toLocaleString() + ' MW';
                document.getElementById('avg-price').textContent = '
                 + portfolio.avg_price.toFixed(2) + '/MWh';
                document.getElementById('active-positions').textContent = portfolio.active_positions;
            }
        }
        
        async function updateOpportunities() {
            try {
                const response = await fetch('/api/opportunities');
                const data = await response.json();
                
                currentData.opportunities = data.opportunities;
                
                const opportunitiesList = document.getElementById('opportunities-list');
                opportunitiesList.innerHTML = '';
                
                data.opportunities.slice(0, 3).forEach(opp => {
                    const oppDiv = document.createElement('div');
                    oppDiv.className = 'opportunity-item';
                    const riskLevel = opp.risk < 0.4 ? 'Low' : opp.risk < 0.7 ? 'Medium' : 'High';
                    oppDiv.innerHTML = `
                        <strong>${opp.type.replace(/_/g, ' ').toUpperCase()}: ${opp.zone_from} → ${opp.zone_to}</strong>
                        <div class="opportunity-profit">Profit Potential: ${opp.profit.toLocaleString()}</div>
                        <div>Spread: ${opp.spread.toFixed(2)}/MWh | Volume: ${opp.volume.toLocaleString()} MW | Risk: ${riskLevel}</div>
                    `;
                    opportunitiesList.appendChild(oppDiv);
                });
                
                return true;
            } catch (error) {
                console.error('Error updating opportunities:', error);
                return false;
            }
        }
        
        async function updateAlerts() {
            try {
                const response = await fetch('/api/alerts');
                const data = await response.json();
                
                currentData.alerts = data.alerts;
                
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
                
                return true;
            } catch (error) {
                console.error('Error updating alerts:', error);
                return false;
            }
        }
        
        function refreshAllData() {
            const refreshMessage = document.getElementById('refresh-message');
            refreshMessage.innerHTML = '<div class="success-message">🔄 Refreshing market data...</div>';
            
            // Call refresh API
            fetch('/api/refresh')
                .then(response => response.json())
                .then(() => {
                    return Promise.all([
                        updateZoneData(),
                        updateOpportunities(),
                        updateAlerts()
                    ]);
                })
                .then(() => {
                    const activeTab = document.querySelector('.nav-tab.active').textContent.toLowerCase();
                    if (activeTab.includes('overview')) {
                        initPriceComparisonChart();
                    } else if (activeTab.includes('trading')) {
                        initOpportunityChart();
                    }
                    refreshMessage.innerHTML = '<div class="success-message">✅ Market data refreshed successfully!</div>';
                    setTimeout(() => {
                        refreshMessage.innerHTML = '';
                    }, 3000);
                })
                .catch(error => {
                    console.error('Error refreshing data:', error);
                    refreshMessage.innerHTML = '<div class="success-message">⚠️ Connection issue - data may be cached</div>';
                    setTimeout(() => {
                        refreshMessage.innerHTML = '';
                    }, 5000);
                });
        }
        
        // Auto-refresh every 3 minutes
        setInterval(refreshAllData, 180000);
        
        // Initialize on page load
        document.addEventListener('DOMContentLoaded', () => {
            // Load initial data
            Promise.all([
                updateZoneData(),
                updateOpportunities(),
                updateAlerts()
            ]).then(() => {
                initializeCharts('overview');
            }).catch(error => {
                console.error('Error loading initial data:', error);
                // Still initialize charts with empty data
                initializeCharts('overview');
            });
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
    try:
        data = data_generator.generate_zone_data()
        return jsonify(data)
    except Exception as e:
        print(f"Error generating zone data: {e}")
        return jsonify({'error': 'Data generation failed'}), 500

@app.route('/api/opportunities')
def get_opportunities():
    try:
        opportunities = data_generator.generate_opportunities()
        return jsonify({'opportunities': opportunities})
    except Exception as e:
        print(f"Error generating opportunities: {e}")
        return jsonify({'error': 'Opportunities generation failed'}), 500

@app.route('/api/alerts')
def get_alerts():
    try:
        alerts = data_generator.generate_alerts()
        return jsonify({'alerts': alerts})
    except Exception as e:
        print(f"Error generating alerts: {e}")
        return jsonify({'error': 'Alerts generation failed'}), 500

@app.route('/api/refresh')
def refresh_data():
    try:
        # Simulate data refresh
        time.sleep(0.5)  # Small delay to simulate processing
        return jsonify({
            'success': True,
            'message': 'Data refreshed successfully',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        print(f"Error refreshing data: {e}")
        return jsonify({'error': 'Refresh failed'}), 500

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'NYISO Enterprise Trading Platform',
        'version': '5.0.0 - Standalone',
        'features': [
            'Real-time market simulation',
            'Trading opportunity analysis', 
            'Dynamic price forecasting',
            'Market alerts system',
            'Portfolio tracking',
            'Multi-zone monitoring'
        ],
        'zones_monitored': len(data_generator.zones),
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🚀 Starting NYISO Enterprise Trading Platform V5...")
    print("💡 Standalone Version - No Dependencies")
    print("📊 Dashboard: Fully self-contained")
    print("🔄 Data: Dynamic generation")
    print("⚡ All NYISO zones: Real-time simulation")
    print("🎯 Ready for immediate use...")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

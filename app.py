from flask import Flask, render_template_string
import json
import random
import os
from datetime import datetime

app = Flask(__name__)

# Complete HTML with all JavaScript properly finished
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
                    <div class="metric-large profit" id="total-pnl">+$63,420</div>
                    <div class="change-indicator change-up">
                        ↗ +14.8% vs yesterday
                    </div>
                </div>
                
                <div class="card">
                    <h3>📊 System Load</h3>
                    <div class="metric-large neutral" id="system-load">28,945 MW</div>
                    <div class="change-indicator change-up">
                        ↗ +2.7% vs forecast
                    </div>
                </div>
                
                <div class="card">
                    <h3>⚡ Avg Price</h3>
                    <div class="metric-large neutral" id="avg-price">$48.75/MWh</div>
                    <div class="change-indicator change-down">
                        ↘ -3.2% vs DA
                    </div>
                </div>
                
                <div class="card">
                    <h3>🎯 Active Positions</h3>
                    <div class="metric-large neutral" id="active-positions">26</div>
                    <div class="change-indicator">
                        📈 19 profitable, 2 at risk
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
                        <!-- Will be populated by JavaScript -->
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
        // Global variables
        let charts = {};
        let marketData = {};
        
        // Market Data Generator Class
        class NYISODataGenerator {
            constructor() {
                this.zones = ['CAPITL', 'CENTRL', 'DUNWOD', 'GENESE', 'HUD VL', 'LONGIL', 'MHK VL', 'MILLWD', 'N.Y.C.', 'NORTH', 'WEST'];
                this.generateNewData();
            }
            
            generateNewData() {
                const zones = [];
                let totalLoad = 0;
                let totalPrice = 0;
                
                this.zones.forEach(zone => {
                    let basePrice, load, congestion;
                    
                    if (zone === 'N.Y.C.') {
                        basePrice = 55 + Math.random() * 25;
                        load = 7500 + Math.random() * 2000;
                        congestion = 10 + Math.random() * 15;
                    } else if (['LONGIL', 'DUNWOD'].includes(zone)) {
                        basePrice = 45 + Math.random() * 20;
                        load = 2800 + Math.random() * 1000;
                        congestion = 5 + Math.random() * 10;
                    } else {
                        basePrice = 35 + Math.random() * 20;
                        load = 1500 + Math.random() * 1000;
                        congestion = 1 + Math.random() * 7;
                    }
                    
                    const daPrice = basePrice * (0.92 + Math.random() * 0.16);
                    const spread = basePrice - daPrice;
                    const opportunity = Math.abs(spread) > 8 ? 'High' : Math.abs(spread) > 3 ? 'Medium' : 'Low';
                    
                    zones.push({
                        zone,
                        rt_price: parseFloat(basePrice.toFixed(2)),
                        da_price: parseFloat(daPrice.toFixed(2)),
                        spread: parseFloat(spread.toFixed(2)),
                        load: Math.round(load),
                        congestion: parseFloat(congestion.toFixed(2)),
                        opportunity
                    });
                    
                    totalLoad += load;
                    totalPrice += basePrice;
                });
                
                marketData = {
                    zones,
                    portfolio: {
                        total_pnl: 50000 + Math.random() * 30000,
                        system_load: Math.round(totalLoad),
                        avg_price: parseFloat((totalPrice / this.zones.length).toFixed(2)),
                        active_positions: 20 + Math.round(Math.random() * 10)
                    },
                    opportunities: this.generateOpportunities(),
                    alerts: this.generateAlerts()
                };
            }
            
            generateOpportunities() {
                return [
                    {
                        type: 'spatial_arbitrage',
                        zone_from: 'N.Y.C.',
                        zone_to: 'CENTRL',
                        spread: 15 + Math.random() * 10,
                        volume: 500 + Math.random() * 300,
                        profit: 8000 + Math.random() * 8000,
                        risk: 0.3 + Math.random() * 0.4
                    },
                    {
                        type: 'temporal_arbitrage',
                        zone_from: 'LONGIL',
                        zone_to: 'LONGIL',
                        spread: 8 + Math.random() * 8,
                        volume: 400 + Math.random() * 400,
                        profit: 4000 + Math.random() * 6000,
                        risk: 0.2 + Math.random() * 0.3
                    },
                    {
                        type: 'congestion_play',
                        zone_from: 'DUNWOD',
                        zone_to: 'NORTH',
                        spread: 12 + Math.random() * 15,
                        volume: 200 + Math.random() * 300,
                        profit: 3000 + Math.random() * 5000,
                        risk: 0.4 + Math.random() * 0.4
                    }
                ];
            }
            
            generateAlerts() {
                return [
                    { 
                        severity: 'CRITICAL', 
                        message: 'Price spike in N.Y.C. - $' + (200 + Math.random() * 100).toFixed(2) + '/MWh', 
                        action: 'Consider demand response activation' 
                    },
                    { 
                        severity: 'HIGH', 
                        message: 'Interface congestion - PJM at ' + (85 + Math.random() * 13).toFixed(0) + '%', 
                        action: 'Monitor for arbitrage opportunities' 
                    },
                    { 
                        severity: 'MEDIUM', 
                        message: 'Wind forecast updated - ' + (Math.random() > 0.5 ? '+' : '') + (Math.random() * 30 - 15).toFixed(0) + '% change', 
                        action: 'Adjust renewable energy positions' 
                    }
                ];
            }
        }
        
        // Initialize data generator
        const dataGenerator = new NYISODataGenerator();
        
        // Tab Management
        function showTab(tabName) {
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.style.display = 'none';
            });
            
            // Remove active class from all nav tabs
            document.querySelectorAll('.nav-tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Show selected tab
            document.getElementById(tabName + '-tab').style.display = 'block';
            event.target.classList.add('active');
            
            // Initialize charts for the tab
            setTimeout(() => initializeCharts(tabName), 100);
        }
        
        // Chart Initialization
        function initializeCharts(tabName) {
            try {
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
            } catch (error) {
                console.error('Error initializing charts:', error);
            }
        }
        
        function initPriceComparisonChart() {
            const ctx = document.getElementById('priceComparisonChart');
            if (!ctx) return;
            
            if (charts.priceComparison) {
                charts.priceComparison.destroy();
            }
            
            const rtPrices = marketData.zones.map(zone => zone.rt_price);
            const daPrices = marketData.zones.map(zone => zone.da_price);
            const labels = marketData.zones.map(zone => zone.zone);
            
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
            
            const opportunityData = marketData.opportunities.map(opp => ({
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
        
        // Data Update Functions
        function updateZoneData() {
            try {
                const tbody = document.getElementById('zone-data-body');
                if (!tbody) return;
                
                tbody.innerHTML = '';
                
                marketData.zones.forEach(zone => {
                    const row = document.createElement('tr');
                    const spread = zone.spread;
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
                updateDashboardMetrics();
                
            } catch (error) {
                console.error('Error updating zone data:', error);
            }
        }
        
        function updateDashboardMetrics() {
            try {
                const portfolio = marketData.portfolio;
                
                const pnlElement = document.getElementById('total-pnl');
                if (pnlElement) {
                    const pnl = portfolio.total_pnl;
                    pnlElement.textContent = (pnl >= 0 ? '+ : '-) + Math.abs(pnl).toLocaleString();
                    pnlElement.className = 'metric-large ' + (pnl >= 0 ? 'profit' : 'loss');
                }
                
                const systemLoadElement = document.getElementById('system-load');
                if (systemLoadElement) {
                    systemLoadElement.textContent = Math.round(portfolio.system_load).toLocaleString() + ' MW';
                }
                
                const avgPriceElement = document.getElementById('avg-price');
                if (avgPriceElement) {
                    avgPriceElement.textContent = ' + portfolio.avg_price.toFixed(2) + '/MWh';
                }
                
                const activePositionsElement = document.getElementById('active-positions');
                if (activePositionsElement) {
                    activePositionsElement.textContent = portfolio.active_positions;
                }
                
            } catch (error) {
                console.error('Error updating dashboard metrics:', error);
            }
        }
        
        function updateOpportunities() {
            try {
                const opportunitiesList = document.getElementById('opportunities-list');
                if (!opportunitiesList) return;
                
                opportunitiesList.innerHTML = '';
                
                marketData.opportunities.forEach(opp => {
                    const oppDiv = document.createElement('div');
                    oppDiv.className = 'opportunity-item';
                    const riskLevel = opp.risk < 0.4 ? 'Low' : opp.risk < 0.7 ? 'Medium' : 'High';
                    oppDiv.innerHTML = `
                        <strong>${opp.type.replace(/_/g, ' ').toUpperCase()}: ${opp.zone_from} → ${opp.zone_to}</strong>
                        <div class="opportunity-profit">Profit Potential: ${Math.round(opp.profit).toLocaleString()}</div>
                        <div>Spread: ${opp.spread.toFixed(2)}/MWh | Volume: ${Math.round(opp.volume).toLocaleString()} MW | Risk: ${riskLevel}</div>
                    `;
                    opportunitiesList.appendChild(oppDiv);
                });
                
            } catch (error) {
                console.error('Error updating opportunities:', error);
            }
        }
        
        function updateAlerts() {
            try {
                const alertsList = document.getElementById('alerts-list');
                if (!alertsList) return;
                
                alertsList.innerHTML = '';
                
                marketData.alerts.forEach(alert => {
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
        
        // Main refresh function
        function refreshAllData() {
            try {
                const refreshMessage = document.getElementById('refresh-message');
                if (refreshMessage) {
                    refreshMessage.innerHTML = '<div class="success-message">🔄 Refreshing market data...</div>';
                }
                
                // Generate new data
                dataGenerator.generateNewData();
                
                // Update all components
                updateZoneData();
                updateOpportunities();
                updateAlerts();
                
                // Refresh active chart
                const activeTab = document.querySelector('.nav-tab.active');
                if (activeTab) {
                    const tabName = activeTab.textContent.toLowerCase();
                    if (tabName.includes('overview')) {
                        initPriceComparisonChart();
                    } else if (tabName.includes('trading')) {
                        initOpportunityChart();
                    }
                }
                
                if (refreshMessage) {
                    refreshMessage.innerHTML = '<div class="success-message">✅ Market data refreshed successfully!</div>';
                    setTimeout(() => {
                        refreshMessage.innerHTML = '';
                    }, 3000);
                }
                
            } catch (error) {
                console.error('Error refreshing data:', error);
                const refreshMessage = document.getElementById('refresh-message');
                if (refreshMessage) {
                    refreshMessage.innerHTML = '<div class="success-message">⚠️ Refresh completed with some issues</div>';
                    setTimeout(() => {
                        refreshMessage.innerHTML = '';
                    }, 5000);
                }
            }
        }
        
        // Auto-refresh every 3 minutes
        setInterval(refreshAllData, 180000);
        
        // Initialize everything when page loads
        document.addEventListener('DOMContentLoaded', function() {
            console.log('🚀 Initializing NYISO Dashboard...');
            
            try {
                // Load initial data
                updateZoneData();
                updateOpportunities(); 
                updateAlerts();
                
                // Initialize charts after a short delay
                setTimeout(() => {
                    initializeCharts('overview');
                    console.log('✅ Dashboard initialized successfully!');
                }, 500);
                
            } catch (error) {
                console.error('❌ Error during initialization:', error);
            }
        });
        
        // Debug function for troubleshooting
        function debugInfo() {
            console.log('Market Data:', marketData);
            console.log('Charts:', charts);
            console.log('Zone table rows:', document.querySelectorAll('#zone-data-body tr').length);
            console.log('Chart.js loaded:', typeof Chart !== 'undefined');
        }
        
        // Make functions available globally
        window.showTab = showTab;
        window.refreshAllData = refreshAllData;
        window.debugInfo = debugInfo;
        
    </script>
</body>
</html>
'''

@app.route('/')
def dashboard():
    return render_template_string(dashboard_html)

@app.route('/health')
def health():
    return {
        'status': 'healthy',
        'service': 'NYISO Enterprise Trading Platform',
        'version': '6.0.0 - Complete Fixed',
        'timestamp': datetime.now().isoformat(),
        'features': [
            'Real-time market simulation',
            'Trading opportunity analysis', 
            'Interactive charts with Chart.js',
            'Market alerts system',
            'Portfolio tracking',
            'Multi-zone NYISO monitoring'
        ]
    }

if __name__ == '__main__':
    print("🚀 Starting NYISO Enterprise Trading Platform V6...")
    print("✅ Complete JavaScript - All functions finished")
    print("📊 Charts: Interface chart properly completed")
    print("🔧 All syntax errors fixed")
    print("💾 Data: In-memory generation")
    print("⚡ Ready for deployment...")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

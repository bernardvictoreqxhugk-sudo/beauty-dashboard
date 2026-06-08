/* ================================================================
   美妆品牌分析仪表板 — 共享 JS 工具 & ECharts 图表函数
   ================================================================ */

// 品牌颜色映射 (固定颜色，确保同一品牌在不同图表中颜色一致)
const BRAND_COLORS = [
    '#e94560','#3498db','#2ecc71','#f1c40f','#9b59b6','#1abc9c',
    '#e67e22','#e74c3c','#2980b9','#27ae60','#f39c12','#8e44ad',
    '#16a085','#d35400','#c0392b'
];

// ================================================================
// ECharts 暗色主题
// ================================================================
const DARK_THEME = {
    textStyle: { color: '#8899aa' },
    title: { textStyle: { color: '#e8edf2' } },
};

// ================================================================
// 通用：创建横向柱状图 (用于排名)
// ================================================================
function createRankChart(domId, categories, values, title, colorFunc) {
    const chart = echarts.init(document.getElementById(domId));
    const data = categories.map((name, i) => ({
        value: values[i], itemStyle: { color: colorFunc ? colorFunc(values[i]) : BRAND_COLORS[i % BRAND_COLORS.length] }
    }));
    chart.setOption({
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
        grid: { left: '15%', right: '10%', top: '5%', bottom: '5%' },
        xAxis: { type: 'value', axisLabel: { color: '#8899aa' }, splitLine: { lineStyle: { color: '#2a3a4a' } } },
        yAxis: { type: 'category', data: categories.reverse(), axisLabel: { color: '#e8edf2', fontSize: 11 }, inverse: true },
        series: [{ type: 'bar', data: data.reverse(), barMaxWidth: 28,
            label: { show: true, position: 'right', color: '#8899aa', fontSize: 10,
                formatter: p => p.value.toFixed(3) } }]
    });
    return chart;
}

// ================================================================
// 通用：气泡/散点图
// ================================================================
function createBubbleChart(domId, data, xKey, yKey, sizeKey, colorKey) {
    const chart = echarts.init(document.getElementById(domId));
    const maxSize = Math.max(...data.map(d => d[sizeKey]));
    chart.setOption({
        tooltip: {
            formatter: p => `${p.data[3]}<br/>价格: ¥${p.data[0].toFixed(0)}<br/>销量: ${p.data[1].toFixed(0)}<br/>评论: ${p.data[2]}<br/>情感: ${p.data[4].toFixed(3)}`
        },
        grid: { left: '12%', right: '8%', top: '5%', bottom: '8%' },
        xAxis: { type: 'value', name: '平均价格 (¥)', nameTextStyle: { color: '#8899aa' },
            axisLabel: { color: '#8899aa' }, splitLine: { lineStyle: { color: '#2a3a4a' } } },
        yAxis: { type: 'value', name: '平均销量', nameTextStyle: { color: '#8899aa' },
            axisLabel: { color: '#8899aa' }, splitLine: { lineStyle: { color: '#2a3a4a' } } },
        series: [{
            type: 'scatter', data: data.map((d, i) => ([d[xKey], d[yKey], (d[sizeKey]/maxSize)*60 + 10, d['品牌'], d[colorKey]])),
            symbolSize: d => d[2],
            itemStyle: { opacity: 0.8 },
            label: { show: true, formatter: p => p.data[3], position: 'top', color: '#e8edf2', fontSize: 10 },
            encode: { tooltip: [0,1,2,3,4] }
        }]
    });
    return chart;
}

// ================================================================
// 堆叠柱状图 (情感分布)
// ================================================================
function createStackedBar(domId, categories, posData, neuData, negData) {
    const chart = echarts.init(document.getElementById(domId));
    chart.setOption({
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
        legend: { data: ['正面', '中性', '负面'], textStyle: { color: '#8899aa' }, top: 5 },
        grid: { left: '15%', right: '5%', top: '15%', bottom: '5%' },
        xAxis: { type: 'value', max: 100, axisLabel: { color: '#8899aa', formatter: '{value}%' },
            splitLine: { lineStyle: { color: '#2a3a4a' } } },
        yAxis: { type: 'category', data: categories, axisLabel: { color: '#e8edf2', fontSize: 10 } },
        series: [
            { name: '正面', type: 'bar', stack: 'total', data: posData, itemStyle: { color: '#2ecc71' }, barMaxWidth: 22 },
            { name: '中性', type: 'bar', stack: 'total', data: neuData, itemStyle: { color: '#f1c40f' } },
            { name: '负面', type: 'bar', stack: 'total', data: negData, itemStyle: { color: '#e94560' } },
        ]
    });
    return chart;
}

// ================================================================
// 雷达图
// ================================================================
function createRadarChart(domId, brandData, maxValues) {
    const chart = echarts.init(document.getElementById(domId));
    const indicators = [
        { name: '情感得分', max: maxValues[0] || 1 },
        { name: '评分', max: maxValues[1] || 5 },
        { name: '正面占比', max: maxValues[2] || 1 },
        { name: '销量', max: maxValues[3] || 20000 },
        { name: '评论数', max: maxValues[4] || 1000 },
    ];
    chart.setOption({
        radar: {
            indicator: indicators,
            shape: 'polygon',
            splitArea: { areaStyle: { color: ['rgba(52,152,219,0.05)', 'rgba(52,152,219,0.1)'] } },
            axisName: { color: '#8899aa' },
        },
        series: brandData.map((bd, i) => ({
            type: 'radar',
            data: [{ value: bd.values, name: bd.name }],
            symbol: 'circle',
            symbolSize: 5,
            lineStyle: { width: 2, color: BRAND_COLORS[i] },
            areaStyle: { color: BRAND_COLORS[i], opacity: 0.15 },
            itemStyle: { color: BRAND_COLORS[i] },
        }))
    });
    return chart;
}

// ================================================================
// 热力图 (品牌 × 维度矩阵)
// ================================================================
function createHeatmap(domId, xLabels, yLabels, data) {
    const chart = echarts.init(document.getElementById(domId));
    chart.setOption({
        tooltip: { position: 'top' },
        grid: { left: '18%', right: '5%', top: '5%', bottom: '10%' },
        xAxis: { type: 'category', data: xLabels, axisLabel: { color: '#8899aa', fontSize: 10, rotate: 30 },
            splitArea: { show: true } },
        yAxis: { type: 'category', data: yLabels, axisLabel: { color: '#e8edf2', fontSize: 10 },
            splitArea: { show: true } },
        visualMap: { min: 0, max: Math.max(...data.map(d => d[2])), calculable: true,
            orient: 'horizontal', left: 'center', bottom: 0, inRange: { color: ['#1a2736', '#2ecc71'] },
            textStyle: { color: '#8899aa' } },
        series: [{ type: 'heatmap', data: data, label: { show: true, color: '#e8edf2', fontSize: 10 },
            emphasis: { itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.5)' } } }]
    });
    return chart;
}

// ================================================================
// 分组柱状图 (模型对比)
// ================================================================
function createGroupedBar(domId, categories, seriesData) {
    const chart = echarts.init(document.getElementById(domId));
    chart.setOption({
        tooltip: { trigger: 'axis' },
        legend: { data: seriesData.map(s => s.name), textStyle: { color: '#8899aa' }, top: 5 },
        grid: { left: '10%', right: '5%', top: '20%', bottom: '8%' },
        xAxis: { type: 'category', data: categories, axisLabel: { color: '#e8edf2', rotate: 20, fontSize: 10 } },
        yAxis: { type: 'value', axisLabel: { color: '#8899aa' }, splitLine: { lineStyle: { color: '#2a3a4a' } } },
        series: seriesData.map(s => ({
            name: s.name, type: 'bar', data: s.data,
            itemStyle: { borderRadius: [4,4,0,0] }, barMaxWidth: 30,
            label: { show: true, position: 'top', color: '#8899aa', fontSize: 9,
                formatter: p => p.value.toFixed(3) }
        }))
    });
    return chart;
}

// ================================================================
// 工具：API 请求
// ================================================================
async function fetchAPI(endpoint) {
    const resp = await fetch(endpoint);
    if (!resp.ok) throw new Error(`API error: ${resp.status}`);
    return resp.json();
}

// ================================================================
// 响应式图表 resize
// ================================================================
window.addEventListener('resize', () => {
    document.querySelectorAll('.chart-container').forEach(el => {
        const instance = echarts.getInstanceByDom(el);
        if (instance) instance.resize();
    });
});

// ================================================================
// 汉堡菜单切换
// ================================================================
function toggleMenu() {
    document.querySelector('.navbar-nav').classList.toggle('open');
}
document.addEventListener('click', (e) => {
    if (!e.target.closest('.navbar')) {
        document.querySelector('.navbar-nav')?.classList.remove('open');
    }
});

// ================================================================
// Loading Skeleton
// ================================================================
function showLoading(containerId) {
    const el = document.getElementById(containerId);
    if (el) { el.innerHTML = '<div class="skeleton"></div><p class="loading-text">加载中...</p>'; }
}
function hideLoading(containerId) {
    const el = document.getElementById(containerId);
    if (el) { el.querySelector('.skeleton')?.remove(); el.querySelector('.loading-text')?.remove(); }
}

// ================================================================
// 回到顶部按钮
// ================================================================
document.addEventListener('DOMContentLoaded', () => {
    const btn = document.createElement('button');
    btn.className = 'back-to-top';
    btn.innerHTML = '↑';
    btn.title = '回到顶部';
    btn.onclick = () => window.scrollTo({ top: 0, behavior: 'smooth' });
    document.body.appendChild(btn);

    window.addEventListener('scroll', () => {
        btn.classList.toggle('visible', window.scrollY > 500);
    });
});

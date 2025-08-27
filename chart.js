am5.ready(function () {
    var root = am5.Root.new("chartdiv");

    root.setThemes([am5themes_Animated.new(root)]);

    var stockChart = root.container.children.push(
        am5stock.StockChart.new(root, {})
    );

    var mainPanel = stockChart.panels.push(
        am5stock.StockPanel.new(root, {
            wheelY: "zoomX",
            panX: true,
            panY: true
        })
    );

    var valueAxis = mainPanel.yAxes.push(
        am5xy.ValueAxis.new(root, {
            renderer: am5xy.AxisRendererY.new(root, {})
        })
    );

    var dateAxis = mainPanel.xAxes.push(
        am5xy.DateAxis.new(root, {
            baseInterval: { timeUnit: "day", count: 1 },
            renderer: am5xy.AxisRendererX.new(root, {})
        })
    );

    var series = mainPanel.series.push(
        am5xy.LineSeries.new(root, {
            name: "Members",
            xAxis: dateAxis,
            yAxis: valueAxis,
            valueYField: "value",
            valueXField: "date"
        })
    );

    // Replace this with data fetched from your Python bot
    fetch("data.json")
        .then(res => res.json())
        .then(data => {
            series.data.setAll(data);
        });

    series.appear(1000);
    stockChart.appear(1000, 100);
});

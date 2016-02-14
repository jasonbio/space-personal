    getData();

    function getData() {
        $.get("/ajax/get_host_stats", function(resp) {
            memory = resp['memory']
            cpu_user = resp['cpu_user']
            cpu_system = resp['cpu_system']
            cpu_guest = resp['cpu_guest']
            dates = resp['dates']
            iowait = resp['iowait']
            max_memory = resp['max_memory'][0]
            max_memory_arr = resp['max_memory']
            console.log(max_memory) 
            d = new Date();
            d2 = new Date();
            d2.setHours(d.getHours() - 1);

            makeMemory();
            makeCPU();
            makeIOwait();
        });
    };

    function makeMemory() {
       $('#memory').highcharts({
        title: {
            text: ""
        },
        yAxis: {
            title: {
                text: 'Memory Used (MB)'
            },
            plotLines: [{
                value: 0,
                width: 1,
                color: '#808080'
            }]
        },
        xAxis: {
            title: {
                text: "Minutes Ago"
            },
            categories: [ 60, 59, 58, 57, 56, 55, 54, 53, 52, 51, 50, 49, 48, 47, 46, 45, 44, 43, 42, 41, 40, 39, 38, 37, 36, 35, 34, 33, 32, 31, 30, 29, 28, 27, 26, 25, 24, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1],
            tickInterval:10
        },
        tooltip: {
            valueSuffix: 'MB',
            shared: 'true'
        },
        legend: {
            enabled:false
        },
        credits: {
            enabled:false
        },
        series: [{
            name: 'Memory Total (MB)',
            data: max_memory_arr,
            type: 'area',
            color: '#FFA161'
        },
        {
            name: 'Memory Used (MB)',
            data: memory,
            type: 'area',
            color: '#ff802b'
        }]
    }); 
    };

    function makeCPU() {
       $('#cpu').highcharts({
        title: {
            text: ""
        },
        yAxis: {
            max: 100,
            title: {
                text: 'CPU Used (%)'
            },
            plotLines: [{
                value: 0,
                width: 1,
                color: '#808080'
            }]
        },
        xAxis: {
            title: {
                text: "Minutes Ago"
            },
            categories: [ 60, 59, 58, 57, 56, 55, 54, 53, 52, 51, 50, 49, 48, 47, 46, 45, 44, 43, 42, 41, 40, 39, 38, 37, 36, 35, 34, 33, 32, 31, 30, 29, 28, 27, 26, 25, 24, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1],
            tickInterval:10
        },
        tooltip: {
            valueSuffix: '%',
            shared: true
        },
        plotOptions: {
            area: {
                stacking: 'normal'
            }
        },
        legend: {
            enabled:false
        },
        credits: {
            enabled:false
        },
        series: [{
            name: 'CPU User (%)',
            data: cpu_user,
            type: 'area',
            color: '#FFA161'
        },
        {
            name: 'CPU Guest (%)',
            data: cpu_guest,
            type: 'area',
            color: '#ff802b'
        },
        {
            name: 'CPU System (%)', 
            data: cpu_system,
            type: 'area',
            color: '#ff6700'
        }]
    });
    };

    function makeIOwait() {
       $('#iowait').highcharts({
        title: {
            text: ""
        },
        yAxis: {
            max: 100,
            title: {
                text: 'IOWait (%)'
            },
            plotLines: [{
                value: 0,
                width: 1,
                color: '#808080'
            }]
        },
        xAxis: {
            title: {
                text: "Minutes Ago"
            },
            categories: [ 60, 59, 58, 57, 56, 55, 54, 53, 52, 51, 50, 49, 48, 47, 46, 45, 44, 43, 42, 41, 40, 39, 38, 37, 36, 35, 34, 33, 32, 31, 30, 29, 28, 27, 26, 25, 24, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1],
            tickInterval:10
        },
        tooltip: {
            valueSuffix: '%'
        },
        legend: {
            enabled:false 
        },
        credits: {
            enabled:false
        },
        series: [{
            name: 'IOWait (%)',
            data: iowait,
            type: 'area',
            color: '#FFA161'
        }]
    });
    };

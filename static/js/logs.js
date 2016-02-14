    function URL_add_parameter(url, param, value){
    var hash       = {};
    var parser     = document.createElement('a');

    parser.href    = url;

    var parameters = parser.search.split(/\?|&/);

    for(var i=0; i < parameters.length; i++) {
        if(!parameters[i])
            continue;

        var ary      = parameters[i].split('=');
        hash[ary[0]] = ary[1];
    }

    hash[param] = value;

    var list = [];
    Object.keys(hash).forEach(function (key) {
        list.push(key + '=' + hash[key]);
    });

    parser.search = '?' + list.join('&');
    return parser.href;
    }

    function checkURL() {
        var url = window.location['search'];
        console.log(url);
        if (url != "")
        {
            return false;
        }
        else
        {
            return true;
        }
    }

    function appendDay() {
        location.href = URL_add_parameter(location.href, 'date', 'day');
    }
    function appendWeek() {
        location.href = URL_add_parameter(location.href, 'date', 'week');
    }
    function appendMonth() {
        location.href = URL_add_parameter(location.href, 'date', 'month');
    }
    function appendAll() {
        location.href = URL_add_parameter(location.href, 'date', 'all');
    }
    function appendDebug() {
        location.href = URL_add_parameter(location.href, 'level', '1');
    }
    function appendWarning() {
        location.href = URL_add_parameter(location.href, 'level', '2');
    }
    function appendError() {
        location.href = URL_add_parameter(location.href, 'level', '3');
    }
    function appendPage(page) {
        location.href = URL_add_parameter(location.href, 'page', page);
    }


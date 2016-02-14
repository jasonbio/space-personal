$(document).ready(function() {
    $('.do').hide()
    $('.linode').hide()
    $('.local').show()
});

$('.provider_select').on('change', function() {
    var selection = this.value
    console.log("it changed")
    switch(selection) {
        case 'local':
            $('.do').hide()
            $('.linode').hide()
            $('.local').show()
            break;
        case 'do':
            $('.local').hide()
            $('.linode').hide()
            $('.do').show()
            break;
        case 'linode':
            $('.local').hide()
            $('.do').hide()
            $('.linode').show()
    }
});


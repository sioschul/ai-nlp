$(document).ready(function(){
    path = localStorage.getItem("path_to_graph");
    if (path == 'None.png'){
        $('#display').html('We could not find enough relations!')
    } else{
        url = 'static/images/'+path
        $('#display').html('<img src='+url+' alt=\"Graph\">');
    }
});
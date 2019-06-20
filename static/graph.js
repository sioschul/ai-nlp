$(document).ready(function(){
    path = localStorage.getItem("path_to_graph");
    url = 'static/images/'+path
    $('#display').html('<img src='+url+' alt=\"Graph\">');
});
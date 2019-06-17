$(document).ready(function(){
    var sentences;
    $.ajax({
			url: '/load-display-text',
		 	method: 'GET',
		 	cache: false,
		 	datatype: "text",
		 	success: function(data){
		 	    sentences = data.split('+;');
            }
    });
    $.ajax({
			url: '/load-entities',
		 	method: 'GET',
		 	cache: false,
		 	datatype: "text",
		 	success: function(data){
		 	    var keys = data.split(',');
		 	    // change all entities to spans which trigger get_picture on click
		 	    for (var i = 0; i < sentences.length; i++){
		 	        var sentence = sentences[i].split(' ');
                    for (var j = 0; j < sentence.length; j++){
                        check = sentence[j].replace(/[~`!@#$%^&*(){}\[\];:"'<,.>?\/\\|_+=-]/g,'');
                        if(keys.includes(check)){
                            sentences[i] = sentences[i].replace(sentence[j],
                            '<span class=\"entity\" data-line=\"'+i+'\">'+sentence[j]+'</span>');
                        }
                    }
                }
                for (var i = 0; i < sentences.length; i++){
                    $('#display').append(sentences[i]+' ');
                }
            }
    });
});
$('#display').on('click','.entity', function(){
    var elem = $(this).text().replace(/[~`!@#$%^&*(){}\[\];:"'<,.>?\/\\|_+=-]/g,'');
    var e = $(this)
    var line_num = e.attr('data-line');
    get_picture(elem, line_num);
});

function get_picture(entity, line_number){
    alert('Worked' + entity +' '+line_number);
}
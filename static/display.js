$(document).ready(function(){
    var sentences;
    var copy_sentences;
    $.ajax({
			url: '/load-display-text',
		 	method: 'GET',
		 	cache: false,
		 	datatype: "text",
		 	success: function(data){
		 	    sentences = data.split('+;');
		 	    // create deep copy
		 	    copy_sentences = $.extend(true, [], sentences)
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
                        var check = sentence[j].replace(/[~`!@#$%^&*(){}\[\];:"'<,.>?|+=-]/g,'');
                        if(j+1 < sentence.length){
                            var check2 = sentence[j+1].replace(/[~`!@#$%^&*(){}\[\];:"'<,.>?|+=-]/g,'');
                        }
                        // mark entities and make them clickable
                        // distinguish between multi and single word entities
                        if(keys.includes(check)){
                            entity = check
                            sentences[i] = sentences[i].replace(entity,
                            '<span class=\"entity\" data-line=\"'+i+'\" style=\"cursor:pointer\">'+entity+'</span>');
                        } else if (keys.includes(check+'_'+check2))
                        {
                            entity = sentence[j]+' '+sentence[j+1]
                            sentences[i] = sentences[i].replace(entity,
                            '<span class=\"entity\" data-line=\"'+i+'\" style=\"cursor:pointer\">>'+entity+'</span>');
                        }
                        }
                    }
                for (var i = 0; i < sentences.length; i++){
                    $('#display').append(sentences[i]+' ');
                }
            }
    });
    // get the entity and the sentence it is in when clicking on the entity in the displayed text
    $('#display').on('click','.entity', function(){
        var elem = $(this).text().replace(/[~`!@#$%^&*(){}\[\];:"'<,.>?|+=-]/g,'');
        var e = $(this)
        var line_num = e.attr('data-line');
        generate_graph(elem, parseInt(line_num));
    });

    function generate_graph(entity, line_number){
        $.ajax({
			url: '/generate-graph/'+entity+'/'+copy_sentences[line_number],
		 	method: 'GET',
		 	cache: false,
		 	datatype: "text",
		 	success: function(data){
                localStorage.setItem("path_to_graph", data);
                document.location.assign('/graph')
            }
        });
    }
});
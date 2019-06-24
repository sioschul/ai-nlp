$("#owntext").on("keyup", function(event) {
  if (event.keyCode === 13) {
   event.preventDefault();
   $("#submit1").click();
  }
});
$("#submit1").click(function(){
     var text = $('#owntext').val();
     if(text==''||text.split('.').length < 3){
        alert('Insert at least 3 sentences!')
     } else{
        	$.ajax({
			    url: '/owntext/'+ text,
		 	    method: 'POST',
		 	    datatype: "text",
		 	    success: function(data){
		 		    if(data=='1'){
                        document.location.assign('/display')
		 		    } else{
		 			    alert('Something went wrong!')
		 		    }
		 	    }
		    });
     }
})
function load_book(number){
		$.ajax({
			url: '/load-book/'+number,
		 	method: 'POST',
		 	datatype: "text",
		 	success: function(data){
		 		if(data=='1'){
                	document.location.assign('/select')
		 		} else{
		 			alert('Something went wrong!')
		 		}
		 	}
		});
}
$("#point").on("keyup", function(event) {
  if (event.keyCode === 13) {
   event.preventDefault();
   $("#submit2").click();
  }
});
$("#submit2").click(function(){
     var point = $('#point').val();
     if(point==''){
        alert('Insert a value between 1 and 100!')
     } else{
        var point_str = point.replace('%','');
        var point_int = parseInt(point_str, 10);
        // check if a valid point was chosen
        if(point_int<1 || point_int>100){
            alert('Invalid point in book!')
        } else{
        	$.ajax({
			    url: '/point-book/'+ point_str,
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
     }
})
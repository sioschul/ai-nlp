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
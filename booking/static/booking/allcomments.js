function showAllComm(allcomm) {
	fetch(`/all_comm`, {
		method: 'POST',
		body: JSON.stringify({
			hot_id: allcomm
		})	
	})
    .then(response => response.json())
    .then(comments => {
		console.log(comments);

		if (comments.length>0){

		document.querySelector(`#divallcomm-${allcomm}`).innerHTML = `<p><b>Comments:</b></p>`;

		comments.forEach((comment) => {
			const elem = document.createElement('div');
			elem.innerHTML = `						
			<p>${comment.com_text}</p>
			<p><b>by: </b>${comment.com_us}</p>
			`;
 
            elem.className = "elem";
            
            document.querySelector(`#divallcomm-${allcomm}`).append(elem);
            
        })

		}
		else {document.querySelector(`#divallcomm-${allcomm}`).innerHTML = `<p><b>There are no Comments</b></p>`;}


		
		cm = document.querySelector(`#allcomm-${allcomm}`);
		
		if (cm.innerHTML.trim() === 'See all comments on this hotel') {
			cm.innerHTML = 'Hide comments';
			document.querySelector(`#divallcomm-${allcomm}`).style.display = 'block'			
			}
		else{
			cm.innerHTML = 'See all comments on this hotel'
			document.querySelector(`#divallcomm-${allcomm}`).style.display = 'none'
			}
		
		



	})
}





document.addEventListener('DOMContentLoaded', function() {
	document.querySelectorAll('button').forEach(button => {
		button.onclick = function() {
			if (this.dataset.allcomm){
				showAllComm(this.dataset.allcomm);
			}
			
		}
	})
	
})
		
		
						

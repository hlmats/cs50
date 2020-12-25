function showPostId(postid) {
	bod = document.querySelector(`#comm-body-${postid}`);
	sbm = document.querySelector(`#comm-submit-${postid}`);
							
	sbm.disabled = true;
	sbm.className = "off";

	bod.onkeyup = () => {
		console.log('ok')
		if (bod.value.length > 0) {
			console.log('ok')
			sbm.disabled = false;
			sbm.className = "on";
		}
		else {
			console.log('nok')
			sbm.disabled = true;
			sbm.className = "off";
		}
	}		
	
}





function showOldBookCommId(oldbookcomm) {
	fetch(`/comm_us`, {
		method: 'POST',
		body: JSON.stringify({
			reserv_id: oldbookcomm
		})	
	})
    .then(response => response.json())
    .then(comments => {
		console.log(comments);

		if (comments.length>0){

		document.querySelector(`#divcomm-${oldbookcomm}`).innerHTML = `<p><b>Your Comments:</b></p>`;

		comments.forEach((comment) => {
			const elem = document.createElement('div');
			elem.innerHTML = `						
			<p>${comment.com_text}</p>						
			`;
 
            elem.className = "elem";
            
            document.querySelector(`#divcomm-${oldbookcomm}`).append(elem);
            
        })

		}
		else {document.querySelector(`#divcomm-${oldbookcomm}`).innerHTML = `<p><b>You have no Comments</b></p>`;}


		
		cm = document.querySelector(`#oldbookcomm-${oldbookcomm}`);
		
		if (cm.innerHTML.trim() === 'See your comments on this hotel') {
			cm.innerHTML = 'Hide comments';
			document.querySelector(`#divcomm-${oldbookcomm}`).style.display = 'block'			
			}
		else{
			cm.innerHTML = 'See your comments on this hotel'
			document.querySelector(`#divcomm-${oldbookcomm}`).style.display = 'none'
			}
		
		



	})
}





document.addEventListener('DOMContentLoaded', function() {
	document.querySelectorAll('button').forEach(button => {
		button.onclick = function() {
			if (this.dataset.postid){
				document.querySelector(`#text-comm-${this.dataset.postid}`).style.display = "block";
				document.querySelector(`#item-comm-${this.dataset.postid}`).style.display = "none";
				showPostId(this.dataset.postid);
			}
			else if(this.dataset.oldbookcomm){
				showOldBookCommId(this.dataset.oldbookcomm);
			}
		}
	})
	
})
		
		
						

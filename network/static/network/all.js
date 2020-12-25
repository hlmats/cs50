function showPostId(postid) {
	bod = document.querySelector(`#edit_post-body-${postid}`);
	sbm = document.querySelector(`#edit_post-submit-${postid}`);
							
	sbm.disabled = false;
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




function showPoster(poster) {
	fol = document.querySelector(`#post-poster-${poster}`);

	count = document.querySelector('#f1');
			
	if (fol.innerHTML.trim() === 'follow') {
		fol.innerHTML = 'unfollow';
		count.textContent++
		
		fetch(`/follow_to`, {
		method: 'POST',
		body: JSON.stringify({
			poster: poster,
			fol: 'follow'
			})
		})
		
		}
	else{
		fol.innerHTML = 'follow';
		count.textContent--
		
		fetch(`/follow_to`, {
		method: 'POST',
		body: JSON.stringify({
			poster: poster,
			fol: 'unfollow'
			})
		})
		
	}
	
}





document.addEventListener('DOMContentLoaded', function() {
	document.querySelectorAll('button').forEach(button => {
		button.onclick = function() {
			if (this.dataset.postid){
				document.querySelector(`#text-edit-${this.dataset.postid}`).style.display = "block";
				document.querySelector(`#post-edit-${this.dataset.postid}`).style.display = "none";
				showPostId(this.dataset.postid);
			}
			else if(this.dataset.poster){
				showPoster(this.dataset.poster);
			}
		}
	})
})
		
		
						

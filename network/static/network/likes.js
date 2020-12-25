function Likes(img) {
	img.addEventListener("click", () => {
		id = img.getAttribute("data-id");
		lk = document.querySelector(`#post-likes-${id}`);
		count = document.querySelector(`#post-numlikes-${id}`);
		post_liked = img.getAttribute("data-post_liked");
		
	
	if (post_liked === 'not_liked') {
		lk.src = "https://img.icons8.com/pastel-glyph/64/000000/thumbs-down--v2.png";
        img.setAttribute("data-post_liked", "liked");
		count.textContent++
	
		fetch(`/likes`, {
			method: 'POST',
			body: JSON.stringify({
				post_id: id,
				numlikes: count.textContent,
				like: 'like'
			})
		})	
	}
	else{
		lk.src = "https://img.icons8.com/pastel-glyph/64/000000/facebook-like.png";
		img.setAttribute("data-post_liked", "not_liked");
		count.textContent--
	
		fetch(`/likes`, {
			method: 'POST',
			body: JSON.stringify({
				post_id: id,
				numlikes: count.textContent,
				like: 'unlike'
			})
		})
	}
})

}






document.addEventListener('DOMContentLoaded', function() {
	document.querySelectorAll('img').forEach(img => {
		Likes(img);				
	})
})
		
		
						

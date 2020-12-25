document.addEventListener('DOMContentLoaded', function() {
    const newSubmit = document.querySelector('#new_post-submit');
    const newPost = document.querySelector('#new_post-body');
	if (newSubmit){
		newSubmit.disabled = true;
		newSubmit.className = "off";

		newPost.onkeyup = () => {
			if (newPost.value.length > 0) {
				newSubmit.disabled = false;
				newSubmit.className = "on";
			}
			else {
				newSubmit.disabled = true;
				newSubmit.className = "off";
			}
		}
	}
})
 



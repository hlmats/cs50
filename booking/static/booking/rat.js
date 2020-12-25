function showRatId(ratid) {
	sbm = document.querySelector(`#rat-submit-${ratid}`);
							
	sbm.disabled = false;
	sbm.className = "on";
	
	
}




document.addEventListener('DOMContentLoaded', function() {
	document.querySelectorAll('input').forEach(input => {
		input.oninput = function() {
			if (this.dataset.ratid){
				showRatId(this.dataset.ratid);
			}
			
		}
	})
})
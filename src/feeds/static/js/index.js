function articleClick() {
    'use strict';
    let links = document.getElementsByClassName('article-link');
    for (let i = 0; i < links.length; i++) {
        links[i].addEventListener('click', function(event) {
            let xhttp = new XMLHttpRequest();
            let url = this.getAttribute("href");
            event.preventDefault();
            xhttp.open("POST", this.dataset.link, true);
            xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
            xhttp.send("article=" + this.dataset.pk);
            setTimeout(function(){
                window.location.href = url;
            }, 100);
        });
    }
}


document.addEventListener('DOMContentLoaded', (event) => {
  'use strict';
  articleClick();
});

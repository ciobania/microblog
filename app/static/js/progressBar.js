function check_progress(task_id) {
    console.log("called check progress function");
    const progressBar = document.getElementById(task_id);
    $.get('progress/' + task_id, function(progress) {
        console.log(progress);
        progressBar.style.setProperty('--width', progress);
        progressBar.setAttribute("data-label", progress + "%");
        setTimeout(check_progress, 2000, task_id);
        });
}
export async function JobRunsTitle(pidValue) {
  fetch("/api/jobs/" + pidValue)
    .then((response) => response.json())
    .then((data) => {
      const titleElem = document.getElementsByTagName("h1")[0];
      if (titleElem && data) {
        titleElem.innerHTML = data.title;
      }
    });
}
